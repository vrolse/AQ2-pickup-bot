# AQ2 Pickup Docker

Host the bot using Docker.

## Setup

1. Create an `.env` file for the container with the following variables filled in:

    ```
    PREFIX=for-example-> ! <-
    DISCORDBOTTOKEN=your-bot-token-here
    PERMISSIONS=bot-permissions
    APPID=the-app-id
    YOURDISCORDID=your-discord-id
    GUILDID=guildid
    CHANNELID=channelid
    ROLEID=the-roleid-for-admins
    YOURSITE=url-to-your-site
    QSTAT=path-to-qstat
    TZ=Europe/Stockholm
    REPO_USER=github-username
    REPO_NAME=AQ2-pickup-bot
    BRANCH=eg. main
    DIRECTORY=thumbnails
    DLDIRECTORY=path-to-thumbnails
    EOLMSG=your-eol-msg
    ```

2. You may need to make some changes to the bot's code as it is not perfect. Ensure you edit the delimiter character in `start.sh` so it works with the environment variables.

## Environment Variables

- `PREFIX`: Command prefix for the bot (e.g., `!`)
- `DISCORDBOTTOKEN`: Your bot's token
- `PERMISSIONS`: Bot permissions
- `APPID`: The application ID
- `YOURDISCORDID`: Your Discord user ID
- `GUILDID`: The guild (server) ID
- `CHANNELID`: The channel ID
- `ROLEID`: The role ID for admins
- `YOURSITE`: URL to your site
- `QSTAT`: Path to `qstat`
- `TZ`: Time zone (e.g., `Europe/Stockholm`)
- `REPO_USER`: GitHub username
- `REPO_NAME`: Repository name (e.g., `AQ2-pickup-bot`)
- `BRANCH`: Branch name (e.g., `main`)
- `DIRECTORY`: Directory for thumbnails
- `DLDIRECTORY`: Path to download thumbnails
- `EOLMSG`: The message that should be sent to the bot in a DM for it to shut down and send the message in eol.py
- `BASE_URL`: URL to maps

## Notes

- Ensure all required information is correctly filled in the `.env` file.
- Make necessary changes to the bot code if needed.
- Edit `start.sh` to align with the environment variable delimiters if necessary.
