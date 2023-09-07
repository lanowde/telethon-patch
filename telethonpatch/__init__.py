# GNU V3
# https://github.com/New-dev0/Telethon-Patch
# Copyright  New-dev0

__author__ = "New-Dev0"
__version__ = "0.03b0"


def print_conf():
    from telethon.tl.alltlobjects import LAYER

    print(f"Using Telethon-Patch (v{__version__}) [{LAYER}]")


print_conf()


from . import methods, custom, events, pyrogram

from telethon import TelegramClient

# Rename long name methods..
# TelegramClient.read = TelegramClient.send_read_acknowledge
