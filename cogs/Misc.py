import asyncio
import contextlib
import random

import diskord
import wikipedia as wiki
from BaseFile import *
from Bot import MyBot
from diskord.ext import commands
from diskord.ext.commands import BucketType
from diskord.utils import *
from googletrans import Translator
from googletrans.models import Translated
from utils import *
import warnings

# os.chdir("../launcher.py")


def version():
    with open(
        r"E:\Marcus\Coding\Python\DiscordBot\Hutch_Bot\VERSION.txt", "r+"
    ) as f:
        lines = f.read()
    return lines or "Not Found"


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

inv_url = oauth_url(
    client_id=799973356685361154,
    permissions=diskord.Permissions(
        administrator=True,
        embed_links=True,
        send_messages=True,
        manage_messages=True,
        read_message_history=True,
    ),
)


class Misc(commands.Cog):
    """Hutch Bot Miscellaneous Category"""

    def __init__(self, bot: MyBot):
        self.bot = bot
        # bot.add_command(self.embed)
        self.__cog_description__ = "Hutch Bot Miscellaneous Category"
        self.session = bot.session
        self.invite_cache = Cache()
        self.targets = {
            "discord": "https://discordpy.readthedocs.io/en/latest",
            "jishaku": "https://jishaku.readthedocs.io/en/latest/",
            "diskord": "https://diskord.readthedocs.io/en/latest",
            "master": "https://diskord.readthedocs.io/en/master",
            "python": "https://docs.python.org/3",
        }
        self.aliases = {
            ("discord", "discord.py", "discordpy", "dpy"): "discord",
            ("py", "py3", "python3", "python"): "python",
            ("master", "diskord-master"): "master",
            ("diskord", "dis", "kord"): "diskord",
            ("jsk", "jishaku"): "jishaku",
        }
        self.cache = Cache()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cog {self.__class__.__name__} Loaded")
        print("*" * 50)

    @commands.command(
        aliases=["latency"], help="Sends the latency of the bot", brief="5s"
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def ping(self, ctx: Context):
        """Sends the latency of the bot"""
        await ctx.trigger_typing()
        pingEmbed = diskord.Embed(
            title=":ping_pong: Pong!",
            description=f" My ping is **{round(self.bot.latency * 1000):.2f}**ms",
        )
        await ctx.reply(embed=pingEmbed)

    @commands.command(
        aliases=["credit", "credits"],
        help="Gives credit to those who made the bot AKA me",
        brief="5s",
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def dev(self, ctx: Context):
        """Gives credit to those who made the bot AKA me"""
        await ctx.trigger_typing()
        em = diskord.Embed(
            title="Credits",
            description=f"My Name is Hutch Bot, Developed by {self.bot.config.ME} in 10 days! \nI'm a multi-purpose bot with moderation commands, fun commands and some automod systems like profanity filter too!",
            color=random.choice(colors),
        )
        em.add_field(
            name="Join the support server",
            value="[Link Here](https://discord.gg/5nzgEWSnEG)",
        )
        em.set_thumbnail(url=ctx.guild.icon.url)
        em.set_author(
            name=self.bot.config.ME, url="https://discord.gg/ZhMPxJ6gM2"
        )
        em.set_footer(
            text=f"Send {self.bot.config.ME} Nitro for spending time on making this"
        )
        await ctx.reply(embed=em)

    @commands.command(
        aliases=["inv", "invite", "botinvite"],
        help="Sends the invite link to add me to other servers",
        brief="5s",
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def botinv(self, ctx: Context):
        """Sends the invite link to add me to other servers"""
        url = oauth(ctx)
        await ctx.trigger_typing()
        em = diskord.Embed()
        em.set_author(
            name=self.bot.config.ME,
            icon_url="https://www.youtube.com/channel/UC3e6sBmEMCpsbr6V2QJTgpQ",
            url="https://discord.gg/ZhMPxJ6gM2",
        )
        em.set_thumbnail(url=ctx.guild.icon.url)
        em.add_field(
            name="Add me to your server",
            value=f"[Click This Link]({url})",
            inline=False,
        )
        em.add_field(
            name="Join my server",
            value="[Discord Server Link](https://discord.gg/5nzgEWSnEG)",
            inline=False,
        )
        em.set_footer(
            text=f"Send {self.bot.config.ME} Nitro for spending time on making this"
        )
        await ctx.reply(embed=em)

    @commands.command(
        aliases=["brief", "description", "bot"],
        help="Sends a short description about the bot",
        brief="15s",
    )
    @commands.cooldown(1, 15, BucketType.member)
    async def desc(self, ctx: Context):
        """Sends a short description about the bot"""
        await ctx.trigger_typing()
        em = diskord.Embed(title="Hutch Bot", color=random.choice(colors))
        em.add_field(
            name="Description:",
            value=f"I am a fun bot with a lot of cool commands. I have a built-in profanity filter! I do have some moderation commands like ban unban!\nType `h!help` from more info!",
        )
        em.set_author(name=self.bot.config.ME, icon_url=ctx.author.avatar.url)
        em.set_footer(
            text=f"Send {self.bot.config.ME} Nitro for spending time on making this"
        )
        em.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.reply(embed=em)

    @commands.command(
        aliases=["wiki"],
        help="Searches something in wikipedia and sends the result as an embed",
        brief="5s",
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def wikipedia(self, ctx: Context, *, query: str):
        """Searches something in wikipedia and sends the result as an embed"""
        await ctx.trigger_typing()
        some_list = [3, 4, 5]
        em = diskord.Embed(title=str(query))
        em.set_footer(text="Powered by wikipedia.org")
        try:
            result = wiki.summary(
                query, sentences=random.choice(some_list), chars=2048
            )
            em.color = diskord.Color.green()
            em.description = result
            await ctx.reply(embed=em)
            if len(result) > 2048:
                em.color = diskord.Color.red()
                em.description = f"Result is too long. View the website [here](https://wikipedia.org/wiki/{query.replace(' ', '_')}), or just [Google it](https://google.com)."
                return await ctx.reply(embed=em)
        except wiki.DisambiguationError as e:
            em.title = "Error: Too many pages found"
            options = list(e.options[:10])
            joined = "\n".join(options)
            em.description = f"Is it one of these?\n{joined}"
        except wiki.PageError:
            em.color = diskord.Color.red()
            em.description = "Error: Page not found."
            return await ctx.reply(embed=em)

    async def get_invite(self, guild: diskord.Guild) -> diskord.Invite:
        if self.invite_cache.contains(guild.id):
            return self.invite_cache[guild.id]
        first_channel = guild.text_channels[0]
        invite = await first_channel.create_invite(
            max_uses=1,
            unique=False,
            reason="Requested by bot developer",
        )
        await asyncio.sleep(3)
        # sleeping for 4 sec to not get rate limitted
        return self.invite_cache.insert(guild.id, invite).get(guild.id)

    @commands.command(
        aliases=["servers", "guilds", "joins"],
        help="Sends the name and member count of all the servers the bot is in, soon to be removed...",
        brief="5s",
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def server(self, ctx: Context):
        """Sends the name and member count of all the servers the bot is in, soon to be removed..."""
        await ctx.trigger_typing()
        em = diskord.Embed(title="Servers the bot is in:")
        for guild in self.bot.guilds:
            if self.bot.owner_id == ctx.author.id:
                try:
                    inv = await self.get_invite(guild)
                    em.add_field(
                        name=guild.name,
                        value=f"Member Count: {guild.member_count}\nInvite: [link]({inv})",
                        inline=True,
                    )
                except Exception:
                    em.add_field(
                        name=guild.name,
                        value=guild.member_count,
                        inline=True,
                    )
            else:
                em.add_field(
                    name=guild.name,
                    value=f"Member Count: {guild.member_count}",
                    inline=True,
                )
        return await ctx.reply(embed=em)

    @commands.command(
        help="Mention a member to hug them | Sends a random hugging gif",
        brief="10s",
    )
    @commands.cooldown(1, 10, BucketType.member)
    async def hug(self, ctx: Context, member: diskord.Member = None):
        """Mention a member to hug them | Sends a random hugging gif"""
        await ctx.trigger_typing()
        async with self.session as cs:
            try:
                async with cs.get("https://some-random-api.ml/animu/hug") as r:
                    data = await r.json()
                    if member is None:
                        em = diskord.Embed(
                            title="Hug", color=random.choice(colors)
                        )
                    else:
                        em = diskord.Embed(
                            title=f"{ctx.author.display_name} hugs {member.display_name}",
                            color=random.choice(colors),
                        )
                    em.set_image(url=data["link"])
                    await ctx.send(embed=em)
            except Exception as e:
                await ctx.send(e)

    @commands.command(
        help="Mention a member to pat them | Sends a random patting gif",
        brief="10s",
    )
    @commands.cooldown(1, 10, BucketType.member)
    async def pat(self, ctx: Context, member: diskord.Member = None):
        """Mention a member to pat them | Sends a random patting gif"""
        await ctx.trigger_typing()
        async with self.session as cs:
            try:
                async with cs.get("https://some-random-api.ml/animu/pat") as r:
                    data = await r.json()
                    if member is None:
                        em = diskord.Embed(
                            title="Pat", color=random.choice(colors)
                        )
                    else:
                        em = diskord.Embed(
                            title=f"{ctx.author.display_name} Pats {member.display_name}",
                            color=random.choice(colors),
                        )
                    em = diskord.Embed(
                        title="Pat", color=random.choice(colors)
                    )
                    em.set_image(url=data["link"])
                    await ctx.send(embed=em)
            except Exception as e:
                await ctx.send(e)

    @commands.command(help="Sends a random winking gif", brief="10s")
    @commands.cooldown(1, 10, BucketType.member)
    async def wink(self, ctx: Context):
        """Sends a random winking gif"""
        await ctx.trigger_typing()
        async with self.session as cs:
            try:
                async with cs.get(
                    "https://some-random-api.ml/animu/wink"
                ) as r:
                    data = await r.json()
                    em = diskord.Embed(
                        title="Wink", color=random.choice(colors)
                    )
                    em.set_image(url=data["link"])
                    await ctx.send(embed=em)
            except Exception as e:
                await ctx.send(e)

    @commands.command(
        aliases=["Trans"],
        help="Translate a given text english.",
        brief="5s",
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def translate(self, ctx: Context, *, text: str):
        """Translate a given text english."""
        lang = "en"
        await ctx.trigger_typing()
        try:
            translator = Translator()
            result: Translated = translator.translate(text, lang)
            em = diskord.Embed(
                title="Translation", color=random.choice(colors)
            )
            em.set_thumbnail(url=ctx.guild.icon.url)
            em.set_footer(text=f"Translation requested by {ctx.author}")
            em.add_field(name="Text:", value=text, inline=False)
            em.add_field(name="Source:", value=result.src)
            em.add_field(name="Translation:", value=result.text, inline=False)
            em.add_field(name="Pronunciation:", value=result.pronunciation)
            return await ctx.reply(embed=em)
        except Exception as e:
            return await ctx.reply(e)

    @commands.command(aliases=["em"], brief="10s")
    @commands.cooldown(1, 10, BucketType.user)
    async def embed(self, ctx: Context, *, options: EmbedFlags):
        """
        Make youself a custom embed by providing flags using `flag: value` syntax\n
        Example: `h!embed title: Title Text desc: Description Text`
        """
        em = get_data_from_options(ctx, **options.__dict__)
        await ctx.send(
            # content="Please note that there might be some bugs so please make sure to report them",
            embed=em,
        )

    async def get_message_from_reference(
        self, ctx: Context, from_cache: bool = False
    ) -> diskord.Message:
        if ctx.reference.cached_message and from_cache:
            return ctx.reference.cached_message
        _id: int = ctx.reference.message_id
        return await ctx.fetch_message(_id)

    @commands.command(aliases=["re"], brief="0s")
    async def redo(self, ctx: Context):
        """
        Redo a command by replying to the edited/corrected message.
        You can only redo a message sent by you
        """
        if not ctx.reference:
            return await ctx.to_error(
                "Reply to a message sent by you to redo it."
            )
        try:
            message = await self.get_message_from_reference(ctx)
        except diskord.NotFound:
            return await ctx.to_error("Replied message not found.")
        except diskord.HTTPException:
            return await ctx.send(
                embed=ctx.em("Retrieving the message failed.")
            )
        # all possible exceptions handled, message is defined
        if message.author != ctx.author:
            return await ctx.to_error("You did not send that message?")
        return await self.bot.process_commands(message)

    @commands.command(aliases=["del"], brief="10s")
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def delete(self, ctx: Context):
        """
        Delete a message sent by the bot. useful when the bot unexpectedly sends a wall text or any unwanted message
        """
        if not ctx.reference:
            return await ctx.to_error(
                "Reply to the message you want to delete"
            )
        try:
            message: diskord.Message = self.get_message_from_reference(
                ctx.reference.messsage_id, from_cache=True
            )
        except (diskord.HTTPException, diskord.Forbidden):
            return await ctx.to_error("Retreiving the message failed")
        except diskord.NotFound:
            return await ctx.to_error("Message not found")
        if message.author.id == self.bot.user.id:
            try:
                with contextlib.suppress(diskord.HTTPException):
                    await message.delete()
            except diskord.NotFound:
                return await ctx.to_error("Message already deleted")
        return await ctx.to_error(
            "Can only delete messages sent by the bot through this command"
        )

    # following stuff are copied and modified from
    # https://github.com/MarzaElise/Robocord/blob/main/cogs/rtfm.py
    # they were written by me tho

    async def build(self, target) -> None:
        url = self.targets[target]
        req = await self.session.get(url + "/objects.inv")
        if req.status != 200:
            warnings.warn(
                Warning(
                    f"Received response with status code {req.status} when trying to build RTFM cache for {target} through {url}/objects.inv"
                )
            )
            raise commands.CommandError("Failed to build RTFM cache")
        self.cache[target] = rtfm.SphinxObjectFileReader(
            await req.read()
        ).parse_object_inv(url)

    @commands.command(aliases=["rtfd", "docs"], brief="0s")
    async def rtfm(self, ctx: Context, docs: str, *, term=None):
        """
        Returns the top 10 best matches of documentation links for searching the given term in the given docs
        Returns the entire documentation link if no term given
        """
        docs = docs.lower()
        target: str = None
        for aliases, target_name in self.aliases.items():
            if docs in aliases:
                target: str = target_name

        if not target:
            new = []
            for index, value in enumerate(list(self.targets.keys()), 1):
                lis = [key for key, val in self.aliases.items() if val == value][0]
                temp = " ".join([f"*`{k}`*" for k in lis])
                new.append(f"**{index}. {value}** - {temp}")
            lis = "\n".join(new)

            return await ctx.to_error(
                f"Documentation `{docs}` is invalid. Must be one of \n{lis}"
            )

        if not term:
            return await ctx.reply(self.targets[target])

        cache = self.cache.get(target)
        if not cache:
            await ctx.trigger_typing()
            await self.build(target)
            cache = self.cache.get(target)

        results = rtfm.finder(
            term, list(cache.items()), key=lambda x: x[0], lazy=False
        )[:10]

        if not results:
            return await ctx.reply(
                f"No results found when searching for **{term}** in **{target}**"
            )

        await ctx.reply(
            embed=diskord.Embed(
                title=f"Best matches for {term} in {target}",
                description="\n".join(f"[`{key}`]({url})" for key, url in results),
                color=diskord.Color.dark_theme(),
            )
        )


def setup(bot: commands.Bot):
    bot.add_cog(Misc(bot))
