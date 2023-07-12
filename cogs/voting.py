"""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""
import json
import os
import disnake
import sys
import asyncio
import random
from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from helpers import checks

# Only if you want to use variables that are in the config.json file.
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

# Add what needs to be loaded from config.json
GUILDID = int(config["GUILD_ID"])

# Here we name the cog and create a new class for the cog.
class Voting(commands.Cog, name="voting"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        guild_ids=[GUILDID],
        name='voteserver',
        description='Start a server voting poll for a specific type (pickup/chaos)'
    )
    @checks.not_blacklisted()
    async def voteserver(ctx: ApplicationCommandInteraction, gametype: str = commands.Param(name="gametype", choices=["pickup", "chaos"])):
        with open('servers.json', 'r') as f:
            data = json.load(f)
        await ctx.response.send_message('Processing the voting poll...')

        # Filter the servers based on the specified option
        filtered_servers = [server for server in data['servers'] if server.get('type', '').lower() == gametype.lower()]

        if not filtered_servers:
            await ctx.send(f"No servers found for the type: {gametype}", ephemeral=True)
            return

        # Create an embed to display the server options
        embed = disnake.Embed(title=f'Server Voting Poll - {gametype.capitalize()}', description='Vote for your favorite server of this type!')

        # Add fields for each server option
        for index, server in enumerate(filtered_servers):
            name = server['name']
            ip = server['ip']
            port = server['port']
            emoji_number = chr(ord('0') + index + 1) + '\u20e3'
            embed.add_field(name=f'{emoji_number} {name}', value=f'IP: {ip}:{port}', inline=False)

        # Send the embed to the channel
        message = await ctx.channel.send(embed=embed)

        # Add number reactions for each server option
        for index in range(1, len(filtered_servers) + 1):
            reaction = str(index) + '\u20e3'
            await message.add_reaction(reaction)

        # Define a check function for the reaction event
        def check(reaction, user):
            return (
                user.id != ctx.bot.user.id and
                reaction.message.id == message.id and
                str(reaction.emoji) in [str(i) + '\u20e3' for i in range(1, len(filtered_servers) + 1)]
            )

        # Initialize a dictionary to keep track of votes for each server
        vote_count = {str(i): 0 for i in range(1, len(filtered_servers) + 1)}

        # Initialize a dictionary to keep track of user's vote
        user_votes = {}

        try:
            # Wait for users to react to the message
            end_time = ctx.bot.loop.time() + 60.0  # Set the end time for the voting poll (e.g 60 seconds)
            while ctx.bot.loop.time() < end_time:
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=end_time - ctx.bot.loop.time(), check=check)

                # Check if the user has already voted
                if user.id in user_votes:
                    previous_vote = user_votes[user.id]
                    if previous_vote == reaction.emoji:
                        continue
                    
                    vote_count[str(previous_vote[:-1])] -= 1

                selected_option = int(reaction.emoji[:-1])

                user_votes[user.id] = reaction.emoji

                vote_count[str(selected_option)] += 1

        except asyncio.TimeoutError:
            # If there are no votes, remove the poll and send a message
            if sum(vote_count.values()) == 0:
                await message.delete()
                await ctx.send('The voting poll has been canceled due to no votes.')
                return

        # Get the maximum number of votes
        max_votes = max(vote_count.values())

        # Get the servers with the maximum votes
        winning_servers = [option for option, votes in vote_count.items() if votes == max_votes]

        if len(winning_servers) == 1:
            # Only one server has the maximum votes
            winning_server_index = int(winning_servers[0]) - 1
        else:
            # Multiple servers have the maximum votes, randomly select one
            winning_server_index = random.choice([int(option) - 1 for option in winning_servers])

        # Get the winning server details
        winning_server = filtered_servers[winning_server_index]

        # Remove the reactions from the message
        await message.clear_reactions()

        # Create a new embed to display the voting result
        result_embed = disnake.Embed(title='Voting Result', description='The voting poll has ended!')
        result_embed.add_field(name='Winning Server', value=f'{winning_server["name"]} \nconnect {winning_server["ip"]}:{winning_server["port"]}')
        result_embed.add_field(name='Total Votes', value=sum(vote_count.values()))

        # Send the voting result embed
        await ctx.send(embed=result_embed)
        await message.delete()

def setup(bot):
    bot.add_cog(Voting(bot))
