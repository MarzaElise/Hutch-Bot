import asyncio
import json
import random
import typing

import asyncpraw
import diskord
from BaseFile import *
from Bot import MyBot
from config import get_passwords
from diskord import *
from diskord.ext import commands
from diskord.ext.commands import *
from diskord.utils import *
from utils import *

# os.chdir("../launcher.py")


class CannotDmMember(commands.CommandError):
    pass


class AlreadyOptedOut(commands.CommandError):
    pass


class AlreadyOptedIn(commands.CommandError):
    pass


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

responses = [
    "As I see it, yes.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don’t count on it.",
    "It is certain.",
    "It is decidedly so.",
    "Most likely.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Outlook good.",
    "Reply hazy, try again.",
    "Signs point to yes.",
    "Very doubtful.",
    "Without a doubt.",
    "Yes.",
    "Yes – definitely.",
    "You may rely on it.",
]

secrets = get_passwords()

reddit = asyncpraw.Reddit(
    client_id=secrets.REDDIT_CLIENT_ID,
    client_secret=secrets.REDDIT_CLIENT_SECRET,
    username="Marcus-Is-A-Simp",
    password=secrets.REDDIT_PASS,
    user_agent="MemeCommandPogs",
    check_for_async=True,
)


def can_dm(mem: diskord.Member):  # TODO: move to db
    member = str(mem.id)
    with open("./assets/opt_out.json", "r") as f:
        alr_opted = dict(json.load(f))
    members = alr_opted.keys()
    if member in members:
        if alr_opted[member] == True:
            raise CannotDmMember(
                "Specified member has opted out of the DM command"
            )
        elif alr_opted[member] == False:
            return True
    elif member not in members:
        return True


class Fun(commands.Cog):
    """Hutch Bot Fun Category"""

    def __init__(self, bot: MyBot):
        self.bot = bot

        self.__cog_description__ = "Hutch Bot Fun Category"

    @commands.Cog.listener()
    async def on_ready(self):
        print("*" * 50)
        print(f"Cog {self.__class__.__name__} Loaded")
        print("*" * 50)

    def opt_out(self, member_id: str):  # TODO: move to db
        with open("./assets/opt_out.json", "r") as f:
            dic = json.load(f)
        if member_id in dic.keys():
            if dic[str(member_id)] == True:
                raise AlreadyOptedOut(
                    "You have already opted out of the DM command"
                )
        dic[str(member_id)] = True
        with open("./assets/opt_out.json", "w+") as f:
            json.dump(dic, f, indent=4)
        return True

    def opt_in(self, member_id: str):
        with open("./assets/opt_out.json", "r") as f:  # TODO: move to db
            alr_opted = json.load(f)
        if member_id not in alr_opted.keys():
            raise AlreadyOptedIn(
                f"You are currently opted into the DM command"
            )
        elif alr_opted[member_id] == False:
            raise AlreadyOptedIn("You are currently opted into the DM command")
        elif alr_opted[member_id] == True:
            alr_opted[member_id] = False
            with open("./assets/opt_out.json", "w+") as f:
                json.dump(alr_opted, f, indent=4)
                return True

    def is_opted_out(self, member: diskord.Member):  # TODO: move to db
        with open("./assets/opt_out.json", "r+") as f:
            opt_outs = dict(json.load(f))
        if not str(member.id) in opt_outs.keys():
            return False
        elif opt_outs[str(member.id)] == True:
            return True
        elif opt_outs[str(member.id)] == False:
            return False

    @commands.group(
        help="DM a user of your choice with a message",
        invoke_without_command=True,
        brief="20s",
    )
    @commands.cooldown(1, 20, BucketType.member)
    @commands.guild_only()
    async def dm(
        self, ctx: Context, member: diskord.Member, *, text_to_dm: str
    ):
        """DM a user of your choice with a message"""
        if member.bot:
            return await ctx.to_error("you cannot DM a bot")
        if self.is_opted_out(ctx.author):
            return await ctx.to_error(
                "You must be opted in to the DM command to send DMs through the bot"
            )
        if ctx.guild.id in [681882711945641997, 841721684876328961]:
            return await ctx.to_error(
                "This command is disabled due to the rules"
            )
        can = can_dm(member)
        message: diskord.Message = ctx.message
        em = diskord.Embed(
            description=f"> {text_to_dm}", color=random.choice(colors)
        )
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        em.set_footer(text=f"Use '{ctx.prefix}dm opt out' command to opt out")
        em.set_thumbnail(url=ctx.guild.icon.url)
        if can:
            confirmed = await ctx.confirm(
                f"Are you sure you want to send this DM to {member}",
                timeout=15,
            )
            if not confirmed:
                return await ctx.to_error("Command has been cancelled!")
            try:
                await member.send(embed=em)
                await message.add_reaction("✅")
            except (diskord.Forbidden, diskord.HTTPException):
                reasons = [
                    "1. Member has their DMs turned off",
                    "2. I'm blocked :(",
                    "3. Unknown server side error | try again later",
                    "4. Could not find the user in the bot's cache",
                ]
                em = diskord.Embed(title="DM command Unsuccesful").add_field(
                    name="Possible Reasons:", value="\n".join(reasons)
                )
                return await ctx.send(embed=em)

    @dm.command(
        help="Opt in or out of the DM command | You are opted in by default unless you explicitly opt out",
        brief="12h",
    )
    @commands.cooldown(1, 60 * 60 * 12, BucketType.member)
    async def opt(self, ctx: Context, opted_position: str = None):
        if not opted_position:
            return await ctx.to_error(
                "you need to specify if you want to opt in or opt out of the DM command"
            )
        if opted_position.casefold() == "in":
            self.opt_in(str(ctx.author.id))
            await ctx.send(
                "You Have opted into the DM command, resulting in others being able to DM you through the bot"
            )
        if opted_position.casefold() == "out":
            self.opt_out(str(ctx.author.id))
            await ctx.send(
                "You have opted out of the DM command and you won't receive any message from others through the bot"
            )

    @commands.command(
        aliases=["8ball"],
        help="Sends a random answer to a question",
        brief="5s",
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, BucketType.member)
    async def eightball(self, ctx: Context, *, question: str):
        """Sends a random answer to a question"""
        await ctx.trigger_typing()
        answer = random.choice(responses)
        em = diskord.Embed(color=random.choice(colors))
        em.set_author(
            name=ctx.author.display_name, icon_url=ctx.author.avatar.url
        )
        em.set_thumbnail(url=ctx.guild.icon.url)
        em.add_field(name="Question:", value=question, inline=False)
        em.add_field(name="Answer:", value=answer, inline=False)
        await ctx.reply(embed=em)

    @commands.command(aliases=["say"], help="Repeats your message", brief="5s")
    @commands.cooldown(1, 5, BucketType.member)
    async def echo(
        self,
        ctx: Context,
        channel: typing.Optional[diskord.TextChannel],
        *,
        msg: str,
    ):
        """Repeats your message"""
        with ctx.typing():
            await asyncio.sleep(1)
            if channel:
                await channel.send(msg)
                my_msg = await ctx.reply("Done!")
                await my_msg.add_reaction(emoji="✅")
            else:
                await ctx.message.delete()
                await ctx.send(msg)

    @commands.command(
        aliases=["coin", "flip"],
        help="Flips a coin and sends the result",
        brief="5s",
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def coinflip(self, ctx: Context):
        """Flips a coin and sends the result"""
        with ctx.typing():
            await asyncio.sleep(1)
            flips = ["Heads!", "Tails!"]
            flip = random.choice(flips)
            await ctx.reply(f"The Coin Landed on {flip}")

    @commands.command(
        aliases=["send"],
        help="Repeats a given message for a given amount of times. Note that amount needs to be lower than 7",
        brief="20s",
    )
    @commands.guild_only()
    @commands.cooldown(1, 20, BucketType.member)
    async def repeat(self, ctx: Context, amount: int, *, msg: str):
        """Repeats a given message for a given amount of times. Note that amount needs to be lower than 7"""
        await ctx.trigger_typing()
        if ctx.guild.id in [681882711945641997, 841721684876328961]:
            return await ctx.send("This command is disabled due to the rules")
        if amount > 7:
            return await ctx.to_error(
                "You cannot repeat a message more than 7 times. This is to reduce spamming"
            )
        sent = 0
        while sent != amount:
            await asyncio.sleep(2.5)
            await ctx.send(msg)
            sent = sent + 1

    async def get_response(self, arg, user_id: str):
        from randomstuff import AsyncClient
        from randomstuff.ai_response import AIResponse

        client = AsyncClient(secrets.PGAMER_X_API_KEY)
        response: AIResponse = await client.get_ai_response(
            arg, master="Marcus", bot="Hutch", uid=user_id
        )
        await client.close()
        return str(response.message)

    @commands.command(
        aliases=["c", "talk"],
        help="Chat with the bot. you should use the command every time you talk to it",
        brief="2s",
    )
    @commands.cooldown(1, 2, BucketType.member)
    async def chat(self, ctx: Context, *, text: str):
        """Chat with the bot. you should use the command every time you talk to it"""
        with ctx.typing():
            await asyncio.sleep(1)
            response = await self.get_response(str(text), str(ctx.author.id))
            return await ctx.reply(str(response))

    @commands.command(
        aliases=["turnbinary", "b"],
        help="Turns a text into a binary, just 1s and 0s",
        brief="5s",
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def binary(self, ctx: Context, *, text: str):
        """Turns a text into a binary, just 1s and 0s"""
        text = text.replace(" ", "-")
        await ctx.trigger_typing()
        async with self.bot.session as cs:
            try:
                async with cs.get(
                    f"https://some-random-api.ml/binary?text={text}"
                ) as r:
                    data = await r.json()
                    em = diskord.Embed(
                        title="Binary Converter",
                        url=f"https://some-random-api.ml/binary?text={text}",
                        color=random.choice(colors),
                    )
                    em.add_field(name="Text:", value=text, inline=False)
                    em.add_field(
                        name="Binary:", value=data["binary"], inline=False
                    )
                    em.set_footer(text=f"Requested by {ctx.author}")
                    em.set_thumbnail(url=ctx.guild.icon.url)
                    em.set_author(
                        name=ctx.author.display_name,
                        icon_url=ctx.author.avatar.url,
                    )
                    await ctx.reply(embed=em)
            except Exception as e:
                em = diskord.Embed(description=e)
                await ctx.reply(
                    "I could not convert it to binary :(", embed=em
                )

    @commands.command(
        aliases=["facts", "funfact"], help="Sends a random fact", brief="5s"
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def fact(self, ctx: Context):
        """Sends a random fact"""
        await ctx.trigger_typing()
        async with self.bot.session as cs:
            async with cs.get(
                "https://randomness-api.herokuapp.com/fact"
            ) as res:
                data = dict(await res.json())
        fact = json.loads(data.get("fact", random.choice(random_facts)))
        await ctx.reply(fact)

    @commands.command(
        aliases=["random", "website", "uselessweb", "useless"],
        help="Sends a random website link",
        brief="10s",
    )
    @commands.cooldown(1, 10, BucketType.member)
    @commands.bot_has_permissions(embed_links=True)
    async def web(self, ctx: Context):
        """Sends a random website link"""
        async with self.bot.session as cs:
            async with cs.get("") as res:
                data = dict(await res.json())
        chosen = json.loads(data.get("website", random.choice(website)))
        await ctx.reply()

    @commands.command(
        aliases=["Search", "SearchImage"],
        help="Sends a random image of a specified animal",
        brief="10s",
    )
    @commands.cooldown(1, 10, BucketType.guild)
    async def image(self, ctx: Context, *, image_name: str = None):
        """Sends a random image of a specified animal"""
        image_name = image_name or "cat"
        image_name = image_name.replace(" ", "_")
        categories = [
            "dog",
            "cat",
            "panda",
            "fox",
            "red_panda",
            "koala",
            "birb",
            "racoon",
            "kangaroo",
            "whale",
            "pikachu",
        ]
        if image_name not in categories:
            em = diskord.Embed(title="Categories", color=random.choice(colors))
            em.description = "\n".join(
                [
                    f"`{i}` -> Sends a random image of a `{i}`"
                    for i in categories
                ]
            )
            em.set_footer(text=f"Requested by {ctx.author}")
            em.set_thumbnail(url=ctx.guild.icon.url)
            return await ctx.send(
                content="provided image could not be found! Please make sure image name is one of the below categories",
                embed=em,
            )
        else:
            await ctx.trigger_typing()
            async with self.bot.session as cs:
                try:
                    async with cs.get(
                        f"https://some-random-api.ml/img/{image_name}"
                    ) as r:
                        data = await r.json()
                        embed = diskord.Embed(
                            title=f"{image_name}", color=random.choice(colors)
                        )
                        embed.set_image(url=data["link"])
                        return await ctx.send(embed=embed)
                except Exception as e:
                    return await ctx.send(e)

    @commands.command(
        aliases=["memey"], help="Sends a random meme", brief="5s"
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def meme(self, ctx: Context):
        """Sends a random meme"""
        await ctx.trigger_typing()
        async with self.bot.session as cs:
            try:
                async with cs.get("https://some-random-api.ml/meme") as r:
                    data = await r.json()
                    em = diskord.Embed(
                        title=data["caption"],
                        url=data["image"],
                        color=random.choice(colors),
                    )
                    em.set_image(url=data["image"])
                    return await ctx.send(embed=em)
            except Exception as e:
                return await ctx.reply(e)

    @commands.command(
        aliases=["r", "red"],
        help="Sends an image from a given subreddit, Defaults to r/memes.\nRemove the r/ part when using the command",
        brief="5s",
    )
    @commands.cooldown(1, 5, BucketType.member)
    async def reddit(self, ctx: Context, sub_reddit: str = None):
        """Sends an image from a given subreddit, Defaults to `r/memes`.remember to remove the r/ part when using the command"""
        if not sub_reddit:
            sub_reddit = "memes"
        await ctx.trigger_typing()
        try:
            subreddit_var = await reddit.subreddit(sub_reddit)
            await subreddit_var.load()
            if subreddit_var.over18 and not ctx.channel.is_nsfw():
                return await ctx.to_error(
                    "The given subreddit is NSFW, please provide a non-NSFW subreddit"
                )
            else:
                all_submissions = []
                top = subreddit_var.top(limit=50)
                async for submission in top:
                    all_submissions.append(submission)
                random_submission = random.choice(all_submissions)
                name = random_submission.title
                url = random_submission.url
                em = diskord.Embed(
                    title=name, color=random.choice(colors), url=url
                )
                em.set_image(url=url)
                await ctx.reply(embed=em)
        except Exception as e:
            return await ctx.reply(e)

    @commands.command(
        aliases=["polls", "p"],
        help="Create a poll with a maximum of 5 options.\nTo use multiple words, split them by `-` or `_`",
        brief="5s",
    )
    async def poll(self, ctx: Context, title: str, *options: str):
        """Create a poll with a maximum of 5 options. To use multiple words, split them by `-` or `_`"""
        title = title.replace("_", " ").replace("-", " ").title()
        if len(options) <= 1:
            await ctx.to_error("You need more than one option to make a poll!")
            return
        if len(options) > 5:
            await ctx.to_error(
                "You cannot make a poll for more than 5 options!"
            )
            return

        if (
            len(options) == 2
            and options[0].lower() == "yes"
            and options[1].lower() == "no"
        ):
            reactions = ["✅", "❌"]
        else:
            reactions = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣"]

        description = []
        for x, option in enumerate(options):
            description += "\n {} {}".format(reactions[x], option)
        desc = str("".join(description)).replace("-", "_").replace("_", " ")
        embed = diskord.Embed(title=title, description=desc)
        react_message = await ctx.send(embed=embed)
        for reaction in reactions[: len(options)]:
            await react_message.add_reaction(reaction)
        embed.set_footer(text="Poll ID: {}".format(react_message.id))
        await react_message.edit(embed=embed)

    @commands.command(help="NSFW command UwU :eyes:", brief="10s")
    @commands.cooldown(1, 10, BucketType.member)
    @commands.guild_only()
    async def nsfw(self, ctx: Context):
        ch: diskord.TextChannel = ctx.channel
        if ch.is_nsfw():
            return await ctx.send(
                "you know, https://pornhub.com/ exists for a reason. "
                "if its blocked in ur region then use "
                "https://reddit.com/r/nsfw/. get some help nub"
            )
        else:
            return await ctx.send(
                "Did you know that NSFW outside NSFW channels is against discord ToS?"
            )


def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))
