"""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""

import json
import os
import random
import sys
import disnake
import exceptions
import datetime
import asyncio
from disnake import ApplicationCommandInteraction
from disnake.ext import tasks, commands
from disnake.ext.commands import Bot
from disnake.ext.commands import Context

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)
if not os.path.isfile("qstat"):
    sys.exit("'qstat' not found! Please add it and try again.")

intents = disnake.Intents.default()

#Add what needs to be loaded from config.json
bot = Bot(command_prefix=disnake.ext.commands.when_mentioned, intents=intents)
date = datetime.datetime.now()
DISCORD_CHANNELID = int(config["CHANNEL_ID"])
MVD2URL = config["MVD2URL"]

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"disnake API version: {disnake.__version__}")
    print("-------------------")
    status_task.start()
    match_over.start()

# Setup the game status task of the bot
@tasks.loop(minutes=20.0)
async def status_task():
    statuses = ["AQ2!", "Pickups!", "with M4!", "with SSG!", "with knives!", "with HC!", "with MP5!", "with grenades!", "with Shotgun!", "with Slippers!, AQtion!"]
    await bot.change_presence(activity=disnake.Game(random.choice(statuses)))

## Test new function to get match report from servers directly through q2admin ##
# Load processed filenames and timestamps
def load_processed_files():
    try:
        with open('processed_files.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # Create the file with an empty dictionary
        with open('processed_files.json', 'w') as file:
            json.dump({}, file)
        return {}  # Return empty dictionary

# Save processed filenames and timestamps
def save_processed_files(processed_files):
    with open('processed_files.json', 'w') as file:
        json.dump(processed_files, file)

@tasks.loop()  # seconds=10
async def match_over():
    channel = bot.get_channel(DISCORD_CHANNELID)
    folder_path = './servers'
    processed_files = load_processed_files()

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)

            # Get modified timestamp of file
            modified_timestamp = os.path.getmtime(file_path)

            if filename in processed_files:
                # Compare modified timestamps
                if modified_timestamp == processed_files[filename]:
                    continue  # Skip if file has not been modified

            with open(file_path, 'r') as f:
                file_data = f.read().strip()
            
            if not file_data:
                continue  # Skip empty files

            try:
                data = json.loads(file_data)
            except json.JSONDecodeError:
                continue  # Skip files with invalid JSON
            
            name = data.get('name')
            t1score = data.get('T1')
            t2score = data.get('T2')
            mapname = data.get('map')

            # Get player data and scores from the JSON
            players = data.get('players', [])
            # Filter out "[MVDSPEC]"
            players = [player for player in players if player['name'] != '[MVDSPEC]']
            # Sort players based on their score (descending order)
            sorted_players = sorted(players, key=lambda x: x['score'], reverse=True)

            embedVar = disnake.Embed(
                title=':map:    {}    '.format(mapname),
                description=MVD2URL,
                color=0xE02B2B,
            )
            embedVar.set_footer(text=name)
            thumbnail_path = './thumbnails/{}.jpg'.format(mapname)
            if os.path.isfile(thumbnail_path):
                file = disnake.File(thumbnail_path, filename='map.jpg')
            else:
                file = disnake.File('./thumbnails/map.jpg', filename='map.jpg')
            embedVar.set_thumbnail(url='attachment://map.jpg')
            embedVar.add_field(name='Team Uno', value=t1score)
            embedVar.add_field(name='Team Dos', value=t2score)

            if sorted_players:
                table_str = f"```\n{'Player':<15} {'Score':^7}\n{'-'*15} {'-'*7}"
                for player in sorted_players:
                    table_str += f"\n{player['name']:<15} {player['score']:^7}"
                table_str += "```"
                embedVar.add_field(name="\u200b", value=table_str, inline=False)
            else:
                embedVar.add_field(name="\u200b", value="No player data available.", inline=False)

            await channel.send(file=file, embed=embedVar)

            # Update timestamp
            processed_files[filename] = modified_timestamp

    save_processed_files(processed_files)
    await asyncio.sleep(10)

# Removes the default help command of discord.py to be able to create our custom help command.
bot.remove_command("help")

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")

# The code in this event is executed every time someone sends a message, with or without the prefix
@bot.event
async def on_message(message: disnake.Message):
    # Ignores if a command is being executed by a bot or by the bot itself
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)

# The code in this event is executed every time a slash command has been *successfully* executed
@bot.event
async def on_slash_command(interaction: ApplicationCommandInteraction):
    print(
        f"{date:%Y-%m-%d %H:%M} -- Executed {interaction.data.name} command in {interaction.guild.name} (ID: {interaction.guild.id}) by {interaction.author} (ID: {interaction.author.id})")

# The code in this event is executed every time a normal command has been *successfully* executed
@bot.event
async def on_command_completion(ctx):
    fullCommandName = ctx.command.qualified_name
    split = fullCommandName.split(" ")
    executedCommand = str(split[0])
    print(
        f"{date:%Y-%m-%d %H:%M} -- Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})")

# The code in this event is executed every time a valid slash command catches an error
@bot.event
async def on_slash_command_error(interaction: ApplicationCommandInteraction, error: Exception) -> None:
    if isinstance(error, exceptions.UserNotAdmin):
        embed = disnake.Embed(
            title="Error!",
            description="You are not an admin of the bot!",
            color=0xE02B2B
        )
        print("Someone that is not an admin tried to execute a command.")
        return await interaction.send(embed=embed, ephemeral=True)
    
    elif isinstance(error, exceptions.UserBlacklisted):
        embed = disnake.Embed(
            title="Error!",
            description="You are blacklisted from using the bot.",
            color=0xE02B2B
        )
        print("A blacklisted user tried to execute a command.")
        return await interaction.send(embed=embed, ephemeral=True)
    
    elif isinstance(error, commands.errors.MissingPermissions):
        embed = disnake.Embed(
            title="Error!",
            description="You are missing the permission(s) to execute this command!",
            color=0xE02B2B
        )
        print("An user without permissions tried to execute a command.")
        return await interaction.send(embed=embed, ephemeral=True)
    
    elif isinstance(error, commands.errors.MissingRole):
        embed = disnake.Embed(
            title="Error!",
            description="You don't have the correct role(s) to execute this command!",
            color=0xE02B2B
        )
        print("Someone with the wrong role tried to execute a command.")
        return await interaction.send(embed=embed, ephemeral=True)
    
    raise error

# Run the bot with the token
bot.run(config["token"])
