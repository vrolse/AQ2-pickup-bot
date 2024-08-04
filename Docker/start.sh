#!/bin/bash

# List of required environment variables
required_vars=("DISCORDBOTTOKEN" "APPID" "YOURDISCORDID" "GUILDID" "CHANNELID" "ROLEID" "YOURSITE" "QSTAT" "REPO_USER" "REPO_NAME" "BRANCH" "DIRECTORY" "DLDIRECTORY")

# Check if required environment variables are set
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable(s) not set: $var"
        exit 1
    fi
done

# GitHub repository details
repo_user=$REPO_USER
repo_name=$REPO_NAME
branch=$BRANCH
directory=$DIRECTORY

# Destination directory for downloaded files
download_directory=$DLDIRECTORY

# API URL to get the contents of the directory
api_url="https://api.github.com/repos/${repo_user}/${repo_name}/contents/${directory}?ref=${branch}"

# Function to update config.json
update_config() {
    sed -i "s-PREFIX-$PREFIX-g" AQ2-pickup/config.json
    sed -i "s:DISCORDBOTTOKEN:$DISCORDBOTTOKEN:g" AQ2-pickup/config.json
    sed -i "s-PERMISSIONS-$PERMISSIONS-g" AQ2-pickup/config.json
    sed -i "s-APPID-$APPID-g" AQ2-pickup/config.json
    sed -i "s-YOURDISCORDID-$YOURDISCORDID-g" AQ2-pickup/config.json
    sed -i "s-GUILDID-$GUILDID-g" AQ2-pickup/config.json
    sed -i "s-CHANNELID-$CHANNELID-g" AQ2-pickup/config.json
    sed -i "s-ROLEID-$ROLEID-g" AQ2-pickup/config.json
    sed -i "s-YOURSITE-$YOURSITE-g" AQ2-pickup/config.json
    sed -i "s:PATH_TO_QSTAT:$QSTAT:g" AQ2-pickup/config.json
    sed -i "s:REPOUSERNAME:$REPO_USER:g" AQ2-pickup/config.json
    sed -i "s:REPONAME:$REPO_NAME:g" AQ2-pickup/config.json
    sed -i "s:GITBRANCH:$BRANCH:g" AQ2-pickup/config.json
    sed -i "s:GITDIRECTORY:$DIRECTORY:g" AQ2-pickup/config.json
    sed -i "s:PATH_TO_THUMBS:$DLDIRECTORY:g" AQ2-pickup/config.json
}

# Function to download files from GitHub repository
download_files() {
    downloaded_files=0

    # Check if the download directory exists, create if it doesn't
    if [ ! -d "$download_directory" ]; then
        echo "Download directory not found. Creating $download_directory..."
        mkdir -p "$download_directory"
    fi

    while read -r file_url; do
        filename=$(basename "$file_url")

        if [ ! -e "$download_directory/$filename" ] || [ "$file_url" -nt "$download_directory/$filename" ]; then
            if curl -s -L "$file_url" -o "$download_directory/$filename"; then
                echo "Downloaded: $filename"
                downloaded_files=$((downloaded_files + 1))
            else
                echo "Failed to download: $filename"
            fi
        fi
    done < <(curl -s "$api_url" | grep -o '"download_url": "[^"]*' | cut -d'"' -f4)

    if [ "$downloaded_files" -eq 0 ]; then
        echo "No new files needed to be downloaded."
    else
        echo "Downloaded $downloaded_files file(s)."
    fi
}

# Check if config.json exists
if [ ! -f "AQ2-pickup/config.json" ]; then
    echo "Error: Configuration file not found."
    exit 1
fi

# Update config.json
update_config

# Download files from GitHub repository
download_files

# Start the bot
cd /home/bot/AQ2-pickup/
python3 bot.py
