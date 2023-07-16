"""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""
import json
import logging
import pyrcon
import re
import subprocess
import os
import disnake
import sys
from tabulate import tabulate
from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from helpers import checks

# Only if you want to use variables that are in the config.json file.
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

# Load the servers data from file
with open('servers.json', 'r') as f:
    data = json.load(f)
    server_choices = []
    for server in data['servers']:
        server_choices.append(server['name'])

logging.basicConfig(level=logging.INFO)

#Add what needs to be loaded from config.json
GUILDID = int(config["GUILD_ID"])
MVD2URL = config["MVD2URL"]
qs = config["QSTAT"]
       
class Aq2(commands.Cog, name="AQ2-slash"):
    def __init__(self, bot):
        self.bot = bot
        
    """AQ2 commands below here"""

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="status",
        description="Get status from the different servers.",
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def status(self, interaction: ApplicationCommandInteraction, servers: str = commands.Param(name="server", choices=server_choices)):
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if server['name'] == servers:
                ip = server['ip']
                port = server['port']
                rcon = server['rcon']
                conn = pyrcon.Q2RConnection(ip, port, rcon)
                result = conn.send('status v')
                await interaction.send('```yaml\n{}\n```'.format(result), ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="changemap",
        description="Change map on server.",
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def changemap(self, interaction: ApplicationCommandInteraction, aqserver: str = commands.Param(name="server", choices=server_choices), map: str = commands.Param(name="mapname")) -> None:
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if aqserver in server['name']:
                ip = server['ip']
                port = server['port']
                rcon = server['rcon']
                pyrcon.Q2RConnection(ip, port, rcon).send('gamemap ' + map)
                await interaction.send(f'```yaml\nMap changed to: {map}\nOn server: {aqserver}\n```')

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="lrcon",
        description="To see cmds use listlrconcmds",
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def lrcon(self, interaction: ApplicationCommandInteraction, aqserver: str = commands.Param(choices=server_choices), cmd: str = commands.Param(name='command')) -> None:
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if aqserver in server['name']:
                ip = server['ip']
                port = server['port']
                rcon = server['rcon']
                result = pyrcon.Q2RConnection(ip, port, rcon).send(cmd)
                await interaction.send('```yaml\n{}\n```'.format(result), ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="reset",
        description="Reset the server if something is wrong or for fun just to be an asshole 😄",
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def reset(self, interaction: ApplicationCommandInteraction, aqserver: str = commands.Param(name="server", choices=server_choices)) -> None:
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if aqserver in server['name']:
                ip = server['ip']
                port = server['port']
                rcon = server['rcon']
                pyrcon.Q2RConnection(ip, port, rcon).send(f'recycle Server reset by {interaction.author.display_name}')
                await interaction.send(f'`{aqserver}-server reset by {interaction.author.display_name}!`')

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="last",
        description="See results from the latest map on pickup or cw servers.",
    )
    @checks.not_blacklisted()
    async def last(self, interaction: ApplicationCommandInteraction, result: str = commands.Param(choices={"pickup", "chaos", "cw"})):
        if result .lower()=='pickup':
            file_path = '../matchlogs/pickup.txt'
        elif result .lower()=='cw':
            file_path = '../matchlogs/cw.txt'
        elif result .lower()=='chaos':
            file_path = '../matchlogs/chaos.txt'
        with open(file_path, "r") as f:
            line2 = f.readlines()
        scores = re.match("(.+)> T1 (\d+) vs (\d+) T2 @ (.+)",line2[0])
        if scores:
            date = scores.group(1)
            t1score = scores.group(2)
            t2score = scores.group(3)
            mapname = scores.group(4)
            embedVar = disnake.Embed(
                title = ':map:    {}    '.format(mapname),
                description=date,
                color = 0xE02B2B,
                )
            embedVar.set_footer(text=MVD2URL)
            if not os.path.isfile('./thumbnails/{}.jpg'.format(mapname)):
                file = disnake.File('./thumbnails/map.jpg', filename="map.jpg")
            else:
                file = disnake.File('./thumbnails/{}.jpg'.format(mapname), filename="map.jpg")
            embedVar.set_thumbnail(url="attachment://map.jpg")
            embedVar.add_field(name='Team Uno', value=t1score, inline = True)
            embedVar.add_field(name='Team Dos', value=t2score, inline = True)
            await interaction.send(file=file, embed=embedVar)
        else:
            await interaction.send("`Use pickup, chaos or cw`")

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="check",
        description="Check server.",
    )
    @checks.not_blacklisted()
    async def check(self, interaction: ApplicationCommandInteraction, aqserver: str = commands.Param(choices=server_choices)):
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if aqserver in server['name']:
                ip = server['ip']
                port = server['port']
                s = subprocess.check_output([qs, '-q2s', ip + ':' + port, '-R', '-P', '-sort', 'F', '-json'])
                data = json.loads(s)

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

def setup(bot):
    bot.add_cog(Aq2(bot))
