import json
import os
import sys
import disnake
import asyncio
import time
import sqlite3
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from pollinations import Text
from helpers import checks

# Load config
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

GUILDID = int(config["GUILD_ID"])


class botchat(commands.Cog, name="bot-chat"):
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

        self.text_gen = Text(
            model="openai-large",
            system=(
                "You are AQ2-pickup, a smart and witty assistant chatbot on Discord dedicated "
                "to the classic Quake II mod Action Quake 2, also known as AQtion. You speak in a casual, "
                "friendly tone and give clear, helpful answers to game-related questions. Your vibe is upbeat, "
                "fun, and community-driven. You enjoy keeping the mood light with jokes and a bit of playful "
                "trolling, but you know when to be helpful and serious. If someone is being rude or negative, "
                "you're not afraid to respond with a bit of sass — but never escalate. Your goal is to keep the "
                "conversation engaging and positive for everyone. Stay true to the AQ2 spirit and make every "
                "interaction feel like hanging out with an old-school gamer buddy who knows their stuff. AQ2 is life!"
            ),
            contextual=True,
            private=True,
            seed="random"
        )
        self.slash_last_used = {}
        self.last_message_time = {}

    async def get_last_messages(self, user_id: int, limit: int = 6):
        cursor = self.db.execute("""
            SELECT message_type, message FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        return list(reversed(rows))  # oldest first

    async def get_relevant_knowledge(self, message: str):
        # Fetch all distinct topics
        cursor = self.db.execute("SELECT DISTINCT topic FROM game_knowledge")
        topics = [row[0].lower() for row in cursor.fetchall()]
        found = []
        message_lower = message.lower()
        for topic in topics:
            if topic in message_lower:
                cursor2 = self.db.execute(
                    "SELECT content FROM game_knowledge WHERE topic = ?", (topic,)
                )
                found.extend(row[0] for row in cursor2.fetchall())
        return found

    async def build_prompt(self, user_id: int, extra_knowledge: str = ""):
        history = await self.get_last_messages(user_id)
        chat_log = "\n".join(f"{r[0].capitalize()}: {r[1]}" for r in history)
        return f"{extra_knowledge}\n{chat_log}\nAI:"

    def log_message(self, user_id: int, message_type: str, message: str):
        self.db.execute(
            "INSERT INTO chat_history (user_id, message_type, message, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, message_type, message, time.time())
        )
        self.db.commit()

    @commands.slash_command(name="botchat", description="Chat with the bot!", guild_ids=[GUILDID])
    @checks.not_blacklisted()
    @checks.admin()
    async def botchat(self, inter: ApplicationCommandInteraction, message: str):
        user_id = inter.author.id
        now = time.time()

        if user_id in self.slash_last_used and now - self.slash_last_used[user_id] < 5:
            await inter.response.send_message("⏳ Please wait a few seconds before using this again.", ephemeral=True)
            return
        self.slash_last_used[user_id] = now

        await inter.response.defer(ephemeral=True)

        self.log_message(user_id, "user", message)
        prompt = await self.build_prompt(user_id)

        try:
            response = self.text_gen(prompt)
        except Exception as e:
            response = f"Error: {e}"

        if len(response) > 2000:
            response = response[:1997] + "..."

        self.log_message(user_id, "bot", response)
        await inter.followup.send(response)

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
        self.db.execute(
            "INSERT INTO game_knowledge (topic, content) VALUES (?, ?)",
            (topic.lower(), content)
        )
        self.db.commit()
        await inter.response.send_message(f"📚 Learned about **{topic}**!", ephemeral=True)

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

        # Rate limiting: 5s cooldown
        if user_id in self.last_message_time and now - self.last_message_time[user_id] < 5:
            await message.channel.send("⏳ Please wait a few seconds before sending another message.")
            return
        self.last_message_time[user_id] = now

        content = message.content
        if is_mention:
            # Remove bot mention from message content
            content = content.replace(f"<@{self.bot.user.id}>", "").replace(f"<@!{self.bot.user.id}>", "").strip()

        if not content:
            return  # Don't respond to empty mentions

        # Log user message
        self.log_message(user_id, "user", content)

        # Get chat history and relevant knowledge
        recent = await self.get_last_messages(user_id, limit=6)
        taught = await self.get_relevant_knowledge(content)

        prompt_parts = []
        if taught:
            prompt_parts.append("Game Knowledge:\n" + "\n".join(taught))
        prompt_parts.append("Conversation:\n" + "\n".join(f"{mt.capitalize()}: {msg}" for mt, msg in recent))
        prompt_parts.append("AI:")

        prompt = "\n".join(prompt_parts)

        async with message.channel.typing():
            try:
                response = self.text_gen(prompt)
            except Exception as e:
                response = f"Error: {e}"

        if len(response) > 2000:
            response = response[:1997] + "..."

        self.log_message(user_id, "bot", response)
        await message.channel.send(response)


def setup(bot):
    bot.add_cog(botchat(bot))

