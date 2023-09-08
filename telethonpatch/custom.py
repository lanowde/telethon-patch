# GNU V3
# https://github.com/New-dev0/Telethon-Patch
# Copyright  New-dev0

from telethon.tl.custom import Message


# msg.comment
async def comment(self: "Message", *args, **kwargs):
    """Bound Method to comment."""
    if self._client:
        return await self._client.send_message(
            self.chat_id, comment_to=self.id, *args, **kwargs
        )


# msg.react
async def react(self: "Message", *args, **kwargs):
    """Bound method to react to messages"""
    if self._client:
        return await self._client.send_reaction(self.chat_id, self.id, *args, **kwargs)


setattr(Message, "comment", comment)
setattr(Message, "react", react)
