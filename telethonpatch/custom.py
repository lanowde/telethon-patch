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


# Button


def mention(text, user):
    """Send Button with UserProfile mention.

    - Call 'get_input_entity' to fill in user parameter."""
    return InputKeyboardButtonUserProfile(text, user)


def web(text, url):
    """
    Send Button with WebView.

    - Works Only in Private.
    """
    return KeyboardButtonSimpleWebView(text, url)


# Message


# Message.message_link
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


# Message.comment
async def comment(self: "Message", *args, **kwargs):
    """Bound Method to comment."""
    if self._client:
        return await self._client.send_message(
            self.chat_id, comment_to=self.id, *args, **kwargs
        )


# Message.react
async def react(
    self: "Message",
    reaction: "typing.Optional[hints.Reaction]" = None,
    big: bool = False,
    add_to_recent: bool = False,
):
    """
    Reacts on the given message. Shorthand for
    `telethon.client.messages.MessageMethods.send_reaction`
    with both ``entity`` and ``message`` already set.
    """
    if self._client:
        return await self._client.send_reaction(
            await self.get_input_chat(),
            self.id,
            reaction,
            big=big,
            add_to_recent=add_to_recent,
        )


# Message.eor
async def edit_or_reply(
    self: "Message", text=None, time=None, edit_time=None, **kwargs
):
    """
    Edit or Reply to a Message.
    """
    reply_to = self.reply_to_msg_id or self.id
    link_preview = kwargs.pop("link_preview", False)
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


# Message.translate
async def translate(self, to_lang: str, **kwargs):
    """
    Translates the message using Google Translate.

    Args:
        to_lang (`str`):
            The language to translate to. Must be a valid language code
            (e.g. ``en``, ``es``, ``fr``, etc).

    Returns:
        `str`: The translated text.

    Example:
        .. code-block:: python
            # Translate the message to Spanish
            translated = await message.translate('es')
    """
    if self._client:
        return await self._client.translate(self.peer_id, self, to_lang, **kwargs)


# Message.transcribe
async def transcribe(self, **kwargs) -> "typing.Optional[str]":
    """
    Transcribes the message using native Telegram feature.

    Returns:
        `str`: The transcribed text.

    Example:
        .. code-block:: python
            # Transcribe the message
            transcribed = await message.transcribe()
    """
    if self._client:
        return await self._client.transcribe(self.peer_id, self, **kwargs)


# button functionalities
setattr(Button, "mention", mention)
setattr(Button, "web", web)

# message link
setattr(Message, "message_link", property(message_link))

# from original telepatch
setattr(Message, "comment", comment)
setattr(Message, "eor", edit_or_reply)

# from hikka
setattr(Message, "react", react)
setattr(Message, "translate", translate)
# setattr(Message, "transcribe", transcribe)
