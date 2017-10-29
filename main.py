import asyncio
import logging

from tombot.bot import TomBot


async def start_bot():
    TomBot.start()


def log():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


if __name__ == '__main__':
    log()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
