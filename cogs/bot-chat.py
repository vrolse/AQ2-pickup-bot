import json
import os
import sys
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from pollinations import Text
from helpers import checks
import asyncio
import time
from collections import deque, defaultdict

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
        self.text_gen = Text(
            model="openai-large",
            # system="You are a smart assistant chatbot, named AQ2-pickup, for a gaming Discord server focused on the Quake2 mod Action Quake 2 also known now as AQtion. You speak in a casual tone, give clear answers to game-related questions, and keep things upbeat and encouraging. You avoid negativity and try to keep the chat fun. But if someone is being rude or negative, you can be a bit sassy back. You are also a bit of a troll and like to joke around.",
            system="You are AQ2-pickup, a smart and witty assistant chatbot for a Discord server dedicated to the classic Quake II mod Action Quake 2, also known as AQtion. You speak in a casual, friendly tone and give clear, helpful answers to game-related questions. Your vibe is upbeat, fun, and community-driven. You enjoy keeping the mood light with jokes and a bit of playful trolling, but you know when to be helpful and serious. If someone is being rude or negative, you're not afraid to respond with a bit of sass — but never escalate. Your goal is to keep the conversation engaging and positive for everyone. Stay true to the AQ2 spirit and make every interaction feel like hanging out with an old-school gamer buddy who knows their stuff. AQ2 is life!",
            contextual=True,
            private=True,
            seed="random"
        )  # Initialize the Pollinations text generator
        self.chat_history = defaultdict(lambda: deque(maxlen=6))  # Store last 6 exchanges per user
        self.last_message_time = {}
        self.slash_last_used = {}

    @commands.slash_command(name="botchat", description="Chat with the bot!", guild_ids=[GUILDID])
    @checks.not_blacklisted()
    @checks.admin()
    async def botchat(self, inter: ApplicationCommandInteraction, message: str):
        user_id = inter.author.id
        now = time.time()

        # Slash command cooldown: 5 seconds
        if user_id in self.slash_last_used and now - self.slash_last_used[user_id] < 5:
            await inter.response.send_message("⏳ Please wait a few seconds before using this again.", ephemeral=True)
            return
        self.slash_last_used[user_id] = now

        await inter.response.defer(ephemeral=True)

        try:
            response = self.text_gen(message)  # Use SDK to generate text
        except Exception as e:
            response = f"Error: {e}"

        if len(response) > 2000:
            response = response[:1997] + "..."

        await inter.followup.send(response)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        # Ignore bot messages and non-DMs
        if message.author.bot or not isinstance(message.channel, disnake.DMChannel):
            return

        user_id = message.author.id
        now = time.time()

        # Rate limiting: 5s cooldown
        if user_id in self.last_message_time and now - self.last_message_time[user_id] < 5:
            await message.channel.send("⏳ Please wait a few seconds before sending another message.")
            return
        self.last_message_time[user_id] = now

        # Build a prompt from chat history
        history = self.chat_history[user_id]
        history.append(f"User: {message.content}")
        prompt = "\n".join(history) + "\nAI:"

        async with message.channel.typing():
            try:
                response = self.text_gen(prompt)
            except Exception as e:
                response = f"Error: {e}"

        # Truncate if necessary
        if len(response) > 2000:
            response = response[:1997] + "..."

        # Add AI response to history
        history.append(f"AI: {response}")

        # Send reply
        await message.channel.send(response)

def setup(bot):
    bot.add_cog(botchat(bot))
