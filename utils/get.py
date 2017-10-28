import json
import discord


emote_dict = {
    'YES': "\U0001f1fe",
    'NO': "\U0001f1f3"
}


def get_package_info(arg: str):
    """Fetches `arg` in `package.json`."""
    with open("./package.json") as f:
        config = json.load(f)

    return config[arg]


def get_emote(arg: str):
    """Fetches `arg` in `emote_dict`."""
    return emote_dict[arg]


def get_rule(arg: str):
    """Fetches `arg` in `./cogs/rules.json`."""
    with open("./cogs/rules.json") as f:
        config = json.load(f)
        ret = config[arg]
    return ret


# For on_message
def is_mod(guild: discord.Guild, member: discord.Member):
    return discord.utils.get(guild.roles, name="Moderators™") in member.roles
