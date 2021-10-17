import argparse
import sys

from discord.utils import escape_mentions
from discord.ext import commands

from ._converters import CONVERTERS


class ArgumentParsingError(commands.CommandError):
    def __init__(self, message):
        super().__init__(escape_mentions(message))


class DontExitArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        self.ctx = None
        kwargs.pop('add_help', False)
        super().__init__(*args, add_help=False, **kwargs)

    def error(self, message):
        raise ArgumentParsingError(message)

    def _get_value(self, action, arg_string):
        ctx = False
        type_func = self._registry_get('type', action.type, action.type)

        if hasattr(type_func, '__module__') and type_func.__module__.startswith('discord'):
            try:
                type_func = CONVERTERS[type_func.__name__]
            except KeyError:
                raise KeyError("{!r} is not a valid converter type", type_func)
            ctx = True

        if not callable(type_func):
            msg = '%r is not callable'
            raise argparse.ArgumentError(action, msg % type_func)

        # convert the value to the appropriate type
        try:
            if ctx:
                result = type_func(self.ctx, arg_string)
            else:
                result = type_func(arg_string)

        # ArgumentTypeErrors indicate errors
        except argparse.ArgumentTypeError:
            name = getattr(action.type, '__name__', repr(action.type))
            msg = str(sys.exc_info()[1])
            raise argparse.ArgumentError(action, msg)

        # TypeErrors or ValueErrors also indicate errors
        except (TypeError, ValueError):
            name = getattr(action.type, '__name__', repr(action.type))
            args = {'type': name, 'value': arg_string}
            msg = 'invalid %(type)s value: %(value)r'
            raise argparse.ArgumentError(action, msg % args)

        # return the converted value
        return result

    # noinspection PyMethodOverriding
    def parse_args(self, args, namespace=None, *, ctx):
        self.ctx = ctx
        return super().parse_args(args, namespace)
