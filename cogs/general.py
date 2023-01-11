"""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""

import json, os, platform, sys, random, aiohttp, disnake
from disnake import ApplicationCommandInteraction, Option, OptionType
from disnake.ext import commands
from disnake.ext.commands import Context

from helpers import checks

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

#Add what needs to be loaded from config.json
GUILDID = int(config["GUILD_ID"])

class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="botinfo",
        description="Get some useful (or not) information about the bot.",
    )
    @checks.not_blacklisted()
    async def botinfo(self, context: Context):
        """
        Get some useful (or not) information about the bot.
        """
        embed = disnake.Embed(
            description="Used [Krypton's](https://krypt0n.co.uk) template",
            color=0x9C84EF
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner:",
            value="vrol#0480",
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{platform.python_version()}",
            inline=True
        )
        embed.add_field(
            name="Prefix:",
            value="/ (Slash Commands)",
            inline=False
        )
        embed.set_footer(
            text=f"Requested by {context.author}"
        )
        await context.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="ping",
        description="Ping the bot",
    )
    @checks.not_blacklisted()
    async def ping(self, context):
        """
        Check if the bot is alive.
        """
        embed = disnake.Embed(
            title="🍆 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x9C84EF
        )
        await context.send(embed=embed, ephemeral=True)
    
def setup(bot):
    bot.add_cog(General(bot))
