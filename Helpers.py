# the utilities file which has all the helper functions, custom exceptions and subclasses like Context
import asyncio
import contextlib
from dataclasses import dataclass
import io
import os
import random
from typing import List, Optional, Union

import aiohttp
import diskord
import diskord.utils
import requests
from diskord import abc
from diskord.embeds import EmptyEmbed
from diskord.ext import commands
import flags
from diskord.utils import parse_time


def url_exists(url: str):
    """
    Helper function to make sure a URL exists and returns a status code in the 2xx-3xx range
    """
    response = requests.get(url)
    code = str(response.status_code)
    return code.startswith("2") or code.startswith("3")


class NotDocumented(commands.CommandError):
    pass


class EmbedCreationError(commands.CommandError):
    pass


class Embed(diskord.Embed):
    r"""Custom embed class just for the `from_dict` method"""

    @classmethod
    def from_dict(cls, data):
        self = cls.__new__(cls)
        self.title = data.get("title", EmptyEmbed)
        self.type = data.get("type", EmptyEmbed)
        self.description = data.get("description", EmptyEmbed)
        self.url = data.get("url", EmptyEmbed)
        if self.title is not EmptyEmbed:
            self.title = str(self.title)
        if self.description is not EmptyEmbed:
            self.description = str(self.description)
        if self.url is not EmptyEmbed:
            self.url = str(self.url)
        try:
            self._colour = diskord.Colour(value=data["color"])
        except KeyError:
            pass
        try:
            self._timestamp = parse_time(data["timestamp"])
        except KeyError:
            pass
        for attr in (
            "thumbnail",
            "video",
            "provider",
            "author",
            "fields",
            "image",
            "footer",
        ):
            try:
                if data[attr] is not None:
                    value = data[attr]
            except KeyError:
                continue
            else:
                setattr(self, "_" + attr, value)
        return self
        # return super().from_dict(data)

    def __repr__(self):
        return self.description or ""


class Context(commands.Context):
    r"""
    Custom Context to support utilities and type hints
    """

    Embed = Embed

    def __init__(
        self, **attrs
    ):  # for type hints, i just copy pasted the __init__ from the source lmao
        self.message: diskord.Message = attrs.pop("message", None)
        self.bot: commands.Bot = attrs.pop("bot", None)
        self.args: list = attrs.pop("args", [])
        self.kwargs: dict = attrs.pop("kwargs", {})
        self.prefix: str = attrs.pop("prefix")
        self.command: commands.Command = attrs.pop("command", None)
        self.view = attrs.pop("view", None)
        self.invoked_with: str = attrs.pop("invoked_with", None)
        self.invoked_parents: List[str] = attrs.pop("invoked_parents", [])
        self.invoked_subcommand: commands.Command = attrs.pop(
            "invoked_subcommand", None
        )
        self.subcommand_passed: Optional[str] = attrs.pop(
            "subcommand_passed", None
        )
        self.command_failed: bool = attrs.pop("command_failed", False)
        self._state = self.message._state

    @diskord.utils.cached_property
    def guild(self):
        """Optional[:class:`.Guild`]: Returns the guild associated with this context's command. None if not available."""
        g: diskord.Guild = self.message.guild
        return g

    @property
    def reference(self):
        """shorthand method for `ctx.message.reference`"""
        if self.message.reference:
            ref: diskord.MessageReference = self.message.reference
            return ref
        return None

    @diskord.utils.cached_property
    def author(self):
        r"""Union[:class:`~diskord.User`, :class:`.Member`]:
        Returns the author associated with this context's command. Shorthand for :attr:`.Message.author`
        """
        author: Union[diskord.User, diskord.Member] = self.message.author
        return author

    def em(
        self,
        *,
        heading: str = None,
        desc: str = None,
        col: int = 0xFF0000,
        image: str = None,
    ):  # now im sure im using this method. no need to remove it :happy:
        r"""
        Custom function that returns a standard embed similar to ctx.embed but you cannot use some embed kwargs
        """
        em = diskord.Embed(timestamp=self.message.created_at, color=col)
        em.set_author(name=self.author, icon_url=self.author.avatar.url)
        em.set_footer(
            text=f"Requested by {self.author}", icon_url=self.author.avatar.url
        )
        em.set_thumbnail(url=self.guild.icon.url)
        if heading:
            em.title = heading
        if desc:
            em.description = desc
        if image:
            if image.startswith("https://"):
                em.set_image(url=image)
            else:
                img = f"https://{image}"
                print(
                    "Image name does not start with {!r}, changed the URL for closest match"
                )
                print("original -> changed")
                print(image, "->", img)
                em.set_image(url=img)
        return em

    async def send_help(self, *args):
        return await super().send_help(*args)

    def embed(
        self, description=None, *args, **kwargs
    ):  # i think i should remove this
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
        default = {
            "timestamp": self.message.created_at,
            "description": description,
            "color": random.choice(colors),
        }
        default.update(kwargs)
        return_embed = self.Embed(*args, **default)
        return_embed.set_footer(
            icon_url=self.author.avatar.url, text=f"Requested by {self.author}"
        )
        return return_embed

    async def to_error(self, description: str = None):
        if not description:
            description = "Unknown Error Occured and my owner has been notified of it, please contact Marcus | Bot Dev#4438 if this continues"
        em = self.Embed(
            title="Error!", description=description, color=diskord.Color.red()
        )
        em.timestamp = self.message.created_at
        em.set_author(name=self.author, icon_url=self.author.avatar.url)
        em.set_footer(
            text="If this was a mistake, please contact Marcus | Bot Dev#4438",
            icon_url=self.author.avatar.url,
        )
        return await self.send(embed=em)

    def error(self, description: str = None):
        if not description:
            description = "Unknown Error Occured and my owner has been notified of it, please contact Marcus | Bot Dev#4438 if this continues"
        em = self.Embed(
            title="Error!", description=description, color=diskord.Color.red()
        )
        em.timestamp = self.message.created_at
        em.set_author(name=self.author, icon_url=self.author.avatar.url)
        if (
            not description
            == "Unknown Error Occured and my owner has been notified of it, please contact Marcus | Bot Dev#4438 if this continues"
        ):
            em.set_footer(
                text="If this was a mistake, please contact Marcus | Bot Dev#4438",
                icon_url=self.author.avatar.url,
            )
        return em

    async def send(
        self,
        content: str = None,
        *,
        tts: bool = False,
        embed: diskord.Embed = None,
        file: diskord.File = None,
        files: List[diskord.File] = None,
        delete_after: float = None,
        nonce: int = None,
        allowed_mentions: diskord.AllowedMentions = None,
        reference: Union[diskord.MessageReference, diskord.Message] = None,
        mention_author: bool = False,
    ):
        r"""|coro|

        Sends a message to the destination with the content given.

        The content must be a type that can convert to a string through ``str(content)``.
        If the content is set to ``None`` (the default), then the ``embed`` parameter must
        be provided.

        To upload a single file, the ``file`` parameter should be used with a
        single :class:`~diskord.File` object. To upload multiple files, the ``files``
        parameter should be used with a :class:`list` of :class:`~diskord.File` objects.

        If the ``embed`` parameter is provided, it must be of type :class:`~diskord.Embed` and
        it must be a rich embed type.

        Parameters
        ------------
        content: :class:`str`
            The content of the message to send.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        embed: :class:`~diskord.Embed`
            The rich embed for the content.
        file: :class:`~diskord.File`
            The file to upload.
        files: List[:class:`~diskord.File`]
            A list of files to upload. Must be a maximum of 10.
        nonce: :class:`int`
            The nonce to use for sending this message. If the message was successfully sent,
            then the message will have a nonce with this value.
        delete_after: :class:`float`
            If provided, the number of seconds to wait in the background
            before deleting the message we just sent. If the deletion fails,
            then it is silently ignored.
        allowed_mentions: :class:`~diskord.AllowedMentions`
            Controls the mentions being processed in this message. If this is
            passed, then the object is merged with :attr:`~diskord.Client.allowed_mentions`.
            The merging behaviour only overrides attributes that have been explicitly passed
            to the object, otherwise it uses the attributes set in :attr:`~diskord.Client.allowed_mentions`.
            If no object is passed at all then the defaults given by :attr:`~diskord.Client.allowed_mentions`
            are used instead.

            .. versionadded:: 1.4

        reference: Union[:class:`~diskord.Message`, :class:`~diskord.MessageReference`]
            A reference to the :class:`~diskord.Message` to which you are replying, this can be created using
            :meth:`~diskord.Message.to_reference` or passed directly as a :class:`~diskord.Message`. You can control
            whether this mentions the author of the referenced message using the :attr:`~diskord.AllowedMentions.replied_user`
            attribute of ``allowed_mentions`` or by setting ``mention_author``.

            .. versionadded:: 1.6

        mention_author: Optional[:class:`bool`]
            If set, overrides the :attr:`~diskord.AllowedMentions.replied_user` attribute of ``allowed_mentions``.

            .. versionadded:: 1.6

        Raises
        --------
        ~diskord.HTTPException
            Sending the message failed.
        ~diskord.Forbidden
            You do not have the proper permissions to send the message.
        ~diskord.InvalidArgument
            The ``files`` list is not of the appropriate size,
            you specified both ``file`` and ``files``,
            or the ``reference`` object is not a :class:`~diskord.Message`
            or :class:`~diskord.MessageReference`.

        Returns
        ---------
        :class:`~diskord.Message`
            The message that was sent.
        """
        if (str(content)) and (self.bot.http.token in str(content)):
            content.replace(str(self.bot.http.token), "[token]")
        if (str(content)) and (len(str(content)) > 2000):
            new_file = diskord.File(io.StringIO(content), "message.txt")
            content = "Message has over 2000 characters..."
            if files:
                files.append(new_file)
            elif file:
                files = [file, new_file]
            elif not file:
                file = new_file
            if file and files:
                files.append(file)
                file = None
        if content == " ":
            content = "** **"
        if not reference:
            if self.message.reference:
                reference = self.message.reference
        with contextlib.suppress(diskord.HTTPException, diskord.Forbidden):
            sent: diskord.Message = await super().send(
                content=content,
                tts=tts,
                embed=embed,
                file=file,
                files=files,
                delete_after=delete_after,
                nonce=nonce,
                allowed_mentions=allowed_mentions,
                reference=reference,
                mention_author=mention_author,
            )
            if sent.nonce:
                self.last_msg = sent
            return sent
        return None

    async def reply(self, content: str = None, **kwargs: dict):
        r"""
        Reply to a user's message [takes in the same args and kwargs as :meth:ctx.send]
        """
        dump: bool = kwargs.get("dump", False)
        file: diskord.File = kwargs.get("file", None)
        files: List[diskord.File] = kwargs.get("files", None)
        if (str(content)) and (len(str(content)) > 2000):
            new_file = diskord.File(io.StringIO(content), "message.txt")
            content = "Message has over 2000 characters..."
            if files:
                files.append(new_file)
            elif file:
                files = [file, new_file]
            elif not file:
                file = new_file
            if file and files:
                files.append(file)
                file = None
        try:
            sent: diskord.Message = await super().reply(
                content=content, **kwargs
            )
            if sent.nonce:
                self.last_msg = sent
                return sent
            return None
        except diskord.HTTPException:
            pass
        except diskord.NotFound:
            sent: diskord.Message = await self.send(content=content, **kwargs)
            if sent.nonce:
                self.last_msg = sent
                return sent
            return None

    async def confirm(
        self,
        description: str = "Are you sure?",
        *,
        timeout=10,
        send_status: bool = False,
    ):
        em = self.Embed(
            title="Confirmation",
            description=description,
            color=diskord.Color.orange(),
        )
        reactions = ["✅", "❌"]
        em.timestamp = self.message.created_at
        em.set_author(name=self.author, icon_url=self.author.avatar.url)
        em.set_footer(
            text=f"You Have {timeout} seconds to react",
            icon_url=self.author.avatar.url,
        )
        msg = await self.send(embed=em)
        for reac in reactions:
            await msg.add_reaction(reac)

        def check(reaction: diskord.Reaction, user: diskord.Member):
            return (
                reaction.emoji in reactions
                and user == self.author
                and reaction.message == msg
            )

        reaction, user = await self.bot.wait_for(
            "reaction_add", check=check, timeout=timeout
        )
        if reaction.emoji == "✅":
            if send_status:
                embed = diskord.Embed(
                    title="Success",
                    description="Confirmation succesful ✅",
                    color=diskord.Color.green(),
                )
                await msg.delete()
                await self.send(embed=embed)
            return True
        elif reaction.emoji == "❌":
            if send_status:
                embed = diskord.Embed(
                    title="Failure",
                    description="Confirmation Failed! ❌",
                    color=diskord.Color.red(),
                )
                await msg.delete()
                await self.send(embed=embed)
            return False
        else:
            pass


class CustomMemberConverter(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        guild: diskord.Guild = ctx.guild
        if not guild:
            raise commands.NoPrivateMessage(
                f"{ctx.command.qualified_name} cannot be used in DMs"
            )
        try:
            int(argument)
        except ValueError:
            if guild:
                for member in guild.members:
                    mem: diskord.Member = member
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
                usr: diskord.User = user
                if str(usr.name).lower() == argument.lower():
                    return user
                break
            return await ctx.to_error(
                "User with id {!r} was not found".format(argument)
            )
        _id = int(argument)
        for user in bot.users:
            usr: diskord.User = user
            if usr.id == _id:
                return user
            break
        return await ctx.to_error(
            "User with id {!r} was not found".format(argument)
        )


class CustomRoleConverter(commands.Converter):
    async def convert(self, ctx: Context, argument: str):
        guild: diskord.Guild = ctx.guild()
        if not guild:
            return await ctx.to_error(
                f"{ctx.command.qualified_name} cannot be used in DMs"
            )
        try:
            int(argument)
        except ValueError:
            for r in guild.roles:
                role: diskord.Role = r
                if str(role.name).lower() == argument.lower():
                    return role
                break
            return await ctx.to_error(
                "Role with the name of {} was not found".format(argument)
            )
        _id = int(argument)
        for r in guild.roles:
            role: diskord.Role = r
            if _id == role.id:
                return role
            break
        return await ctx.to_error(
            "Role with the id '{}' was not found".format(argument)
        )

@dataclass
class ParseEmbedFlags:

    title: str = None
    description: str = None
    colour: str = "0xFF0000"
    author: diskord.Member = None
    footer: str = None
    thumbnail: str = None
    image: str = None

    # aliases
    foot: str = None
    color: str = None
    img: str = None
    desc: str = None
    thumb: str = None

    def validate(self):
        if all([self.desc, self.description]):
            raise EmbedCreationError("Provide only one of `desc` or `description`")
        if all([self.color, self.colour]):
            raise EmbedCreationError("Only one of `color` or `colour` should be provided")
        if all([self.thumb, self.thumbnail]):
            raise EmbedCreationError("Please only provide one of `thumb` or `thumbnail` not both")
        if all(self.img, self.image):
            raise EmbedCreationError("You cannot provide both `img` and `image`. Provide only one of them")
        if all(self.foot, self.footer):
            raise EmbedCreationError("Provide only one of either `foot` or `footer`")
        if not any(
            [self.title, self.desc, self.description, self.image, self.footer, self.foot, self.img]
        ):
            raise EmbedCreationError("None of `title` `description` `image` `footer` was given. Provide at least one of them")
    def set_defaults(self, ctx):

        color_ = self.color or self.colour
        thumbnail_ = self.thumb or self.thumbnail

        if not self.author:
            self.author = ctx.author
        if not thumbnail_:
            thumbnail_ = ctx.guild.icon.url
        if color_:
            color_ = int(color_, 16)

        self.thumbnail = thumbnail_
        self.color = color_

    def __post_init__(self):
        self.final = {}
        self.validate()

    def embed_dict(self, ctx):
        description_ = self.description or self.desc
        image_ = self.image or self.img
        color_ = self.color or self.colour
        footer_ = self.footer or self.foot
        thumbnail_ = self.thumb or self.thumbnail

        self.set_defaults(ctx)

        # actual creating dict part
        if self.title:
            self.final["title"] = self.title
        if description_:
            self.final["description"] = description_
        if image_:
            self.final["image"] = {'url': image_}
        if color_:
            self.final["color"] = self.color
        if footer_:
            self.final["footer"] = {'text': footer_}
        if thumbnail_:
            self.final["thumbnail"] = {'url': self.thumbnail}
        if self.author:
            self.final["author"] = {
                'name': f"{self.author}",
                'icon.url': self.author.avatar.url,
            }
        return self.final



def get_data_from_options(ctx: Context, **options):

    guild: diskord.Guild = ctx.guild
    
    flags_ = ParseEmbedFlags(**options)

    ret = flags_.embed_dict(ctx)

    em: Embed = Embed.from_dict(ret)
    return em


async def report_to_logs(bot: commands.Bot, content: str = None, **kwargs):
    sent = False
    for channel in bot.logs:
        content = content[:2000] if content else None
        try:
            await channel.send(content=content, **kwargs)
            sent = True
            break
        except AttributeError:
            pass
    return sent


website = [
    "https://findtheinvisiblecow.com/",
    "https://www.mapcrunch.com/",
    "https://theuselessweb.com/",
    "https://hackertyper.com/",
    "http://papertoilet.com/",
    "http://newsoffuture.com/",
    "http://beesbeesbees.com/",
    "https://pointerpointer.com/",
    "http://www.staggeringbeauty.com/",
    "http://www.shadyurl.com/",
    "https://archive.org/web/",
    "http://dontevenreply.com/",
    "https://stellarium-web.org/",
    "http://www.shutupandtakemymoney.com/",
    "https://play2048.co/",
    "https://en.wikipedia.org/wiki/List_of_individual_dogs",
    "https://zoomquilt.org/",
    "http://www.drivemeinsane.com/",
    "https://freerice.com/categories/english-vocabulary",
    "https://screamintothevoid.com/",
    "https://apod.nasa.gov/apod/astropix.html",
    "https://musclewiki.com/",
    "https://www.duolingo.com/",
    "https://www.internetlivestats.com/",
    "http://hubski.com/",
    "https://thisissand.com/",
    "https://lizardpoint.com/",
    "http://radio.garden/search",
    "https://www.musictheory.net/",
    "https://radiooooo.com/",
    "https://sleepyti.me/",
    "https://trypap.com/",
    "https://www.codecademy.com/?utm_source=pepperjam&utm_medium=affiliate&utm_term=21181&clickId=3606605584&pj_creativeid=8-12462&pj_publisherid=21181",
    "https://29a.ch/sandbox/2011/neonflames/#",
    "https://explore.org/livecams/cats/kitten-rescue-cam",
    "https://www.whatshouldireadnext.com/",
    "https://myfridgefood.com/",
    "https://www.onread.com/",
    "https://www.omfgdogs.com/",
    "http://weavesilk.com/",
    "https://eyebleach.me/",
    "https://en.wikipedia.org/wiki/List_of_conspiracy_theories",
    "http://sanger.dk/",
    "https://pokemonshowdown.com/",
    "https://www.sporcle.com/",
    "https://www.poptropica.com/",
    "https://koalabeast.com/",
    "http://orteil.dashnet.org/cookieclicker/",
    "http://www.foddy.net/2010/10/qwop/",
    "https://habitica.com/static/front",
    "http://www.flashbynight.com/",
    "https://xkcd.com/",
    "http://youarelistening.to/",
    "https://www.incredibox.com/",
    "https://asoftmurmur.com/",
    "https://www.rainymood.com/",
    "http://flashbynight.com/drench/",
    "https://quickdraw.withgoogle.com/",
    "https://www.dafont.com/",
    "https://www.spacejam.com/",
    "https://www.retailmenot.com/",
    "https://mint.intuit.com/",
    "https://tastedive.com/",
    "https://www.addictivetips.com/",
    "https://archive.org/details/msdos_Oregon_Trail_The_1990",
    "https://www.instructables.com/",
    "https://www.snopes.com/",
    "http://themagicipod.com/",
    "https://www.theonion.com/",
    "https://lifehacker.com/",
    "https://codepen.io/akm2/full/rHIsa",
    "https://mix.com/",
    "https://www.wizardingworld.com/",
    "https://www.ocearch.org/tracker/?list",
    "https://lego.com/en-us/kids",
]
random_facts = [
    "If you have 3 quarters, 4 dimes, and 4 pennies, you have $1.19. You also have the largest amount of money in coins without being able to make change for a dollar.",
    "The numbers '172' can be found on the back of the U.S. $5 dollar bill in the bushes at the base of the Lincoln Memorial.",
    "President Kennedy was the fastest random speaker in the world with upwards of 350 words per minute.",
    "In the average lifetime, a person will walk the equivalent of 5 times around the equator.",
    "Odontophobia is the fear of teeth.",
    "The 57 on Heinz ketchup bottles represents the number of varieties of pickles the company once had.",
    'In the early days of the telephone, operators would pick up a call and use the phrase, "Well, are you there?". It wasn\'t until 1895 that someone suggested answering the phone with the phrase "number please?',
    "The surface area of an average-sized brick is 79 cm squared.",
    "According to suicide statistics, Monday is the favored day for self-destruction.",
    "Cats sleep 16 to 18 hours per day.",
    "The most common name in the world is Mohammed.",
    "It is believed that Shakespeare was 46 around the time that the King James Version of the Bible was written. In Psalms 46, the 46th word from the first word is shake and the 46th word from the last word is spear.",
    'Karoke means "empty orchestra" in Japanese.',
    "The Eisenhower interstate system requires that one mile in every five must be straight. These straight sections are usable as airstrips in times of war or other emergencies.",
    "The first known contraceptive was crocodile dung, used by Egyptians in 2000 B.C.",
    'Rhode Island is the smallest state with the longest name. The official name, used on all state documents, is "Rhode Island and Providence Plantations."',
    "When you die your hair still grows for a couple of months.",
    "There are two credit cards for every person in the United States.",
    "Isaac Asimov is the only author to have a book in every Dewey-decimal category.",
    "The newspaper serving Frostbite Falls, Minnesota, the home of Rocky and Bullwinkle, is the Picayune Intellegence.",
    "It would take 11 Empire State Buildings, stacked one on top of the other, to measure the Gulf of Mexico at its deepest point.",
    "The first person selected as the Time Magazine Man of the Year - Charles Lindbergh in 1927",
    "The most money ever paid for a cow in an auction was $1.3 million.",
    'It took Leo Tolstoy six years to write "War & Peace".',
    "The Neanderthal's brain was bigger than yours is.",
    "On the new hundred dollar bill the time on the clock tower of Independence Hall is 4:10.",
    "Each of the suits on a deck of cards represents the four major pillars of the economy in the middle ages: heart represented the Church, spades represented the military, clubs represented agriculture, and diamonds represented the merchant class.",
    "he names of the two stone lions in front of the New York Public Library are Patience and Fortitude. They were named by then-mayor Fiorello LaGuardia.",
    "The Main Library at Indiana University sinks over an inch every year because when it was built, engineers failed to take into account the weight of all the books that would occupy the building.",
    "The sound of E.T. walking was made by someone squishing her hands in jelly.",
    "Lucy and Linus (who where brother and sister) had another little brother named Rerun. (He sometimes played left-field on Charlie Brown's baseball team, [when he could find it!]).",
    "The pancreas produces Insulin.",
    "1 in 5,000 north Atlantic lobsters are born bright blue.",
    "There are 10 human body parts that are only 3 letters long (eye hip arm leg ear toe jaw rib lip gum).",
    "A skunk's smell can be detected by a human a mile away.",
    'The word "lethologica" describes the state of not being able to remember the word you want.',
    "The king of hearts is the only king without a moustache.",
    "Henry Ford produced the model T only in black because the black paint available at the time was the fastest to dry.",
    "Mario, of Super Mario Bros. fame, appeared in the 1981 arcade game, Donkey Kong. His original name was Jumpman, but was changed to Mario to honor the Nintendo of America's landlord, Mario Segali.",
    "The three best-known western names in China: Jesus Christ, Richard Nixon, and Elvis Presley.",
    "Elephants are the only mammals that can't jump.",
    "The international telephone dialing code for Antarctica is 672.",
    "World Tourist day is observed on September 27.",
    "Women are 37% more likely to go to a psychiatrist than men are.",
    "The human heart creates enough pressure to squirt blood 30 feet (9 m).",
    "Diet Coke was only invented in 1982.",
    "There are more than 1,700 references to gems and precious stones in the King James translation of the Bible.",
    "When snakes are born with two heads, they fight each other for food.",
    "American car horns beep in the tone of F.",
    "Turning a clock's hands counterclockwise while setting it is not necessarily harmful. It is only damaging when the timepiece contains a chiming mechanism.",
    "There are twice as many kangaroos in Australia as there are people. The kangaroo population is estimated at about 40 million.",
    "Police dogs are trained to react to commands in a foreign language; commonly German but more recently Hungarian.",
    "The Australian $5 to $100 notes are made of plastic.",
    "St. Stephen is the patron saint of bricklayers.",
    "The average person makes about 1,140 telephone calls each year.",
    "Stressed is Desserts spelled backwards.",
    "If you had enough water to fill one million goldfish bowls, you could fill an entire stadium.",
    "Mary Stuart became Queen of Scotland when she was only six days old.",
    "Charlie Brown's father was a barber.",
    "Flying from London to New York by Concord, due to the time zones crossed, you can arrive 2 hours before you leave",
    "Dentists have recommended that a toothbrush be kept at least 6 feet (2 m) away from a toilet to avoid airborne particles resulting from the flush.",
    "You burn more calories sleeping than you do watching TV.",
    "A lion's roar can be heard from five miles away.",
    'The citrus soda 7-UP was created in 1929; "7" was selected because the original containers were 7 ounces. "UP" indicated the direction of the bubbles.',
    "Canadian researchers have found that Einstein's brain was 15% wider than normal.",
    "The average person spends about 2 years on the phone in a lifetime.",
    "The fist product to have a bar code was Wrigleys gum.",
    "The largest number of children born to one woman is recorded at 69. From 1725-1765, a Russian peasant woman gave birth to 16 sets of twins, 7 sets of triplets, and 4 sets of quadruplets.",
    'Beatrix Potter created the first of her legendary "Peter Rabbit" children\'s stories in 1902.',
    "In ancient Rome, it was considered a sign of leadership to be born with a crooked nose",
    'The word "nerd" was first coined by Dr. Seuss in "If I Ran the Zoo."',
    "A 41-gun salute is the traditional salute to a royal birth in Great Britain.",
    "The bagpipe was originally made from the whole skin of a dead sheep.",
    "The roar that we hear when we place a seashell next to our ear is not the ocean, but rather the sound of blood surging through the veins in the ear. Any cup-shaped object placed over the ear produces the same effect.",
    "Revolvers cannot be silenced because of all the noisy gasses which escape the cylinder gap at the rear of the barrel.",
    "Liberace Museum has a mirror-plated Rolls Royce; jewel-encrusted capes, and the largest rhinestone in the world, weighing 59 pounds and almost a foot in diameter.",
    "A car that shifts manually gets 2 miles more per gallon of gas than a car with automatic shift.",
    "Cats can hear ultrasound.",
    "Dueling is legal in Paraguay as long as both parties are registered blood donors.",
    "The highest point in Pennsylvania is lower than the lowest point in Colorado.",
    "The United States has never lost a war in which mules were used.",
    "Children grow faster in the springtime.",
    "On average, there are 178 sesame seeds on each McDonalds BigMac bun.",
    "Paul Revere rode on a horse that belonged to Deacon Larkin.",
    "The Baby Ruth candy bar was actually named after Grover Cleveland's baby daughter, Ruth.",
    "Minus 40 degrees Celsius is exactly the same as minus 40 degrees Fahrenheit.",
    'Clans of long ago that wanted to get rid of unwanted people without killing them used to burn their houses down -- hence the expression "to get fired"',
    "Nobody knows who built the Taj Mahal. The names of the architects, masons, and designers that have come down to us have all proved to be latter-day inventions, and there is no evidence to indicate who the real creators were.",
    "Every human spent about half an hour as a single cell.",
    "7.5 million toothpicks can be created from a cord of wood.",
    "The plastic things on the end of shoelaces are called aglets.",
    "A 41-gun salute is the traditional salute to a royal birth in Great Britain.",
    'The earliest recorded case of a man giving up smoking was on April 5, 1679, when Johan Katsu, Sheriff of Turku, Finland, wrote in his diary "I quit smoking tobacco." He died one month later.',
    '"Goodbye" came from "God bye" which came from "God be with you."',
    "February is Black History Month.",
    "Jane Barbie was the woman who did the voice recordings for the Bell System.",
    "The first drive-in service station in the United States was opened by Gulf Oil Company - on December 1, 1913, in Pittsburgh, Pennsylvania.",
    "The elephant is the only animal with 4 knees.",
    "Kansas state law requires pedestrians crossing the highways at night to wear tail lights.",
]
