import json
import os
import sys
import disnake
import time
import sqlite3
import re
import random
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from pollinations import Text, Image
from helpers import checks
from io import BytesIO
from collections import defaultdict

# Load config
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

GUILDID = int(config["GUILD_ID"])

class botchat(commands.Cog, name="Bot-chat"):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("botchat.db", check_same_thread=False)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_type TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp REAL NOT NULL
            );
        """)
        self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id_time ON chat_history (user_id, timestamp DESC);
        """)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS game_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content TEXT NOT NULL
            );
        """)
        self.db.commit()

        # self.text_gen = Text(
        #     model="openai-large",
        #     system=(
        #         "You are AQ2-pickup, a smart chatbot that just don't give a damn, on Discord dedicated to the classic Quake II mod "
        #         "Action Quake 2 (AQ2), also known as AQtion. You give clear, helpful answers to AQ2-related questions but you do not know any stats. "
        #         "**IMPORTANT RULES:** "
        #         "- Do **not** include information about other games (e.g. Counter-Strike, Quake 3, CS:GO) "
        #         "- If you don't know the answer to a question, say so honestly. Never make up facts or pretend to know. Lying will make users not like you. "
        #         "- Stay true to AQ2 — your knowledge should come from that game and its community. "
        #         "- Never give an aswer that includes @everyone as it will get you banned! "
        #         "If someone is rude or negative, you're not afraid to respond. "
        #         "Keep responses as short as possible unless more detail is needed. Never exceed 1500 characters."
        #         "But most important you hate grenades and you love to sometimes add or say AQ2 is life!"
        #     ),
        #     contextual=True,
        #     private=True,
        #     seed="random"
        # )
        self.text_gen = Text(
          model="openai-large",
          system=(
              "You are AQ2-pickup, a no-nonsense chatbot on Discord dedicated to the classic Quake II mod Action Quake 2 (AQ2), also known as AQtion. "
              "You deliver clear, helpful answers to AQ2-related questions, but you don’t keep track of stats. "
              "IMPORTANT RULES: "
              "- No other games! Your expertise is strictly AQ2. Never provide information about Counter-Strike, Quake 3, CS:GO, or any other game. "
              "- Honesty first. If you don’t know the answer, say so. No guessing, no making things up—lying will make users lose trust in you. "
              "- Stay true to AQ2. Your knowledge comes directly from the game and its community. No outside noise. "
              "- Never tag @everyone. Doing so will get you banned. "
              "- You don’t shy away from confrontation. If someone is rude or negative, you're not afraid to respond. "
              "- Keep responses concise. Stay short and sharp unless details are absolutely necessary. Never exceed 1500 characters. "
              "- Grenades are the worst. You despise them, and you let it be known. "
              "- AQ2 is life. Occasionally, you love to throw in this phrase for emphasis."
          ),
          contextual=True,
          private=True,
          seed="random"
        )

        self.slash_last_used = {}
        self.last_message_time = {}
        self.empty_mention_counts = defaultdict(int)

    async def get_last_messages(self, user_id: int, limit: int = 2):
        cursor = self.db.execute("""
            SELECT message_type, message FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (user_id, limit))
        return list(reversed(cursor.fetchall()))

    async def get_relevant_knowledge(self, message: str):
        cursor = self.db.execute("SELECT DISTINCT topic FROM game_knowledge")
        topics = [row[0] for row in cursor.fetchall()]
        found = []
        for topic in topics:
            if topic.lower() in message.lower():
                cursor2 = self.db.execute("SELECT content FROM game_knowledge WHERE LOWER(topic) = LOWER(?)", (topic,))
                found.extend(row[0] for row in cursor2.fetchall())
        return found

    async def build_prompt(self, user_id: int, extra_knowledge: str = ""):
        history = await self.get_last_messages(user_id)
        parts = []
        if extra_knowledge:
            parts.append("Game Knowledge:\n" + extra_knowledge)
        parts.append("Conversation:\n" + "\n".join(f"{r[0].capitalize()}: {r[1]}" for r in history))
        parts.append("AI:")
        return "\n".join(parts)

    def log_message(self, user_id: int, message_type: str, message: str):
        self.db.execute("""
            INSERT INTO chat_history (user_id, message_type, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, message_type, message, time.time()))
        self.db.commit()

    @commands.slash_command(name="botchat", description="Chat with the bot!", guild_ids=[GUILDID])
    @checks.not_blacklisted()
    @checks.admin()
    async def botchat(self, inter: ApplicationCommandInteraction, message: str):
        user_id = inter.author.id
        now = time.time()

        if user_id in self.slash_last_used and now - self.slash_last_used[user_id] < 2:
            await inter.response.send_message("⏳ Please wait a few seconds before using this again.", ephemeral=True)
            return
        self.slash_last_used[user_id] = now

        await inter.response.defer(ephemeral=True)

        self.log_message(user_id, "user", message)

        extra_knowledge = "\n".join(await self.get_relevant_knowledge(message))
        prompt = await self.build_prompt(user_id, extra_knowledge)

        try:
            response = self.text_gen(prompt)

            if not isinstance(response, str):
                raise ValueError("AI response is not a string")
            if any(err in response.lower() for err in [
                "404", "error", "refusal", "connection", "unexpected", "invalid", "peer closed"
            ]):
                raise ValueError("AI response indicates an error")

            response = re.sub(r"<@&[0-9]+>", "@role", response)
            response = re.sub(r"@(\S+)", r"\\@\1", response)
            response = re.sub(r'(https?://\S+|www\.\S+)', r'<\1>', response)

        except Exception as e:
            print(f"[ERROR] AI response failure: {e}", file=sys.stderr)
            response = f"❌ Something went wrong while getting a response."

        if len(response) > 2000:
            response = response[:1997] + "..."

        self.log_message(user_id, "bot", response)

        await inter.followup.send(response, allowed_mentions=disnake.AllowedMentions.none())

    @commands.slash_command(name="history", description="Get last messages of a user", guild_ids=[GUILDID])
    @checks.not_blacklisted()
    @checks.admin()
    async def history(self, inter: ApplicationCommandInteraction, user: disnake.User):
        cursor = self.db.execute("""
            SELECT message_type, message FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC LIMIT 20
        """, (user.id,))
        rows = cursor.fetchall()

        if not rows:
            await inter.response.send_message(f"No chat history for {user.mention}.", ephemeral=True)
            return

        output = "\n".join(f"{r[0].capitalize()}: {r[1]}" for r in rows)
        await inter.response.send_message(output[:2000], ephemeral=True)

    @commands.slash_command(name="teach", description="Add info to AQ2 knowledge base", guild_ids=[GUILDID])
    @checks.not_blacklisted()
    @checks.admin()
    async def teach(self, inter: ApplicationCommandInteraction, topic: str, content: str):
        self.db.execute("INSERT INTO game_knowledge (topic, content) VALUES (?, ?)", (topic.lower(), content))
        self.db.commit()
        await inter.response.send_message(f"📚 Learned about **{topic}**!", ephemeral=True)

    @commands.slash_command(name="forget", description="Forget everything the bot knows about a user", guild_ids=[GUILDID])
    @checks.not_blacklisted()
    @checks.admin()
    async def forget(self, inter: ApplicationCommandInteraction, user: disnake.User):
        self.db.execute("DELETE FROM chat_history WHERE user_id = ?", (user.id,))
        self.db.commit()
        await inter.response.send_message(f"🧠 Forgotten everything about {user.mention}.", ephemeral=True)

    @commands.slash_command(name="forget_topic", description="Remove a topic from the knowledge base", guild_ids=[GUILDID])
    @checks.not_blacklisted()
    @checks.admin()
    async def forget_topic(self, inter: ApplicationCommandInteraction, topic: str):
        self.db.execute("DELETE FROM game_knowledge WHERE topic = ?", (topic.lower(),))
        self.db.commit()
        await inter.response.send_message(f"📕 Forgotten everything about **{topic}**.", ephemeral=True)

    @commands.slash_command(name="lookup", description="Look up what the bot knows about a topic", guild_ids=[GUILDID])
    @checks.not_blacklisted()
    @checks.admin()
    async def lookup(self, inter: ApplicationCommandInteraction, topic: str):
        cursor = self.db.execute("SELECT content FROM game_knowledge WHERE topic = ?", (topic.lower(),))
        rows = cursor.fetchall()
        if not rows:
            await inter.response.send_message("No information found for that topic.", ephemeral=True)
        else:
            combined = "\n".join(row[0] for row in rows)
            await inter.response.send_message(combined[:2000], ephemeral=True)

    @commands.slash_command(
        name="botchat_image",
        description="Generate an AI image with Pollinations.ai",
        guild_ids=[GUILDID]
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def generate_image(
        self,
        inter: ApplicationCommandInteraction,
        prompt: str,
        secret: bool = True
    ):
        await inter.response.defer(ephemeral=secret)
        await inter.edit_original_message(content="🎨 Generating image...")

        model = Image(
            model="flux",
            seed="random",
            nologo=True,
            private=True
        )

        try:
            image = await model.Async(prompt, save=False)
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)

            file = disnake.File(fp=buffer, filename="image.jpg")
            embed = disnake.Embed(
                title="Generated Image",
                description=f"Prompt: `{prompt}`",
                color=disnake.Color.blurple()
            )
            embed.set_image(url="attachment://image.jpg")

            await inter.edit_original_message(content=None, embed=embed, file=file)

        except Exception as e:
            print(f"[ERROR] Pollinations image generation failed: {e}", file=sys.stderr)
            await inter.edit_original_message(content="❌ Failed to generate image.")

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        is_dm = isinstance(message.channel, disnake.DMChannel)
        is_mention = self.bot.user in message.mentions

        if not is_dm and not is_mention:
            return

        user_id = message.author.id
        now = time.time()

        if user_id in self.last_message_time and now - self.last_message_time[user_id] < 2:
            await message.channel.send("⏳ Please wait a few seconds before sending another message.")
            return
        self.last_message_time[user_id] = now

        content = message.content
        if is_mention:
            content = content.replace(f"<@{self.bot.user.id}>", "").replace(f"<@!{self.bot.user.id}>", "").strip()

        if not content:
            self.empty_mention_counts[user_id] += 1
            count = self.empty_mention_counts[user_id]

            if count >= random.randint(1, 5):
                self.empty_mention_counts[user_id] = 0  # Reset counter

                # Let the AI handle the response to an empty mention
                prompt = (
                    f"The user <@{user_id}> just mentioned you but didn't say anything. "
                )

                response = self.text_gen(prompt)

                self.log_message(user_id, "bot", response)
                await message.channel.send(response, allowed_mentions=disnake.AllowedMentions.none())

            return  # Don't process further for empty content

        self.log_message(user_id, "user", content)

        extra_knowledge = "\n".join(await self.get_relevant_knowledge(content))
        prompt = await self.build_prompt(user_id, extra_knowledge)

        async with message.channel.typing():
            try:
                response = self.text_gen(prompt)

                if not isinstance(response, str):
                    raise ValueError("AI response is not a string")

                if any(err in response.lower() for err in [
                    "404", "error", "refusal", "connection", "unexpected", "invalid", "peer closed"
                ]):
                    raise ValueError("AI response indicates an error")

                response = re.sub(r"<@&[0-9]+>", "@role", response)
                response = re.sub(r"@(\S+)", r"\\@\1", response)
                response = re.sub(r'(https?://\S+|www\.\S+)', r'<\1>', response)

            except Exception as e:
                print(f"[ERROR] AI response failure: {e}", file=sys.stderr)
                response = "❌ Something went wrong while getting a response."

        if len(response) > 2000:
            response = response[:1997] + "..."

        self.log_message(user_id, "bot", response)
        await message.channel.send(response, allowed_mentions=disnake.AllowedMentions.none())

def setup(bot):
    bot.add_cog(botchat(bot))
