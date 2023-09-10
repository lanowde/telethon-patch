# GNU V3
# https://github.com/New-dev0/Telethon-Patch
# Copyright  New-dev0

import asyncio

from telethon.tl import types
from telethon.tl.custom import Button, Message
from telethon.errors import MessageNotModifiedError
from telethon.tl.types import (
    InputKeyboardButtonUserProfile,
    KeyboardButtonSimpleWebView,
)


# ------------------ Button ----------------------------


# Button.mention
def mention(text, user):
    """Send Button with UserProfile mention.

    - Call 'get_input_entity' to fill in user parameter."""
    return InputKeyboardButtonUserProfile(text, user)


# Button.web
def web(text, url):
    """
    Send Button with WebView.

    - Works Only in Private.
    """
    return KeyboardButtonSimpleWebView(text, url)


setattr(Button, "mention", mention)
setattr(Button, "web", web)


# ------------------ Message ----------------------------


# message.message_link
def message_link(self: "Message"):
    """Returns the message link."""
    if isinstance(self.chat, types.User) or self.is_private:
        fmt = "tg://openmessage?user_id={user_id}&message_id={msg_id}"
        return fmt.format(user_id=self.chat_id, msg_id=self.id)
    if getattr(self.chat, "username", None):
        return f"https://t.me/{self.chat.username}/{self.id}"
    if self.chat_id:
        chat = self.chat_id
        if str(chat).startswith(("-", "-100")):
            chat = int(str(chat).removeprefix("-100").removeprefix("-"))
    elif self.chat and self.chat.id:
        chat = self.chat.id
    else:
        return
    return f"https://t.me/c/{chat}/{self.id}"


# message.comment
async def comment(self: "Message", *args, **kwargs):
    """Bound Method to comment."""
    if self._client:
        return await self._client.send_message(
            self.chat_id, comment_to=self.id, *args, **kwargs
        )


# message.react
async def react(self: "Message", *args, **kwargs):
    """Bound method to react to messages"""
    if self._client:
        return await self._client.send_reaction(self.chat_id, self.id, *args, **kwargs)


# message.eor
async def edit_or_reply(
    self: "Message", text=None, time=None, edit_time=None, **kwargs
):
    """
    Edit or Reply to a Message.
    """
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


setattr(Message, "message_link", property(message_link))

setattr(Message, "comment", comment)
setattr(Message, "eor", edit_or_reply)
setattr(Message, "react", react)
