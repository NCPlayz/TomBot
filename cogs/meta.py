import discord
from utils import get
from discord.ext import commands

from utils.paginator import HelpPaginator


class Meta:
    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    async def __error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(error)

    @commands.command(name='help')
    async def _help(self, ctx, *, command: str = None):
        """Shows help about a command or the bot."""

        try:
            if command is None:
                p = await HelpPaginator.from_bot(ctx)
            else:
                entity = self.bot.get_cog(command) or self.bot.get_command(command)

                if entity is None:
                    clean = command.replace('@', '@\u200b')
                    return await ctx.send(f'Command or category "{clean}" not found.')
                elif isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)

            await p.paginate()
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    async def about(self, ctx):
        """Tells you about me. 👀"""
        about_embed = discord.Embed(
            title="Hello there!",
            description=get.get_package_info("about"),
            color=discord.Color.teal()
        )
        about_embed.set_thumbnail(url=self.bot.user.avatar_url)
        about_embed.set_footer(text=f"""TomBot | Version {get.get_package_info("version")} | Requested by: 
        {ctx.message.author}""", icon_url=ctx.message.author.avatar_url)

        await ctx.send(embed=about_embed)

    @commands.command(aliases=["user_info"])
    async def userinfo(self, ctx, member: discord.Member = None):
        """Shows a profile. Defaults to you."""
        if member is None:
            member = ctx.message.author

        userinfo_embed = discord.Embed(
            title=f"{member.name}'s Profile",
            color=member.color
        )
        userinfo_embed.add_field(
            name="User:",
            value=str(member)
        )
        if member.display_name != member.name:
            userinfo_embed.add_field(
                name="Nickname:",
                value=member.display_name
            )
        userinfo_embed.add_field(
            name="Status:",
            value=str(member.status).title()
        )
        userinfo_embed.add_field(
            name="Playing:",
            value=str(member.game)
        )
        userinfo_embed.add_field(
            name="ID:",
            value=str(member.id)
        )
        userinfo_embed.add_field(
            name="Account Created At:",
            value=f"{member.created_at} UTC"
        )
        userinfo_embed.add_field(
            name="Joined Guild At:",
            value=f"{member.joined_at} UTC"
        )
        roles_list = [r.mention.replace(f'<@&{ctx.guild.id}>', '@everyone') for r in
                      reversed(sorted(member.roles, key=lambda role: role.position))]
        roles = ', '.join(roles_list)
        userinfo_embed.add_field(
            name="Roles",
            value=roles
        )
        userinfo_embed.set_thumbnail(url=member.avatar_url)
        userinfo_embed.set_footer(text=f"""{member}'s Profile | Requested by: 
        {ctx.message.author}""", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=userinfo_embed)

    @commands.command(aliases=["guild", "guildinfo", "serverinfo"])
    async def server(self, ctx):
        """Displays Server Info.
           Roles Credit: GiovanniMCMXCIX (Gio#0335 or GiovanniMCMXCIX#1211)"""
        if ctx.guild.emojis:
            emotes = ''.join((str(x) for x in ctx.guild.emojis))
        server_embed = discord.Embed(
            title=f"The {ctx.guild.name} Server"
        )
        server_embed.add_field(
            name="Server ID:",
            value=str(ctx.guild.id)
        )
        text_count = len(ctx.guild.text_channels)
        voice_count = len(ctx.guild.voice_channels)
        text_hid = sum(
            1 for c in ctx.guild.channels
            if c.overwrites_for(ctx.guild.default_role).read_messages is False)
        server_embed.add_field(
            name="Channels",
            value=f"{text_count} Text ({text_hid}) Hidden / {voice_count} Voice"
        )
        server_embed.add_field(
            name="Owner:",
            value=ctx.guild.owner.mention
        )
        server_embed.add_field(
            name="Region:",
            value=ctx.guild.region
        )
        server_embed.add_field(
            name="Created:",
            value=f"{ctx.guild.created_at} UTC"
        )
        server_embed.add_field(
            name="Emotes:",
            value=f"{emotes}"
        )
        server_embed.add_field(
            name="Server Members:",
            value=str(ctx.guild.member_count)
        )
        roles_list = [r.mention.replace(f'<@&{ctx.guild.id}>', '@everyone') for r in
                      reversed(sorted(ctx.guild.roles, key=lambda role: role.position))]
        roles = ', '.join(roles_list)
        server_embed.add_field(
            name="Roles",
            value=roles
        )
        server_embed.set_thumbnail(url=ctx.guild.icon_url)
        server_embed.set_footer(text=f"""The {ctx.guild.name} Server Information | Requested by: 
        {ctx.message.author}""", icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=server_embed)

    @commands.command()
    async def suggest(self, ctx, *, suggestion: str=None):
        """Give a suggestion for TomBot."""
        if suggestion is not None:
            suggest_embed = discord.Embed(
                title="TomBot Suggestion"
            )
            suggest_embed.add_field(
                name="Suggestion By:",
                value=ctx.author.mention
            )
            suggest_embed.add_field(
                name="Suggestion:",
                value=suggestion
            )
            suggest_embed.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.send(embed=suggest_embed)
            await ctx.send("Your suggestion is being taken into consideration.")
        else:
            await ctx.send("Please write your suggestion")


def setup(bot):
    bot.add_cog(Meta(bot))
