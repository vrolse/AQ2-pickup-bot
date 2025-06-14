""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 4.1
"""

import json
import disnake
from typing import TypeVar, Callable

from disnake.ext import commands

from exceptions import *

T = TypeVar("T")


def is_owner() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is an owner of the bot.
    """

    async def predicate(context: commands.Context) -> bool:
        with open("config.json") as file:
            data = json.load(file)
        if context.author.id not in data["owners"]:
            raise UserNotOwner
        return True

    return commands.check(predicate)


def not_blacklisted() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is blacklisted.
    """

    async def predicate(context: commands.Context) -> bool:
        with open("blacklist.json") as file:
            data = json.load(file)
        if context.author.id in data["ids"]:
            raise UserBlacklisted
        return True

    return commands.check(predicate)

def admin() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is an admin.
    """

    async def predicate(context: commands.Context) -> bool:
        if not context.guild or not isinstance(context.author, disnake.Member):
            raise NotInGuild
        with open("config.json") as file:
            role_ids = json.load(file)["ROLE_ID"]
        if any(role.id in role_ids for role in context.author.roles):
            return True
        else:
            print("NOT HAPPY! :(")
            raise UserNotAdmin

    return commands.check(predicate)
