import json, logging, sys, os #bcrypt
from disnake import Embed
from disnake.ext import commands
from helpers import checks

# Only if you want to use variables that are in the config.json file.
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

logging.basicConfig(level=logging.INFO)

GUILDID = int(config["GUILD_ID"])

class Servers(commands.Cog, name="servers"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILDID], name='addserver', description='Add a new AQtion server to the list')
    @checks.not_blacklisted()
    @checks.admin()
    async def add_server(self, ctx, name: str, ip: str, port: str, rcon: str, admin: str):
        # See if server with name already exists
        # Load the data from servers.json
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            if server['name'] == name:
                await ctx.send(f"A server with the name {name} already exists.", ephemeral=True)
                self.bot.reload_extension("cogs.aq2-slash")
                return
        
        # Hash the RCON password
        #rcon_hash = bcrypt.hashpw(rcon.encode(), bcrypt.gensalt()).decode()
    
        # Add the new server to the data
        new_server = {
            'name': name,
            'ip': ip,
            'port': port,
            'rcon': rcon,
            'admin': admin
            #'rcon': rcon_hash
        }
        data['servers'].append(new_server)
        
        # Save updated servers.json
        with open('servers.json', 'w') as f:
            json.dump(data, f, indent=4)
        
        # Yass.. send success
        await ctx.send(f"Server {name} ({ip}:{port}) has been added to the list. \N{SMILING FACE WITH HEART-SHAPED EYES}", ephemeral=True)

    @commands.slash_command(guild_ids=[GUILDID], name='removeserver', description='Remove a AQtion server from the list')
    @checks.not_blacklisted()
    @checks.admin()
    async def remove_server(self, ctx, name: str):
        with open('servers.json', 'r') as f:
            data = json.load(f)
        # See if server with name exists
        for server in data['servers']:
            if server['name'] == name:
                data['servers'].remove(server)
                
                # Save updated servers.json
                with open('servers.json', 'w') as f:
                    json.dump(data, f, indent=4)
                # Yass.. send success
                await ctx.send(f"Server {name} has been removed from the list. \N{GHOST}" , ephemeral=True)
                self.bot.reload_extension("cogs.aq2-slash")
                return
        
        # Ohno.. send error :(
        await ctx.send(f"A server with the name {name} was not found.", ephemeral=True)
    
    @commands.slash_command(guild_ids=[GUILDID], name='listservers', description='List all AQtion servers')
    @checks.not_blacklisted()
    @checks.admin()
    async def list_servers(ctx):
        embed = Embed(title='AQtion Server List', color=0x00ff00)
        # Loop through the servers and add them to the message (embed)
        with open('servers.json', 'r') as f:
            data = json.load(f)
        for server in data['servers']:
            embed.add_field(name=server['name'], value=f"{server['ip']}:{server['port']} :: Admin:{server['admin']}")
        
        await ctx.send(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Servers(bot))
