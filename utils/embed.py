import discord
import datetime
from discord.ext import commands


class Strike:
    async def send_log(self, ctx: commands.Context, member: discord.Member, reason: str):
        strike_embed = discord.Embed(
            title="Strike",
            color=discord.Color.red()
        )
        strike_embed.add_field(
            name="User:",
            value=str(member)
        )
        strike_embed.add_field(
            name="ID:",
            value=member.id
        )
        strike_embed.add_field(
            name="Reason:",
            value=reason
        )
        strike_embed.set_footer(
            text=f"Strike given by {ctx.message.author}. | {datetime.datetime.utcnow()} UTC",
            icon_url=ctx.message.author.avatar_url
        )

        await discord.utils.get(ctx.guild.channels, name='bot-log').send(embed=strike_embed)

    async def send_user(self, ctx: commands.Context, member: discord.Member, reason: str):
        strike_embed = discord.Embed(
            title=f"Strike",
            description=f"You, {member.mention}, have been given a strike by {ctx.message.author}.",
            color=discord.Color.red()
        )
        strike_embed.add_field(
            name="Reason:",
            value=reason
        )
        strike_embed.set_footer(
            text=f"{datetime.datetime.utcnow()} UTC",
            icon_url=ctx.message.author.avatar_url
        )

        await member.send(embed=strike_embed)
