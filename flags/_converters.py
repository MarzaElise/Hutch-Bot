"""
Synchronous object converters so I don't have to make argparse async
"""

import inspect
import re

import discord
from discord.ext.commands import BadArgument, NoPrivateMessage


def _get_id_match(argument):
    return RE.match(argument)


def _get_from_guilds(bot, getter, argument):
    result = None
    for guild in bot.guilds:
        result = getattr(guild, getter)(argument)
        if result:
            return result
    return result


def convert_to_member(ctx, argument):
    bot = ctx.bot
    match = _get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
    guild = ctx.guild
    if match is None:
        if guild:
            result = guild.get_member_named(argument)
        else:
            result = _get_from_guilds(bot, 'get_member_named', argument)
    else:
        user_id = int(match.group(1))
        if guild:
            result = guild.get_member(user_id)
        else:
            result = _get_from_guilds(bot, 'get_member', user_id)
    if result is None:
        raise BadArgument('Member "{}" not found'.format(argument))
    return result


def convert_to_user(ctx, argument):
    match = _get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
    state = ctx._state

    if match is not None:
        user_id = int(match.group(1))
        result = ctx.bot.get_user(user_id)
    else:
        arg = argument
        # check for discriminator if it exists
        if len(arg) > 5 and arg[-5] == '#':
            discrim = arg[-4:]
            name = arg[:-5]
            predicate = lambda u: u.name == name and u.discriminator == discrim
            result = discord.utils.find(predicate, state._users.values())
            if result is not None:
                return result

        predicate = lambda u: u.name == arg
        result = discord.utils.find(predicate, state._users.values())

    if result is None:
        raise BadArgument('User "{}" not found'.format(argument))
    return result


def convert_to_text_channel(ctx, argument):
    bot = ctx.bot

    match = _get_id_match(argument) or re.match(r'<#([0-9]+)>$', argument)
    guild = ctx.guild

    if match is None:
        # not a mention
        if guild:
            result = discord.utils.get(guild.text_channels, name=argument)
        else:
            def check(c):
                return isinstance(c, discord.TextChannel) and c.name == argument

            result = discord.utils.find(check, bot.get_all_channels())
    else:
        channel_id = int(match.group(1))
        if guild:
            result = guild.get_channel(channel_id)
        else:
            result = _get_from_guilds(bot, 'get_channel', channel_id)

    if not isinstance(result, discord.TextChannel):
        raise BadArgument('Channel "{}" not found.'.format(argument))

    return result


def convert_to_voice_channel(ctx, argument):
    bot = ctx.bot
    match = _get_id_match(argument) or re.match(r'<#([0-9]+)>$', argument)
    guild = ctx.guild

    if match is None:
        # not a mention
        if guild:
            result = discord.utils.get(guild.voice_channels, name=argument)
        else:
            def check(c):
                return isinstance(c, discord.VoiceChannel) and c.name == argument

            result = discord.utils.find(check, bot.get_all_channels())
    else:
        channel_id = int(match.group(1))
        if guild:
            result = guild.get_channel(channel_id)
        else:
            result = _get_from_guilds(bot, 'get_channel', channel_id)

    if not isinstance(result, discord.VoiceChannel):
        raise BadArgument('Channel "{}" not found.'.format(argument))

    return result


def convert_to_category_channel(ctx, argument):
    bot = ctx.bot

    match = _get_id_match(argument) or re.match(r'<#([0-9]+)>$', argument)
    guild = ctx.guild

    if match is None:
        # not a mention
        if guild:
            result = discord.utils.get(guild.categories, name=argument)
        else:
            def check(c):
                return isinstance(c, discord.CategoryChannel) and c.name == argument

            result = discord.utils.find(check, bot.get_all_channels())
    else:
        channel_id = int(match.group(1))
        if guild:
            result = guild.get_channel(channel_id)
        else:
            result = _get_from_guilds(bot, 'get_channel', channel_id)

    if not isinstance(result, discord.CategoryChannel):
        raise BadArgument('Channel "{}" not found.'.format(argument))

    return


def convert_to_colour(ctx, argument):
    arg = argument.replace('0x', '').lower()

    if arg[0] == '#':
        arg = arg[1:]
    try:
        value = int(arg, base=16)
        if not (0 <= value <= 0xFFFFFF):
            raise BadArgument('Colour "{}" is invalid.'.format(arg))
        return discord.Colour(value=value)
    except ValueError:
        arg = arg.replace(' ', '_')
        method = getattr(discord.Colour, arg, None)
        if arg.startswith('from_') or method is None or not inspect.ismethod(method):
            raise BadArgument('Colour "{}" is invalid.'.format(arg))
        return method()


def convert_to_role(ctx, argument):
    guild = ctx.guild
    if not guild:
        raise NoPrivateMessage()

    match = _get_id_match(argument) or re.match(r'<@&([0-9]+)>$', argument)
    if match:
        result = guild.get_role(int(match.group(1)))
    else:
        result = discord.utils.get(guild._roles.values(), name=argument)

    if result is None:
        raise BadArgument('Role "{}" not found.'.format(argument))
    return result


def convert_to_emoji(ctx, argument):
    match = _get_id_match(argument) or re.match(r'<a?:[a-zA-Z0-9\_]+:([0-9]+)>$', argument)
    result = None
    bot = ctx.bot
    guild = ctx.guild

    if match is None:
        # Try to get the emoji by name. Try local guild first.
        if guild:
            result = discord.utils.get(guild.emojis, name=argument)

        if result is None:
            result = discord.utils.get(bot.emojis, name=argument)
    else:
        emoji_id = int(match.group(1))

        # Try to look up emoji by id.
        if guild:
            result = discord.utils.get(guild.emojis, id=emoji_id)

        if result is None:
            result = discord.utils.get(bot.emojis, id=emoji_id)

    if result is None:
        raise BadArgument('Emoji "{}" not found.'.format(argument))

    return result


def convert_to_partial_emoji(ctx, argument):
    match = re.match(r'<(a?):([a-zA-Z0-9_]+):([0-9]+)>$', argument)

    if match:
        emoji_animated = bool(match.group(1))
        emoji_name = match.group(2)
        emoji_id = int(match.group(3))

        return discord.PartialEmoji.with_state(ctx.bot._connection, animated=emoji_animated, name=emoji_name,
                                               id=emoji_id)

    raise BadArgument('Couldn\'t convert "{}" to PartialEmoji.'.format(argument))


def convert_to_clean_content(ctx, argument):
    message = ctx.message
    transformations = {}

    if ctx.guild:
        def resolve_member(id, *, _get=ctx.guild.get_member):
            m = _get(id)
            return '@' + m.display_name if m else '@deleted-user'
    else:
        def resolve_member(id, *, _get=ctx.bot.get_user):
            m = _get(id)
            return '@' + m.name if m else '@deleted-user'

    transformations.update(
        ('<@%s>' % member_id, resolve_member(member_id))
        for member_id in message.raw_mentions
    )

    transformations.update(
        ('<@!%s>' % member_id, resolve_member(member_id))
        for member_id in message.raw_mentions
    )

    if ctx.guild:
        def resolve_role(_id, *, _find=ctx.guild.get_role):
            r = _find(_id)
            return '@' + r.name if r else '@deleted-role'

        transformations.update(
            ('<@&%s>' % role_id, resolve_role(role_id))
            for role_id in message.raw_role_mentions
        )

    def repl(obj):
        return transformations.get(obj.group(0), '')

    pattern = re.compile('|'.join(transformations.keys()))
    result = pattern.sub(repl, argument)

    # Completely ensure no mentions escape:
    return discord.utils.escape_mentions(result)


CONVERTERS = {
    'User': convert_to_user,
    'Member': convert_to_member,
    'TextChannel': convert_to_text_channel,
    'VoiceChannel': convert_to_voice_channel,
    'CategoryChannel': convert_to_category_channel,
    'Colour': convert_to_colour,
    'Color': convert_to_colour,
    'Role': convert_to_role,
    'Emoji': convert_to_emoji,
    'PartialEmoji': convert_to_partial_emoji,
    'clean_content': convert_to_clean_content
}
RE = re.compile(r'([0-9]{15,21})$')
