"""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""
import json, logging, pyrcon, re, subprocess, os, disnake, sys
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
    async def status(self, context, servers: str = commands.Param(name="server", choices=server_choices)):
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if server['name'] == servers:
                ip = server['ip']
                port = server['port']
                rcon = server['rcon']
                conn = pyrcon.Q2RConnection(ip, port, rcon)
                result = conn.send('status v')
                await context.send('```yaml\n{}\n```'.format(result), ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="changemap",
        description="Change map on server.",
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def changemap(self, context, cserver: str = commands.Param(name="server", choices=server_choices), map: str = commands.Param(name="mapname")) -> None:
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if cserver in server['name']:
                ip = server['ip']
                port = server['port']
                rcon = server['rcon']
                pyrcon.Q2RConnection(ip, port, rcon).send('gamemap ' + map)
                await context.send(f'```yaml\nMap changed to: {map}\nOn server: {cserver}\n```')

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="lrcon",
        description="To see cmds use listlrconcmds",
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def lrcon(self, context, cserver: str = commands.Param(choices=server_choices), cmd: str = commands.Param(name='command')) -> None:
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if cserver in server['name']:
                ip = server['ip']
                port = server['port']
                rcon = server['rcon']
                result = pyrcon.Q2RConnection(ip, port, rcon).send(cmd)
                await context.send('```yaml\n{}\n```'.format(result), ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="reset",
        description="Reset the server if something is wrong or for fun just to be an asshole 😄",
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def reset(self, context, cserver: str = commands.Param(name="server", choices=server_choices)) -> None:
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if cserver in server['name']:
                ip = server['ip']
                port = server['port']
                rcon = server['rcon']
                pyrcon.Q2RConnection(ip, port, rcon).send(f'recycle Server reset by {context.author.display_name}')
                await context.send(f'`{cserver}-server reset by {context.author.display_name}!`')

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="last",
        description="See results from the latest map on pickup or cw servers.",
    )
    @checks.not_blacklisted()
    async def last(self, context, result: str = commands.Param(choices={"pickup", "chaos", "cw"})):
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
            await context.send(file=file, embed=embedVar)
        else:
            await context.send("`Use pickup, chaos or cw`")

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="check",
        description="Check server.",
    )
    @checks.not_blacklisted()
    async def check(self, context, cserver: str = commands.Param(choices=server_choices)):
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if cserver in server['name']:
                ip = server['ip']
                port = server['port']
                scores = []
                s = subprocess.check_output([qs, '-q2s', ip + ':' + port, '-R', '-P', '-sort', 'F', '-json'])
                sdata = json.loads(s)
                for te in sdata:
                    print()
                for each in sdata[0]['players']:
                    scores.append("{:>6d} - {}".format(each['score'],each['name']))
                scores = "\n".join(scores)
                nl = '\n'
                await context.send(f"```json{nl}{te['name']}{nl+nl}Map: {te['map']}{nl}Time: {te['rules']['maptime']}{nl+nl}Team1 vs Team2{nl}  {te['rules']['t1']}       {te['rules']['t2']}{nl+nl}Frags:   Players:{nl}{scores}```")

def setup(bot):
    bot.add_cog(Aq2(bot))
