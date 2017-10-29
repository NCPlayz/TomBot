"""./cog/core.py"""
import datetime
import re
import textwrap

import discord

from utils import get


DISCORD_INVITE = r'discord(?:app\.com|\.gg)[\/invite\/]?(?:(?!.*[Ii10OolL]).[a-zA-Z0-9]{5,6}|[a-zA-Z0-9\-]{2,32})'
INVITE_WHITELIST = ["discord.gg/ENqjbVy", "discord.gg/heychrissa", "discord.gg/r8xvkPC",
                    "discord.gg/vadact", "discord.gg/nysira", "discord.gg/zswz3wC", "discord.gg/Uvu4mss",
                    "discord.gg/basicallybea", "discord.gg/hatfilms", "discord.gg/yogscast", "discord.gg/ryogscast"]
OPUS_LIBS = [
    'libopus-0.x86.dll',
    'libopus-o.x64.dll',
    'libopus-0.dll',
    'libopus.so.0',
    'libopus.0.dylib'
]


class Core:
    def __init__(self, bot):
        self.bot = bot
        self.main_guild = None

    @staticmethod
    def get_invites(message):
        """Fetches all invites from message"""
        regex = re.match(DISCORD_INVITE, message.content)

        return regex

    @staticmethod
    def load_opus_lib(opus_libs=OPUS_LIBS):
        """Loads LibOpus For `bot`."""
        if discord.opus.is_loaded():
            return True
        for opus_lib in opus_libs:
            try:
                discord.opus.load_opus(opus_lib)
                return True
            except OSError:
                pass

    async def on_ready(self):
        """Notifies console when the bot is ready."""
        self.bot.up_time = datetime.datetime.now()
        self.main_guild = self.bot.get_guild(266593626501545984)
        a = await self.bot.application_info()
        print(textwrap.dedent(f"""
        -------------------------------------
        Username: {self.bot.user.name}
        User ID: {self.bot.user.id}
        Started: {self.bot.up_time}
        Opus Loaded: {'True' if self.load_opus_lib else 'False'}
        -------------------------------------"""))

    async def on_message(self, message):
        """A `bot` event triggered when a message is sent."""
        if message.author.bot:
            return

        if message.guild is not self.main_guild:
            return

        if self.bot.user.mention in message.content:
            msg = 'Who dares to ping me at this time of day? Was it you, {}?'.format(message.author.mention)
            await message.channel.send(msg)

        if '123785931474862080' in message.content:
            msg = 'Do not ping Tom! (Warning) - {}'.format(message.author.mention)
            await message.channel.send(msg)
            await message.delete()

        # Checks if non-mod
        if not get.is_mod(message.guild, message.author):

            if self.get_invites(message):
                    invite_ping = f"Do Not Advertise! {message.author.mention}\n\n{get.get_rule('6')}"
                    await message.author.send(invite_ping)
                    await message.delete()

            if message.content.isupper():
                if len(message.content) >= 75:
                    msg = 'Do not spam in all caps! (Warning) - {}'.format(message.author.mention)
                    await message.channel.send(msg)
                    await message.delete()

        if "y/n" in message.content:
            await message.add_reaction(get.get_emote('YES'))
            await message.add_reaction(get.get_emote('NO'))


def setup(bot):
    bot.add_cog(Core(bot))
