from discord.ext.commands import group
import math
import discord


class Math:
    def __init__(self, bot):
        self.bot = bot

    @group(invoke_without_command=True, aliases=["maths"])
    async def math(self, ctx):
        """Various mathematical functions, collected for your enjoyment."""
        if ctx.invoked_subcommand is None:
            pass

    @math.group(name="circumference", aliases=["circ"])
    async def _circumference(self, ctx):
        """Calculate the circumference of a circle given its radius or diameter."""
        if ctx.invoked_subcommand is None:
            pass

    @_circumference.command(name="radius")
    async def _radius(self, ctx, number: int):
        """Calculate the circumference of a circle given its radius."""
        answer = (math.pi * 2) * number
        await ctx.send(answer)

    @_circumference.command(name="diameter")
    async def _diameter(self, ctx, number: int):
        """Calculate the circumference of a circle given its diameter."""
        answer = math.pi * number
        await ctx.send(answer)

    @math.command(name="power")
    async def _power(self, ctx, number: int, power: int):
        """Calculate x raised to the power y."""
        answer = math.pow(number, power)
        await ctx.send(answer)

    @math.command(name="root")
    async def _root(self, ctx, number: int, degree: int=2):
        """Calculate the principal root of a number.
        If no degree is given, calculates the square root."""
        if degree == 2:
            answer = math.sqrt(number)
        else:
            answer = math.pow(number, 1.0/degree)
        await ctx.send(answer)

    @group()
    async def temp(self, ctx):
        """Commands to convert between different units of temperature."""
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
