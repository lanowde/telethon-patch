# GNU V3
# https://github.com/New-dev0/Telethon-Patch
# Copyright  New-dev0

__author__ = "New-Dev0"
__version__ = "1.6.0"


print(f"Starting telethonpatch - [v{__version__}]")


# dont change import order
from . import methods, events, custom, pyrogram


# Rename long name methods..

# from telethon import TelegramClient

# TelegramClient.read = TelegramClient.send_read_acknowledge


from telethon.tl.alltlobjects import LAYER

print(f"Patched Successfully! - [Layer {LAYER}]")
