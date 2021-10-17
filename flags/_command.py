import shlex
from collections import namedtuple

import discord
from discord.ext import commands
from discord.ext.commands import converter

from . import _parser

__all__ = ["add_flag", "command", "group", "FlagCommand", "FlagGroup"]


argument = namedtuple("argument", "args kwargs")


def command(**kwargs):
    def inner(func):
        cls = kwargs.get('cls', FlagCommand)
        return cls(func, **kwargs)
    return inner


def group(**kwargs):
    def inner(func):
        cls = kwargs.get('cls', FlagGroup)
        return cls(func, **kwargs)
    return inner


def add_flag(*flag_names, **kwargs):
    def inner(func):
        if isinstance(func, commands.Command):
            nfunc = func.callback
        else:
            nfunc = func

        if not hasattr(nfunc, '_def_parser'):
            nfunc._def_parser = _parser.DontExitArgumentParser()
        nfunc._def_parser.add_argument(*flag_names, **kwargs)
        return func
    return inner


class FlagCommand(commands.Command):
    async def _parse_flag_arguments(self, ctx):
        if not hasattr(self.callback, '_def_parser'):
            return
        arg = ctx.view.read_rest()
        namespace = self.callback._def_parser.parse_args(shlex.split(arg), ctx=ctx)
        ctx.kwargs.update(vars(namespace))

    @property
    def old_signature(self):
        if self.usage is not None:
            return self.usage

        params = self.clean_params
        if not params:
            return ''

        result = []
        for name, param in params.items():
            greedy = isinstance(param.annotation, converter._Greedy)

            if param.default is not param.empty:
                # We don't want None or '' to trigger the [name=value] case and instead it should
                # do [name] since [name=None] or [name=] are not exactly useful for the user.
                should_print = param.default if isinstance(param.default, str) else param.default is not None
                if should_print:
                    result.append('[%s=%s]' % (name, param.default) if not greedy else
                                  '[%s=%s]...' % (name, param.default))
                    continue
                else:
                    result.append('[%s]' % name)

            elif param.kind == param.VAR_POSITIONAL:
                result.append('[%s...]' % name)
            elif greedy:
                result.append('[%s]...' % name)
            elif self._is_typing_optional(param.annotation):
                result.append('[%s]' % name)
            elif param.kind == param.VAR_KEYWORD:
                pass
            else:
                result.append('<%s>' % name)

        return ' '.join(result)

    @property
    def signature(self):
        result = self.old_signature
        to_append = [result]
        parser = self.callback._def_parser  # type: _parser.DontExitArgumentParser

        for action in parser._actions:
            # in argparse, options are done before positionals
            #  so we need to loop over it twice unfortunately
            if action.option_strings:
                name = action.dest.upper()
                flag = action.option_strings[0].lstrip('-').replace('-', '_')
                k = '-' if len(flag) == 1 else '--'
                should_print = action.default is not None and action.default != ''
                if action.required:
                    if should_print:
                        to_append.append('<%s%s %s=%s>' % (k, flag, name, action.default))
                    else:
                        to_append.append('<%s%s %s>' % (k, flag, name))
                else:
                    if should_print:
                        to_append.append('[%s%s %s=%s]' % (k, flag, name, action.default))
                    else:
                        to_append.append('[%s%s %s]' % (k, flag, name))

        for action in parser._actions:
            # here we do the positionals
            if not action.option_strings:
                name = action.dest
                should_print = action.default is not None and action.default != ''
                if action.nargs in ('*', '?'):  # optional narg types
                    if should_print:
                        to_append.append('[%s=%s]' % (name, action.default))
                    else:
                        to_append.append('[%s]' % name)
                else:
                    if should_print:
                        to_append.append('<%s=%s>' % (name, action.default))
                    else:
                        to_append.append('<%s>' % name)

        return ' '.join(to_append)

    async def _parse_arguments(self, ctx):
        ctx.args = [ctx] if self.cog is None else [self.cog, ctx]
        ctx.kwargs = {}
        args = ctx.args
        kwargs = ctx.kwargs

        view = ctx.view
        iterator = iter(self.params.items())

        if self.cog is not None:
            # we have 'self' as the first parameter so just advance
            # the iterator and resume parsing
            try:
                next(iterator)
            except StopIteration:
                fmt = 'Callback for {0.name} command is missing "self" parameter.'
                raise discord.ClientException(fmt.format(self))

        # next we have the 'ctx' as the next parameter
        try:
            next(iterator)
        except StopIteration:
            fmt = 'Callback for {0.name} command is missing "ctx" parameter.'
            raise discord.ClientException(fmt.format(self))

        for name, param in iterator:
            if param.kind == param.POSITIONAL_OR_KEYWORD:
                transformed = await self.transform(ctx, param)
                args.append(transformed)
            elif param.kind == param.KEYWORD_ONLY:
                # kwarg only param denotes "consume rest" semantics
                if self.rest_is_raw:
                    converter = self._get_converter(param)
                    argument = view.read_rest()
                    kwargs[name] = await self.do_conversion(ctx, converter, argument, param)
                else:
                    kwargs[name] = await self.transform(ctx, param)
                break
            elif param.kind == param.VAR_POSITIONAL:
                while not view.eof:
                    try:
                        transformed = await self.transform(ctx, param)
                        args.append(transformed)
                    except RuntimeError:
                        break
            elif param.kind == param.VAR_KEYWORD:
                await self._parse_flag_arguments(ctx)
                break

        if not self.ignore_extra:
            if not view.eof:
                raise commands.TooManyArguments('Too many arguments passed to ' + self.qualified_name)


class FlagGroup(FlagCommand, commands.Group):
    pass
