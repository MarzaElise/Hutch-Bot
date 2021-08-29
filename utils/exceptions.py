from discord.ext import commands


class NotDocumented(commands.CommandError):
    pass


class EmbedCreationError(commands.CommandError):
    pass


class MemberBlacklisted(commands.CommandError):
    pass
