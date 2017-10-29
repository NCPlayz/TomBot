from tombot.bot import TomBot
import logging
import os


def log():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


if __name__ == '__main__':
    log()
    TomBot().run(os.environ['TOKEN'])
