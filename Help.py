import os
import random
import re
import traceback
from typing import *
from typing import List, Optional, Union

import discord
from discord import *
from discord.ext import *
from paginator import Paginator
from discord.utils import oauth_url
from dpymenus import BaseMenu, Page, PaginatedMenu

from Helpers import *

# os.chdir("./launcher.py")


class NoHelpCommand(commands.CommandError):
    pass


colors = [
    0xF3FF00,  # Yellow
    0x00FFFF,  # Lighter Cyan
    0x0036FF,  # Normal Blue
    0xF000FF,  # Pink
    0xFF0000,  # Red
    0x17FF00,  # Light Green
    0x00FF93,  # Cyan
    0x00B2FF,  # Light Blue
    0x0013FF,  # Dark Blue
    0x65FF00,  # Green
]


class CustomHelp(commands.MinimalHelpCommand):
    def __init__(self, bot, **options):
        self.show_hidden = True
        self.verify_checks = False
        self.bot = bot
        # self.cog = bot.get_cog("Misc")
        super().__init__(**options)

    def get_docs_for(self, entity=None):
        ctx: Context = self.context
        docs = ctx.bot.get_docs(entity, error=False)
        if entity == False or docs == False:
            return "https://hutch-bot.readthedocs.io"
        return docs

    def get_opening_note(self):
        return super().get_opening_note()

    def get_opening_page(self, entity=None):
        nav = (
            "⏪ - *Go to the first page*\n"
            "\n◀️ - *Go to the previous page*\n"
            "\n▶️ - *Go to the next page*\n"
            "\n⏩ - *Go to the last page*\n"
            "\n:stop_button: - *Delete the message*\n"
        )
        em = discord.Embed(
            title="Welcome To The Hutch Bot Help Command",
            description=self.get_opening_note() + "\n",
            timestamp=self.context.message.created_at,
            color=random.choice(colors),
        )
        em.set_footer(
            text=self.get_ending_note(),
            icon_url=self.context.author.avatar_url,
        )
        em.set_author(
            name=self.context.author, icon_url=self.context.author.avatar_url
        )
        em.set_thumbnail(url=self.context.guild.icon_url)
        em.add_field(name="Navigation", value=f"{nav}\n\n", inline=False)
        em.add_field(
            name="Bugs:",
            value=f"If you find any bugs, please report it in the bot's DMs using the `{self.clean_prefix}report` command\n\n",
        )
        # em.add_field(
        #     name="Documentation",
        #     value=f"Please view the [official documentation]({self.get_docs_for(entity)}) for more info",
        # )
        self.add_link(em, entity)
        return em

    def get_second_page(self, entity=None):
        ctx: Context = self.context
        em = discord.Embed(color=random.choice(colors))
        em.title = "Command Signatures"
        em.description = "You can understand command signature using this"
        em.add_field(
            name="<argument>",
            value="If an argument is surrounded with `<>` it represents a **required** argument",
            inline=False,
        )
        em.add_field(
            name="[argument]",
            value="An argument surrounded with `[]` represents an **optional** argument",
            inline=False,
        )
        em.add_field(
            name="[argument...]",
            value="An argument ending with `...` means you can have multiple arguments",
            inline=False,
        )
        em.add_field(
            name="[argument]...",
            value="If an argument ends with `...` its means you can pass in multiple arguments of the same type. For example, multiple members",
            inline=False,
        )

        em.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        em.set_thumbnail(url=ctx.guild.icon_url)
        em.set_footer(
            text=self.get_ending_note(), icon_url=ctx.author.avatar_url
        )
        self.add_link(em, entity)
        return em

    def add_link(self, embed: discord.Embed, entity):
        ctx: Context = self.context
        docs = self.get_docs_for(entity)
        url = oauth_url(
            ctx.me.id,
            permissions=discord.Permissions.all(),
            guild=ctx.guild,
        )
        links = [
            f"[Bot Invite]({url})",
            "[Support Server](https://discord.gg/NVHJcGdWBC)",
            f"[Official Documentation]({docs})",
        ]
        embed.add_field(
            name="Useful Links", value=" | ".join(links), inline=False
        )
        return embed

    def get_destination(self):
        ctx: Context = self.context
        author: Union[discord.User, discord.Member] = ctx.author
        channel: discord.TextChannel = ctx.channel
        return channel

    def get_aliases(self, command: commands.Command):
        if command.full_parent_name == "":
            return [f"`{a}`" for a in command.aliases]
        return [
            f"`{command.full_parent_name} {alias}`"
            for alias in command.aliases
        ]

    def get_ending_note(self):
        string = "Use {0.clean_prefix}{0.invoked_with} [command] for more info on a command"
        return string.format(self)

    def get_command_signature(
        self, command: Union[commands.Command, commands.Group]
    ):  # h!ban <member> [reason]
        if command.qualified_name == "embed":
            return f"{self.context.prefix}help embed"
        signature = command.signature.replace("_", " ")
        return "{}{} {}".format(
            self.clean_prefix, command.qualified_name, signature
        )

    async def send_bot_help(self, mapping):  # h!help
        channel: discord.TextChannel = self.context.channel
        ctx: Context = self.context
        if not (channel.permissions_for(ctx.guild.me).send_messages):
            return
        if not (channel.permissions_for(ctx.guild.me).embed_links) and (
            channel.permissions_for(ctx.guild.me).add_reactions
        ):
            return await ctx.send(
                "I am missing one or more of these permissions\n-Embed Links\n-Add reactions\n"
                "Please make sure I have all of these permissions enabled to work properly"
            )
        try:
            _embeds = []
            _embeds.append(self.get_opening_page())
            _embeds.append(self.get_second_page())
            for cog, cmds in mapping.items():
                em = discord.Embed(color=random.choice(colors))
                em.title = getattr(cog, "qualified_name", "No Category")
                em.description = cog.description if cog else "\n"
                em.set_thumbnail(url=ctx.guild.icon_url)
                em.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                em.set_footer(
                    text="<> - Required | [] - Optional",
                    icon_url=ctx.author.avatar_url,
                )
                if cog:
                    filtered = cog.get_commands()
                    for command in filtered:
                        signature = self.get_command_signature(command)
                        # if command.qualified_name != "embed":
                        em.add_field(
                            name=str(command.qualified_name).title(),
                            value=f"`{signature}`",
                            inline=True,
                        )
                        # else:
                        #     em.add_field(
                        #         name=command.qualified_name.title(),
                        #         value=f"`{ctx.prefix}help embed`",
                        #     )
                if len(em.fields) >= 5:
                    _embeds.append(em)
            Pag = Paginator(self.context, embeds=_embeds)
            await Pag.start()
        except Exception as e:
            tb = traceback.format_exception(type(e), e, e.__traceback__)
            trace = tb[-1]
            string = f"```py\n{trace}\n```"
            embed = ctx.em(desc=string)
            await self.get_destination().send(embed=embed)

    async def send_command_help(
        self, command: commands.Command
    ):  # h!help ping
        ctx: Context = self.context
        channel: TextChannel = ctx.channel
        if not (channel.permissions_for(ctx.guild.me).send_messages):
            return
        if not (channel.permissions_for(ctx.guild.me).embed_links) and (
            channel.permissions_for(ctx.guild.me).add_reactions
        ):
            return await ctx.send(
                "I am missing one or more of these permissions\n-Embed Links\n-Add reactions\n"
                "Please make sure I have all of these permissions enabled to work properly"
            )
        _embeds = []
        _embeds.append(self.get_opening_page(command))
        em = discord.Embed(color=random.choice(colors))
        em.title = command.qualified_name.title()
        em.description = command.help
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        em.set_thumbnail(url=self.context.guild.icon_url)
        em.set_footer(
            text="<> - Required | [] - Optional",
            icon_url=ctx.author.avatar_url,
        )
        em.add_field(
            name="Usage:",
            value=f"`{self.get_command_signature(command)}`",
            inline=False,
        )

        if command.aliases:
            alias = self.get_aliases(command)
            em.add_field(
                name="Aliases",
                value=f'`{command.qualified_name}`, {", ".join(alias)}',
                inline=False,
            )

        em.add_field(name="Cooldown", value=command.brief, inline=False)
        em.add_field(
            name="Documentation",
            value=f"Please view the [official documentation]({self.get_docs_for(command)}) for more info",
        )
        em.set_footer(
            text=self.get_ending_note(),
            icon_url=self.context.author.avatar_url,
        )
        _embeds.append(em)
        Pag = Paginator(self.context, embeds=_embeds)
        await Pag.start()

    def chunk(self, data: List, chunk_by: int):
        return [data[i : i + chunk_by] for i in range(0, len(data), chunk_by)]

    async def send_cog_help(self, cog: commands.Cog):  # h!help misc
        channel: discord.TextChannel = self.context.channel
        ctx: Context = self.context
        if not (channel.permissions_for(ctx.guild.me).send_messages):
            return
        if not (channel.permissions_for(ctx.guild.me).embed_links) and (
            channel.permissions_for(ctx.guild.me).add_reactions
        ):
            return await ctx.send(
                "I am missing one or more of these permissions\n-Embed Links\n-Add reactions\n"
                "Please make sure I have all of these permissions enabled to work properly"
            )
        _embeds = []
        _embeds.append(self.get_opening_page(cog))
        data = cog.get_commands()
        paginated = self.chunk(data, 5)
        for index, chunk in enumerate(paginated):
            em = discord.Embed(color=random.choice(colors))
            em.title = f"{cog.qualified_name} Commands"
            em.description = cog.description
            em.set_thumbnail(url=self.context.guild.icon_url)
            em.set_author(name=self.context.author)
            em.set_footer(
                text=self.get_ending_note(),
                icon_url=self.context.author.avatar_url,
            )
            for command in chunk:
                qual_name = str(command.qualified_name).title()
                if isinstance(command, commands.Group):
                    qual_name = (
                        str(command.qualified_name).title()
                        + " | Has Subcommands"
                    )
                em.add_field(
                    name=qual_name,
                    value=command.help if command.help else "No Help Found",
                    inline=False,
                )
            _embeds.append(em)
        Pag = Paginator(self.context, embeds=_embeds)
        if len(_embeds) > 1:
            await Pag.start()
        else:
            await ctx.send(embed=_embeds[1])

    async def send_group_help(self, group: commands.Group):  # h!help warn del
        channel: discord.TextChannel = self.context.channel
        ctx: Context = self.context
        if not (channel.permissions_for(ctx.guild.me).send_messages):
            return
        if not (channel.permissions_for(ctx.guild.me).embed_links) and (
            channel.permissions_for(ctx.guild.me).add_reactions
        ):
            return await ctx.send(
                "I am missing one or more of these permissions\n-Embed Links\n-Add reactions\n"
                "Please make sure I have all of these permissions enabled to work properly"
            )
        command = str(group.qualified_name).title() + "'s Subcommands"
        data = list(group.commands)
        paginated = self.chunk(data, 5)
        _embeds = []
        _embeds.append(self.get_opening_page(group))
        for index, chunk in enumerate(paginated):
            em = discord.Embed(
                title=command,
                description=group.help,
                color=random.choice(colors),
            )
            em.set_thumbnail(url=ctx.guild.icon_url)
            em.set_footer(
                text=self.get_ending_note(), icon_url=ctx.author.avatar_url
            )
            em.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            for cmd in chunk:
                em.add_field(
                    name=str(cmd.qualified_name).title(),
                    value=cmd.help,
                    inline=False,
                )
            _embeds.append(em)

        if len(_embeds) > 1:
            Pag = Paginator(self.context, embeds=_embeds)
            await Pag.start()
        else:
            await self.get_destination().send(embed=_embeds[1])

    async def send_error_message(self, error):
        ctx: Context = self.context
        await ctx.to_error(error)

    async def on_help_command_error(
        self, ctx: Context, error: commands.CommandError
    ):
        if isinstance(error, commands.CommandNotFound):
            return await ctx.to_error("No Command with that name was found")
        if isinstance(error, commands.CommandOnCooldown):
            desc = f"That Command is on cooldown. Try again after **{error.retry_after:.2f}** secs"
            return await ctx.to_error(desc)
        if isinstance(error, commands.DisabledCommand):
            desc = "This Command is disabled throughout the bot, please wait patiently until it is enabled again"
            return await ctx.to_error(desc)
        if not isinstance(error, commands.CommandInvokeError):
            ctx.command.reset_cooldown(ctx)
            title = " ".join(
                re.compile(r"[A-Z][a-z]*").findall(error.__class__.__name__)
            )
            em = discord.Embed(
                title=title, description=str(error), color=discord.Color.red()
            )
            em.set_footer(
                text="If this was a mistake please contact Marcus | Bot Dev#4438",
                icon_url=ctx.author.avatar_url,
            )
            return await ctx.send(embed=em)
