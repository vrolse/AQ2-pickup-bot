FROM python:slim

# Set environment variables
ENV USER=bot
ENV UID=1001

# Create a non-root user
RUN adduser --disabled-password --gecos "" --uid "$UID" "$USER"

# Switch to the new user
USER bot
WORKDIR /home/bot

# Copy scripts
COPY start.sh get-thumbs.sh /home/bot/

# Install dependencies, download and set up required files
RUN apt-get update -qq \
    && apt-get install --no-install-recommends -y curl nano git unzip python3-pip \
    && curl -sSL -o main.zip https://github.com/vrolse/AQ2-pickup-bot/archive/refs/heads/main.zip \
    && unzip -qq main.zip -d tmp \
    && mv /home/bot/tmp/AQ2-pickup-bot-main /home/bot/AQ2-pickup \
    && curl -sSL -o release.zip https://github.com/Unity-Technologies/qstat/releases/download/v2.17/release.zip \
    && unzip -qq release.zip -d tmp \
    && mv /home/bot/tmp/bin/linux_amd64/qstat /home/bot/AQ2-pickup/ \
    && rm -rf tmp main.zip release.zip \
    && cd /home/bot/AQ2-pickup \
    && pip install --no-cache-dir -r requirements.txt \
    && cd /home/bot \
    && mkdir /home/bot/matchlogs \
    && apt-get remove -y git unzip \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Make scripts executable
RUN chmod +x start.sh get-thumbs.sh /home/bot/AQ2-pickup/qstat

# Set entrypoint
ENTRYPOINT ["/home/bot/start.sh"]

# Set environment variables
ENV PREFIX for-example->!<-
ENV DISCORDBOTTOKEN your-bot-token-here
ENV PERMISSIONS bot-permissions
ENV APPID the-app-id
ENV YOURDISCORDID your-discord-id
ENV GUILDID guildid
ENV CHANNELID channelid
ENV ROLEID the-roleid-for-admins
ENV YOURSITE YOURSITE
ENV QSTAT PATH_TO_QSTAT
ENV TZ Europe/Stockholm
ENV REPO_USER REPOUSERNAME
ENV REPO_NAME REPONAME
ENV BRANCH GITBRANSH
ENV DIRECTORY GITDIRECTORY
ENV DLDIRECTORY PATH_TO_THUMBS
