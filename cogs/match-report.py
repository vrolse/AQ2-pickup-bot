"""
Work in Progress:
This cog monitors a log file for new AQ2 match data, processes it using AI, and sends a formatted report to a Discord channel.
"""
import json
import disnake
import re
import requests
import threading
import asyncio
import os
import sys
import hashlib
from openai import OpenAI
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from disnake.ext import commands, tasks

# Load config
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

client = OpenAI(api_key=config["OPENAI_API_KEY"])  # REPLACE with your OpenAI API key
POLLINATIONS_API_KEY = config.get("POLLINATIONS_API_KEY")  # REPLACE with your Pollinations API key

LOG_FILE_PATH = "path/to/your/aq2.log"  # REPLACE with your log file path
DISCORD_CHANNEL_ID = 1234567890  # REPLACE with your channel id

START_MARKER = "The round will begin in 20 seconds!"
END_MARKER = "Match is over, waiting for next map, please vote a new one.."

SYSTEM_PROMPT = (
    "You are a witty, concise, and professional esports commentator. "
    "Summarize the following AQ2 match log with a fun, entertaining, clear, and Discord-formatted commentary (max ~1000 characters). "
    "Highlight exciting plays and major moments, praise players who earn 'Accuracy' or 'Impressive,' and if anyone achieves 'Excellent,' note that they are truly on a hot streak. "
    "Keep the tone fun, punchy, and professional. Do NOT include links or URLs. Always include the final score or result of the match at the end."
)

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    def on_modified(self, event):
        if os.path.realpath(event.src_path) == os.path.realpath(LOG_FILE_PATH):
            asyncio.run_coroutine_threadsafe(self.cog.process_new_match(), self.cog.bot.loop)

class MatchReporter(commands.Cog):
    LAST_HASH_FILE = "last_match_hash.txt"

    def __init__(self, bot):
        self.bot = bot
        self.last_match = None
        self.last_match_hash = self.load_last_match_hash()
        self.log_observer = None
        threading.Thread(target=self.start_log_watcher, daemon=True).start()

    def get_match_hash(self, match_text):
        return hashlib.sha256(match_text.encode("utf-8")).hexdigest()

    def load_last_match_hash(self):
        try:
            with open(self.LAST_HASH_FILE, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def save_last_match_hash(self, match_hash):
        with open(self.LAST_HASH_FILE, "w") as f:
            f.write(match_hash)

    def start_log_watcher(self):
        event_handler = LogFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(LOG_FILE_PATH) or '.', recursive=False)
        observer.start()
        self.log_observer = observer
        print("🟢 Log watcher started.")
        try:
            observer.join()  # Will block until observer is stopped
        except KeyboardInterrupt:
            observer.stop()
            observer.join()

    def extract_latest_match(self):
        try:
            with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return None
        match_section = []
        end_found = False
        for line in reversed(lines):
            if not end_found and END_MARKER in line:
                end_found = True
                match_section.append(line)
                continue
            if end_found:
                match_section.append(line)
                if START_MARKER in line:
                    break
        if not end_found or not match_section:
            return None
        match_section.reverse()
        match_text = "".join(match_section)
        # Clean IPs
        match_text = re.sub(r"(\[)?\d{1,3}(?:\.\d{1,3}){3}:\d{1,5}(\])?", "[REDACTED_IP]", match_text)
        # Remove timestamps like [YYYY-MM-DD HH:MM]
        match_text = re.sub(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]\s?", "", match_text)
        # Remove chat lines
        match_text = re.sub(
            r"^(?:\[DEAD\] (?:\([^)]+\)|[^():\n]+): .*$|\([^)]+\): .*$)",
            "",
            match_text,
            flags=re.MULTILINE
        )
        # Remove empty lines
        match_text = "\n".join([line for line in match_text.splitlines() if line.strip() != ""])
        return match_text.strip()

    def fallback_to_openai(self, content):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content}
                ],
                max_tokens=500,
                temperature=0.8,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ OpenAI fallback failed: {e}")
            return "Error: Major server meltdown. 🫠"

    def send_to_pollinations_ai(self, content, model="openai-large"):
        url = "https://text.pollinations.ai/openai"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {POLLINATIONS_API_KEY}"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            "seed": "random",
            "private": True,
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"⚠️ Pollinations AI failed, falling back to OpenAI: {e}")
            return self.fallback_to_openai(content)

    async def process_new_match(self):
        match_text = self.extract_latest_match()
        if not match_text:
            return

        match_hash = self.get_match_hash(match_text)
        if match_hash == self.last_match_hash:
            return  # Already sent this match

        self.last_match = match_text
        self.last_match_hash = match_hash
        self.save_last_match_hash(match_hash)

        commentary = await asyncio.to_thread(self.send_to_pollinations_ai, match_text)
        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            embed = disnake.Embed(
                title=":trophy: AQ2 Match Report",
                description=f"**AI Commentary:**\n {commentary}",
                color=disnake.Color.green(),
                timestamp=disnake.utils.utcnow()
            )
            embed.set_footer(text="AQ2 Match Reporter • Powered by Pollinations.ai ❤️")
            await channel.send(embed=embed)
        else:
            print("❌ Discord channel not found.")

    def cog_unload(self):
        if self.log_observer:
            self.log_observer.stop()
            self.log_observer.join()

def setup(bot):
    bot.add_cog(MatchReporter(bot))
