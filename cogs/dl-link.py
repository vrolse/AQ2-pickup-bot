import requests
import disnake
import json
import sys
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from disnake.ext import commands
from disnake import ApplicationCommandInteraction

# Only if you want to use variables that are in the config.json file.
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)
        
#Add what needs to be loaded from config.json
GUILDID = int(config["GUILD_ID"])

# Fake User-Agent to mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

# List of allowed file extensions
ALLOWED_EXTENSIONS = (".zip", ".rar", ".7z", ".tar", ".pak", ".pkz", ".tar.gz")


class MapDownloader(commands.Cog, name="Map Downloader"):
    def __init__(self, bot, base_url):
        self.bot = bot
        self.base_url = base_url

    def get_file_links(self, url):
        """Fetch and filter file links"""
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            file_links = []
            for a_tag in soup.find_all("a", href=True):
                full_url = urljoin(url, a_tag["href"])
                if full_url.lower().endswith(ALLOWED_EXTENSIONS):
                    file_links.append(full_url)

            return file_links
        except requests.RequestException as e:
            print(f"Error fetching the webpage: {e}")
            return []

    def find_matching_file(self, links, mapname):
        """Find the matching file link for a given map name."""
        lower_map_name = mapname.lower()
        for link in links:
            file_name = link.rsplit("/", 1)[-1].lower()
            if file_name.startswith(lower_map_name):
                return link
        return None

    @commands.slash_command(
        guild_ids=[GUILDID],
        name="downloadmap",
        description="Get the download link for a map."
        )
    async def downloadmap(self, inter: ApplicationCommandInteraction, mapname: str):

        await inter.response.defer(ephemeral=True)

        # Fetch file links
        file_links = self.get_file_links(self.base_url)

        # Search for matching files
        matching_link = self.find_matching_file(file_links, mapname)
        if matching_link:
            await inter.send(f"Here is the download link to the map **{mapname}**:\n{matching_link}", ephemeral=True)
        else:
            await inter.send(f"Sorry, I couldn't find a file for the map **{mapname}**. Please check the name and try again.", ephemeral=True,)


def setup(bot):
    BASE_URL = config["BASE_URL"]
    bot.add_cog(MapDownloader(bot, BASE_URL))
