# GNU V3
# https://github.com/New-dev0/Telethon-Patch
# Copyright  New-dev0

__author__ = "New-Dev0"
__version__ = "1.0.9"


print(f"Starting telethonpatch - v{__version__}")


from . import methods, custom, events, pyrogram

from telethon import TelegramClient


# Rename long name methods..
# TelegramClient.read = TelegramClient.send_read_acknowledge


from telethon.tl.alltlobjects import LAYER

print(f"Patched Successfully! • Layer {LAYER}")
