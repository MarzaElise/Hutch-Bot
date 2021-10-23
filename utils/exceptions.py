from diskord.ext import commands


class NotDocumented(commands.CommandError):
    pass


class EmbedCreationError(commands.CommandError):
    pass


class MemberBlacklisted(commands.CommandError):
    pass


class CannotDmMember(commands.CommandError):
    pass


class AlreadyOptedOut(commands.CommandError):
    pass


class AlreadyOptedIn(commands.CommandError):
    pass
