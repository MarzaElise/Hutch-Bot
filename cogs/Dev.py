import asyncio
import os
import random
import sys
import traceback
from inspect import getsource, getsourcefile
from io import StringIO
from typing import List

import diskord
import humanize
import psutil
from BaseFile import *
from Bot import MyBot
from diskord import Message
from diskord.ext import *
from diskord.ext.commands import BucketType
from diskord.ext.commands.cooldowns import CooldownMapping
from diskord.utils import *
from utils.helpers import *
from jishaku.modules import package_version


class MemberBlacklisted(commands.CommandError):
    pass


def version():
    with open("./VERSION.txt", "r+") as f:
        lines = f.read()
    return lines or "3.4.1"


inv_url = oauth_url(
    client_id=799973356685361154,
    permissions=diskord.Permissions.all(),
    guild=None,
    redirect_uri=None,
)

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


class Dev(commands.Cog):
    r"""Developer Stuff mainly related to the bot itself"""

    def __init__(self, bot: MyBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.__class__.__name__} Loaded")
        print("*" * 50)

    # "https://dsc.bio/marcussimps"

    @commands.command(
        aliases=["restart"], help="Restart the entire bot", brief="0s"
    )
    @commands.is_owner()
    async def reboot(self, ctx: Context):
        try:
            await ctx.send("Rebooting")
            await self.bot.close()
            os.execv(
                sys.executable, ["python"] + sys.argv
            )  # really retarded way but it works :shrug:
        except Exception as e:  # i dont know what error could be raised
            tb = "".join(
                traceback.format_exception(type(e), e, e.__traceback__)
            )
            await ctx.em(heading="Reboot Failed", desc=f"``py\n{tb}\n```")

    @commands.command(
        name="reload", help="Reaload all the cogs of this bot", brief="0s"
    )
    @commands.is_owner()
    async def _reload(self, ctx: Context):
        """Reloads all the cogs of this bot"""
        reloaded = []
        exceptions = []
        # reloading  all the cogs
        for ext in self.bot.initial_ext:
            try:
                self.bot.reload_extension(ext)
                reloaded.append(ext)
            except Exception as e:
                trace = traceback.format_exception(
                    type(e), e, e.__traceback__
                )[-1]
                # cant get full tb cos it would pass the maximum embed value limit
                # so just the error would be enough
                exceptions.append(f"```py\n{trace}\n```")

        reload_ = "Success" if len(exceptions) == 0 else "Unsuccesfull :("
        em = diskord.Embed(title=reload_, color=random.choice(colors))
        em.add_field(
            name="Reloaded Extensions", value="\n".join(reloaded), inline=False
        )
        if len(exceptions) > 0:
            for tb in exceptions:
                em.add_field(name="Error:", value=tb, inline=True)
        await ctx.send(embed=em)

    @commands.command(help="Enable a previously disabled command", brief="0s")
    @commands.is_owner()
    async def enable(self, ctx: Context, *, command_name: str):
        command = self.bot.get_command(command_name)
        if not command:
            return await ctx.to_error("Command not Found")
        cmd: commands.Command = command
        if cmd.enabled:
            return await ctx.to_error("That command is already enabled")
        if not cmd.enabled:
            cmd.enabled = True
            em = ctx.em(
                heading="Command Enabled",
                desc=f"Command {command_name} is enabled",
                col=diskord.Color.green(),
            )
            await ctx.send(embed=em)

    @commands.command(help="Disable a command throught the bot", brief="0s")
    @commands.is_owner()
    async def disable(self, ctx: Context, *, command_name: str):
        command = self.bot.get_command(command_name)
        if not command:
            return await ctx.to_error("Command not found")
        cmd: commands.Command = command
        if not cmd.enabled:
            return await ctx.to_error("Command already disabled")
        if cmd.enabled:
            cmd.enabled = False
            em = ctx.em(
                heading="Command Disabled",
                desc=f"Command {command_name} is disabled",
                col=diskord.Color.red(),
            )
            await ctx.send(embed=em)

    @commands.command(
        aliases=["uv"], help="Update the VERSION.txt file", brief="0s"
    )
    @commands.is_owner()
    async def update(self, ctx: Context, *, new_version: str):
        try:
            with open("./VERSION.txt", "r+") as f:
                f.write(new_version)
            new = version()
            await ctx.send(f"Updated bot version to {new}")
        except Exception as e:
            err = traceback.format_exception(type(e), e, e.__traceback__)
            em = diskord.Embed(description=f"```py\n{err}\n```")
            await ctx.send(embed=em)

    @commands.command(help="Report a bug to the dev", brief="12h")
    @commands.dm_only()
    @commands.cooldown(1, 60 * 60 * 12, commands.BucketType.user)
    async def report(self, ctx: Context, *, message: str = None):
        """Report a bug to the dev"""
        if not message:
            return await ctx.send(
                "You need to send something with 50+ characters to report a bug"
            )
        if not len(message) > 50:
            return await ctx.send(
                "Your report needs to have more than 50 characters to be sent!"
            )
        me: List[diskord.TextChannel] = self.bot.logs
        try:
            for ch in me:
                try:
                    await ch.send(f"{message} \n\n-***{ctx.author}***")
                    break
                except AttributeError:
                    pass
        except Exception as e:
            return await ctx.to_error("Sending report failed\n\n{}".format(e))
            # if it couldnt report, then we would have to show the error to the
            # user and let them report it to me manually
        my_msg = await ctx.send("Report Sent successfully")
        return await my_msg.add_reaction("✅")

    @commands.command(brief="0s")
    @commands.is_owner()
    @commands.guild_only()
    @commands.bot_has_permissions(change_nickname=True)
    async def botnick(self, ctx: Context, *, new_nickname=None):
        me: diskord.Member = ctx.me
        try:
            if not new_nickname:
                await ctx.send(f"Current Display name -> *{me.display_name}*")
            await me.edit(nick=new_nickname)
            await ctx.send(
                f"Succesfully changed my display name -> {new_nickname}"
            )
        except Exception as e:
            await ctx.send(e)

    @commands.command(help="Display the statistic of the bot", brief="5s")
    @commands.cooldown(1, 5, BucketType.user)
    async def stats(self, ctx: Context):
        """Display the statistics of the bot"""
        em = diskord.Embed(
            color=diskord.Color.random(), timestamp=ctx.message.created_at
        )
        em.set_thumbnail(url=ctx.guild.icon_url)
        em.add_field(name="Bot Version", value=version(), inline=False)
        em.add_field(
            name="Total Users:", value=len(self.bot.users), inline=False
        )
        em.add_field(
            name="Total Servers:", value=len(self.bot.guilds), inline=False
        )
        em.add_field(
            name="Library:",
            value=f'diskord, version {package_version("diskord")}',
            inline=False,
        )
        url = oauth(ctx)
        links = [
            f"[Bot Invite]({url})",
            "[Support Server](https://discord.gg/NVHJcGdWBC)",
            "[Official Documentation][https://hutch-bot.readthedocs.io/en/latest]",
        ]
        em.add_field(
            name="Useful Links", value=" | ".join(links), inline=False
        )
        em.set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
        em.set_footer(
            text=f"Send {self.bot.config.ME} nitro for making this bot :)",
            icon_url=ctx.author.avatar_url,
        )
        await ctx.send(embed=em)

    @commands.group(
        help="View the latest changlogs of the bot",
        brief="5s",
        invoke_without_command=True,
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def changelogs(self, ctx: Context):
        """View the latest changlogs of the bot"""
        with open("./CHANGELOGS.txt", "r+") as f:
            logs = f.readlines()
        l = "".join(logs)
        em = diskord.Embed(color=random.choice(colors))
        em.title = f"Changelogs for version {version()}"
        em.description = f">>> {l}"
        em.set_author(
            name=f"{self.bot.user}", icon_url=self.bot.user.avatar_url
        )
        em.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=em)

    @changelogs.command(
        help="Change the changelogs to the latest features", brief="0s"
    )
    @commands.is_owner()
    async def new(self, ctx: Context, *, new_logs: str):
        """Change the changelogs to the latest features"""
        with open("./CHANGELOGS.txt", "w+") as f:
            f.write(new_logs)
        await ctx.send("Succesfully wrote new change logs. New Changelogs:")
        with open("./CHANGELOGS.txt", "r+") as f:
            logs = f.readlines()
        l = "".join(logs)
        em = diskord.Embed(color=random.choice(colors))
        em.title = f"Changelogs for version {version()}"
        em.description = f">>> {l}"
        em.set_author(
            name=f"{self.bot.user}", icon_url=self.bot.user.avatar_url
        )
        em.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=em)

    @commands.command(
        help="Get source code of a specific command as a file | Under development",
        brief="10s",
    )
    @commands.cooldown(10, 1, commands.BucketType.member)
    @commands.is_owner()
    async def source(self, ctx: Context, *, command: str):
        cmd = (
            self.bot.help_command.__class__
            if command in ["help", "helps"]
            else self.bot.get_command(command).callback
        )
        if not cmd:
            return await ctx.to_error(f"No Command called {command} was found")
        file = diskord.File(
            StringIO(getsource(cmd)), getsourcefile(cmd).split("\\")[-1]
        )
        await ctx.send(file=file)

    @commands.command(
        help="Get source code of a specific command as a file | Under development",
        brief="10s",
    )
    @commands.cooldown(10, 1, commands.BucketType.member)
    @commands.is_owner()
    async def source(self, ctx: Context, *, command: str):
        cmd = (
            self.bot.help_command.__class__
            if command in ["help", "helps"]
            else self.bot.get_command(command)
        )
        if not cmd:
            return await ctx.to_error(f"No Command called {command} was found")
        if command not in ["help", "helps"]:
            cmd = cmd.callback
        file = diskord.File(
            StringIO(getsource(cmd)), getsourcefile(cmd).split("/")[-1]
        )
        await ctx.send(file=file)

    def load_json(self, file_path):  # TODO: move to db
        import json

        with open(file_path, "r") as file:
            try:
                data = dict(json.load(file))
            except OSError:
                file.write("{}")
                data = dict(json.load(file))
            return data

    def write_json(self, file_path, data: dict):  # TODO: move to db
        import json

        with open(file_path, "w+") as fp:
            json.dump(data, fp, indent=4)

    def is_blacklisted(self, member: diskord.Member):  # TODO: move to db
        import json

        _id = str(member.id)
        blacklisted = self.load_json("./assets/blacklist.json")
        if _id in blacklisted.keys():
            return True
        return False

    @commands.command(
        help="Blacklist a certain member from the bot making them unable to use the bot",
        brief="0s",
    )
    @commands.is_owner()
    async def blacklist(
        self, ctx: Context, member: diskord.Member, *, reason: str = None
    ):
        reason = reason
        if self.is_blacklisted(member):
            return await ctx.to_error("Member already blacklisted")
        blacklists = self.load_json("./assets/blacklist.json")
        blacklists[str(member.id)]["reason"] = reason
        self.write_json("./assets/blacklist.json", blacklists)
        await ctx.em(
            heading="Success",
            desc="Member Succesfully blacklisted.",
            col=0x2ECC71,
        )


def setup(bot: commands.Bot):
    bot.add_cog(Dev(bot))
