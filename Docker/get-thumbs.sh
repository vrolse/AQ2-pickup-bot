#!/bin/bash

# GitHub repository details
repo_user=$REPO_USER
repo_name=$REPO_NAME
branch=$BRANCH

# Directory within the repository to download
directory=$DIRECTORY

# Destination directory for downloaded files
download_directory=$DLDIRECTORY

# API URL to get the contents of the directory
api_url="https://api.github.com/repos/${repo_user}/${repo_name}/contents/${directory}?ref=${branch}"

# Create the thumbnails directory if it doesn't exist
mkdir -p "$download_directory"

# Download files from the GitHub repository only if they are newer or don't exist
download_files() {
    downloaded_files=0
    
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

# Run the download function
download_files
