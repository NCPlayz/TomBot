import json
import discord
import os
from discord.ext import commands
import aiohttp


class TomBotContext(commands.Context):

    def is_float(self, string):
        try:
            return float(string)  # True if string is a number contains a dot
        except ValueError:  # String is not a number
            return False

    async def send(self, content=None, *args, **kwargs):
        """Override for send to add message filtering"""
        if content:
            if self.is_float(content) or content.isdigit():
                content = str(content)
            content.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")
        sent_message = await super().send(content, *args, **kwargs)
        return sent_message

    @property
    def session(self):
        return self.bot.session


class Utils:
    @staticmethod
    def get_package_info(arg: str):
        """Fetches `arg` in `package.json`."""
        json_data = json.load(open('./package.json'))
        return json_data[arg]


class TomBotBase(commands.Bot):
    """This is the class that initializes the bot."""
    def __init__(self):
        self.presence = discord.Game(name=f'TomBot v{Utils.get_package_info("version")} | &help'
                                     , url="https://www.twitch.tv/yogscast", type=1)
        self.token = os.environ['TOKEN']
        self.session = aiohttp.ClientSession()

        def get_prefix():
            """Fetches all known prefixes."""
            return ["&",
                    "TomBot ",
                    "TB "]

        def get_description():
            """Fetches description."""
            return Utils.get_package_info("description")

        def get_game():
            """Fetches game presence."""
            return self.presence

        super().__init__(command_prefix=get_prefix(), game=get_game(), description=get_description(), pm_help=None,
                         help_attrs=dict(hidden=True))

        startup_extensions = []
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                startup_extensions.append(file.replace('.py', ''))
        for extension in startup_extensions:
            if extension == "__init__":
                return
            else:
                try:
                    self.load_extension(f'cogs.{extension}')
                except Exception as e:
                    error = f'{extension}\n {type(e).__name__}: {e}'
                    print(f'Failed to load extension {error}')

    def run(self):
        super().run(self.token.value)

    async def on_message(self, message):
        ctx = await self.get_context(message, cls=TomBotContext)
        await self.invoke(ctx)

    async def fetch(self, url: str, headers: dict = None, timeout: float = None,
                    return_type: str = None, **kwargs):

        async with self.session.get(url, headers=headers, timeout=timeout, **kwargs) as resp:
            if return_type:
                cont = getattr(resp, return_type)
                return resp, await cont()
            else:
                return resp, None


class TomBot(TomBotBase):
    pass
