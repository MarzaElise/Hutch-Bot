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

import datetime
import difflib
import json
import random
import re
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

from config import *
from Help import CustomHelp
from utils.helpers import *

load_dotenv()

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


class MyBot(commands.Bot):
    def __init__(self, token_type="TOKEN_2"):
        self.config = get_config(token_type)
        self.set_bot_config()
        help_obj = CustomHelp(self)
        help_obj.show_hidden = True
        help_obj.verify_checks = False
        help_obj.command_attrs = {
            "name": "help",
            "help": "Shows help about a command or a category",
            "aliases": ["helps"],
            "cooldown": commands.Cooldown(1, 5, commands.BucketType.channel),
            "brief": "5s",
        }
        # weird way of passing in token_type in params and running the bot
        # but this is the only way I found to run bots with two tokens without changing much code.
        super().__init__(
            command_prefix=self.prefix,  # [self.config.DEFAULT_PREFIX, "H!"],
            intents=discord.Intents.all(),
            help_command=help_obj,
            description="Hutch Bot - A moderation bot with many fun commands and essential moderation commands",
            owner_id=self.config.OWNER_ID,
            strip_after_prefix=True,
            case_insensitive=True,
        )

        self.logs: Union[
            List[discord.TextChannel], None
        ] = None  # logs channels are set in on_ready

        self._session = (
            aiohttp.ClientSession()
        )  # global session to interact with external APIs
        self.load_all_extensions()

    def set_bot_config(self):
        """Function called inside __init__ to reduce code inside init and make shit more organized"""
        environ["JISHAKU_NO_UNDERSCORE"] = "True"
        environ["JISHAKU_RETAIN"] = "True"

        self.colors = colors  # handpicked colors
        self.colours = colors  # aliasing
        self.testing_guilds = [
            681882711945641997,  # TCA
            690557545965813770,  # PgamerX
            841721684876328961,  # TCA bot testing
            # 710534717652336732, # Space Kingdom
            804592931586572298,  # zennithh
        ]
        # servers where the bot is invited for testing with extra rules and limitations
        # self.help_command = help_obj

    @property
    def session(self):
        return self._session

    def generate_cache(self):
        """Generates a cache dict for each of the most used models to reduce querying."""
        from models import GuildModel, MemberModel

        # i dont rlly need these in the global scope, only for a few lines in here
        # TODO: fill this method

    def load_all_extensions(self):
        self.initial_ext = [
            "cogs.Fun",
            "cogs.Misc",
            "cogs.Dev",
            "cogs.Moderation",
            "jishaku",
        ]
        for ext in self.initial_ext:
            try:
                self.load_extension(ext)
            except Exception as e:
                # raise e
                print(
                    f"ERROR: [{ext}] \n{traceback.format_exception(type(e), e, e.__traceback__)[-1]}"
                )
                # minimal info is enough to know what happened in most cases.
                # I can just change this whenever I want to see the entire exception

    def prefix(self, bot, message: discord.Message):
        ret = [self.config.DEFAULT_PREFIX, "H!"]
        # if message.author.id == self.owner_id: # causes chaos. :bruh:
        #     ret.append("")  # empty prefix for me
        return ret

    async def get_context(self, message: discord.Message, *, cls=Context):
        ctx: Context = await super().get_context(message, cls=Context)
        return ctx

    async def on_ready(self):
        self.logs: List[discord.TextChannel] = [
            self.get_channel(_id)
            for _id in [847931426938945597, 845739412867514442]
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
        await report_to_logs(
            self,
            content=f"<@!754557382708822137> im up! - <t:{int(datetime.datetime.utcnow().timestamp())}>",
        )

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        ctx: Context = await self.get_context(message, cls=Context)
        channel: discord.TextChannel = message.channel

        if (f"<@!{self.user.id}>" in message.content) and (
            len(message.mentions) == 1
        ):
            await ctx.send(
                f"Hello :wave:, my prefix is {self.config.DEFAULT_PREFIX}. You can do `{self.config.DEFAULT_PREFIX}help` to get some help!"
            )
        if not message.author.bot:
            await self.process_commands(message)

    async def on_error(self, event_method, *args, **kwargs):
        tb = traceback.format_exc()
        file = None
        embed = discord.Embed()
        embed.title = str(event_method).title()
        embed.description = f"```py\n{tb}\n```"
        if len(tb) > 2000:
            file = discord.File(io.StringIO(tb), str(event_method))
            embed = (
                None  # we dont need an embed if we are going to send a file
            )

        await report_to_logs(self, content=None, embed=embed, file=file)

    async def on_guild_join(self, guild: discord.Guild):
        embed = discord.Embed(
            title="Joined New Server",
            description=f"{guild.name} | {guild.member_count}",
        )
        await report_to_logs(self, content=None, embed=embed)
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

    async def logout(self):
        return await self.close()

    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ):
        author: discord.User = after.author
        ctx: Context = await self.get_context(after, cls=Context)
        if (
            (before.content != after.content)
            and (author.bot == False)
            and (after.author.id == self.owner_id)
        ):
            await self.invoke(ctx)

    def get_all_commands(
        self,
        cmds: Set[Union[commands.Command, commands.Group]] = None,
        lis: list = list(),
    ):
        """
        Gets all of the bot's commands or a group's commands as a list which is converted
        to a set before hand to remove any repeated command names
        """
        cmds = cmds or self.commands
        if isinstance(cmds, commands.Group):
            lis.append(cmds.qualified_name)
            self.get_all_commands(cmds.commands, lis)
        if isinstance(cmds, commands.Command):
            lis.append(cmds.qualified_name)
        if isinstance(cmds, set):
            for cmd in cmds:
                self.get_all_commands(cmd, lis)
        return list(set(lis))

    async def on_command(self, ctx: Context):
        if ctx.author.id == self.owner_id:
            ctx.command.reset_cooldown(ctx)

    async def on_command_error(
        self, ctx: Context, error: commands.CommandError
    ):

        if isinstance(error, commands.CommandNotFound):
            matches = difflib.get_close_matches(
                str(error).split('"')[1], self.get_all_commands()
            )
            if len(matches) > 0:
                fmt = "\n".join(matches)
                desc = f"Command was not found, closest matches are...\n{fmt}"
                return await ctx.to_error(desc)
            return

        if hasattr(ctx.command, "on_error"):
            return

        if isinstance(error, commands.CommandOnCooldown):
            desc = f"That Command is on cooldown. Try again after **{error.retry_after:.2f}** secs"
            return await ctx.to_error(desc)

        if isinstance(error, commands.DisabledCommand):
            desc = "This Command is disabled throughout the bot, please wait patiently until it is enabled again"
            return await ctx.to_error(desc)

        # i handled the above errors like that since the default error message isnt really helpful at times
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

        trace = traceback.format_exception(
            type(error), error, error.__traceback__
        )
        tb = "".join(trace)
        # _1, _2, _3 = trace[-3], trace[-2], trace[-1]
        err = tb[
            :2000
        ]  # minimal info which would include which error was raised and stuff
        info = [
            ("Guild:", ctx.guild.name if ctx.guild else f"{ctx.author}"),
            ("Id:", ctx.guild.id if ctx.guild else ctx.author.id),
            (
                "Message:",
                f"`{ctx.message.content}` | [Link]({ctx.message.jump_url})",
            ),
            ("Channel:", f"{ctx.channel.name} | {ctx.channel.mention}"),
        ]
        embed = discord.Embed(description=f"```py\n{err}\n```")
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

    def get_docs(
        self,
        entity: Optional[
            Union[commands.Command, commands.Group, commands.Cog]
        ] = None,
        *,
        error=True,
    ) -> str:
        """
        Get the documentation link for a given category or a command (including group commands)

        Takes in one ``entity`` argument that you need the documentation link for. Returns the home page if no entity given

        Raises:
            :class:`NotDocumented`: Requested entity is not documented
        """
        base = "https://hutch-bot.readthedocs.io"
        # base = "http://127.0.0.1:8000" # for testing
        if not entity:
            if error:
                raise NotDocumented(
                    "No entity was given to get the documentation link for. Are you sure you spelt it correctly?"
                )
            name = "/home"
        if isinstance(entity, commands.Cog):
            name = "/commands/" + str(entity.qualified_name).lower()
        if isinstance(entity, (commands.Command, commands.Group)):
            cmd = str(entity.qualified_name).lower().replace(" ", "-")
            if not entity.cog:
                if error:
                    raise NotDocumented(
                        f"Command {entity.qualified_name} is not documented yet."
                    )
                return False
            category = entity.cog.qualified_name.lower()
            name = "/commands" + f"/{category}" + f"/#{cmd}"
        final = base + name
        if url_exists(final):
            return final
        if error:
            raise NotDocumented(
                f"{entity.qualified_name} was not found in the documentation."
            )
        return False

    async def get_message(
        self, channel_id: int, msg_id: int, formatted: bool = True
    ):  # not tested
        if not isinstance(msg_id, int):
            try:
                msg_id = int(msg_id)
            except ValueError:
                return f"Expected msg_id to be an int, received {msg_id.__class__.__name__} instead"
        if not isinstance(channel_id, int):
            try:
                channel_id = int(channel_id)
            except ValueError:
                return f"Expected channel_id to be an int, received {channel_id.__class__.__name__} instead"
        message = await self.http.get_message(channel_id, msg_id)
        fmt = json.dumps(message, indent=4)
        if formatted:
            return f"```\n{fmt}\n```"
        return fmt
