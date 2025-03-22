# A library that provides a testing suite fot python-telegram-bot
# which can be found on https://github.com/python-telegram-bot/python-telegram-bot
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
"""This module provides a class for a Mockbot"""

import functools
import logging
import warnings

import time

from telegram import (Location, TelegramObject, User)
from telegram.error import TelegramError

from utils.deprecation import deprecated, reason

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Mockbot(TelegramObject):
    """
    The Mockbot is a fake telegram-bot that does not require a token or a connection to Telegram's
    servers. It's used to mimmick all methods of a ``python-telegram-bot`` instance, without a single network connection.
    All methods described in :py:class:`telegram.Bot` are functional and here are described only
    the special methods added for testing functionality.


    Parameters:
        username (Optional[str]): Username for this bot. Defaults to 'MockBot'.
    """
    def __init__(self, username="MockBot", **kwargs):
        self._updates = []
        self._bot = None
        self._username = username
        self._sendmessages = []
        from .messagegenerator import MessageGenerator
        from .chatgenerator import ChatGenerator
        self._mg = MessageGenerator(bot=self)
        self._cg = ChatGenerator()

    @property
    def sent_messages(self):
        """
        A list of every message sent with this bot.

        It contains the data dict usually passed to the methods that actually send data to Telegram, with an added field
        named ``method`` which will contain the method used to send this message to the server.

        Examples:
            A call to

            ``send_message(1, "hello")``

            will return the following

            ``{'text': 'hello', 'chat_id': 1, 'method': 'send_message'}``

            A call to

            ``edit_message_text(text="test 2", inline_message_id=404, disable_web_page_preview=True)``::

            results in

            ``{'inline_message_id': 404, 'text': 'test 2', 'method': 'edit_message_text', 'disable_web_page_preview': True}``
        """
        return self._sendmessages

    @property
    def updates(self):
        """Contains a list of updates received by the bot."""
        tmp = self._updates
        self._updates = []
        return tmp

    def reset(self):
        """
        Resets the ``sent_messages`` property to an empty list.
        """
        self._sendmessages = []

    def info(func):
        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            if not self._bot:
                self.get_me()

            result = func(self, *args, **kwargs)
            return result

        return decorator

    @property
    @info
    def id(self):
        """Return the bot's ID."""
        return self._bot.id

    @property
    @info
    def first_name(self):
        """Return the bot's first name as a string."""
        return self._bot.first_name

    @property
    @info
    def last_name(self):
        """Return the bot's last name as a string."""
        return self._bot.last_name

    @property
    @info
    def username(self):
        """Return the bot's username as a string."""
        return self._bot.username

    @property
    def name(self):
        """Return the username handle as a string."""
        return '@{0}'.format(self.username)

    def message(func):
        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            data = func(self, *args, **kwargs)

            if kwargs.get('reply_to_message_id'):
                data['reply_to_message_id'] = kwargs.get('reply_to_message_id')

            if kwargs.get('disable_notification'):
                data['disable_notification'] = kwargs.get(
                    'disable_notification')

            if kwargs.get('reply_markup'):
                reply_markup = kwargs.get('reply_markup')
                if isinstance(reply_markup, TelegramObject):
                    data['reply_markup'] = reply_markup.to_json()
                else:
                    data['reply_markup'] = reply_markup
            data['method'] = func.__name__
            self._sendmessages.append(data)
            if data['method'] in ['send_chat_action']:
                return True
            dat = kwargs.copy()
            dat.update(data)
            del (dat['method'])
            dat.pop('disable_web_page_preview', "")
            dat.pop('disable_notification', "")
            dat.pop('reply_markup', "")
            dat['user'] = self.get_me()
            cid = dat.pop('chat_id', None)
            if cid:
                dat['chat'] = self._cg.get_chat(id=cid)
            else:
                dat['chat'] = None
            mid = dat.pop('reply_to_message_id', None)
            if mid:
                dat['reply_to_message'] = self._mg.get_message(
                    id=mid, chat=dat['chat']).message
            #dat['forward_from_message_id'] = dat.pop('message_id', None)
            cid = dat.pop('from_chat_id', None)
            if cid:
                dat['forward_from_chat'] = self._cg.get_chat(
                    id=cid, type='channel')
            dat.pop('inline_message_id', None)
            dat.pop('performer', '')
            dat.pop('title', '')
            dat.pop('duration', '')
            dat.pop('duration', '')
            dat.pop('phone_number', '')
            dat.pop('first_name', '')
            dat.pop('last_name', '')
            dat.pop('filename', '')
            dat.pop('latitude', '')
            dat.pop('longitude', '')
            dat.pop('foursquare_id', '')
            dat.pop('address', '')
            dat.pop('game_short_name', '')
            dat['document'] = dat.pop('document2', None)
            dat['audio'] = dat.pop('audio2', None)
            dat['voice'] = dat.pop('voice2', None)
            dat['video'] = dat.pop('video2', None)
            dat['sticker'] = dat.pop('sticker2', None)
            phot = dat.pop('photo', None)
            if phot:
                dat['photo'] = True
            return self._mg.get_message(**dat).message

        return decorator

    @deprecated(reason["PEP8"])
    def getMe(self, *args, **kwargs):
        return self.get_me(args, kwargs)

    def get_me(self, timeout=None, **kwargs):
        """Return a bot, a ``telegram.User`` instance.

        Arguments:
            id ([int]): The ID for the bot.
            first_name ([str]): The first name of the user or bot.
            is_bot ([bool]): True if the user is a bot.
            last_name ([str]): The last name of the user or bot.
            username ([str]): The username of the user or bot.

        Returns:
            :class:`telegram.User`: An user or a bot with the supplied arguments.
        """
        self._bot = User(0, "Mockbot", True, last_name="Bot", username=self._username)
        return self._bot

    @deprecated(reason["PEP8"])
    def sendMessage(self, *args, **kwargs):
        return self.send_message(args, kwargs)

    @message
    def send_message(self,
                    chat_id,
                    text,
                    parse_mode=None,
                    disable_web_page_preview=None,
                    disable_notification=False,
                    reply_to_message_id=None,
                    reply_markup=None,
                    timeout=None,
                    **kwargs):
        data = {'chat_id': chat_id, 'text': text}

        if parse_mode:
            data['parse_mode'] = parse_mode
        if disable_web_page_preview:
            data['disable_web_page_preview'] = disable_web_page_preview

        return data

    @deprecated(reason["PEP8"])
    def forwardMessage(self, *args, **kwargs):
        return self.forward_message(args, kwargs)

    @message
    def forward_message(self,
                       chat_id,
                       from_chat_id,
                       message_id,
                       disable_notification=False,
                       timeout=None,
                       **kwargs):
        data = {}

        if chat_id:
            data['chat_id'] = chat_id
        if from_chat_id:
            data['from_chat_id'] = from_chat_id
        if message_id:
            data['message_id'] = message_id

        return data

    @deprecated(reason["PEP8"])
    def sendPhoto(self, *args, **kwargs):
        return self.send_photo(args, kwargs)

    @message
    def send_photo(self,
                  chat_id,
                  photo,
                  caption=None,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        data = {'chat_id': chat_id, 'photo': photo}

        if caption:
            data['caption'] = caption

        return data

    @deprecated(reason["PEP8"])
    def sendAudio(self, *args, **kwargs):
        return self.send_audio(args, kwargs)

    @message
    def send_audio(self,
                  chat_id,
                  unique_id,
                  audio_unique_id,
                  duration=None,
                  performer=None,
                  title=None,
                  caption=None,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        data = {'chat_id': chat_id, 'audio': unique_id}
        data['audio2'] = {'file_id': unique_id, 'file_unique_id': audio_unique_id}
        if duration:
            data['duration'] = duration
            data['audio2']['duration'] = duration
        if performer:
            data['performer'] = performer
            data['audio2']['performer'] = performer
        if title:
            data['title'] = title
            data['audio2']['title'] = title
        if caption:
            data['caption'] = caption
            data['caption'] = caption

        print(data)

        return data

    @deprecated(reason["PEP8"])
    def sendDocument(self, *args, **kwargs):
        return self.send_document(args, kwargs)

    @message
    def send_document(self,
                     chat_id,
                     document,
                     document_unique_id,
                     filename=None,
                     caption=None,
                     disable_notification=False,
                     reply_to_message_id=None,
                     reply_markup=None,
                     timeout=None,
                     **kwargs):
        data = {
            'chat_id': chat_id,
            'document': document,
            'document2': {
                'file_id': document,
                'file_unique_id': document_unique_id
            }
        }
        if filename:
            data['filename'] = filename
            data['document2']['file_name'] = filename
        if caption:
            data['caption'] = caption

        return data

    @deprecated(reason["PEP8"])
    def sendSticker(self, *args, **kwargs):
        return self.send_sticker(args, kwargs)

    @message
    def send_sticker(self,
                    chat_id,
                    sticker,
                    sticker_unique_id,
                    width,
                    height,
                    is_animated,
                    is_video,
                    sticker_type,
                    disable_notification=False,
                    reply_to_message_id=None,
                    reply_markup=None,
                    timeout=None,
                    **kwargs):
        data = {
            'chat_id': chat_id,
            'sticker': sticker,
            'sticker2': {
                'file_id': sticker,
                'file_unique_id': sticker_unique_id,
                'width': width,
                'height': height,
                'is_animated': is_animated,
                'is_video': is_video,
                'type': sticker_type
            }
        }

        return data

    @deprecated(reason["PEP8"])
    def sendVideo(self, *args, **kwargs):
        return self.send_video(args, kwargs)

    @message
    def send_video(self,
                  chat_id,
                  video,
                  video_unique_id,
                  width,
                  height,
                  duration,
                  caption=None,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        data = {
            'chat_id': chat_id,
            'video': video,
            'video2': {
                'file_id': video,
                'file_unique_id': video_unique_id,
                'width': width,
                'height': height,
                'duration': duration
            }
        }

        if caption:
            data['caption'] = caption

        return data

    @deprecated(reason["PEP8"])
    def sendVoice(self, *args, **kwargs):
        return self.send_voice(args, kwargs)

    @message
    def send_voice(self,
                  chat_id,
                  voice,
                  voice_unique_id,
                  duration=None,
                  caption=None,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        data = {
            'chat_id': chat_id,
            'voice': voice,
            'voice2': {
                'file_id': voice,
                'file_unique_id': voice_unique_id
            }
        }

        if duration:
            data['duration'] = duration
            data['voice2']['duration'] = duration
        if caption:
            data['caption'] = caption

        return data

    @deprecated(reason["PEP8"])
    def sendLocation(self, *args, **kwargs):
        return self.send_location(args, kwargs)

    @message
    def send_location(self,
                     chat_id,
                     latitude,
                     longitude,
                     disable_notification=False,
                     reply_to_message_id=None,
                     reply_markup=None,
                     timeout=None,
                     **kwargs):
        data = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            'location': {
                'latitude': latitude,
                'longitude': longitude
            }
        }

        return data

    @deprecated(reason["PEP8"])
    def sendVenue(self, *args, **kwargs):
        return self.send_venue(args, kwargs)

    @message
    def send_venue(self,
                  chat_id,
                  latitude,
                  longitude,
                  title,
                  address,
                  foursquare_id=None,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        loc = Location(longitude, latitude)
        data = {
            'chat_id': chat_id,
            'venue': {
                'location': loc,
                'address': address,
                'title': title
            }
        }

        if foursquare_id:
            data['foursquare_id'] = foursquare_id
            data['venue']['foursquare_id'] = foursquare_id

        return data

    @deprecated(reason["PEP8"])
    def sendContact(self, *args, **kwargs):
        return self.send_contact(args, kwargs)

    @message
    def send_contact(self,
                    chat_id,
                    phone_number,
                    first_name,
                    last_name=None,
                    disable_notification=False,
                    reply_to_message_id=None,
                    reply_markup=None,
                    timeout=None,
                    **kwargs):
        data = {
            'chat_id': chat_id,
            'phone_number': phone_number,
            'first_name': first_name,
            'contact': {
                'phone_number': phone_number,
                'first_name': first_name
            }
        }

        if last_name:
            data['last_name'] = last_name
            data['contact']['last_name'] = last_name

        return data

    @deprecated(reason["PEP8"])
    def sendGame(self, *args, **kwargs):
        return self.send_game(args, kwargs)

    @message
    def send_game(self, chat_id, game_short_name, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'game_short_name': game_short_name}

        return data

    @deprecated(reason["PEP8"])
    def sendChatAction(self, *args, **kwargs):
        return self.send_chat_action(args, kwargs)

    @message
    def send_chat_action(self, chat_id, action, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'action': action}

        return data

    @deprecated(reason["PEP8"])
    def answerInlineQuery(self, *args, **kwargs):
        return self.answer_inline_query(args, kwargs)

    def answer_inline_query(self,
                          inline_query_id,
                          results,
                          cache_time=300,
                          is_personal=None,
                          next_offset=None,
                          switch_pm_text=None,
                          switch_pm_parameter=None,
                          timeout=None,
                          **kwargs):
        results = [res.to_dict() for res in results]

        data = {'inline_query_id': inline_query_id, 'results': results}

        if cache_time or cache_time == 0:
            data['cache_time'] = cache_time
        if is_personal:
            data['is_personal'] = is_personal
        if next_offset is not None:
            data['next_offset'] = next_offset
        if switch_pm_text:
            data['switch_pm_text'] = switch_pm_text
        if switch_pm_parameter:
            data['switch_pm_parameter'] = switch_pm_parameter
        data['method'] = "answer_inline_query"

        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def getUserProfilePhotos(self, *args, **kwargs):
        return self.get_user_profile_photos(args, kwargs)

    def get_user_profile_photos(self,
                             user_id,
                             offset=None,
                             limit=100,
                             timeout=None,
                             **kwargs):
        data = {'user_id': user_id}

        if offset:
            data['offset'] = offset
        if limit:
            data['limit'] = limit

        data['method'] = "get_user_profile_photos"

        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def getFile(self, *args, **kwargs):
        return self.get_file(args, kwargs)

    def get_file(self, file_id, timeout=None, **kwargs):
        data = {'file_id': file_id}

        data['method'] = "get_file"
        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def kickChatMember(self, *args, **kwargs):
        return self.kick_chat_member(args, kwargs)

    def kick_chat_member(self, chat_id, user_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'user_id': user_id}

        data['method'] = "kick_chat_member"

        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def unbanChatMember(self, *args, **kwargs):
        return self.unban_chat_member(args, kwargs)

    def unban_chat_member(self, chat_id, user_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'user_id': user_id}

        data['method'] = "unban_chat_member"

        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def answerCallbackQuery(self, *args, **kwargs):
        return self.answer_callback_query(args, kwargs)

    def answer_callback_query(self,
                            callback_query_id,
                            text=None,
                            show_alert=False,
                            url=None,
                            cache_time=None,
                            timeout=None,
                            **kwargs):
        data = {'callback_query_id': callback_query_id}

        if text:
            data['text'] = text
        if show_alert:
            data['show_alert'] = show_alert
        if url:
            data['url'] = url
        if cache_time is not None:
            data['cache_time'] = cache_time

        data['method'] = "answer_callback_query"

        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def editMessageText(self, *args, **kwargs):
        return self.edit_message_text(args, kwargs)

    @message
    def edit_message_text(self,
                        text,
                        chat_id=None,
                        message_id=None,
                        inline_message_id=None,
                        parse_mode=None,
                        disable_web_page_preview=None,
                        reply_markup=None,
                        timeout=None,
                        **kwargs):
        data = {'text': text}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id
        if parse_mode:
            data['parse_mode'] = parse_mode
        if disable_web_page_preview:
            data['disable_web_page_preview'] = disable_web_page_preview

        return data

    @deprecated(reason["PEP8"])
    def editMessageCaption(self, *args, **kwargs):
        return self.edit_message_caption(args, kwargs)

    @message
    def edit_message_caption(self,
                           chat_id=None,
                           message_id=None,
                           inline_message_id=None,
                           caption=None,
                           reply_markup=None,
                           timeout=None,
                           **kwargs):
        if inline_message_id is None and (chat_id is None or
                                          message_id is None):
            raise TelegramError(
                'edit_message_caption: Both chat_id and message_id are required when '
                'inline_message_id is not specified')

        data = {}

        if caption:
            data['caption'] = caption
        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return data

    @deprecated(reason["PEP8"])
    def editMessageReplyMarkup(self, *args, **kwargs):
        return self.edit_message_markup(args, kwargs)

    @message
    def edit_message_reply_markup(self,
                               chat_id=None,
                               message_id=None,
                               inline_message_id=None,
                               reply_markup=None,
                               timeout=None,
                               **kwargs):
        if inline_message_id is None and (chat_id is None or
                                          message_id is None):
            raise TelegramError(
                'edit_message_caption: Both chat_id and message_id are required when '
                'inline_message_id is not specified')

        data = {}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return data

    @deprecated(reason["PEP8"])
    def insertUpdate(self, *args, **kwargs):
        return self.insert_update(args, kwargs)

    def insert_update(self, update):
        """
        Inserts an update into the bot's storage. These will be retrieved on a call to
        ``get_updates`` which is used by the :py:class:`telegram.Updater`. This way the updater can function without any
        modifications.

        Args:
            update (telegram.Update): The update to insert in the queue.
        """
        self._updates.append(update)
        time.sleep(.3)

    @deprecated(reason["PEP8"])
    def getUpdates(self, *args, **kwargs):
        return self.get_updates(args, kwargs)

    def get_updates(self,
                   offset=None,
                   limit=100,
                   timeout=0,
                   network_delay=None,
                   read_latency=2.,
                   **kwargs):
        """Retrieve the updates contained in the bot's storage."""
        return self.updates

    @deprecated(reason["PEP8"])
    def setWebhook(self, *args, **kwargs):
        return self.set_webhook(args, kwargs)

    def set_webhook(self,
                   webhook_url=None,
                   certificate=None,
                   timeout=None,
                   **kwargs):
        return None

    @deprecated(reason["PEP8"])
    def leaveChat(self, *args, **kwargs):
        return self.leave_chat(args, kwargs)

    def leave_chat(self, chat_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id}

        data['method'] = "leave_chat"

        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def getChat(self, *args, **kwargs):
        return self.get_chat(args, kwargs)

    def get_chat(self, chat_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id}

        data['method'] = "get_chat"

        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def getChatAdministrators(self, *args, **kwargs):
        return self.get_chat_administrators(args, kwargs)

    def get_chat_administrators(self, chat_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id}

        data['method'] = "get_chat_administrators"

        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def getChatMembersCount(self, *args, **kwargs):
        return self.get_chat_members_count(args, kwargs)

    def get_chat_members_count(self, chat_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id}

        data['method'] = "get_chat_members_count"

        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def getChatMember(self, *args, **kwargs):
        return self.get_chat_member(args, kwargs)

    def get_chat_member(self, chat_id, user_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'user_id': user_id}

        data['method'] = "get_chat_member"

        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def setGameScore(self, *args, **kwargs):
        return self.set_game_score(args, kwargs)

    def set_game_score(self,
                     user_id,
                     score,
                     chat_id=None,
                     message_id=None,
                     inline_message_id=None,
                     edit_message=None,
                     force=None,
                     disable_edit_message=None,
                     timeout=None,
                     **kwargs):
        data = {'user_id': user_id, 'score': score}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id
        if force is not None:
            data['force'] = force
        if disable_edit_message is not None:
            data['disable_edit_message'] = disable_edit_message
        if edit_message is not None:
            warnings.warn(
                'edit_message is deprecated, use disable_edit_message instead')
            if disable_edit_message is None:
                data['edit_message'] = edit_message
            else:
                warnings.warn(
                    'edit_message is ignored when disable_edit_message is used')

        data['method'] = "set_game_score"
        self._sendmessages.append(data)

    @deprecated(reason["PEP8"])
    def getGameHighScore(self, *args, **kwargs):
        return self.get_game_high_score(args, kwargs)

    def get_game_high_score(self,
                          user_id,
                          chat_id=None,
                          message_id=None,
                          inline_message_id=None,
                          timeout=None,
                          **kwargs):
        data = {'user_id': user_id}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        data['method'] = "get_game_high_score"

        self._sendmessages.append(data)

    @staticmethod
    def de_json(data, bot):
        data = super(Mockbot, Mockbot).de_json(data, bot)

        return Mockbot(**data)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'first_name': self.username
        }

        if self.last_name:
            data['last_name'] = self.last_name

        return data

