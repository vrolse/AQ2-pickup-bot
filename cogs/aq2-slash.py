import json, configparser, logging, pyrcon, re, subprocess, os, requests, disnake
from random import choices
from disnake import ApplicationCommandInteraction, Option, OptionType
from disnake.ext import commands
from disnake.ext.commands import Context
from helpers import checks

"""
# Only if you want to use variables that are in the config.json file.
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)
"""

config = configparser.ConfigParser()
config.read('config.ini')
VERSION = 'MC4xMQ== //? h4x by TgT (¬_¬)'
GUILDID = int(os.getenv('GUILDID'))
ROLEID = int(os.getenv('ROLEID'))

logging.basicConfig(level=logging.INFO)

servername = config['DEFAULT']['SERVERNAME']
serverport = config['DEFAULT']['SERVERPORT']
rcon_password = config['DEFAULT']['RCON_PASSWORD']
serverport2 = config['DEFAULT']['SERVERPORT2']
serverport3 = config['DEFAULT']['SERVERPORT3']
serverport4 = config['DEFAULT']['SERVERPORT4']
serverport5 = config['DEFAULT']['SERVERPORT5']
serverport6 = config['DEFAULT']['SERVERPORT6']
serverport7 = config['DEFAULT']['SERVERPORT7']

conn = pyrcon.Q2RConnection(servername, serverport, rcon_password)
conn2 = pyrcon.Q2RConnection(servername, serverport2, rcon_password)
conn3 = pyrcon.Q2RConnection(servername, serverport3, rcon_password)
conn4 = pyrcon.Q2RConnection(servername, serverport4, rcon_password)
conn5 = pyrcon.Q2RConnection(servername, serverport5, rcon_password)
conn7 = pyrcon.Q2RConnection(servername, serverport7, rcon_password)


qs = '/home/bot/AQ2-pickup/qstat'
tp = [qs, '-q2s', servername + ':' + serverport, '-R', '-P', '-sort', 'F', '-json']
dmc = [qs, '-q2s', servername + ':' + serverport2, '-R', '-P', '-sort', 'F', '-json']
pickup = [qs, '-q2s', servername + ':' + serverport3, '-R', '-P', '-sort', 'F', '-json']
cw = [qs, '-q2s', servername + ':' + serverport4, '-R', '-P', '-sort', 'F', '-json']
chaos = [qs, '-q2s', servername + ':' + serverport5, '-R', '-P', '-sort', 'F', '-json']
tdm = [qs, '-q2s', servername + ':' + serverport6, '-R', '-P', '-sort', 'F', '-json']
ladder = [qs, '-q2s', servername + ':' + serverport7, '-R', '-P', '-sort', 'F', '-json']
new = [qs, '-q2s', 'IP:PORT', '-R', '-P', '-sort', 'F', '-json']
new2 = [qs, '-q2s', 'IP:PORT', '-R', '-P', '-sort', 'F', '-json']

# Here we name the cog and create a new class for the cog.
class Aq2(commands.Cog, name="AQ2-slash"):
    def __init__(self, bot):
        self.bot = bot
    @commands.slash_command(
        guild_ids=[GUILDID],
        name="iinfo",
        description="Pickupbot info.",
    )
    @checks.not_blacklisted()
    async def info(self, context):
        embed = disnake.Embed(
        title="AQ2-pickup",
        description="Bot to check pickup-server and\nmaybe more to come. :)",
        color=0xeee657
        )
        embed.add_field(
        name="Author",
        value=config['DEFAULT']['AUTHOR']
        )
        embed.add_field(
        name="Bot Version",
        value=VERSION
        )
        await context.send(embed=embed, delete_after=10, ephemeral=True)

    """AQ2 commands below here"""

    @commands.slash_command(
        guild_ids=[GUILDID], #[914515437679689729]
        name="status",
        description="Get status from the different servers.",
    )
    @checks.not_blacklisted()
    @checks.is_owner()
    @commands.has_role(ROLEID)
    async def status(self, context, check: str = commands.Param(name="server", choices=["pickup", "cw", "chaos", "ladder"])) -> None:
        if not check:
            await context.send("`Use one of the following: pickup, cw, chaos, ladder`")
        elif check == "pickup":
            result = conn3.send('status v')
        elif check == "cw":
            result = conn4.send('status v')
        elif check == "ladder":
            result = conn7.send('status v')
        elif check == "chaos":
            result = conn5.send('status v')
        await context.send('```yaml\n{}\n```'.format(result), ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="changemap",
        description="Change map on server.",
    )
    @checks.not_blacklisted()
    @checks.is_owner()
    @commands.has_role(ROLEID)
    async def changemap(self, context, server: str = commands.Param(name="server", choices=["pickup", "cw", "chaos", "ladder"]), map: str = commands.Param(name="mapname")):
        if map is None:
            return await context.send("`You need to write a mapname`")
        if server == "pickup":
            conn3.send('gamemap ' + map)
        elif server == "ladder":
            conn7.send('gamemap ' + map)
        elif server == "cw":
            conn4.send("gamemap " + map)
        elif server == "chaos":
            conn5.send("gamemap " + map)
        await context.send(f'```yaml\nMap changed to: {map}\nOn server: {server}\n```')

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="lrcon",
        description="Test of lrcon. See cmds use list",
    )
    @checks.not_blacklisted()
    @checks.is_owner()
    @commands.has_role(ROLEID)
    async def lrcon(self, context, *, server: str = commands.Param(choices={"pickup", "cw", "chaos", "ladder", "list"}), cmd = True) -> None:
        if server == "list":
            result = conn3.send("listlrconcmds")
            return await context.send('```yaml\n{}\n```'.format(result), ephemeral=True)
        elif server == "pickup":
            result = conn3.send(cmd)
        elif server == "ladder":
            result = conn7.send(cmd)
        elif server == "cw":
            result = conn4.send(cmd)
        elif server == "chaos":
            result = conn5.send(cmd)
        await context.send('```yaml\n{}\n```'.format(result), ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="reset",
        description="Reset the server if something is wrong or for fun just to be an asshole 😄",
    )
    @checks.not_blacklisted()
    @checks.is_owner()
    @commands.has_role(ROLEID)
    async def reset(self, context, *, server: str = commands.Param(choices={"pickup", "cw", "chaos", "ladder"})):
        if server == "pickup":
            conn3.send('recycle Reset server!')
        elif server == "cw":
            conn4.send('recycle Reset server!')
        elif server =="ladder":
            conn7.send('recycle Reset server!')
        elif server == "chaos":
            conn5.send('recycle Reset server!')
        await context.send(f'`{server}-server reset by {context.author}!`')

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="last",
        description="See results from the latest map on pickup or cw server.",
    )
    @checks.not_blacklisted()
    async def last(self, context, result: str = commands.Param(choices={"pickup", "chaos", "cw"})):
        if not result:
            await context.send("`Use pickup, chaos or cw`")
        elif result .lower()=='pickup':
            file_path = '/home/bot/matchlogs2/pickup.txt'
            with open(file_path, "r") as f:
              line2 = f.readlines()
            scores = re.match("(.+)> T1 (\d+) vs (\d+) T2 @ (.+)",line2[0])
            if scores:
                MVD2URL = "https://vrol.se/demos"
                serverName = "aq2.vrol.se:27930"
                date = scores.group(1)
                t1score = scores.group(2)
                t2score = scores.group(3)
                mapname = scores.group(4)
                embedVar = disnake.Embed(
                    title=':map:    {}    '.format(mapname), 
                    description=date, 
                    color=0xE02B2B,
                    )
                embedVar.set_footer(text=MVD2URL)
                file = disnake.File('./thumbnails/{}.jpg'.format(mapname), filename="map.jpg")
                embedVar.set_thumbnail(url="attachment://map.jpg")
                embedVar.add_field(name='Team Uno', value=t1score, inline = True)
                embedVar.add_field(name='Team Dos', value=t2score, inline = True)
                #OldMatch = LastMatch
                await context.send(file=file, embed=embedVar)
        elif result .lower()=='cw':
            file_path = '/home/bot/matchlogs2/cw.txt'
            with open(file_path, "r") as f:
              line2 = f.readlines()
            scores = re.match("(.+)> T1 (\d+) vs (\d+) T2 @ (.+)",line2[0])
            if scores:
                MVD2URL = "https://vrol.se/demos"
                serverName = "aq2.vrol.se:27940"
                date = scores.group(1)
                t1score = scores.group(2)
                t2score = scores.group(3)
                mapname = scores.group(4)
                embedVar = disnake.Embed(
                    title=':map:    {}    '.format(mapname),
                    description=date,
                    color=0xE02B2B,
                    )
                embedVar.set_footer(text=MVD2URL)
                file = disnake.File('./thumbnails/{}.jpg'.format(mapname), filename="map.jpg")
                embedVar.set_thumbnail(url="attachment://map.jpg")
                embedVar.add_field(name='Team Uno', value=t1score, inline = True)
                embedVar.add_field(name='Team Dos', value=t2score, inline = True)
                await context.send(file=file, embed=embedVar)
        elif result .lower()=='chaos':
            file_path = '/home/bot/matchlogs/chaos.txt'
            with open(file_path, "r") as f:
              line2 = f.readlines()
            scores = re.match("(.+)> T1 (\d+) vs (\d+) T2 @ (.+)",line2[0])
            if scores:
              MVD2URL = "https://demos.aq2world.com/"
              serverName = "chaos @ aq2.vrol.se:27950"
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
    async def check(self, context, server: str = commands.Param(choices={"pickup", "cw", "chaos", "ladder"})
    ):
        if server is None:
            return await context.send("`Use one of the following: pickup, cw, chaos, ladder`")
        try:
            if server.lower()=='pickup':
                test = pickup
            elif server.lower()=='cw':
                test = cw
            elif server.lower()=='tp':
                test = tp
            elif server.lower()=='dmc':
                test = dmc
            elif server.lower()=='chaos':
                test = chaos
            elif server.lower()=='tdm':
                test = tdm
            elif server.lower()=='ladder':
                test = ladder
            scores = []
            s = subprocess.check_output(test)
            data = json.loads(s)
            for te in data:
                print()
            for each in data[0]['players']:
                scores.append("{:>6d} - {}".format(each['score'],each['name']))
            scores = "\n".join(scores)
            nl = '\n'
            await context.send(f"```json{nl}{te['name']}{nl+nl}Map: {te['map']}{nl}Time: {te['rules']['maptime']}{nl+nl}Team1 vs Team2{nl}  {te['rules']['t1']}       {te['rules']['t2']}{nl+nl}Frags:   Players:{nl}{scores}```")
        except KeyError as e:
            print(e)
            await context.send("`Use one of the following: pickup, cw, chaos, ladder`")

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.

def setup(bot):
    bot.add_cog(Aq2(bot))
