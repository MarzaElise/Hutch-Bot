import asyncio
import random
from typing import *
from BaseFile import *
import typing
import aiosqlite
import diskord
from better_profanity import *
from diskord.ext import *
from diskord.utils import *
from utils.helpers import *
from diskord.ext.commands import BucketType
from Bot import MyBot
import os
from data import Database
import traceback
import datetime
from diskord.ext.commands.errors import BotMissingPermissions

# os.chdir("../launcher.py")

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

non_automod_channels = [826515312538812496]

white_listed = [
    "lmao",
    "lol",
    "duck",
    "hell",
    "crap",
    "god",
    "wad",
    "smfh",
    "rot",
    "lmfao",
    "wtf",
    "damn",
    "stupid",
    "omg",
    "ugly",
    "kill",
]


class Moderation(commands.Cog):
    """Hutch Bot Moderation Category"""

    def __init__(self, bot: MyBot):
        self.bot = bot
        self.__cog_description__ = "Hutch Bot Moderation Category"

    @commands.Cog.listener()
    async def on_ready(self):
        # print("*" * 50)
        print(f"Cog {self.__class__.__name__} Loaded")
        print("*" * 50)

    def profanity_filter(self, message: diskord.Message):
        profanity.load_censor_words(whitelist_words=white_listed)
        if (
            profanity.contains_profanity(message.content)
            and len(message.role_mentions) == 0
        ):
            if (
                (message.guild)
                and (message.channel.id not in non_automod_channels)
                and (not message.mention_everyone)
            ):
                if (message.author.id != self.bot.owner_id) and (
                    message.author.id != message.guild.owner_id
                ):
                    if message.guild.id not in [
                        841721684876328961,
                        681882711945641997,
                        804592931586572298,
                        710534717652336732,
                    ]:
                        return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message: diskord.Message):
        # i honestly dont care about the automod shit. so, if any error, stfu and pass it :hahayes:
        if message.author.bot:
            return

        if self.profanity_filter(message):
            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention} watch your language!",
                    delete_after=5,
                )
            except:
                pass
        if (
            message.mention_everyone
            and message.guild.id not in self.bot.testing_guilds
        ):
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
        if message.mentions and len(message.mentions) > 5:
            if (
                message.guild
                and message.guild.id not in self.bot.testing_guilds
            ):
                try:
                    await message.author.send(
                        f"You were kicked from the server for mentioning too many people!"
                    )
                    await message.author.kick(
                        reason="Automoderator: Mass Mentioning"
                    )
                    await message.channel.send(
                        f"{message.author.mention} was kicked for mass mentioning"
                    )
                except:
                    pass

    @commands.command(help="Kick someone from the server", brief="0s")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx: Context, user: diskord.Member, *, reason=None):
        """kick someone from the server"""
        reason = reason or "No Reason Provided"
        await ctx.trigger_typing()
        if user == ctx.guild.me:
            return await ctx.send("No, I won't kick myself")
        if user == ctx.author:
            return await ctx.send("You dumb?")
        if user.top_role >= ctx.author.top_role:
            return await ctx.send(
                f"{ctx.author.mention} you cannot kick {user.display_name}"
            )
        if user.top_role >= ctx.guild.me.top_role:
            return await ctx.send(
                "I cannot kick members who are ranked above me"
            )
        if user.bot:
            await user.kick(reason=f"{ctx.author}: {reason}")
            return await ctx.send(f"Succesfully kicked **{user.mention}**")
        else:
            try:
                em = diskord.Embed(
                    title="\n", description="\n", color=random.choice(colors)
                )
                em.set_author(
                    name=ctx.author.display_name,
                    icon_url=ctx.author.avatar.url,
                )
                em.set_thumbnail(url=ctx.guild.icon.url)
                em.add_field(
                    name="Kicked",
                    value=f"You were Kicked from **{ctx.guild}**",
                    inline=False,
                )
                em.add_field(
                    name="By:", value=f"-*{ctx.author}*", inline=False
                )
                em.add_field(
                    name="Reason:", value=f"-*{reason}*", inline=False
                )
                await user.send(embed=em)
                await user.kick(reason=f"{ctx.author}: {reason}")
            except diskord.Forbidden:
                await user.kick(reason=f"{ctx.author}: {reason}")
            finally:
                await ctx.send(f"Succesfully kicked **{user.mention}**")

    def can_ban(
        self, ctx: Context, member: Union[diskord.Member, diskord.User]
    ):
        """Helper function that returns True if we can ban a member without raising any errors with Permissions"""
        if not ctx.guild:
            return False
        member = (
            ctx.guild.get_member(member.id)
            if ctx.guild.get_member(member.id)
            else member
        )
        if member.id == self.bot.user.id:
            return False
        if member.id == ctx.author.id:
            return False
        if isinstance(member, diskord.Member):
            if member.top_role >= ctx.author.top_role:
                return False
            if member.top_role >= ctx.guild.me.top_role:
                return False

    @commands.command(help="Ban someone from the server", brief="0s")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(
        self,
        ctx: Context,
        user: typing.Union[diskord.Member, diskord.User],
        *,
        reason=None,
    ):
        """Ban someone from the server"""
        reason = reason or "No Reason Provided"
        guild: diskord.Guild = ctx.guild
        await ctx.trigger_typing()
        if self.can_ban(ctx, user, send=True):

            if isinstance(user, diskord.User):
                await guild.ban(user, reason=f"{ctx.author}: {reason}")
                return await ctx.send(f"Succesfully banned **{user.mention}**")

            if isinstance(user, diskord.Member):
                await ctx.send(f"Succesfully banned **{user.mention}**")
                try:
                    em = (
                        diskord.Embed(
                            title="\n",
                            description="\n",
                            color=random.choice(colors),
                        )
                        .set_author(
                            name=ctx.author.display_name,
                            icon_url=ctx.author.avatar.url,
                        )
                        .set_thumbnail(url=ctx.guild.icon.url)
                        .add_field(
                            name="Banned",
                            value=f"You were Banned from **{ctx.guild}**",
                            inline=False,
                        )
                        .add_field(
                            name="By:", value=f"-*{ctx.author}*", inline=False
                        )
                        .add_field(
                            name="Reason:", value=f"-*{reason}*", inline=False
                        )
                    )
                    if not user.bot:
                        await user.send(embed=em)
                except (
                    diskord.Forbidden,
                    diskord.HTTPException,
                ):  # couldnt DM member about ban
                    pass
                finally:
                    await user.ban(reason=f"{ctx.author}: {reason}")

    @commands.command(help="Mass Ban Membes", brief="0s")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def massban(
        self,
        ctx: Context,
        members: commands.Greedy[diskord.User],
        *,
        reason: str = None,
    ):
        members: List[diskord.User] = members
        reason = reason or "No Reason Provided"
        reason = f"{ctx.author}: {reason}"
        guild: diskord.Guild = ctx.guild
        for member in members:
            if self.can_ban(ctx, member, send=True):
                await guild.ban(member, reason=reason, delete_message_days=7)
            else:
                return await ctx.to_error(f"Could not ban {member}")
        await ctx.send(
            f"Succesfully banned {len(members)} members for reason: `{reason}`"
        )

    @commands.command(help="Unban a previously banned member", brief="0s")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx: Context, member: diskord.User, *, reason=None):
        """Unban a previously banned member"""
        reason = reason or "No Reason Provided"
        try:
            await ctx.guild.unban(diskord.Object(id=member.id), reason=reason)
            await ctx.send(f"**{member}** was succesfully unbanned")
        except BotMissingPermissions:
            await ctx.send("I dont have unban permissions")

    @commands.command(
        aliases=["rule"],
        help="Sends a breif description of common rules",
        brief="10s",
    )
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 10, BucketType.member)
    @commands.guild_only()
    async def rules(self, ctx: Context):
        """Sends a breif description of common rules"""
        with ctx.typing():
            await asyncio.sleep(1)
            newEmbed = diskord.Embed(
                title="Rules", color=random.choice(colors)
            )
            newEmbed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar.url
            )
            newEmbed.set_thumbnail(url=ctx.guild.icon.url)
            newEmbed.add_field(
                name="Rule 1",
                value="Follow Discord TOS and Guidlines",
                inline=False,
            )
            newEmbed.add_field(
                name="Rule 2",
                value="Respect Everyone, especially staff",
                inline=False,
            )
            newEmbed.add_field(
                name="Rule 3",
                value="Do what a staff tells you to do",
                inline=False,
            )
            newEmbed.add_field(
                name="Rule 4", value="Don't DM advertise", inline=False
            )
            newEmbed.add_field(
                name="Rule 5", value="Don't be annoying", inline=False
            )
            newEmbed.set_footer(text=f"Requested by: {ctx.author}")
            await ctx.send(embed=newEmbed)
            await ctx.message.delete()

    @commands.command(
        aliases=["purge", "clean"],
        help="Purge an amount of messages from the current channel",
        brief="5s",
    )
    @commands.cooldown(1, 5, BucketType.member)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    async def clear(self, ctx: Context, amount: int = None):
        """Purge an amount of messages from the current channel"""
        amount = amount or 1
        with ctx.typing():
            await asyncio.sleep(1)
            if amount > 100:
                return await ctx.send("Cannot delete more than 100 messages!")
            elif amount < 1:
                with ctx.typing():
                    return await ctx.send(
                        "Please provide a number higher than 1 to purge"
                    )
            else:
                await ctx.channel.purge(limit=amount + 1)
                await ctx.send(f"{amount} messages purged", delete_after=5)

    @commands.command(
        aliases=["sm", "setdelay", "delay", "slow"],
        help="Sets slowmode to the current channel",
        brief="3s",
    )
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, BucketType.member)
    @commands.guild_only()
    async def slowmode(self, ctx: Context, secs: int = None):
        """Sets slowmode to the current channel"""
        secs = secs or 0
        with ctx.typing():
            await asyncio.sleep(1)
            if secs == 0:
                await ctx.channel.edit(slowmode_delay=0)
                return await ctx.reply(
                    f"Slowmode for {ctx.channel.mention} has been reset!"
                )
            else:
                await ctx.channel.edit(slowmode_delay=secs)
                return await ctx.reply(
                    f"Slow mode for {ctx.channel.mention} set to {secs}"
                )

    def get_aks(self, ctx: Context, member: diskord.Member):
        """get the server acknowledgements for a member with a given context"""
        aks = "Server Member"
        if member.bot:
            aks = "Server Bot"
        if member == ctx.guild.me:
            aks = "The one and only me"
        if member.guild_permissions.manage_messages:
            aks = "Server Moderator"
        if (
            member.guild_permissions.administrator
            and member.id != ctx.guild.owner_id
        ):
            aks = "Server Admin"
        if member.id == ctx.guild.owner_id:
            aks = "Server Owner"
        return aks

    @commands.command(
        aliases=["user", "userinfo", "about", "who"],
        help="Receive information about a member",
        brief="15s",
    )
    @commands.guild_only()
    @commands.cooldown(1, 15, BucketType.member)
    @commands.guild_only()
    async def whois(self, ctx: Context, member: diskord.Member = None):
        """Receive information about a member"""
        member = member or ctx.author
        aks = self.get_aks(ctx, member)
        permissions: List[str] = [
            perm[0] for perm in member.guild_permissions if perm[1]
        ]  # iter(member.guild_permissions) returns (perm, bool) value where bool is True if they do have that permission.
        formatted = []
        for element in permissions:
            fmt = (
                element.lower()
                .replace("_", " ")
                .replace("guild", "server")
                .title()
            )
            formatted.append(f"`{fmt}`")
        created = member.created_at.strftime("%c")
        joined = member.joined_at.strftime("%c")
        roles = [role.mention for role in member.roles[1:]][
            ::-1
        ]  # slice from the first (@@everyone) role and reverse it
        # member_perms = ", ".join(perm for perm in perm_list)
        with ctx.typing():
            await asyncio.sleep(1)
            em = diskord.Embed()
            em.set_author(
                name=f"{member}",
                url=f"https://discord.com/users/{member.id}",
                icon_url=member.avatar.url,
            )
            em.set_thumbnail(url=member.avatar.url)
            em.add_field(name="Joined at:", value=joined, inline=True)
            em.add_field(name="Created at:", value=created, inline=True)
            em.add_field(name="ID:", value=member.id, inline=True)
            em.add_field(
                name=f"Roles [{len(member.roles) - 1}]",
                value="|".join(roles) if len(roles) > 0 else "N/A",
                inline=False,
            )
            em.add_field(
                name="Top Role:",
                value=f"{member.top_role.mention}",
                inline=False,
            )
            em.add_field(
                name="Permissions:", value=", ".join(formatted), inline=False
            )
            em.add_field(
                name="Server Acknowledgements", value=aks, inline=False
            )
            em.add_field(
                name="Status",
                value=f"```{member.activity.name if member.activity else 'N/A'}```",
                inline=False,
            )
            em.add_field(
                name="Nickname",
                value=f"```{member.nick if member.nick else 'N/A'}```",
            )
            return await ctx.send(embed=em)


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))
