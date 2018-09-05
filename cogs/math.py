from discord.ext.commands import group
import math
import discord


class Math:
    def __init__(self, bot):
        self.bot = bot

    @group(invoke_without_command=True)
    async def math(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @math.group(name="circumference")
    async def _circumference(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @_circumference.command(name="radius")
    async def _radius(self, ctx, number: int):
        answer = (math.pi * 2) * number
        await ctx.send(answer)

    @_circumference.command(name="diameter")
    async def _diameter(self, ctx, number: int):
        answer = math.pi * number
        await ctx.send(answer)

    @math.command(name="power")
    async def _power(self, ctx, number: int, power: int):
        answer = math.pow(number, power)
        await ctx.send(answer)

    @group()
    async def temp(self, ctx):
        pass

    @temp.command()
    async def f(self, ctx, temperature: int):
        """Converts Fahrenheit Temperatures to Celsius Temperatures."""
        ans = (temperature-32) * 5/9
        await ctx.send(embed=discord.Embed(
            title="Conversion",
            description=f"{ans} °C",
            color=discord.Color.dark_orange()
        ))

    @temp.command()
    async def c(self, ctx, temperature: int):
        """Converts Celsius Temperatures to Fahrenheit Temperatures."""
        ans = (temperature*1.8)+32
        await ctx.send(embed=discord.Embed(
            title="Conversion",
            description=f"{ans} °F",
            color=discord.Color.dark_orange()
        ))


def setup(bot):
    bot.add_cog(Math(bot))
