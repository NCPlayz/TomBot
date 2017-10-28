from discord.ext.commands import command, BucketType, cooldown
from random import choice
import json


class Quotes:
    """Quote commands."""
    def __init__(self, bot):
        self.bot = bot

    def get_quote(self, user):
        """
        :param user: name of a user with a registered command
        :return: random quote from user.
        """
        with open(f"./quotes/{user}.json") as f:
            config = json.load(f)
            ret = choice(config)
        return ret

    @cooldown(1, 300, BucketType.guild)
    @command(aliases=["akh"])
    async def akhawais(self, ctx):
        """Randomises a quote made by Akhawais."""
        await ctx.send(self.get_quote('akhawais'))

    @cooldown(1, 300, BucketType.guild)
    @command()
    async def ang(self, ctx):
        """Randomises a quote made by AngMod."""
        await ctx.send(self.get_quote('ang'))

    @cooldown(1, 300, BucketType.guild)
    @command()
    async def connor(self, ctx):
        """Randomises a quote made by Connor."""
        await ctx.send(self.get_quote('connor'))

    @cooldown(1, 300, BucketType.guild)
    @command()
    async def dan(self, ctx):
        """Randomises a quote made by Dan."""
        await ctx.send(self.get_quote('dan'))

    @cooldown(1, 300, BucketType.guild)
    @command()
    async def flufs(self, ctx):
        """Randomises a quote made by Flufs."""
        await ctx.send(self.get_quote('flufs'))

    @command()
    async def hackerman(self, ctx):
        async with ctx.session.get('https://hacker.actor/quote') as r:
            res = await r.json(content_type=None)
            await ctx.send(res['quote'])


def setup(bot):
    bot.add_cog(Quotes(bot))
