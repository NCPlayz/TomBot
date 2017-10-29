import discord
from discord.ext import commands
import os


class Random:
    def __init__(self, bot):
        self.bot = bot
        self.unsplash_client_id = os.environ['UNSPLASH_ID']

    async def get_image(self, ctx, link: str, name: str):
        image_embed = discord.Embed(
            title=f"{name} Pic!"
        )
        image = ""
        if name is "Cat":
            async with ctx.session.get(link) as r:
                res = await r.json()
                image = res['file']
        if name is "Dog":
            async with ctx.session.get(link) as r:
                res = await r.json()
                image = res['url']
        if name is "Random":
            async with ctx.session.get(link) as r:
                res = await r.json()
                image = res['urls']['regular']
        image_embed.set_image(url=image)
        await ctx.send(embed=image_embed)

    @commands.group()
    async def random(self, ctx):
        return

    @random.command()
    async def cat(self, ctx):
        await self.get_image(
            ctx, 'http://random.cat/meow', "Cat"
        )

    @random.command()
    async def dog(self, ctx):
        await self.get_image(
            ctx, 'http://random.dog/woof.json', "Dog"
        )

    @random.command()
    async def pic(self, ctx):
        await self.get_image(
            ctx, f'https://api.unsplash.com/photos/random/?client_id={self.unsplash_client_id}', "Random"
        )


def setup(bot):
    bot.add_cog(Random(bot))
