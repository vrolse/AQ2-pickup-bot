"""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""
import json
import pyrcon
import re
import subprocess
import os
import disnake
import sys
from datetime import datetime
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

try:
    # Load the servers data from file
    with open('servers.json', 'r') as f:
        data = json.load(f)
        server_choices = [server.get('name', 'N/A') for server in data.get('servers', [])]
except (json.JSONDecodeError, FileNotFoundError):
    data = {'servers': []}
    # Save default data to servers.json
    with open('servers.json', 'w') as f:
        json.dump(data, f, indent=4)
    # Handle decoding errors or missing file
    server_choices = []
    # Provide an error message
    print("Error loading the server list or the list is empty, creating a new.")

#Add what needs to be loaded from config.json
GUILDID = int(config["GUILD_ID"])
MVD2URL = config["MVD2URL"]
qs = config["QSTAT"]

def parse_status_response(response: str) -> dict:
    players = {}
    pattern = re.compile(r"(\d+)\s+(\S+)")
    for line in response.splitlines():
        match = pattern.match(line)
        if match:
            player_num = int(match.group(1))
            player_name = match.group(2)
            players[player_num] = player_name
    return players

def get_server_details(aqserver: str):
    """Retrieve server details (ip, port, rcon) based on the server name."""
    with open('servers.json', 'r') as f:
        data = json.load(f)
    for server in data['servers']:
        if aqserver.strip().lower() == server['name'].strip().lower():  # Ensure match
            return server['ip'], server['port'], server['rcon']
    raise ValueError(f"Server '{aqserver}' not found.")

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
    async def status(self, interaction: ApplicationCommandInteraction, aqserver: str = commands.Param(name="server", choices=server_choices)):
        try:
            ip, port, rcon = get_server_details(aqserver)
            conn = pyrcon.Q2RConnection(ip, port, rcon)
            result = conn.send('status v')
            await interaction.send(f'```yaml\n{result}\n```', ephemeral=True)
        except ValueError:
            await interaction.send(f'```yaml\nServer {aqserver} not found.\n```', ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="changemap",
        description="Change map on server.",
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def changemap(self, interaction: ApplicationCommandInteraction, aqserver: str = commands.Param(name="server", choices=server_choices), map: str = commands.Param(name="mapname")) -> None:
        try:
            ip, port, rcon = get_server_details(aqserver)
            pyrcon.Q2RConnection(ip, port, rcon).send('gamemap ' + map)
            await interaction.send(f'```yaml\nMap changed to: {map}\nOn server: {aqserver}\n```')
        except ValueError:
            await interaction.send(f'```yaml\nServer {aqserver} not found.\n```', ephemeral=True)
            
    @commands.slash_command(
        guild_ids=[GUILDID],
        name="lrcon",
        description="To see cmds use listlrconcmds",
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def lrcon(self, interaction: ApplicationCommandInteraction, aqserver: str = commands.Param(choices=server_choices), cmd: str = commands.Param(name='command')) -> None:
        try:
            ip, port, rcon = get_server_details(aqserver)
            
            if cmd.startswith('teamnone'):
                try:
                    _, number = cmd.split()
                    number = int(number)
                    status_response = pyrcon.Q2RConnection(ip, port, rcon).send("status v")
                    players = parse_status_response(status_response)
                    
                    if number in players:
                        player_name = players[number]
                        result = pyrcon.Q2RConnection(ip, port, rcon).send(f"teamnone {number}")
                        await interaction.send(
                            f'```yaml\nPlayer {player_name} (ID {number}) has been removed from the team\n```', ephemeral=True
                        )
                    else:
                        await interaction.send(
                            f'```yaml\nNo player with ID {number} found.\n```', ephemeral=True
                        )
                except ValueError:
                    await interaction.send(
                        '```yaml\nInvalid format for teamnone. Please provide a valid number.\n```', ephemeral=True
                    )
            else:
                result = pyrcon.Q2RConnection(ip, port, rcon).send(cmd)
                await interaction.send(f'```yaml\n{result}\n```', ephemeral=True)
                
        except ValueError as e:
            await interaction.send(f'```yaml\n{e}\n```', ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="reset",
        description="Reset the server if something is wrong or for fun just to be an asshole 😄",
    )
    @checks.not_blacklisted()
    @checks.admin()
    async def reset(self, interaction: ApplicationCommandInteraction, aqserver: str = commands.Param(name="server", choices=server_choices)) -> None:
        try:
            ip, port, rcon = get_server_details(aqserver)
            pyrcon.Q2RConnection(ip, port, rcon).send(f'recycle Server reset by {interaction.author.display_name}')
            await interaction.send(f'`{aqserver}-server reset by {interaction.author.display_name}!`')
        except ValueError:
            await interaction.send(f'```yaml\nServer {aqserver} not found.\n```', ephemeral=True)

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="last",
        description="See results from the latest match on pickup or cw servers.",
    )
    @checks.not_blacklisted()
    async def last(self, interaction: ApplicationCommandInteraction):
        folder_path = './servers/'  # Update this path to the correct location
                
        try:
            # Check if folder exists
            if not os.path.isdir(folder_path):
                await interaction.send("No match data found.")
                return
            
            file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.json')]

            if not file_paths:
                await interaction.send("No match data found.")
                return

            latest_file_path = max(file_paths, key=os.path.getmtime)

            if os.path.isfile(latest_file_path):
                with open(latest_file_path, "r") as f:
                    data = json.load(f)

                # Extract relevant information from data
                date = datetime.fromtimestamp(os.path.getmtime(latest_file_path)).strftime("%Y-%m-%d %H:%M")
                name = data.get("name", "N/A")
                t1score = data.get("T1", "N/A")
                t2score = data.get("T2", "N/A")
                mapname = data.get("map", "N/A")

                players = data.get('players', [])
                # Filter out "[MVDSPEC]"
                players = [player for player in players if player['name'] != '[MVDSPEC]']
                # Sort players based on their score (descending order)
                sorted_players = sorted(players, key=lambda x: x['score'], reverse=True)

                # Create and send the embed
                embedVar = disnake.Embed(
                    title=f':map:    {mapname}    ',
                    description=date,
                    color=0xE02B2B,
                )
                embedVar.set_footer(text=name)
                thumbnail_path = './thumbnails/{}.jpg'.format(mapname)
                if os.path.isfile(thumbnail_path):
                    file = disnake.File(thumbnail_path, filename='map.jpg')
                else:
                    file = disnake.File('./thumbnails/map.jpg', filename='map.jpg')
                embedVar.set_thumbnail(url='attachment://map.jpg')
                embedVar.add_field(name='Team Uno', value=t1score, inline=True)
                embedVar.add_field(name='Team Dos', value=t2score, inline=True)

                if sorted_players:
                    table_str = f"```\n{'Player':<15} {'Score':^7}\n{'-'*15} {'-'*7}"
                    for player in sorted_players:
                        table_str += f"\n{player['name']:<15} {player['score']:^7}"
                    table_str += "```"
                    embedVar.add_field(name="\u200b", value=table_str, inline=False)
                else:
                    embedVar.add_field(name="\u200b", value="No player data available.", inline=False)

                await interaction.send(file=file, embed=embedVar)

        except Exception as e:
            print(f"Error reading file: {e}")
            await interaction.send("An error occurred while reading the match data.")

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="check",
        description="Check server.",
    )
    @checks.not_blacklisted()
    async def check(self, interaction: ApplicationCommandInteraction, aqserver: str = commands.Param(choices=server_choices)):
        try:
            ip, port, rcon = get_server_details(aqserver)
            s = subprocess.check_output([qs, '-q2s', ip + ':' + port, '-R', '-P', '-sort', 'F', '-json'], timeout=10)
            data = json.loads(s)
            if data[0]['status'] in ['offline', 'timeout']:
                await interaction.send(f"The server {aqserver} is offline or not available.")
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
            await interaction.send(f"The server {aqserver} did not respond within the expected time.")
        except Exception as e:
            await interaction.send(f"An error occurred while checking the server")

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="mapimage",
        description="Send DM with a picture of the map",
    )
    @checks.not_blacklisted()
    async def map_image(self, interaction: ApplicationCommandInteraction, mapname: str):
        # Check if the map image file exists
        imagedir = config["DLDIRECTORY"]
        map_filename = f"{mapname}.jpg"
        map_path = os.path.join(imagedir, map_filename)

        if os.path.isfile(map_path):
            # Get the user who invoked the command
            user = interaction.user

            # Send the map image as a direct message to the user
            with open(map_path, "rb") as file:
                await user.send(f"Here is the map image for {mapname}:", file=disnake.File(file, map_filename))
            
            await interaction.response.send_message("Map image sent as a DM.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Map image for {mapname} not found.", ephemeral=True)

def setup(bot):
    bot.add_cog(Aq2(bot))
