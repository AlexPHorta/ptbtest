#!/usr/bin/env python
# pylint: disable=E0611,E0213,E1102,C0103,E1101,W0613,R0913,R0904
#
# A library that provides a testing suite fot python-telegram-bot
# wich can be found on https://github.com/python-telegram-bot/python-telegram-bot
# Copyright (C) 2017
# Pieter Schutz - https://github.com/eldinnie
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module provides a class to generate telegram mesages"""
import datetime
import time

from .updategenerator import update
from .ptbgenerator import PtbGenerator
from .entityparser import EntityParser
from ptbtest import (UserGenerator, ChatGenerator, Mockbot)
from ptbtest.errors import (BadUserException, BadMessageException,
                            BadChatException, BadBotException,
                            BadMarkupException)
from telegram import (Audio, Chat, Contact, Document, Location, Message,
                      PhotoSize, Sticker, User, Venue, Video, Voice)


class MessageGenerator(PtbGenerator):
    """
        Message generator class.

        Attributes:
            bot (ptbtest.Mockbot): Bot to encode with the messages

        Args:
            bot (Optional[ptbtest.Mockbot]): supply your own for a custom botname
    """

    def __init__(self, bot=None):
        PtbGenerator.__init__(self)
        self.idgen = self._gen_id()
        self.ug = UserGenerator()
        self.cg = ChatGenerator()
        if not bot:
            self.bot = Mockbot()
        elif isinstance(bot, Mockbot):
            self.bot = bot
        else:
            raise BadBotException

    def _gen_id(self):
        x = 1
        while True:
            yield x
            x += 1

    @update("edited_channel_post")
    def get_edited_channel_post(self, channel_post=None, **kwargs):
        """
        Parameters:
            channel_post (Optional(telegram.Message)): The edited_channel_post will the same user, chat and message_id
            **kwargs: See get_message for the full list

        Returns:
            telegram.Update: A telegram update object containing a :py:class:`telegram.Message`.
        """

        id, user, chat = None, None, None
        if channel_post:
            if not isinstance(channel_post, Message):
                raise BadMessageException
            id = channel_post.message_id
            user = channel_post.from_user
            chat = channel_post.chat

        return self.get_channel_post(id=id, user=user, chat=chat,
                                     **kwargs).channel_post

    @update("channel_post")
    def get_channel_post(self, chat=None, user=None, **kwargs):
        """
        Parameters:
            chat (Optional[telegram.Chat]): Chat with type='channel' to use with this update
            user (Optional[telegram.User]): User for the update. None if omitted
            **kwargs: See get_message

        Returns:
            telegram.Update: A telegram update object containing a :py:class:`telegram.Message.
        """
        if chat:
            if not isinstance(chat, Chat):
                raise BadChatException
            if not chat.type == "channel":
                raise BadChatException(
                    "Can only use chat.type='channel' for get_channel_post")
        else:
            chat = ChatGenerator().get_chat(chat_type="channel")

        return self.get_message(chat=chat, user=user, channel=True,
                                **kwargs).message

    @update("edited_message")
    def get_edited_message(self, message=None, **kwargs):
        """
        Parameters:
            message (Optional(telegram.Message)): The edited_message will have the same user, chat and message_id
            **kwargs: See get_message for the full list

        Returns:
            telegram.Update: A telegram update object containing a :py:class:`telegram.Message`.

        """
        id, user, chat = None, None, None
        if message:
            if not isinstance(message, Message):
                raise BadMessageException
            id = message.message_id
            user = message.from_user
            chat = message.chat

        return self.get_message(id=id, user=user, chat=chat, **kwargs).message

    @update("message")
    def get_message(self,
                    id=None,
                    user=None,
                    chat=None,
                    private=True,
                    forward_from=None,
                    forward_from_chat=None,
                    forward_date=None,
                    reply_to_message=None,
                    text=None,
                    entities=None,
                    audio=None,
                    document=None,
                    photo=None,
                    sticker=None,
                    video=None,
                    voice=None,
                    caption=None,
                    contact=None,
                    location=None,
                    venue=None,
                    new_chat_members=None,
                    left_chat_member=None,
                    new_chat_title=None,
                    new_chat_photo=None,
                    delete_chat_photo=False,
                    group_chat_created=False,
                    supergroup_chat_created=False,
                    migrate_to_chat_id=None,
                    migrate_from_chat_id=None,
                    channel_chat_created=False,
                    pinned_message=None,
                    forward_from_message_id=None,
                    parse_mode=None,
                    channel=False,
                    bot=None):
        """
        When called without arguments will return an update object for a message from a private chat with a
        random user. for modifiers see args.

        Notes:
            whenever a list of telegram.PhotoSize objects is expected but not supplied it will always be a
            list with two random sizes between 40-400 pixels. These will not be valid file id's

        Parameters:
            user (Optional[telegram.User]): User the message is from (m.from_user)
            chat (Optional[telegram.Chat]): Chat the message is from (m.chat).
            private (Optional[bool]): If the message is private (optionally with the supplied user) default=True
            text (str): The text for the message, can make use of markdown or html, make sure to specify with parse_mode
            parse_mode (Optional[str]): "HTML" or "Markdown" parses the text and fills entities
            entities (Optional[lst(telegram.MessageEntity)]): when text and parsemode are set this will be filled with the entities in the text.  # noqa: E501
            reply_to_message (Optional[telegram.Message): Messages this one is a reply to
            forward_from (Optional[telegram.User): User this message is forwarded from
            forward_from_chat (Optional[telegram.Chat]): channel this message is forwarded from
            forward_date (Optional[int]): Original sent date
            forward_from_message_id (Optional[int]): message id from forwarded channel post.
            new_chat_members (Optional[lst(telegram.User)]): List of new members for this chat
            left_chat_member (Optional[telegram.User]): Member left this chat
            new_chat_title (Optional[str]): New title for the chat
            new_chat_photo (Optional[lst(telegram.Photosize)] or True): New picture for the group
            pinned_message (Optional[telegram.Message]): Pinned message for supergroups
            channel_chat_created (Optional[True]): Not integrated
            migrate_from_chat_id (Optional[int]): Not integrated
            migrate_to_chat_id (Optional[int]): Not integrated
            supergroup_chat_created (Optional[True]): Not integrated
            group_chat_created (Optional[True]): Not integrated
            delete_chat_photo (Optional[True]): Not integrated
            venue (Optional[telegram.Venue or True]): Either the right object or True to generate one
            location (optional[telegram.Location or True]): Either the right object or True to generate one
            contact (optional[telegram.Contact or True]): Either the right object or True to generate one
            caption (Optional[str or True]: Either the right object or True to generate one
            voice (Optional[telegram.Voice or True]): Either the right object or True to generate one
            video (Optional[telegram.Video or True]): Either the right object or True to generate one
            sticker (Optional[telegram.Sticker] or True): Either the right object or True to generate one
            photo (Optional[lst(telegram.PhotoSize) or True]): Either the right object or True to generate one
            document (Optional[telegram.Document or True]): Either the right object or True to generate one
            audio (Optional[telegram.Audio] or True): Either the right object or True to generate one

        Returns:
            telegram.Update: A telegram update object containing a :py:class:`telegram.Message`.
        """
        if not channel:
            user, chat = self._get_user_and_chat(user, chat, private)

        if reply_to_message and not isinstance(reply_to_message, Message):
            raise BadMessageException

        forward_date, forward_from, forward_from_message_id = self._handle_forward(
            forward_date, forward_from, forward_from_chat,
            forward_from_message_id)

        text, entities = self._handle_text(text, parse_mode)

        new_chat_photo = self._handle_status(
            channel_chat_created, chat, delete_chat_photo, group_chat_created,
            left_chat_member, migrate_from_chat_id, migrate_to_chat_id,
            new_chat_members, new_chat_photo, new_chat_title, pinned_message,
            supergroup_chat_created)

        audio, contact, document, location, photo, sticker, venue, video, voice = self._handle_attachments(
            audio, contact, document, location, photo, sticker, user, venue,
            video, voice, caption)

        return Message(message_id=id or next(self.idgen),
                       date=None,
                       chat=chat,
                       from_user=user,
                       text=text,
                       forward_from=forward_from,
                       forward_from_chat=forward_from_chat,
                       reply_to_message=reply_to_message,
                       entities=entities,
                       audio=audio,
                       document=document,
                       photo=photo,
                       sticker=sticker,
                       video=video,
                       voice=voice,
                       caption=caption,
                       contact=contact,
                       location=location,
                       venue=venue,
                       new_chat_members=new_chat_members,
                       left_chat_member=left_chat_member,
                       new_chat_title=new_chat_title,
                       new_chat_photo=new_chat_photo,
                       delete_chat_photo=delete_chat_photo,
                       group_chat_created=group_chat_created,
                       supergroup_chat_created=supergroup_chat_created,
                       migrate_to_chat_id=migrate_to_chat_id,
                       migrate_from_chat_id=migrate_from_chat_id,
                       channel_chat_created=channel_chat_created,
                       pinned_message=pinned_message,
                       forward_from_message_id=forward_from_message_id,
                       forward_date=forward_date,
                       bot=bot or self.bot)

    def _handle_attachments(self, audio, contact, document, location, photo,
                            sticker, user, venue, video, voice, caption):
        attachments = [
            x for x in [
                photo, venue, location, contact, voice, video, sticker,
                document, audio
            ] if x
        ]
        if caption and not attachments:
            raise BadMessageException(
                "Can't have a caption without attachment")
        if len(attachments) > 1:
            raise BadMessageException("can't add more than one attachment")
        if photo:
            if isinstance(photo, list):
                if all([isinstance(x, PhotoSize) for x in photo]):
                    pass
                else:
                    raise BadMessageException(
                        "photo must either be True or list(telegram.PhotoSize)"
                    )
            elif isinstance(photo, bool):
                photo = self._get_photosize()
            else:
                raise BadMessageException(
                    "photo must either be True or list(telegram.PhotoSize)")
        if location:
            if isinstance(location, Location):
                pass
            elif isinstance(location, dict):
                location = Location(**location)
            elif isinstance(location, bool):
                location = self._get_location()
            else:
                raise BadMessageException(
                    "location must either be True or telegram.Location")
        if venue:
            if isinstance(venue, Venue):
                pass
            elif isinstance(venue, bool):
                venue = self._get_venue()
            elif isinstance(venue, dict):
                venue['location'] = Location(**venue)
                venue = Venue(**venue)
            else:
                raise BadMessageException(
                    "venue must either be True or telegram.Venue")
        if contact:
            if isinstance(contact, Contact):
                pass
            elif isinstance(contact, dict):
                contact = Contact(**contact)
            elif isinstance(contact, bool):
                contact = self._get_contact(user)
            else:
                raise BadMessageException(
                    "contact must either be True or telegram.Contact")
        if voice:
            if isinstance(voice, Voice):
                pass
            elif isinstance(voice, bool):
                voice = self._get_voice()
            elif isinstance(voice, dict):
                voice = Voice(**voice)
            else:
                raise BadMessageException(
                    "voice must either be True or telegram.Voice")
        if video:
            if isinstance(video, Video):
                pass
            elif isinstance(video, bool):
                video = self._get_video()
            elif isinstance(video, dict):
                video = self._get_video(data=video)
            else:
                raise BadMessageException(
                    "video must either be True or telegram.Video")
        if sticker:
            if isinstance(sticker, Sticker):
                pass
            elif isinstance(sticker, bool):
                sticker = self._get_sticker()
            elif isinstance(sticker, dict):
                sticker = self._get_sticker(sticker)
            else:
                raise BadMessageException(
                    "sticker must either be True or telegram.Sticker")
        if document:
            if isinstance(document, Document):
                pass
            elif isinstance(document, dict):
                document = Document(**document)
            elif isinstance(document, bool):
                document = self._get_document()
            else:
                raise BadMessageException(
                    "document must either be True or telegram.Document")
        if audio:
            if isinstance(audio, Audio):
                pass
            elif isinstance(audio, bool):
                audio = self._get_audio()
            elif isinstance(audio, dict):
                audio = Audio(**audio)
            else:
                raise BadMessageException(
                    "audio must either be True or telegram.Audio")
        return audio, contact, document, location, photo, sticker, venue, video, voice

    def _handle_forward(self, forward_date, forward_from, forward_from_chat,
                        forward_from_message_id):
        if forward_from and not isinstance(forward_from, User):
            raise BadUserException()
        if forward_from_chat:
            if not isinstance(forward_from_chat, Chat):
                raise BadChatException
            if forward_from_chat.type != "channel":
                raise BadChatException(
                    'forward_from_chat must be of type "channel"')
            if not forward_from:
                forward_from = UserGenerator().get_user()
        if forward_from and not isinstance(forward_date, int):
            if not isinstance(forward_date, datetime.datetime):
                now = datetime.datetime.now()
            else:
                now = forward_date
            try:
                # Python 3.3+
                forward_date = int(now.timestamp())
            except AttributeError:
                # Python 3 (< 3.3) and Python 2
                forward_date = int(time.mktime(now.timetuple()))
        if (forward_from_message_id
                and not isinstance(forward_from_message_id, int)) or (
                    forward_from_chat and not forward_from_message_id):
            forward_from_message_id = next(self.idgen)
        return forward_date, forward_from, forward_from_message_id

    def _handle_status(self, channel_chat_created, chat, delete_chat_photo,
                       group_chat_created, left_chat_member,
                       migrate_from_chat_id, migrate_to_chat_id,
                       new_chat_members, new_chat_photo, new_chat_title,
                       pinned_message, supergroup_chat_created):
        status_messages = [
            new_chat_members, left_chat_member, new_chat_title, new_chat_photo,
            delete_chat_photo, group_chat_created, supergroup_chat_created,
            channel_chat_created, migrate_to_chat_id, migrate_from_chat_id,
            pinned_message
        ]
        if len([x for x in status_messages if x]) > 1:
            raise BadMessageException(
                "Limit to only one status message per message")
        if new_chat_members:
            if chat.type == "private":
                raise BadChatException("Can not add members to private chat")
            for new_chat_member in new_chat_members:
                if not isinstance(new_chat_member, User):
                    raise BadUserException
        if left_chat_member:
            if not isinstance(left_chat_member, User):
                raise BadUserException
            if chat.type == "private":
                raise BadChatException("People can not leave a private chat")
        if new_chat_title:
            if chat.type == "private":
                raise BadChatException("Can not change title of private chat")
            chat.title = new_chat_title
        if new_chat_photo:
            if chat.type == "private":
                raise BadChatException(
                    "Can't change the photo for a private chat a private chat")
            if isinstance(new_chat_photo, list):
                if all([isinstance(x, PhotoSize) for x in new_chat_photo]):
                    pass
                else:
                    raise BadMessageException(
                        "new_cgat_photo must either be True or list(telegram.PhotoSize)"
                    )
            elif isinstance(new_chat_photo, bool) and new_chat_photo:
                new_chat_photo = self._get_photosize()
            else:
                raise BadMessageException(
                    "new_cgat_photo must either be True or list(telegram.PhotoSize)"
                )
        if pinned_message:
            if not isinstance(pinned_message, Message):
                raise BadMessageException
            elif chat.type != "supergroup":
                raise BadChatException(
                    "Messages can only be pinned in supergroups")
            else:
                pinned_message.reply_to_message = None
        return new_chat_photo

    def _get_user_and_chat(self, user, chat, private):
        if chat:
            if not isinstance(chat, Chat):
                raise BadChatException
            if chat.type == "channel":
                raise BadChatException(
                    "Use get_channel_post to get channel updates.")
        if user:
            if not isinstance(user, User):
                raise BadUserException
        if chat:
            if not user:
                if chat.type == "private":
                    user = self.ug.get_user(first_name=chat.first_name,
                                            last_name=chat.last_name,
                                            username=chat.username,
                                            id=chat.id)
                else:
                    user = self.ug.get_user()
        elif user and private:
            chat = self.cg.get_chat(user=user)
        elif user:
            chat = self.cg.get_chat(chat_type="group")
        elif private:
            user = self.ug.get_user()
            chat = self.cg.get_chat(user=user)
        else:
            user = self.ug.get_user()
            chat = self.cg.get_chat(chat_type="group")
        return user, chat

    def _handle_text(self, text, parse_mode):
        if text and parse_mode:
            if parse_mode not in ["HTML", "Markdown"]:
                raise BadMarkupException(
                    'Mardown mode must be HTML or Markdown')
            elif parse_mode == "HTML":
                text, entities = EntityParser.parse_html(text)
            else:
                text, entities = EntityParser.parse_markdown(text)
        else:
            entities = []
        return text, entities

    def _get_photosize(self):
        tmp = []
        import uuid
        from random import randint
        for _ in range(2):
            w, h = randint(40, 400), randint(40, 400)
            s = w * h * 0.3
            tmp.append(
                PhotoSize(str(uuid.uuid4()),
                          str(uuid.uuid4()),
                          w,
                          h,
                          file_size=s))
        return tmp

    def _get_location(self):
        from random import uniform
        return Location(uniform(-180.0, 180.0), uniform(-90.0, 90.0))

    def _get_venue(self):
        loc = self._get_location()
        address = "somewherestreet 23"
        name = "Awesome place"
        return Venue(loc, name, address)

    def _get_contact(self, user):
        return Contact("06123456789", user.first_name)

    def _get_voice(self):
        import uuid
        from random import randint
        return Voice(str(uuid.uuid4()), str(uuid.uuid4()), randint(1, 120))

    def _get_video(self, data=None):
        import uuid
        from random import randint
        if data:
            data['width'] = randint(40, 400)
            data['height'] = randint(40, 400)
            return Video(**data)
        return Video(str(uuid.uuid4()), str(uuid.uuid4()), randint(40, 400),
                     randint(40, 400), randint(2, 300))

    def _get_sticker(self, data=None):
        import uuid
        from random import randint
        if data:
            data['width'] = randint(20, 200)
            data['height'] = randint(20, 200)
            return Sticker(**data)
        return Sticker(str(uuid.uuid4()), str(uuid.uuid4()), randint(20, 200),
                       randint(20, 200), False, False)

    def _get_document(self):
        import uuid
        return Document(str(uuid.uuid4()),
                        str(uuid.uuid4()),
                        file_name="somedoc.pdf")

    def _get_audio(self):
        import uuid
        from random import randint
        return Audio(str(uuid.uuid4()),
                     str(uuid.uuid4()),
                     randint(1, 120),
                     title="Some song")
