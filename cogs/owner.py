""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 4.1
"""

import json
import os
import sys
import requests
import disnake
from disnake import ApplicationCommandInteraction, Option, OptionType
from disnake.ext import commands
from helpers import json_manager, checks

if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

#Add what needs to be loaded from config.json
GUILDID = int(config["GUILD_ID"])

class Owner(commands.Cog, name="Owner"):
    def __init__(self, bot):
        self.bot = bot

    async def reload_cogs(self, cogs_to_reload):
        for cog_name in cogs_to_reload:
            try:
                self.bot.reload_extension(cog_name)
                print(f"Cog {cog_name} reloaded successfully.")
            except commands.ExtensionError as e:
                print(f"Failed to reload cog {cog_name}: {e}")

    @commands.slash_command(
        name="blacklist",
        description="Get the list of all blacklisted users.",
    )
    @checks.is_owner()
    async def blacklist(self, interaction: ApplicationCommandInteraction) -> None:
        """
        Lets you add or remove a user from not being able to use the bot.
        :param interaction: The application command interaction.
        """
        pass
    @blacklist.sub_command(
        base="blacklist",
        name="list",
        description="List all blacklisted users",
    )
    @checks.is_owner()
    async def blacklist_list(self, interaction: ApplicationCommandInteraction) -> None:
        with open("blacklist.json") as file:
            blacklist = json.load(file)
        embed = disnake.Embed(
            title=f"There are currently {len(blacklist['ids'])} blacklisted IDs",
            description=f"{', '.join(str(id) for id in blacklist['ids'])}",
            color=0x9C84EF
        )
        await interaction.send(embed=embed, ephemeral=True)

    @blacklist.sub_command(
        base="blacklist",
        name="add",
        description="Lets you add a user from not being able to use the bot.",
        options=[
            Option(
                name="user",
                description="The user you want to add to the blacklist.",
                type=OptionType.user,
                required=True
            )
        ],
    )
    @checks.is_owner()
    async def blacklist_add(self, interaction: ApplicationCommandInteraction, user: disnake.User = None) -> None:
        """
        Lets you add a user from not being able to use the bot.
        :param interaction: The application command interaction.
        :param user: The user that should be added to the blacklist.
        """
        try:
            user_id = user.id
            with open("blacklist.json") as file:
                blacklist = json.load(file)
            if user_id in blacklist['ids']:
                embed = disnake.Embed(
                    title="Error!",
                    description=f"**{user.name}** is already in the blacklist.",
                    color=0xE02B2B
                )
                return await interaction.send(embed=embed, ephemeral=True)
            json_manager.add_user_to_blacklist(user_id)
            embed = disnake.Embed(
                title="User Blacklisted",
                description=f"**{user.name}** has been successfully added to the blacklist",
                color=0x9C84EF
            )
            with open("blacklist.json") as file:
                blacklist = json.load(file)
            embed.set_footer(
                text=f"There are now {len(blacklist['ids'])} users in the blacklist"
            )
            await interaction.send(embed=embed, ephemeral=True)
        except Exception as exception:
            embed = disnake.Embed(
                title="Error!",
                description=f"An unknown error occurred when trying to add **{user.name}** to the blacklist.",
                color=0xE02B2B
            )
            await interaction.send(embed=embed, ephemeral=True)
            print(exception)

    @blacklist.sub_command(
        base="blacklist",
        name="remove",
        description="Lets you remove a user from not being able to use the bot.",
        options=[
            Option(
                name="user",
                description="The user you want to remove from the blacklist.",
                type=OptionType.user,
                required=True
            )
        ],
    )
    @checks.is_owner()
    async def blacklist_remove(self, interaction: ApplicationCommandInteraction, user: disnake.User = None):
        """
        Lets you remove a user from not being able to use the bot.
        :param interaction: The application command interaction.
        :param user: The user that should be removed from the blacklist.
        """
        try:
            json_manager.remove_user_from_blacklist(user.id)
            embed = disnake.Embed(
                title="User removed from blacklist",
                description=f"**{user.name}** has been successfully removed from the blacklist",
                color=0x9C84EF
            )
            with open("blacklist.json") as file:
                blacklist = json.load(file)
            embed.set_footer(
                text=f"There are now {len(blacklist['ids'])} users in the blacklist"
            )
            await interaction.send(embed=embed, ephemeral=True)
        except ValueError:
            embed = disnake.Embed(
                title="Error!",
                description=f"**{user.name}** is not in the blacklist.",
                color=0xE02B2B
            )
            await interaction.send(embed=embed, ephemeral=True)
        except Exception as exception:
            embed = disnake.Embed(
                title="Error!",
                description=f"An unknown error occurred when trying to add **{user.name}** to the blacklist.",
                color=0xE02B2B
            )
            await interaction.send(embed=embed, ephemeral=True)
            print(exception)
            
    @commands.slash_command(
        guild_ids=[GUILDID],
        name="getthumbs",
        description="Download/update map thumbnails",
    )
    @checks.is_owner()
    @checks.not_blacklisted()
    async def getthumbs(self, interaction: ApplicationCommandInteraction):
        # Defer the interaction response first
        await interaction.response.defer(ephemeral=True)

        # GitHub repository details
        repo_user = config["REPO_USER"]
        repo_name = config["REPO_NAME"]
        branch = config["BRANCH"]
        directory = config["DIRECTORY"]

        # Destination directory for downloaded files
        download_directory = config["DLDIRECTORY"]

        # API URL to get the contents of the directory
        api_url = f"https://api.github.com/repos/{repo_user}/{repo_name}/contents/{directory}?ref={branch}"
        downloaded_files = 0
        file_names = []
        messages = []

        response = requests.get(api_url)
        if response.status_code == 200:
            files_data = response.json()

            for file_data in files_data:
                filename = file_data["name"]
                file_url = file_data["download_url"]
                file_path = os.path.join(download_directory, filename)

                if not os.path.exists(file_path) or os.path.getsize(file_path) != file_data["size"]:
                    # File doesn't exist or sizes are different, download it
                    with open(file_path, "wb") as file:
                        response = requests.get(file_url)
                        if response.status_code == 200:
                            file.write(response.content)
                            file_names.append(filename)
                            downloaded_files += 1
                        else:
                            messages.append(f"Failed to download: {filename} (HTTP status code: {response.status_code})")

        if downloaded_files == 0:
            messages.append("No new files needed to be downloaded.")
        else:
            # Send only the names of the downloaded files, up to 10 files
            if len(file_names) <= 10:
                messages.extend([f"Downloaded: {filename}" for filename in file_names])
            else:
                messages.append(f"Downloaded {downloaded_files} file(s) in total.")

        # Send the ephemeral response to the user who used the command
        await interaction.followup.send("\n".join(messages))


    @commands.slash_command(
            guild_ids=[GUILDID],
            name="reload",
            description="Reload all bot cogs (owner only)."
            )
    @checks.is_owner()
    @checks.not_blacklisted()
    async def reload(self, inter: disnake.ApplicationCommandInteraction):
        if await self.bot.is_owner(inter.author):
            await inter.response.defer(ephemeral=True)
            
            cogs_to_reload = []
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py") and not filename.startswith("_"):
                    cogs_to_reload.append(f"cogs.{filename[:-3]}")

            await self.reload_cogs(cogs_to_reload)

            await inter.edit_original_message(content=f"✅ Reloaded {len(cogs_to_reload)} cogs.")
        else:
            await inter.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)
            
def setup(bot):
    bot.add_cog(Owner(bot))
