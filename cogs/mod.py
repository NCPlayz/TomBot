"""./cog/mod.py"""
import asyncio

import discord
from discord.ext.commands import command

from utils.embed import Strike
from utils.get import get_rule


class Mod:
    """Moderation Commands."""
    def __init__(self, bot):
        self.bot = bot
        self.strike = Strike()

    def __local_check(self, ctx):
        return discord.utils.get(ctx.guild.roles, name="Moderators™") in ctx.message.author.roles

    @command(aliases=["onlyfro"])
    async def noreact(self, ctx, member: discord.Member):
        """Prevents guild members from reacting to messages."""
        audit_reason = f"{member.name}({member.id}) was given the role by a moderator."
        await member.add_roles(discord.utils.get(ctx.guild.roles, name="No-React"), reason=audit_reason)
        await ctx.send(f"Added No-React Role to {member.name}({member.id})")

    @command()
    async def react(self, ctx, member: discord.Member):
        """Let's guild members react to messages - if forbidden from before."""
        audit_reason = f"{member.name}({member.id}) was stripped of the role by a moderator."
        await member.remove_roles(discord.utils.get(ctx.guild.roles, name="No-React"), reason=audit_reason)
        await ctx.send(f"Removed No-React Role from {member.name}({member.id})")

    @command()
    async def strike(self, ctx, member: discord.Member, *, reason: str = None):
        """Strike a user."""
        if reason:
            await self.strike.send_log(ctx, member, reason)
            await self.strike.send_user(ctx, member, reason)
        else:
            await ctx.send('Please input reason.')

    @command()
    async def kick(self, ctx, member: discord.Member, *, reason: str="Violation of one or more rules."):
        """Kick a user."""
        await member.send(f'You have been kicked for the following issue:\n{reason}')
        await asyncio.sleep(5)
        await member.kick(reason=reason)
        await asyncio.sleep(5)
        await ctx.send(f'Kicked {member} | Reason: {reason}')

    @command()
    async def ban(self, ctx, member: discord.Member, *, reason: str="Violation of one or more rules."):
        """Ban a user."""
        await member.send(f'You have been kicked for the following issue:\n{reason}')
        await asyncio.sleep(5)
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member} | Reason: {reason}')

    @command()
    async def softban(self, ctx, member: discord.Member, *, reason: str="Violation of one or more rules."):
        """Softban a user."""
        await member.send(f'You have been softbanned for the the following issue:\n{reason}')
        await member.ban(reason=reason, delete_message_days=2)
        await member.unban()
        await ctx.send(f'Softbanned {member} | Reason: {reason}')

    @command()
    async def hackban(self, ctx, member_id: discord.Object, *, reason: str="Violation of one or more rules."):
        """Ban a user."""
        await ctx.guild.ban(user=member_id, reason=reason)

    @command()
    async def purge(self, ctx, count: int):
        """Purge an amount of messages from a channel."""
        if count <= 1:
            msg = ctx.send('Please input a valid number of messages.')
            await asyncio.sleep(8)
            await msg.delete()
        elif count >= 1:
            deleted_messages = await ctx.channel.purge(limit=(count + 1))
            message_number = max((len(deleted_messages) - 1), 0)
            resp = 'Deleted `{} message{}` 👌 '.format(message_number, ('' if (message_number < 2) else 's'))
            confirm_message = await ctx.send(resp)
            await asyncio.sleep(8)
            await confirm_message.delete()

    @command()
    async def rule(self, ctx, number: int):
        """Posts a specified rule."""
        if number >= 8:
            await ctx.send(f'There are only 7 rules. {ctx.author.mention}')
        else:
            await ctx.send('\n'.join(
                [phrase for phrase in get_rule(str(number))]
            ))


def setup(bot):
    bot.add_cog(Mod(bot))
