"""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""

import json, os, platform, random, sys, re, asyncio, disnake, exceptions

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
bot = Bot(command_prefix=config["prefix"], intents=intents)

DISCORD_CHANNELID = int(config["CHANNEL_ID"])
MVD2URL = config["MVD2URL"]
serverName = config["SRV_NAME"]
serverName2 = config["SRV_NAME2"]
serverName3 = config["SRV_NAME3"]
serverName4 = config["SRV_NAME4"]

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f"disnake API version: {disnake.__version__}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
    print("-------------------")
    status_task.start()
    pickup_over.start()
    cw_over.start()
    chaos_over.start()
    #pickup_interp_over.start()

# Setup the game status task of the bot
@tasks.loop(minutes=20.0)
async def status_task():
    statuses = ["AQ2!", "Pickups!", "with M4!", "with SSG!", "with knives!", "with HC!", "with MP5!", "with grenades!", "with Shotgun!", "with Slippers!, AQtion!"]
    await bot.change_presence(activity=disnake.Game(random.choice(statuses)))

@tasks.loop()
async def pickup_over():
    channel = bot.get_channel(DISCORD_CHANNELID)
    file_path = '../matchlogs/pickup.txt'
    get_time = lambda f: os.stat(f).st_ctime
    fn = file_path
    prev_time = get_time(fn)
    while True:
        t = get_time(fn)
        if t != prev_time:
            with open(file_path, "r") as f:
                line2 = f.readlines()
            scores = re.match(".+> T1 (\d+) vs (\d+) T2 @ (.+)",line2[0])
            if scores:
                t1score = scores.group(1)
                t2score = scores.group(2)
                mapname = scores.group(3)
                embedVar = disnake.Embed(
                    title=':map:    {}    '.format(mapname),
                    description=MVD2URL,
                    color=0xE02B2B,
                    )
                embedVar.set_footer(text=serverName)
                if not os.path.isfile('./thumbnails/{}.jpg'.format(mapname)):
                    file = disnake.File('./thumbnails/map.jpg', filename="map.jpg")
                else:
                    file = disnake.File('./thumbnails/{}.jpg'.format(mapname), filename="map.jpg")
                embedVar.set_thumbnail(url="attachment://map.jpg")
                embedVar.add_field(name='Team Uno', value=t1score)
                embedVar.add_field(name='Team Dos', value=t2score)
                prev_time = t
                await channel.send(file=file, embed=embedVar)
        await asyncio.sleep(10)

@tasks.loop()
async def chaos_over():
    channel = bot.get_channel(DISCORD_CHANNELID)
    file_path = '../matchlogs/cw.txt'
    get_time = lambda f: os.stat(f).st_ctime
    fn = file_path
    prev_time = get_time(fn)
    while True:
        t = get_time(fn)
        if t != prev_time:
            with open(file_path, "r") as f:
                line2 = f.readlines()
            scores = re.match(".+> T1 (\d+) vs (\d+) T2 @ (.+)",line2[0])
            if scores:
                t1score = scores.group(1)
                t2score = scores.group(2)
                mapname = scores.group(3)
                embedVar = disnake.Embed(
                    title=':map:    {}    '.format(mapname),
                    description=MVD2URL,
                    color=0xE02B2B,
                    )
                embedVar.set_footer(text=serverName2)
                if not os.path.isfile('./thumbnails/{}.jpg'.format(mapname)):
                    file = disnake.File('./thumbnails/map.jpg', filename="map.jpg")
                else:
                    file = disnake.File('./thumbnails/{}.jpg'.format(mapname), filename="map.jpg")
                embedVar.set_thumbnail(url="attachment://map.jpg")
                embedVar.add_field(name='Team Uno', value=t1score)
                embedVar.add_field(name='Team Dos', value=t2score)
                prev_time = t
                await channel.send(file=file, embed=embedVar)
        await asyncio.sleep(10)

@tasks.loop()
async def cw_over():
    channel = bot.get_channel(DISCORD_CHANNELID)
    file_path = '../matchlogs/chaos.txt'
    get_time = lambda f: os.stat(f).st_ctime
    fn = file_path
    prev_time = get_time(fn)
    while True:
        t = get_time(fn)
        if t != prev_time:
            with open(file_path, "r") as f:
                line2 = f.readlines()
            scores = re.match(".+> T1 (\d+) vs (\d+) T2 @ (.+)",line2[0])
            if scores:
                t1score = scores.group(1)
                t2score = scores.group(2)
                mapname = scores.group(3)
                embedVar = disnake.Embed(
                    title=':map:    {}    '.format(mapname),
                    description=MVD2URL,
                    color=0xE02B2B,
                    )
                embedVar.set_footer(text=serverName3)
                if not os.path.isfile('./thumbnails/{}.jpg'.format(mapname)):
                    file = disnake.File('./thumbnails/map.jpg', filename="map.jpg")
                else:
                    file = disnake.File('./thumbnails/{}.jpg'.format(mapname), filename="map.jpg")
                embedVar.set_thumbnail(url="attachment://map.jpg")
                embedVar.add_field(name='Team Uno', value=t1score)
                embedVar.add_field(name='Team Dos', value=t2score)
                prev_time = t
                await channel.send(file=file, embed=embedVar)
        await asyncio.sleep(10)

# @tasks.loop()
# async def pickup_interp_over():
#     channel = bot.get_channel(DISCORD_CHANNELID)
#     file_path = '../matchlogs/pickup_interp.txt'
#     get_time = lambda f: os.stat(f).st_ctime
#     fn = file_path
#     prev_time = get_time(fn)
#     while True:
#         t = get_time(fn)
#         if t != prev_time:
#             with open(file_path, "r") as f:
#                 line2 = f.readlines()
#             scores = re.match(".+> T1 (\d+) vs (\d+) T2 @ (.+)",line2[0])
#             if scores:
#                 t1score = scores.group(1)
#                 t2score = scores.group(2)
#                 mapname = scores.group(3)
#                 embedVar = disnake.Embed(
#                     title=':map:    {}    '.format(mapname),
#                     description=MVD2URL,
#                     color=0xE02B2B,
#                     )
#                 embedVar.set_footer(text=serverName4)
#                 if not os.path.isfile('./thumbnails/{}.jpg'.format(mapname)):
#                     file = disnake.File('./thumbnails/map.jpg', filename="map.jpg")
#                 else:
#                     file = disnake.File('./thumbnails/{}.jpg'.format(mapname), filename="map.jpg")
#                 embedVar.set_thumbnail(url="attachment://map.jpg")
#                 embedVar.add_field(name='Team Uno', value=t1score)
#                 embedVar.add_field(name='Team Dos', value=t2score)
#                 prev_time = t
#                 await channel.send(file=file, embed=embedVar)
#         await asyncio.sleep(10)

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
        f"Executed {interaction.data.name} command in {interaction.guild.name} (ID: {interaction.guild.id}) by {interaction.author} (ID: {interaction.author.id})")

# The code in this event is executed every time a valid slash command catches an error
@bot.event
async def on_slash_command_error(interaction: ApplicationCommandInteraction, error: Exception):
    if isinstance(error, exceptions.UserBlacklisted):
        """
        The code here will only execute if the error is an instance of 'UserBlacklisted', which can occur when using
        the @checks.is_owner() check in your command, or you can raise the error by yourself.
        
        'hidden=True' will make so that only the user who execute the command can see the message
        """
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
            description="You are missing the permission(s) `" + ", ".join(
                error.missing_permissions) + "` to execute this command!",
            color=0xE02B2B
        )
        print("A blacklisted user tried to execute a command.")
        return await interaction.send(embed=embed, ephemeral=True)
    raise error

# The code in this event is executed every time a normal command has been *successfully* executed
@bot.event
async def on_command_completion(ctx):
    fullCommandName = ctx.command.qualified_name
    split = fullCommandName.split(" ")
    executedCommand = str(split[0])
    print(
        f"Executed {executedCommand} command in {ctx.guild.name} (ID: {ctx.message.guild.id}) by {ctx.message.author} (ID: {ctx.message.author.id})")

@bot.event
async def on_slash_command_error(interaction: ApplicationCommandInteraction, error: Exception) -> None:
    """
    The code in this event is executed every time a valid slash command catches an error
    :param interaction: The slash command that failed executing.
    :param error: The error that has been faced.
    """
    if isinstance(error, exceptions.UserBlacklisted):
        """
        The code here will only execute if the error is an instance of 'UserBlacklisted', which can occur when using
        the @checks.is_owner() check in your command, or you can raise the error by yourself.
        
        'hidden=True' will make so that only the user who execute the command can see the message
        """
        embed = disnake.Embed(
            title="Error!",
            description="You are blacklisted from using the bot.",
            color=0xE02B2B
        )
        print("A blacklisted user tried to execute a command.")
        return await interaction.send(embed=embed)
    elif isinstance(error, exceptions.UserNotAdmin):
        embed = disnake.Embed(
            title="Error!",
            description="You don't have the correct role to execute this command!",
            color=0xE02B2B
        )
        print("Someone that is not an admin tried to execute a command.")
        return await interaction.send(embed=embed, ephemeral=True)
    elif isinstance(error, commands.errors.MissingPermissions):
        embed = disnake.Embed(
            title="Error!",
            description="You are missing the permission(s) to execute this command!",
            color=0xE02B2B
        )
        print("A blacklisted user tried to execute a command.")
        return await interaction.send(embed=embed)
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
