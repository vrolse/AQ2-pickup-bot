import json
import logging
import sys
import os
# import bcrypt
from disnake import Embed, ApplicationCommandInteraction
from disnake.ext import commands
from helpers import checks

# Define reload_cogs function
async def reload_cogs(bot, cogs_to_reload):
    for cog_name in cogs_to_reload:
        try:
            bot.reload_extension(cog_name)
            print(f"Cog {cog_name} reloaded successfully.")
        except commands.ExtensionError as e:
            print(f"Failed to reload cog {cog_name}: {e}")

# Only if you want to use variables that are in the config.json file.
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

# Load server names from the servers.json file
try:
    with open('servers.json', 'r') as f:
        data = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    server_choices = []
else:
    server_choices = [server['name'] for server in data.get('servers', [])]

logging.basicConfig(level=logging.INFO)

GUILDID = int(config["GUILD_ID"])
cogs_to_reload = ["cogs.aq2-slash", "cogs.serverslist"]

class Servers(commands.Cog, name="servers"):
    def __init__(self, bot):
        self.bot = bot

    # Add reload_cogs call to reduce code duplication
    async def send_embed_and_reload_cogs(self, interaction, embed, cogs_to_reload):
        await interaction.send(embed=embed, ephemeral=True)
        await reload_cogs(self.bot, cogs_to_reload)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name='addserver',
        description='Add a new AQtion server to the list'
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def add_server(
        self, interaction: ApplicationCommandInteraction,
        name: str,
        ip: str,
        port: str,
        rcon: str,
        admin: str,
        gametype: str = commands.Param(name="gametype", choices=["pickup", "chaos"])
        ):
        embed = Embed(title='AQtion Server List', color=0x00ff00)

        # Create an empty dictionary if servers.json is empty or doesn't exist
        try:
            with open('servers.json', 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = {'servers': []}

        for server in data['servers']:
            if server['name'] == name:
                embed.description = f"A server with the name **{name}** already exists.  :heart_on_fire:"
                await self.send_embed_and_reload_cogs(interaction, embed, cogs_to_reload)
                return

        # Hash the RCON password
        #rcon_hash = bcrypt.hashpw(rcon.encode(), bcrypt.gensalt()).decode()

        # Add the new server to the data
        new_server = {
            'name': name,
            'ip': ip,
            'port': port,
            'rcon': rcon,
            'admin': admin,
            'type': gametype
            #'rcon': rcon_hash
        }
        data['servers'].append(new_server)

        # Save updated servers.json
        with open('servers.json', 'w') as f:
            json.dump(data, f, indent=4)

        # Yass.. send success
        self.bot.reload_extension("cogs.aq2-slash")
        embed.description = f"Server **{name}** ({ip}:{port}) has been added to the list.  :heart_eyes:"
        await self.send_embed_and_reload_cogs(interaction, embed, cogs_to_reload)

    @commands.slash_command(
        guild_ids=[GUILDID], 
        name='removeserver', 
        description='Remove an AQtion server from the list'
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def remove_server(self, interaction: ApplicationCommandInteraction, name: str = commands.Param(name="server", choices=server_choices)):
        embed = Embed(title='AQtion Server List', color=0x00ff00)
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
                embed.description = f"Server **{name}** has been removed from the list.  :ghost:"
                await self.send_embed_and_reload_cogs(interaction, embed, cogs_to_reload)
                return
        # Ohno.. send error :(
        embed.description = f"A server with the name **{name}** was not found.  :see_no_evil:"
        await interaction.send(embed=embed, ephemeral=True)
        await reload_cogs(self.bot, cogs_to_reload)

    @commands.slash_command(
        guild_ids=[GUILDID], 
        name='listservers', 
        description='List all AQtion servers'
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def list_servers(self, interaction: ApplicationCommandInteraction):
        embed = Embed(title='AQtion Server List', color=0x00ff00)
    
        try:
            with open('servers.json', 'r') as f:
                data = json.load(f)
    
            if not data.get('servers'):
                embed.description = "No servers found in the server list.  :exploding_head:"
            else:
                for server in data['servers']:
                    server_name = server.get('name', 'N/A')
                    server_ip = server.get('ip', 'N/A')
                    server_port = server.get('port', 'N/A')
                    server_admin = server.get('admin', 'N/A')
    
                    server_info = f"IP: {server_ip}:{server_port}\nAdmin: {server_admin}"
                    embed.add_field(name=server_name, value=server_info, inline=False)
        except (json.JSONDecodeError, FileNotFoundError):
            embed.description = "Error loading the server list."
    
        await interaction.send(embed=embed, ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID], 
        name='editservers', 
        description='Edit an existing AQtion server'
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def edit_server(
        self,
        interaction: ApplicationCommandInteraction,
        servers: str = commands.Param(name="server", choices=server_choices),
        ip: str = None,
        port: str = None,
        rcon: str = None,
        admin: str = None,
        gametype: str = commands.Param(name="gametype", choices=["pickup", "chaos"])
    ):
        embed = Embed(title='AQtion Server List', color=0x00ff00)

        # Load existing server data
        try:
            with open('servers.json', 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            embed.description = "Error loading the server list."
            await interaction.send(embed=embed, ephemeral=True)
            await reload_cogs(self.bot, cogs_to_reload)
            return

        # Find the server to be edited
        server_to_edit = None
        for server in data['servers']:
            if server['name'] == servers:
                server_to_edit = server
                break

        if not server_to_edit:
            embed.description = f"A server with the name **{servers}** was not found."
            await interaction.send(embed=embed, ephemeral=True)
            await reload_cogs(self.bot, cogs_to_reload)
            return

        # Update server info
        if ip is not None:
            server_to_edit['ip'] = ip
        if port is not None:
            server_to_edit['port'] = port
        if rcon is not None:
            server_to_edit['rcon'] = rcon
        if admin is not None:
            server_to_edit['admin'] = admin
        if gametype is not None:
            server_to_edit['type'] = gametype

        # Save updated servers.json
        with open('servers.json', 'w') as f:
            json.dump(data, f, indent=4)

        # Yass.. send success
        embed.description = f"Server **{servers}** has been successfully updated."
        await interaction.send(embed=embed, ephemeral=True)
        await reload_cogs(self.bot, cogs_to_reload)


def setup(bot):
    bot.add_cog(Servers(bot))
