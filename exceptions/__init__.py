""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 4.1
"""
from disnake.ext import commands

class UserBlacklisted(commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is blacklisted.
    """

    def __init__(self, message="User is blacklisted!"):
        self.message = message
        super().__init__(self.message)


class UserNotOwner(commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is not an owner of the bot.
    """

    def __init__(self, message="User is not an owner of the bot!"):
        self.message = message
        super().__init__(self.message)


class UserNotAdmin(commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is not an admin of the bot.
    """

    def __init__(self, message="User is not an admin of the bot!"):
        self.message = message
        super().__init__(self.message)


class NotInGuild(commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is not in a guild.
    """

    def __init__(self, message="User is not in a guild!"):
        self.message = message
        super().__init__(self.message)
