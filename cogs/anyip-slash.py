"""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""
import json
import subprocess
import os
import sys
from tabulate import tabulate
from disnake.ext import commands
from disnake import ApplicationCommandInteraction, Option, OptionType
from helpers import checks

# Only if you want to use variables that are in the config.json file.
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

#Add what needs to be loaded from config.json
qs = config["QSTAT"]
GUILDID = int(config["GUILD_ID"])

# Here we name the cog and create a new class for the cog.
class anyip(commands.Cog, name="anyip-slash"):
    def __init__(self, bot):
        self.bot = bot

    """AQ2 commands below here"""

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="checkip",
        description="Check server by ip or ip:port.",
        options=[
            Option(
                name="ip",
                description="Fill in ip and/or port to the server.",
                type=OptionType.string,
                required=True
            )
        ],
    )
    @checks.not_blacklisted()
    async def checkip(self, interaction: ApplicationCommandInteraction, ip: str = None):
        if ip is None:
            return await interaction.send("`Shiieeeet.. did you forget the IP?!`")
        try:
            qstat = [qs, '-q2s', f'{ip}', '-R', '-P', '-sort', 'F', '-json']
            s = subprocess.check_output(qstat)
            data = json.loads(s)
            
            if data[0]['status'] in ['offline', 'timeout']:
                await interaction.send(f"The server is offline or not available.")
            else:
                player_headers = ['Player', 'Score', 'Ping']
                player_data = []
                team_data = []

                if 't1' in data[0]['rules'] and 't2' in data[0]['rules']:
                    team_data.append({'Team uno': data[0]['rules']['t1'], 'Team dos': data[0]['rules']['t2']})

                    for player in data[0]['players']:
                        player_data.append([player['name'], player['score'], player['ping']])

                    map = data[0]['map']
                    maptime = data[0]['rules']['maptime']
                    teamscore = tabulate(team_data, headers='keys', tablefmt='rounded_outline', numalign='center')
                    players = tabulate(player_data, headers=player_headers, tablefmt='simple', numalign='center')
                    await interaction.send(f"```json\n{data[0]['name']}\n\nMap: {map}\nTime: {maptime}\n\n{teamscore}\n\n{players}```")
        except subprocess.TimeoutExpired:
            await interaction.send(f"The server did not respond within the expected time.")
        except Exception as e:
            await interaction.send("`Dang it! Invalid IP or not an AQ2-server 🤦‍`")

# And the we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(anyip(bot))
