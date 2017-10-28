import datetime
import traceback

import discord
from discord.ext import commands


class TomBotException(Exception):
    pass


class InvalidChannelCheck(commands.CommandError):
    def __init__(self, command):
        msg = f'A TextChannel type check for {command.qualified_name} has failed'
        super().__init__(msg)


class BotPermissionsCheck(commands.CommandError):
    def __init__(self, command):
        msg = f'A bot permissions check for {command.qualified_name} has failed'
        super().__init__(msg)


class ResponseStatusError(TomBotException):
    def __init__(self, status, reason, url):
        msg = f'REQUEST::[STATUS TOO HIGH    ]: {status} - {reason} - [[{url}]]'
        super().__init__(msg)


class ExplicitCheckFailure(commands.CommandError):
    """Raised when NSFW checks fail."""

    def __init__(self, command):
        msg = f'An explicit content check for {command.qualified_name} has failed'
        super().__init__(msg)


class CommandErrorHandler:
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog:
            attr = f'_{cog.__class__.__name__}__error'
            if hasattr(cog, attr):
                return

        error = getattr(error, 'original', error)

        ignored = (commands.CommandNotFound, commands.UserInputError)
        if isinstance(error, ignored):
            return

        handler = {
            discord.Forbidden: '**I do not have the required permissions to run this command.**',
            commands.DisabledCommand: f'{ctx.command} has been disabled.',
            commands.NoPrivateMessage: f'{ctx.command} can not be used in Private Messages.',
            commands.CheckFailure: '**You aren\'t allowed to use this command!**',
            ExplicitCheckFailure: f'This command can only be used in a **NSFW** channel.',
            InvalidChannelCheck: f'{ctx.command} can only be used in a server',
            BotPermissionsCheck: 'For **any** of the moderation commands, the bot must be given\n'
                                 'Manage Messages, Manage Nicknames, Kick Members and Ban Members'
        }

        try:
            message = handler[type(error)]
        except KeyError:
            pass
        else:
            return await ctx.send(message)

        embed = discord.Embed(title=f'Command Exception', color=discord.Color.red())
        embed.set_footer(text='Occured on')
        embed.timestamp = datetime.datetime.utcnow()

        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
        exc = exc.replace('`', '\u200b`')
        embed.description = f'```py\n{exc}\n```'

        embed.add_field(name='Command', value=ctx.command.qualified_name)
        embed.add_field(name='Invoker', value=ctx.author)
        embed.add_field(name='Location', value=f'Guild: {ctx.guild}\nChannel: {ctx.channel}')
        embed.add_field(name='Message', value=ctx.message.content)

        await ctx.bot.get_channel(372503186260492308).send(embed=embed)


def setup(bot):
    bot.add_cog(CommandErrorHandler())
