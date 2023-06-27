"""
Copyright © Krypton 2021 - https://github.com/kkrypt0nn (https://krypt0n.co.uk)
Description:
This is a template to create your own discord bot in python.

Version: 4.0.1
"""
import json, os, disnake, sys, asyncio, random
from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from helpers import checks

# Only if you want to use variables that are in the config.json file.
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

#Add what needs to be loaded from config.json
GUILDID = int(config["GUILD_ID"])

# Here we name the cog and create a new class for the cog.
class voting(commands.Cog, name="voting"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        guild_ids=[GUILDID], 
        name='voting', 
        description='Start a server voting poll'
    )
    @checks.not_blacklisted()
    async def voting(ctx: ApplicationCommandInteraction):
        # Send an initial response indicating the command has been received
        await ctx.response.send_message('Processing the voting poll...')

        # Read the server data from the JSON file
        with open('servers.json', 'r') as f:
            server_data = json.load(f)

        # Create an embed to display the server options
        embed = disnake.Embed(title='Server Voting Poll', description='Vote for your favorite server!')

        # Add fields for each server option
        for index, server in enumerate(server_data['servers'], 1):
            name = server['name']
            ip = server['ip']
            port = server['port']
            embed.add_field(name=f'Server {index}', value=f'Name: {name}\nIP: {ip}:{port}', inline=False)

        # Send the embed to the channel
        message = await ctx.channel.send(embed=embed)

        # Add number reactions for each server option
        for index in range(1, len(server_data['servers']) + 1):
            reaction = str(index) + '\u20e3'  # Append '\u20e3' to represent the number as a Unicode emoji
            await message.add_reaction(reaction)

        # Define a check function for the reaction event
        def check(reaction, user):
            return (
                user.id != ctx.bot.user.id and
                reaction.message.id == message.id and
                str(reaction.emoji) in [str(i) + '\u20e3' for i in range(1, len(server_data['servers']) + 1)]
            )

        # Initialize a dictionary to keep track of votes for each server
        vote_count = {str(i): 0 for i in range(1, len(server_data['servers']) + 1)}

        # Initialize a set to keep track of users who have voted
        voted_users = set()

        try:
            # Wait for users to react to the message
            end_time = ctx.bot.loop.time() + 20.0  # Set the end time for the voting poll (30 seconds)
            while ctx.bot.loop.time() < end_time:
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=end_time - ctx.bot.loop.time(), check=check)

                # Check if the user has already voted
                if user.id in voted_users:
                    continue  # Ignore the vote if the user has already voted

                voted_users.add(user.id)  # Add the user to the set of voted users

                selected_option = int(reaction.emoji[:-1])  # Strip the last character ('\u20e3') from the emoji string

                # Reduce the vote count for the previously voted server (if any)
                for option, votes in vote_count.items():
                    if user.id == votes:
                        vote_count[option] -= 1
                        break

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
        winning_servers = [index for index, votes in vote_count.items() if votes == max_votes]

        if len(winning_servers) == 1:
            # Only one server has the maximum votes
            winning_server_index = int(winning_servers[0]) - 1
        else:
            # Multiple servers have the maximum votes, randomly select one
            winning_server_index = random.choice([int(server) - 1 for server in winning_servers])

        # Get the winning server details
        winning_server = server_data['servers'][winning_server_index]

        # Remove the reactions from the message
        await message.clear_reactions()

        # Create a new embed to display the voting result
        result_embed = disnake.Embed(title='Voting Result', description='The voting poll has ended!')
        result_embed.add_field(name='Winning Server', value=f'{winning_server["name"]} \nconnect {winning_server["ip"]}:{winning_server["port"]}')
        result_embed.add_field(name='Total Votes', value=sum(vote_count.values()))

        # Send the voting result embed
        await ctx.send(embed=result_embed)

def setup(bot):
    bot.add_cog(voting(bot))
