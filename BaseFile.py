# core file to handle circular imports

import json
import os
from itertools import cycle
from typing import *

import diskord
from diskord.ext import tasks
from diskord.utils import oauth_url
from pydantic import BaseModel

import Bot
from data import Database
from utils.helpers import Context


def version():
    with open("./VERSION.txt", "r+") as f:
        lines = f.read()
    return lines or "3.4.1"


def oauth(ctx: Context):
    url = oauth_url(
        client_id=ctx.me.id,
        permissions=diskord.Permissions.all(),
        guild=ctx.guild,
        redirect_uri="https://discord.gg/5nzgEWSnEG",  # Join btw
    )
    return url


@tasks.loop(seconds=30)
async def change_status(bot):
    """Test"""
    status = cycle(
        [
            "Banning Rule Breakers",
            "Follow the rules",
            "Get Gud lol",
            "Sub to DCR",
            "Give Marcus Boost Nitro",
            f"DM {bot.config.ME} for a custom bot",
            "It took Marcus 10 Days to Make me",
            "Fun Fact: Marcus was born on June 10th",
            f"Helping people",
        ]
    )
    await bot.wait_until_ready()
    await bot.change_presence(
        activity=diskord.Activity(
            type=diskord.ActivityType.watching, name=f"{next(status)} | h!help"
        )
    )
