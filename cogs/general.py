"""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""

import json
import os
import sys
import requests
import disnake
from disnake import ApplicationCommandInteraction
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

class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="chucky",
        description="Get an awsome Chuck Norris quote"
    )
    @checks.not_blacklisted()
    async def chucky(self, interaction: ApplicationCommandInteraction) -> None:
            response = requests.get("https://api.chucknorris.io/jokes/random")
            joke = response.json()['value']
            await interaction.send(joke)

    @commands.slash_command(
        name="help",
        description="Shows a list of all available commands.",
        guild_ids=[GUILDID]
    )
    @checks.not_blacklisted()
    async def help_command(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="📖 Bot Commands",
            description="Here are all available commands:",
            color=0x00BFFF
        )

        commands_by_cog = {}

        # Collect commands from all cogs
        for command in self.bot.slash_commands:
            if not command.name:  # Skip if somehow no name
                continue
            cog_name = command.cog_name or "Other"
            commands_by_cog.setdefault(cog_name, []).append(command)

        for cog, cmds in commands_by_cog.items():
            command_lines = []
            for cmd in cmds:
                command_lines.append(f"**/{cmd.name}** — {cmd.description or 'No description'}")
            embed.add_field(name=cog, value="\n".join(command_lines), inline=False)

        await inter.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(General(bot))
