"""
## The MIT License (MIT)

`Copyright (c) 2021-present Marcus`

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the rsons to whom the
Software is furnished to do so, subject to the foll ("Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
> OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
> FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
> DEALINGS IN THE SOFTWARE.
"""

import asyncio
import json
import os
import random
import re
import sys
import traceback
from os import environ
from typing import *

import aiohttp
import discord
from discord import *
from discord.ext import commands, tasks
from discord.ext.commands import core
from discord.ext.paginator import Paginator
from DiscordUtils import *
from dotenv import load_dotenv
from pydantic import BaseModel

from config import Tokens
from Help import CustomHelp
from Helpers import *

load_dotenv()
# os.chdir("./launcher.py")

colors = [
    0xF3FF00,
    0x00FFFF,
    0x0036FF,
    0xF000FF,
    0xFF0000,
    0x17FF00,
    0x00FF93,
    0x00B2FF,
    0x0013FF,
    0x65FF00,
]


def version():
    with open("./VERSION.txt", "r+") as f:
        lines = f.read()
    return lines or "3.4.1"


def get_all_tokens():
    secrets = Tokens(_env_file=".env")
    return secrets


def get_token(TOKEN_TYPE: str = None):
    TOKENS = get_all_tokens()
    if TOKEN_TYPE == "TOKEN_2":
        token = TOKENS.TOKEN_2
    # elif TOKEN_TYPE == "ME":
    #     token = os.getenv("ME")
    else:
        token = TOKENS.TOKEN
    if not token:
        raise TypeError("No Token detected")
    return token


class Config(BaseModel):
    BOT_TOKEN: str = None
    DEFAULT_PREFIX: str = None
    EXTENSIONS: List[str] = None
    OWNER_ID: int = None
    ME: Optional[str] = "Marcus | Bot Dev#4438"


def get_config(token_type: str = "TOKEN_2"):
    with open("./assets/secrets.json", "r+") as f:
        dat = json.load(f)
    if ("BOT_TOKEN" not in dat.keys()) or (dat["BOT_TOKEN"] is None):
        dat["BOT_TOKEN"] = get_token(token_type)
    conf = Config(**dat)
    return conf


help_obj = CustomHelp()
help_obj.show_hidden = True
help_obj.verify_checks = False
help_obj.command_attrs = {
    "name": "help",
    "help": "Shows help about a command or a category",
    "aliases": ["helps"],
    "cooldown": commands.Cooldown(1, 5, commands.BucketType.channel),
    "brief": "5s",
}


class MyBot(commands.Bot):
    def __init__(self, token_type="TOKEN_2"):
        self.token = token_type
        intents = discord.Intents().default()
        intents.members = True
        self.config = get_config(token_type)
        super().__init__(
            command_prefix=[self.config.DEFAULT_PREFIX, "H!"],
            help_command=help_obj,
            description="Hutch Bot - A moderation bot with many fun commands and essential moderation commands",
            owner_id=self.config.OWNER_ID,
            intents=intents,
            strip_after_prefix=True,
            case_insensitive=True,
        )
        environ["JISHAKU_NO_UNDERSCORE"] = "True"
        environ["JISHAKU_RETAIN"] = "True"
        self.logs: Union[List[discord.TextChannel], None] = None

        # NOTE: USELESS ATTRIBUTES
        self.__author__ = "Marcus"
        self.__title__ = "Hutch Bot"
        self.__license__ = "MIT"
        self.__copyright__ = "Copyright 2021-present Marcus"
        self.__version__ = version() or "3.4.1"

        # NOTE: USEFUL ATTRIBUTES
        self.colors = colors
        self.colours = colors
        self.paginator = Paginator
        self.initial_ext = [
            "cogs.Fun",
            "cogs.Misc",
            "cogs.Dev",
            "cogs.Moderation",
            "jishaku",
        ]

        self.session = aiohttp.ClientSession()

        # NOTE: LOADING EXTENSIONS
        for ext in self.initial_ext:
            try:
                self.load_extension(ext)
            except Exception as e:
                # raise e
                err: List[str] = traceback.format_exception(type(e), e, e.__traceback__)
                _1, _2, _3 = err[-3], err[-2], err[-1]
                exc = f"{_1}{_2}{_3}"
                print(f"ERROR: [{ext}] \n{exc}")

        # NOTE:  DATABASES
        from data import Database

        self.warns = Database("./databases/warns.sqlite")

    async def get_context(self, message: discord.Message, *, cls=Context):
        ctx: Context = await super().get_context(message, cls=Context)
        return ctx

    async def on_ready(self):
        self.logs: List[discord.TextChannel] = [
            self.get_channel(_id) for _id in [847931426938945597, 845739412867514442]
        ]
        print("\n")
        print("-" * 50)
        print("The Servers The Bot is in:")
        for guild in self.guilds:
            print("\t" + guild.name)
        print("-" * 50)
        print("{0.name} is Running!".format(self.user))
        print("-" * 50)
        if self.is_ready():
            print("Cache Ready:", self.owner_id)
            print("-" * 50)
        for ch in self.logs:
            try:
                import datetime

                await ch.send(
                    f"<@!754557382708822137> im up! - {datetime.datetime.utcnow()}"
                )
                break
            except AttributeError:
                pass

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        ctx: Context = await self.get_context(message, cls=Context)
        channel: discord.TextChannel = message.channel

        if (f"<@!{self.user.id}>" in message.content) and (len(message.mentions) == 1):
            await ctx.send(
                f"Hello :wave:, my prefix is {self.config.DEFAULT_PREFIX}. You can do `{self.config.DEFAULT_PREFIX}help` to get some help!"
            )
        if message.mention_everyone and message.guild.id not in [
            681882711945641997,
            841721684876328961,
        ]:
            if not message.author.guild_permissions.mention_everyone:
                try:
                    message.author.kick(
                        reason="Automoderator: Mentioning @ everyone or @ here without permissions | ToS violation"
                    )
                    await message.channel.send(
                        f"{message.author.mention} was kicked for mentioning everyone or here without permissions | ToS violation"
                    )
                except:
                    pass
        if not message.author.bot:
            await self.process_commands(message)

    async def on_error(self, event_method, *args, **kwargs):
        tb = traceback.format_exc()
        for channel in self.logs:
            try:
                embed = discord.Embed(description=f"```py\n{tb}\n```")
                await channel.send(embed=embed)
                break
            except AttributeError:
                pass

    async def on_guild_join(self, guild: discord.Guild):
        logs: List[discord.TextChannel] = self.logs
        embed = discord.Embed(
            title="Joined New Server",
            description=f"{guild.name} | {guild.member_count}",
        )
        for ch in logs:
            try:
                await ch.send(embed=embed)
                break
            except AttributeError:
                pass
        channel = random.choice(guild.text_channels)
        if channel.permissions_for(guild.me).embed_links:
            em = discord.Embed(title="Thank you for adding me!")
            em.add_field(name="Prefix", value="h!")
            em.add_field(
                name="Config",
                value="You have don't have to waste time configuring since this is a pre-configured bot!",
            )
            em.set_thumbnail(url=guild.icon_url)
            em.set_footer(
                text="Please make sure this bot has `embed_links` permission in all the channels"
            )
            return await channel.send(embed=em)
        else:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(
                        "Thanks for adding!\nPlease make sure I have `embed_links` permission to work properly!"
                    )
                    break
            return

    async def close(self):
        await self.session.close()
        return await super().close()

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        author: discord.User = after.author
        ctx: Context = await self.get_context(after, cls=Context)
        if (before.content != after.content) and not (author.bot):
            await self.invoke(ctx)

    def get_all_commands(
        self,
        cmds: Set[Union[commands.Command, commands.Group]] = None,
        lis: list = list(),
    ):
        """
        Gets all of the bot's commands as a list which is converted
        to a set before hand to remove any repeated command names
        """
        cmds = cmds or self.commands
        if isinstance(cmds, commands.Group):
            lis.append(cmds.qualified_name)
            get_all_commands(cmds.commands, lis)
        if isinstance(cmds, commands.Command):
            lis.append(cmds.qualified_name)
        if isinstance(cmds, set):
            for cmd in cmds:
                get_all_commands(cmd, lis)
        return list(set(lis))

    async def on_command(self, ctx: Context):
        if ctx.author.id == self.owner_id:
            ctx.command.reset_cooldown(ctx)
        else:
            pass

    async def on_command_error(self, ctx: Context, error: commands.CommandError):
        error = getattr(error, "original", error)
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CommandOnCooldown):
            desc = f"That Command is on cooldown. Try again after **{error.retry_after:.2f}** secs"
            return await ctx.to_error(desc)
        if isinstance(error, commands.DisabledCommand):
            desc = "This Command is disabled throughout the bot, please wait patiently until it is enabled again"
            return await ctx.to_error(desc)
        if not isinstance(
            error, commands.CommandInvokeError
        ):  # handling method copied and modified from https://github.com/TechStruck/TechStruck-Bot/
            ctx.command.reset_cooldown(ctx)
            title = " ".join(
                re.compile(r"[A-Z][a-z]*").findall(error.__class__.__name__)
            )
            em = discord.Embed(
                title=title, description=str(error), color=discord.Color.red()
            )
            em.set_footer(
                text=f"If this was a mistake please contact {self.config.ME}",
                icon_url=ctx.author.avatar_url,
            )
            return await ctx.send(embed=em)

        # unexpected error
        traceback.print_exception(type(error), error, error.__traceback__)
        error_em = await ctx.to_error()

        trace = traceback.format_exception(type(error), error, error.__traceback__)
        _1, _2, _3 = trace[-3], trace[-2], trace[-1]
        err = f"{_1}{_2}{_3}"
        info = [
            ("Guild:", ctx.guild.name if ctx.guild else f"{ctx.author}"),
            ("Message:", f"`{ctx.message.content}` | [Link]({ctx.message.jump_url})"),
            ("Channel:", f"{ctx.channel.name} | {ctx.channel.mention}"),
        ]
        embed = discord.Embed(description=f"```py\n{err}\n```")  # f"```py\n{err}```"
        for nam, val in info:
            embed.add_field(name=nam, value=val, inline=False)
        for log in self.logs:
            try:
                await log.send(embed=embed)
                break
            except AttributeError:
                pass
                # ik this is messy but one of the log channel would be NoneType
                # when using each of the bots and I didnt find any better way than this.
                # any help to make this better will be appreciated. : )
