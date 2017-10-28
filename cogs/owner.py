import io
import textwrap
import traceback
from contextlib import redirect_stdout

from discord.ext.commands import command, is_owner


class Owner:
    """Owner Commands."""
    def __init__(self, bot):
        self.bot = bot

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @command(name='eval')
    @is_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates code."""
        env = {
            'bot': ctx.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': ctx.bot._last_result,
            'kkk': 'Racist!'
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        code = textwrap.indent(body, '  ')
        to_compile = f'async def func():\n{code}'

        try:
            exec(to_compile, env)
        except SyntaxError as e:
            return await ctx.send(self.get_syntax_error(e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('🍡')
            except Exception as e:
                await ctx.send('OK')

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                ctx.bot._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @is_owner()
    @command(name='reload', hidden=True)
    async def reload(self, ctx, *, cog: str):
        """Reloads a module."""
        try:
            self.bot.unload_extension("cogs."+cog)
            self.bot.load_extension("cogs."+cog)
            await ctx.send("Reloaded!")
        except Exception as e:
            await ctx.send('Error!')
            await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.message.add_reaction('\N{OK HAND SIGN}')
            print(f"Cog : {cog} Reloaded.")


def setup(bot):
    bot._last_result = None
    bot.add_cog(Owner(bot))
