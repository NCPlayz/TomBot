import discord
from discord.ext.commands import group, check
import datetime


def is_mod():
    def predicate(ctx):
        return discord.utils.get(ctx.guild.roles, name="Moderators™") in ctx.author.roles

    return check(predicate)


def is_private():
    def predicate(ctx):
        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            return True
        else:
            return False

    return check(predicate)


class ModChat:
    def __init__(self, bot):
        self.bot = bot

    async def send(self, ctx, destination: discord.abc.Messageable, is_complaint: bool, content, footer):
        send_embed = discord.Embed(
            title=f"{'Complaint' if is_complaint else 'Reply'} from {ctx.author} ({ctx.author.id})",
            color=discord.Color.dark_teal()
        )
        send_embed.add_field(
            name="Date and Time:",
            value=str(datetime.datetime.utcnow())
        )
        send_embed.add_field(
            name='Complaint' if is_complaint else 'Reply',
            value=content,
            inline=False
        )
        send_embed.set_thumbnail(url=ctx.author.avatar_url)
        send_embed.set_footer(text=footer)
        await destination.send(embed=send_embed)

    @group()
    async def chat(self, ctx):
        pass

    @chat.command(hidden=True)
    @is_private()
    async def complain(self, ctx, *, query: str=None):
        if query:
            mod_log = self.bot.get_channel(373156271056224256)
            await self.send(
                ctx, mod_log, False, query,
                f'Type {ctx.prefix}chat reply {ctx.author.name} to continue this conversation.'
            )
            await ctx.send('Your complaint is being taken into consideration.')
        else:
            await ctx.send('Please enter your query.')

    @chat.command()
    @is_mod()
    async def reply(self, ctx, member: discord.Member, *, reply: str):
        await self.send(
            ctx, member, False, reply,
            f'Type {ctx.prefix}chat complain to continue this conversation.'
        )
        await ctx.send('Sent to user.')


def setup(bot):
    bot.add_cog(ModChat(bot))
