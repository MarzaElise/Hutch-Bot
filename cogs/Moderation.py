import asyncio
import random
from typing import *
from BaseFile import *
import typing
import aiosqlite
import discord
from better_profanity import *
from discord.ext import *
from discord.utils import *
from Helpers import *
from discord.ext.commands import BucketType
from Bot import MyBot
import os
from data import Database
import traceback
import datetime
from discord.ext.commands.errors import BotMissingPermissions

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

    def profanity_filter(self, message: discord.Message):
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
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.profanity_filter(message):
            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention} watch your language!", delete_after=5
                )
            except:
                pass

        if message.mentions and len(message.mentions) > 5:
            if message.guild and message.guild.id not in [
                681882711945641997,
                841721684876328961,
            ]:
                try:
                    await message.author.send(
                        f"You were kicked from the server for mentioning too many people!"
                    )
                    await message.author.kick(reason="Automoderator: Mass Mentioning")
                    await message.channel.send(
                        f"{message.author.mention} was kicked for mass mentioning"
                    )
                except:
                    pass

    @commands.command(help="Kick someone from the server", brief="0s")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx: Context, user: discord.Member, *, reason=None):
        """kick someone from the server"""
        reason = reason or "No Reason Provided"
        if user == ctx.guild.me:
            return await ctx.send("No, I won't kick myself")
        if user == ctx.author:
            return await ctx.send("You dumb?")
        if user.top_role >= ctx.author.top_role:
            with ctx.typing():
                await asyncio.sleep(1)
                return await ctx.send(
                    f"{ctx.author.mention} you cannot kick {user.display_name}"
                )
        if user.top_role >= ctx.guild.me.top_role:
            with ctx.typing():
                await asyncio.sleep(1)
                return await ctx.send(f"I cannot kick members who are ranked above me")
        if user.bot:
            await user.kick(reason=f"{ctx.author}: {reason}")
            return await ctx.send(f"Succesfully kicked **{user.mention}**")
        else:
            with ctx.typing():
                await asyncio.sleep(1)
                try:
                    em = discord.Embed(
                        title="\n", description="\n", color=random.choice(colors)
                    )
                    em.set_author(
                        name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                    )
                    em.set_thumbnail(url=ctx.guild.icon_url)
                    em.add_field(
                        name="Kicked",
                        value=f"You were Kicked from **{ctx.guild}**",
                        inline=False,
                    )
                    em.add_field(name="By:", value=f"-*{ctx.author}*", inline=False)
                    em.add_field(name="Reason:", value=f"-*{reason}*", inline=False)
                    await user.send(embed=em)
                    await user.kick(reason=f"{ctx.author}: {reason}")
                    await ctx.send(f"Succesfully kicked **{user.mention}**")
                except discord.Forbidden:
                    await user.kick(reason=f"{ctx.author}: {reason}")

    @commands.command(help="Ban someone from the server", brief="0s")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(
        self,
        ctx: Context,
        user: typing.Union[discord.Member, discord.User],
        *,
        reason=None,
    ):
        """Ban someone from the server"""
        reason = reason or "No Reason Provided"
        guild: discord.Guild = ctx.guild
        with ctx.typing():
            await asyncio.sleep(1)

            if user == ctx.guild.me:
                return await ctx.send("No, I won't ban myself")

            if user == ctx.author:
                return await ctx.send("You dumb?")

            if isinstance(user, discord.User):
                await guild.ban(user, reason=f"{ctx.author}: {reason}")
                return await ctx.send(f"Succesfully banned **{user.mention}**")

            if isinstance(user, discord.Member):

                if user.top_role >= ctx.author.top_role:
                    return await ctx.send(
                        f"{ctx.author.mention} you cannot ban {user.display_name}"
                    )
                if user.top_role >= ctx.guild.me.top_role:
                    return await ctx.send(
                        f"I cannot ban members who are ranked above me"
                    )
                if user.bot:
                    await user.ban(reason=f"{ctx.author}: {reason}")
                    return await ctx.send(f"Succesfully banned **{user.mention}**")
                else:
                    await ctx.send(f"Succesfully banned **{user.mention}**")
                    try:
                        em = discord.Embed(
                            title="\n", description="\n", color=random.choice(colors)
                        )
                        em.set_author(
                            name=ctx.author.display_name, icon_url=ctx.author.avatar_url
                        )
                        em.set_thumbnail(url=ctx.guild.icon_url)
                        em.add_field(
                            name="Banned",
                            value=f"You were Banned from **{ctx.guild}**",
                            inline=False,
                        )
                        em.add_field(name="By:", value=f"-*{ctx.author}*", inline=False)
                        em.add_field(name="Reason:", value=f"-*{reason}*", inline=False)
                        await user.send(embed=em)
                        await user.ban(reason=f"{ctx.author}: {reason}")
                    except discord.Forbidden:
                        await user.ban(reason=f"{ctx.author}: {reason}")

    @commands.command(help="Mass Ban Membes", brief="0s")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def massban(
        self,
        ctx: Context,
        members: commands.Greedy[discord.User],
        *,
        reason: str = None,
    ):
        members: List[discord.User] = members
        reason = reason or "No Reason Provided"
        reason = f"{ctx.author}: {reason}"
        guild: discord.Guild = ctx.guild
        em = discord.Embed(title="\n", description="\n", color=random.choice(colors))
        em.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        em.set_thumbnail(url=ctx.guild.icon_url)
        em.add_field(
            name="Banned", value=f"You were Banned from **{ctx.guild}**", inline=False
        )
        em.add_field(name="By:", value=f"-*{ctx.author}*", inline=False)
        em.add_field(name="Reason:", value=f"-*{reason}*", inline=False)

        for member in members:
            if member.id == ctx.author.id:
                return await ctx.to_error("You cannot ban yourself")
                break
            if member.id == ctx.bot.user.id:
                return await ctx.to_error("You cannot ban the bot itself")
                break
            is_member: Optional[discord.Member] = guild.get_member(member.id)
            if is_member:
                mem: discord.Member = is_member
                if mem.top_role >= ctx.author.top_role:
                    return await ctx.to_error(f"you cannot ban {mem.display_name}")
                    break
                if mem.top_role >= ctx.guild.me.top_role:
                    return await ctx.to_error(
                        f"I cannot ban members who are ranked above me"
                    )
                    break
                if mem.bot:
                    await guild.ban(mem, reason=reason, delete_message_days=7)
                try:
                    await mem.send(embed=em)
                except discord.Forbidden:
                    pass
                finally:
                    await guild.ban(mem, reason=reason, delete_message_days=7)
            elif is_member is None:
                usr: discord.User = member
                await guild.ban(usr, reason=reason, delete_message_days=7)
        await ctx.send(f"Succesfully banned {len(members)} members")

    @commands.command(help="Unban a previously banned member", brief="0s")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx: Context, member: discord.User, *, reason=None):
        """Unban a previously banned member"""
        reason = reason or "No Reason Provided"
        with ctx.typing():
            await asyncio.sleep(1)
            try:
                await ctx.guild.unban(discord.Object(id=member.id), reason=reason)
                await ctx.send(f"**{member}** was succesfully unbanned")
            except BotMissingPermissions:
                await ctx.send("I dont have unban permissions")

    @commands.command(
        aliases=["rule"], help="Sends a breif description of common rules", brief="10s"
    )
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 10, BucketType.member)
    @commands.guild_only()
    async def rules(self, ctx: Context):
        """Sends a breif description of common rules"""
        with ctx.typing():
            await asyncio.sleep(1)
            newEmbed = discord.Embed(title="Rules", color=random.choice(colors))
            newEmbed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar_url
            )
            newEmbed.set_thumbnail(url=ctx.guild.icon_url)
            newEmbed.add_field(
                name="Rule 1", value="Follow Discord TOS and Guidlines", inline=False
            )
            newEmbed.add_field(
                name="Rule 2", value="Respect Everyone, especially staff", inline=False
            )
            newEmbed.add_field(
                name="Rule 3", value="Do what a staff tells you to do", inline=False
            )
            newEmbed.add_field(name="Rule 4", value="Don't DM advertise", inline=False)
            newEmbed.add_field(name="Rule 5", value="Don't be annoying", inline=False)
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

    @commands.command(
        aliases=["user", "userinfo", "about", "who"],
        help="Receive information about a member",
        brief="15s",
    )
    @commands.guild_only()
    @commands.cooldown(1, 15, BucketType.member)
    @commands.guild_only()
    async def whois(self, ctx: Context, member: discord.Member = None):
        """Receive information about a member"""
        member = member or ctx.author
        aks = "Server Member"
        if member.bot:
            aks = "Server Bot"
        if member == ctx.guild.me:
            aks = "The one and only me"
        if member.guild_permissions.manage_messages:
            aks = "Server Moderator"
        if member.guild_permissions.administrator and member.id != ctx.guild.owner_id:
            aks = "Server Admin"
        if member.id == ctx.guild.owner_id:
            aks = "Server Owner"
        permissions_list = [perm for perm in member.guild_permissions]
        perms_and_values = []
        perm_list = []
        for perm, value in permissions_list:
            if value == True:
                perms_and_values.append(perm)
            else:
                continue
        for perm in perms_and_values:
            perm = perm.replace("_", " ").title()
            perm_list.append(f"`{perm}`")
        created = member.created_at.strftime("%c")
        joined = member.joined_at.strftime("%c")
        roles = [role for role in member.roles[1:]]
        roles = roles[::-1]
        member_perms = ", ".join(perm for perm in perm_list)
        with ctx.typing():
            await asyncio.sleep(1)
            em = discord.Embed()
            em.set_author(name=f"{member}", icon_url=member.avatar_url)
            em.set_thumbnail(url=member.avatar_url)
            em.add_field(name="Joined at:", value=joined, inline=True)
            em.add_field(name="Created at:", value=created, inline=True)
            em.add_field(name="ID:", value=member.id, inline=True)
            try:
                em.add_field(
                    name=f"Roles [{len(member.roles) - 1}]",
                    value="".join([role.mention for role in roles]),
                    inline=False,
                )
                em.add_field(
                    name="Top Role:", value=f"{member.top_role.mention}", inline=False
                )
            except:
                pass
            em.add_field(name="Permissions:", value=member_perms, inline=False)
            em.add_field(name="Server Acknowledgements", value=aks, inline=False)
            em.add_field(
                name="Status",
                value=f"```{member.activity.name if member.activity else 'N/A'}```",
                inline=False,
            )
            em.add_field(
                name="Nickname", value=f"```{member.nick if member.nick else 'N/A'}```"
            )
            return await ctx.send(embed=em)

    @commands.command(
        help="Warn a member for breaking a rule | Under Development", brief="0s"
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx: Context, member: discord.Member, *, reason: str = None):
        """Warn a member for breaking a rule | Under Development"""
        reason = reason or "No Reason Provided"
        # if member.id == self.bot.user.id:
        #     return await ctx.to_error("You cannot warn me")
        if member.id == ctx.author.id:
            return await ctx.to_error("You cannot warn yourself")
        # if member.bot:
        # return await ctx.to_error("You cannot warn a bot")
        em = discord.Embed(
            title=f"{member.display_name} has been warned", color=discord.Color.red()
        ).set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
        em.set_footer(
            text=f"Warned by: {ctx.author}", icon_url=ctx.author.avatar_url
        ).set_thumbnail(url=ctx.guild.icon_url)
        em.add_field(name="Reason", value=reason, inline=False)
        em.add_field(name="Staff", value=f"{ctx.author}", inline=False)
        try:
            db = Database("./databases/warns.sqlite")
            await db.create(
                str(ctx.guild.id),
                """
                "id"	    INTEGER     NOT NULL    UNIQUE,
                "user_id"   INTEGER     NOT NULL,
                "staff"     INTEGER     NOT NULL,
                "reason"    TEXT        NOT NULL,
                "time"      TEXT        NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT) 
                """,
            )
            await asyncio.sleep(3)
            await db.insert(
                str(ctx.guild.id),
                "user_id, staff, reason, time",
                4,
                (member.id, ctx.author.id, reason, f"{datetime.datetime.utcnow()} UTC"),
            )
            await ctx.send(embed=em)
        except Exception as e:
            await ctx.to_error(e)
            traceback.print_exception(type(e), e, e.__traceback__)

    @commands.command(
        help="Show information about a member's warn history | Under Development",
        brief="0s",
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def warns(self, ctx: Context, member: discord.Member):
        """Show information about a member's warn history | Under Development"""
        member = member or ctx.author
        em = discord.Embed(title=f"Displaying Warns for {member}")
        em.set_footer(
            text=f"Warn Commands are under development right now",
            icon_url=ctx.author.avatar_url,
        )
        db = Database("./databases/warns.sqlite")
        all_: Iterable[aiosqlite.Row] = await db.execute_fetch_all(
            f"SELECT id, staff, reason, time FROM {ctx.guild.id} WHERE user_id = ?",
            (member.id,),
        )
        if len(all_) == 0:
            return await ctx.send(
                "User doesn't have any warns or couldn't be displayed"
            )
        for _id, staff, reason, time in all_:
            em.add_field(
                name=f"{_id}: {staff} - {time}", value=f"Reason: {reason}", inline=False
            )
        await ctx.send(embed=em)


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))
