# GNU V3
# https://github.com/New-dev0/Telethon-Patch
# Copyright  New-dev0

import asyncio
import datetime
import typing

from telethon import TelegramClient, events, hints, utils

from telethon.tl import functions, types
from telethon.tl.alltlobjects import tlobjects


fns = {
    obj.__name__[:-7]: obj
    for obj in filter(lambda obj: "functions" in str(obj), tlobjects.values())
}


def _getattr(self, item):
    if item in self.__dict__:
        return self.__dict__[item]
    if (item in fns) or (item[:-7] in fns):
        if item not in fns:
            item = item[:-7]
        fn_ = fns[item]

        async def function(*args, **kwargs):
            return await self(fn_(*args, **kwargs))

        return function
    raise AttributeError(f"{self.__class__.__name__} has no attribute '{item}'")


setattr(TelegramClient, "__getattr__", _getattr)


async def create_group_call(
    self: TelegramClient,
    peer: types.TypeInputPeer,
    rtmp_stream: typing.Optional[bool] = None,
    random_id: int = None,
    title: typing.Optional[str] = None,
    schedule_date: typing.Optional[datetime.datetime] = None,
):
    """
    Create or Schedule a Group Call.
    (You will need to have voice call admin previlege to start a call.)

    Args:
       peer: ChatId/Username of chat.
       rtmp_stream: Whether to start rtmp stream.
       random_id: Any random integer or leave it None.
       title: Title to keep for voice chat.
       schedule (optional): 'datetime' object to schedule call.
    """
    return await self(
        functions.phone.CreateGroupCallRequest(
            peer=peer,
            rtmp_stream=rtmp_stream,
            title=title,
            random_id=random_id,
            schedule_date=schedule_date,
        )
    )


async def join_group_call(
    self: TelegramClient,
    call: types.TypeInputGroupCall,
    join_as: types.TypeInputPeer,
    params: types.TypeDataJSON,
    muted: typing.Optional[bool] = None,
    video_stopped: typing.Optional[bool] = None,
    invite_hash: typing.Optional[str] = None,
):
    """
    Join a Group Call.

    Args:
       call:
       join_as:
       params:
       muted:
       video_stopped:
       invite_hash:
    """
    return await self(
        functions.phone.JoinGroupCallRequest(
            call=call,
            join_as=join_as,
            params=params,
            muted=muted,
            video_stopped=video_stopped,
            invite_hash=invite_hash,
        )
    )


async def leave_group_call(
    self: TelegramClient,
    call: types.TypeInputGroupCall,
    source: int,
):
    """
    Leave a Group Call.

    Args:
       call:
       source:
    """
    return await self(functions.phone.LeaveGroupCallRequest(call=call, source=source))


async def discard_group_call(
    self: TelegramClient,
    call: types.TypeInputGroupCall,
):
    """
    Discard a Group Call.
    (You will need to have voice call admin previlege to start a call.)

    Args:
       call:
    """
    return await self(functions.phone.DiscardGroupCallRequest(call=call))


async def get_group_call(
    self: TelegramClient,
    call: types.TypeInputGroupCall,
    limit: int,
):
    """
    Get a Group Call.

    Args:
       call:
    """
    return await self(functions.phone.GetGroupCallRequest(call=call, limit=limit))


async def send_reaction(
    self: TelegramClient,
    entity: "hints.DialogLike",
    msg_id: "hints.MessageIDLike",
    reaction: "typing.Optional[hints.Reaction]" = None,
    big: bool = False,
    add_to_recent: bool = False,
    **kwargs,
):
    """
    Send reaction to a message.

    Args:
       entity:
       msg_id:
       big:
       reaction:
    """
    result = await self(
        functions.messages.SendReactionRequest(
            peer=entity,
            msg_id=msg_id,
            big=big,
            reaction=utils.convert_reaction(reaction),
            add_to_recent=add_to_recent,
            **kwargs,
        ),
    )
    for update in result.updates:
        if isinstance(update, types.UpdateMessageReactions):
            return update.reactions
        if isinstance(update, types.UpdateEditMessage):
            return update.message.reactions


async def report_reaction(
    self: TelegramClient,
    peer: "hints.EntityLike",
    id: int,
    reaction_peer: "hints.EntityLike",
) -> bool:
    return await self(functions.messages.ReportReactionRequest(peer, id, reaction_peer))


async def set_quick_reaction(
    self: TelegramClient,
    reaction: "hints.Reaction",
):
    return await functions.messages.SetDefaultReactionRequest(
        reaction=utils.convert_reaction(reaction),
    )


async def set_emoji_status(
    self: TelegramClient,
    document_id: int,
    until: typing.Optional[int] = None,
) -> bool:
    return await self(
        functions.account.UpdateEmojiStatusRequest(
            types.EmojiStatusUntil(document_id, until)
            if until
            else types.EmojiStatus(document_id)
        )
    )


async def transcribe(
    self: TelegramClient,
    peer: "hints.EntityLike",
    message: "hints.MessageIDLike",
    timeout: int = 20,
) -> typing.Optional[str]:
    result = await self(
        functions.messages.TranscribeAudioRequest(
            peer,
            utils.get_message_id(message),
        )
    )

    transcription_result = None

    event = asyncio.Event()

    @self.on(events.Raw(types.UpdateTranscribedAudio))
    async def handler(update):
        nonlocal result, transcription_result
        if update.transcription_id != result.transcription_id or update.pending:
            return

        transcription_result = update.text
        event.set()
        raise events.StopPropagation

    try:
        await asyncio.wait_for(event.wait(), timeout=timeout)
    except Exception:
        return None

    return transcription_result


async def translate(
    self: TelegramClient,
    peer: "hints.EntityLike",
    message: "hints.MessageIDLike",
    to_lang: str,
    raw_text: "typing.Optional[str]" = None,
    entities: "typing.Optional[typing.List[types.MessageEntity]]" = None,
) -> str:
    msg_id = utils.get_message_id(message) or 0
    if not msg_id:
        return None

    if not isinstance(message, types.Message):
        message = (await self.get_messages(peer, ids=[msg_id]))[0]

    result = await self(
        functions.messages.TranslateTextRequest(
            peer=peer,
            id=[msg_id],
            text=[
                types.TextWithEntities(
                    raw_text or message.raw_text,
                    entities or message.entities or [],
                )
            ],
            to_lang=to_lang,
        )
    )
    return (
        extensions.html.unparse(
            result.result[0].text,
            result.result[0].entities,
        )
        if result and result.result
        else ""
    )


async def join_chat(
    self: TelegramClient, entity: types.InputChannel = None, hash: str = ""
):
    if entity:
        return await self(functions.channels.JoinChannelRequest(entity))
    elif hash:
        return await self(functions.messages.ImportChatInviteRequest(hash))
    raise ValueError("Either entity or hash is required.")


async def hide_participants(
    self: TelegramClient, channel: types.InputChannel, enabled: bool = False
):
    """Toggle hidden participants"""
    return await self(
        functions.channels.ToggleParticipantsHiddenRequest(channel, enabled)
    )


async def set_contact_photo(
    self: TelegramClient, user: types.InputUser, file=None, **kwargs
):
    if isinstance(file, str):
        file = await self.upload_file(file)
    return await self(
        functions.photos.UploadContactProfilePhotoRequest(user, file=file, **kwargs)
    )


async def create_topic(
    self: TelegramClient,
    entity: "hints.EntityLike",
    title: str,
    icon_color: int = None,
    icon_emoji_id: int = None,
    random_id: int = None,
    send_as: "hints.EntityLike" = None,
) -> types.Message:
    """
    Creates a forum topic in the given channel.
    This method is only available in channels, not in supergroups.

    Arguments
        entity (`entity`):
            The channel where the forum topic should be created.

        title (`str`):
            The title of the forum topic.

        icon_color (`int`, optional):
            The color of the icon.

        icon_emoji_id (`int`, optional):
            The ID of the emoji.

        send_as (`entity`, optional):
            The user who should send the message.

    Returns
        The resulting :tl:`Message` object.

    Example
        .. code-block:: python
            # Create a forum topic in the channel
            await client.create_forum_topic(
                channel,
                'Awesome topic',
                icon_emoji_id=5454182070156794055,
            )
    """
    entity = await self.get_input_entity(entity)
    if send_as is not None:
        send_as = await self.get_input_entity(send_as)
    return await self(
        functions.channels.CreateForumTopicRequest(
            channel=entity,
            title=title,
            icon_color=icon_color,
            icon_emoji_id=icon_emoji_id,
            random_id=random_id,
            send_as=send_as,
        )
    )


async def edit_topic(
    self: TelegramClient,
    entity: "hints.EntityLike",
    topic_id: int,
    title: str = "",
    icon_emoji_id: int = 0,
    closed: bool = False,
):
    """
    Edits the given forum topic.
    This method is only available in channels, not in supergroups.

    Arguments
        entity (`entity`):
            The channel where the forum topic should be edited.

        topic_id (`int`):
            The ID of the topic to edit.

        title (`str`, optional):
            The new title of the topic.

        icon_emoji_id (`int`, optional):
            The new emoji ID of the topic.

        closed (`bool`, optional):
            Whether the topic should be closed or not.

    Returns
        The resulting :tl:`Updates` object.

    Example
        .. code-block:: python
            # Edit the forum topic in the channel
            await client.edit_forum_topic(
                channel,
                123,
                title='Awesome topic',
                icon_emoji_id=5454182070156794055,
            )
    """
    entity = await self.get_input_entity(entity)
    return await self(
        functions.channels.EditForumTopicRequest(
            channel=entity,
            topic_id=topic_id,
            title=title,
            icon_emoji_id=icon_emoji_id,
            closed=closed,
        )
    )


async def get_topics(
    self: TelegramClient,
    entity: "hints.EntityLike",
    topic_id: typing.List[int] = None,
    offset_date: typing.Optional[datetime.datetime] = None,
    offset_id: int = 0,
    offset_topic: int = 0,
    limit: int = None,
    q: typing.Optional[str] = None,
):
    """
    Gets the forum topics in the given channel.
    This method is only available in channels, not in supergroups.

    Arguments
        entity (`entity`):
            The channel where the forum topics should be retrieved.

        topic_id (`int`, optional):
            specific topic_id to get.

        q (`str`, optional):
            The query to search for.

        offset_date (`int`, optional):
            The offset date.

        offset_id (`int`, optional):
            The offset ID.

        offset_topic (`int`, optional):
            The offset topic.

        limit (`int`, optional):
            The maximum number of topics to retrieve.

    Returns
        The resulting :tl:`ForumTopics` object.

    Example
        .. code-block:: python
            # Get the forum topics in the channel
            await client.get_forum_topics(channel)
    """
    entity = await self.get_input_entity(entity)
    if topic_id is None:
        return await self(
            functions.channels.GetForumTopicsRequest(
                channel=entity,
                offset_date=offset_date,
                offset_id=offset_id,
                offset_topic=offset_topic,
                limit=limit,
                q=q,
            )
        )
    return await self(
        functions.channels.GetForumTopicsByIDRequest(channel=channel, topics=topic_id)
    )


async def update_pinned_topic(
    self: TelegramClient,
    entity: "hints.EntityLike",
    topic_id: int,
    pinned: bool,
) -> types.Updates:
    """
    Pins or unpins the given forum topic.
    This method is only available in channels, not in supergroups.

    Arguments
        entity (`entity`):
            The channel where the forum topic should be pinned.

        topic_id (`int`):
            The ID of the topic to pin.

        pinned (`bool`):
            Whether the topic should be pinned or not.

    Returns
        The resulting :tl:`Updates` object.

    Example
        .. code-block:: python
            # Pin the forum topic in the channel
            await client.update_pinned_forum_topic(
                channel,
                123,
                True,
            )
    """
    entity = await self.get_input_entity(entity)
    return await self(
        functions.channels.UpdatePinnedForumTopicRequest(
            channel=entity,
            topic_id=topic_id,
            pinned=pinned,
        )
    )


async def delete_topic(
    self: TelegramClient,
    entity: "hints.EntityLike",
    topic_id: int,
) -> types.messages.AffectedHistory:
    """
    Deletes the history of the given forum topic.
    This method is only available in channels, not in supergroups.

    Arguments
        entity (`entity`):
            The channel where the forum topic should be deleted.

        topic_id (`int`):
            The ID of the topic to delete.

    Returns
        The resulting :tl:`AffectedHistory` object.

    Example
        .. code-block:: python
            # Delete the forum topic in the channel
            await client.delete_topic_history(
                channel,
                123,
            )
    """
    entity = await self.get_input_entity(entity)
    return await self(
        functions.channels.DeleteTopicHistoryRequest(
            channel=entity,
            top_msg_id=topic_id,
        )
    )


# VC functions
setattr(TelegramClient, "create_group_call", create_group_call)
setattr(TelegramClient, "join_group_call", join_group_call)
setattr(TelegramClient, "leave_group_call", leave_group_call)
setattr(TelegramClient, "discard_group_call", discard_group_call)
setattr(TelegramClient, "get_group_call", get_group_call)

# reaction functions
setattr(TelegramClient, "send_reaction", send_reaction)
setattr(TelegramClient, "report_reaction", report_reaction)
setattr(TelegramClient, "set_quick_reaction", set_quick_reaction)

# for premium users maybe!
setattr(TelegramClient, "translate", translate)
setattr(TelegramClient, "translate", translate)
setattr(TelegramClient, "set_emoji_status", set_emoji_status)

# topic functions
setattr(TelegramClient, "create_topic", create_topic)
setattr(TelegramClient, "edit_topic", edit_topic)
setattr(TelegramClient, "get_topics", get_topics)
setattr(TelegramClient, "update_pinned_topic", update_pinned_topic)
setattr(TelegramClient, "delete_topic", delete_topic)

# extra functions
setattr(TelegramClient, "join_chat", join_chat)
setattr(TelegramClient, "hide_participants", hide_participants)

# doesn't works
# setattr(TelegramClient, "set_contact_photo", set_contact_photo)
