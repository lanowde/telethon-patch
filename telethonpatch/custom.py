# GNU V3
# https://github.com/New-dev0/Telethon-Patch
# Copyright  New-dev0

import asyncio

from telethon.tl import types
from telethon.tl.custom import Message
from telethon.errors import MessageNotModifiedError


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


# msg.eor
async def edit_or_reply(
    self: "Message", text=None, time=None, edit_time=None, **kwargs
):
    reply_to = self.reply_to_msg_id or self
    link_preview = kwargs.get("link_preview", False)
    if self.out and not isinstance(self, types.MessageService):
        if edit_time:
            await asyncio.sleep(edit_time)
        if kwargs.get("file") and not self.media:
            await self.delete()
            ok = await self.client.send_message(
                self.chat_id,
                text,
                link_preview=link_preview,
                reply_to=reply_to,
                **kwargs,
            )
        else:
            try:
                ok = await self.edit(text, link_preview=link_preview, **kwargs)
            except MessageNotModifiedError:
                ok = self
    else:
        ok = await self.client.send_message(
            self.chat_id, text, link_preview=link_preview, reply_to=reply_to, **kwargs
        )

    if time:
        await asyncio.sleep(time)
        return await ok.delete()
    return ok


setattr(Message, "comment", comment)
setattr(Message, "eor", edit_or_reply)
setattr(Message, "react", react)
