from diskord.ext import commands
import diskord


class EmbedFlags(commands.FlagConverter, case_insensitive=True):

    title: str = None
    description: str = None
    colour: str = None
    author: diskord.Member = None
    footer: str = None
    thumbnail: str = None
    image: str = None

    # aliases
    color: str = None
    img: str = None
    desc: str = None
