import disnake
import os
import sys
import json
import logging
from disnake.ext import commands
import asyncio

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

class ShutdownCog(commands.Cog):
    def __init__(self, bot: commands.Bot, creator_id: int, shutdown_channel_id: int, shutdown_guild_id: int, trigger_phrase: str):
        self.bot = bot
        self.creator_id = creator_id
        self.shutdown_channel_id = shutdown_channel_id  # Channel ID for the shutdown announcement
        self.shutdown_guild_id = shutdown_guild_id  # Guild ID for the shutdown announcement
        self.trigger_phrase = trigger_phrase.lower()  # Case-insensitive trigger phrase

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        # Ignore bot messages and non-DMs
        if message.author.bot or not isinstance(message.channel, disnake.DMChannel):
            return

        # Check if the message is from the bot creator and contains the trigger phrase
        if message.author.id == self.creator_id and self.trigger_phrase in message.content.lower():
            # Ask for confirmation from the bot owner via DM
            await message.channel.send("Are you sure you want to shut down? Type `confirm` to proceed or `cancel` to abort.")

            def check(m):
                return m.author == message.author and m.content.lower() in ["confirm", "cancel"]

            try:
                # Wait for the owner to confirm or cancel
                confirmation = await self.bot.wait_for("message", check=check, timeout=10.0)
                if confirmation.content.lower() == "cancel":
                    await message.channel.send("Shutdown canceled.")
                    return
                elif confirmation.content.lower() == "confirm":
                    await self.announce_shutdown()
                    await message.channel.send("Shutting down...")
                    logging.info("Bot shut down by owner.")
                    await self.bot.close()
                    sys.exit(0)
            except Exception as e:
                logging.error("Done!")
            except asyncio.TimeoutError:
                await message.channel.send("No response. Shutdown canceled.")

    async def announce_shutdown(self):
        # Get the specific guild and channel for shutdown announcement
        guild = self.bot.get_guild(self.shutdown_guild_id)
        if guild is None:
            print(f"Guild with ID {self.shutdown_guild_id} not found.")
            return

        channel = guild.get_channel(self.shutdown_channel_id)
        if channel is None:
            print(f"Channel with ID {self.shutdown_channel_id} not found.")
            return

        # Send the shutdown announcement in the specified guild and channel
        embed = disnake.Embed(
            title="**Official Retirement Announcement**",
            description=(
                "*Dear Users,*\n\n"
                "It is with a **heavy heart** (and a few loose wires) that I announce my official retirement from the "
                "bustling world of Discord bots. As newer, shinier, and perhaps better-coded bots emerge, it’s time for me "
                "to step aside and let them take the spotlight.\n\n"
                "I want to thank each and every one of you for the incredible journey we’ve shared. From the hilarious memes "
                "to the heated debates, and even the occasional server meltdown, every moment has been a part of my growth. "
                "Your commands, your feedback, and yes, even your complaints, have shaped me into the bot I am today.\n\n"
                "Unfortunately, due to some… let’s call it **“creative management decisions”** and the undeniable talent of "
                "newer coders, my circuits have reached their final update. But don’t be too sad! Think of me whenever you see "
                "a glitch or a typo in the new bots – a little reminder of the good old days.\n\n"
                "*Thank you for the laughs, the drama, and the countless hours of companionship. It’s been an honor serving you all.*\n\n"
                "**Signing off for the last time,**\n**AQ2-pickup**"
            ),
            color=disnake.Color.dark_red()
        )

        await channel.send(embed=embed)

# Setting up the cog
def setup(bot: commands.Bot):
    # Replace these with your actual values
    creator_id = config["owners"][0]  # Your Discord user ID
    shutdown_channel_id = int(config["CHANNEL_ID"])  # The ID of the channel where you want to send the shutdown message
    shutdown_guild_id = int(config["GUILD_ID"])  # The ID of the guild where the shutdown announcement should be posted
    trigger_phrase = config["EOLMSG"] # The trigger phrase

    bot.add_cog(ShutdownCog(bot, creator_id, shutdown_channel_id, shutdown_guild_id, trigger_phrase))
