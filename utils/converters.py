from discord.ext import commands
from utils.helpers import Context
import discord

# i dont use any of this classes lmao


class CustomMemberConverter(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        guild: discord.Guild = ctx.guild
        if not guild:
            raise commands.NoPrivateMessage(
                f"{ctx.command.qualified_name} cannot be used in DMs"
            )
        try:
            int(argument)
        except ValueError:
            if guild:
                for member in guild.members:
                    mem: discord.Member = member
                    if argument.lower() in str(mem.display_name).lower():
                        return mem
                    break
                return await ctx.to_error(
                    "Member {!r} was not found".format(argument)
                )
        _id = int(argument)
        if guild:
            for member in guild.members:
                if _id == member.id:
                    return member
                break
            return await ctx.to_error(
                "Member with id {!r} was not found".format(argument)
            )


class CustomUserConverter(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        bot: commands.Bot = ctx.bot
        try:
            int(argument)
        except ValueError:
            for user in bot.users:
                usr: discord.User = user
                if str(usr.name).lower() == argument.lower():
                    return user
                break
            return await ctx.to_error(
                "User with id {!r} was not found".format(argument)
            )
        _id = int(argument)
        for user in bot.users:
            usr: discord.User = user
            if usr.id == _id:
                return user
            break
        return await ctx.to_error(
            "User with id {!r} was not found".format(argument)
        )


class CustomRoleConverter(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        guild: discord.Guild = ctx.guild()
        if not guild:
            return await ctx.to_error(
                f"{ctx.command.qualified_name} cannot be used in DMs"
            )
        try:
            int(argument)
        except ValueError:
            for r in guild.roles:
                role: discord.Role = r
                if str(role.name).lower() == argument.lower():
                    return role
                break
            return await ctx.to_error(
                "Role with the name of {} was not found".format(argument)
            )
        _id = int(argument)
        for r in guild.roles:
            role: discord.Role = r
            if _id == role.id:
                return role
            break
        return await ctx.to_error(
            "Role with the id '{}' was not found".format(argument)
        )
