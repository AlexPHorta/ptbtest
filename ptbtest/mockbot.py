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
"""This module provides a class for a Mockbot"""

import functools
import logging

import time

from telegram import (User, TelegramObject)
from telegram.utils.request import Request
from telegram.ext import Defaults
from telegram.replymarkup import ReplyMarkup
from telegram.error import TelegramError

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Mockbot(TelegramObject):
    """
    The Mockbot is a fake telegram-bot that does not require a token or a connection to the telegram
    servers. It's used to mimmick all methods of python-telegram-bot instance, but never contact the telegram servers.
    All methods as described in :py:class:`telegram.Bot` are functional and described here are only
    the special methods added for testing functionality



    Attributes:
        sent_messages ([dict<sent message>]): A list of every message sent with this bot.

    It will contain
    the data dict usually passed to the methods actually sending data to telegram. With an added field
    named ``method`` which will contain the method used to send this message to the server.

    Examples:
        A call to ``sendMessage(1, "hello")`` will return the following::

        {'text': 'hello', 'chat_id': 1, 'method': 'sendMessage'}

        A call to ``editMessageText(text="test 2", inline_message_id=404, disable_web_page_preview=True)``::

        {'inline_message_id': 404, 'text': 'test 2', 'method': 'editMessageText', 'disable_web_page_preview': True}
    Parameters:
        username (Optional[str]): Username for this bot. Defaults to 'MockBot'"""

    __slots__ = ("_updates", "bot", "_username", "_sendmessages", "mg", "cg",
                 "request", "defaults", "_counter")

    def __init__(self, username="MockBot", **kwargs):
        self._updates = []
        self.bot = None
        self._username = username
        self._sendmessages = []
        from .messagegenerator import MessageGenerator
        from .chatgenerator import ChatGenerator
        self.mg = MessageGenerator(bot=self)
        self.cg = ChatGenerator()
        self.request = Request()
        self.defaults = Defaults()
        self._counter = 0

    @property
    def sent_messages(self):
        return self._sendmessages

    @property
    def updates(self):
        self._counter = self._counter + 1
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
            if not self.bot:
                self.getMe()

            result = func(self, *args, **kwargs)
            return result

        return decorator

    @property
    @info
    def id(self):
        return self.bot.id

    @property
    @info
    def first_name(self):
        return self.bot.first_name

    @property
    @info
    def last_name(self):
        return self.bot.last_name

    @property
    @info
    def username(self):
        return self.bot.username

    @property
    def name(self):
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
                if isinstance(reply_markup, ReplyMarkup):
                    data['reply_markup'] = reply_markup.to_json()
                else:
                    data['reply_markup'] = reply_markup
            data['method'] = func.__name__
            self._sendmessages.append(data)
            if data['method'] in ['sendChatAction']:
                return True
            dat = kwargs.copy()
            dat.update(data)
            del (dat['method'])
            dat.pop('disable_web_page_preview', "")
            dat.pop('disable_notification', "")
            dat.pop('reply_markup', "")
            dat['user'] = self.getMe()
            cid = dat.pop('chat_id', None)
            if cid:
                dat['chat'] = self.cg.get_chat(cid=cid)
            else:
                dat['chat'] = None
            mid = dat.pop('reply_to_message_id', None)
            if mid:
                dat['reply_to_message'] = self.mg.get_message(
                    id=mid, chat=dat['chat']).message
            dat['forward_from_message_id'] = dat.pop('message_id', None)
            cid = dat.pop('from_chat_id', None)
            if cid:
                dat['forward_from_chat'] = self.cg.get_chat(
                    cid=cid, chat_type='channel')
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
            return self.mg.get_message(**dat).message

        return decorator

    def getMe(self, timeout=None, **kwargs):
        self.bot = User(0,
                        "Mockbot",
                        is_bot=True,
                        last_name="Bot",
                        username=self._username)
        return self.bot

    @message
    def sendMessage(self,
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

    @message
    def forwardMessage(self,
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

    @message
    def sendPhoto(self,
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

    @message
    def sendAudio(self,
                  chat_id,
                  audio,
                  duration=None,
                  performer=None,
                  title=None,
                  caption=None,
                  disable_notification=False,
                  reply_to_message_id=None,
                  reply_markup=None,
                  timeout=None,
                  **kwargs):
        data = {'chat_id': chat_id, 'audio': audio}
        data['audio2'] = {'file_id': audio, 'file_unique_id': audio}
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

        return data

    @message
    def sendDocument(self,
                     chat_id,
                     document,
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
                'file_unique_id': document
            }
        }
        if filename:
            data['filename'] = filename
            data['document2']['file_name'] = filename
        if caption:
            data['caption'] = caption

        return data

    @message
    def sendSticker(self,
                    chat_id,
                    sticker,
                    is_animated,
                    is_video,
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
                'file_unique_id': sticker,
                'is_animated': is_animated,
                'is_video': is_video
            }
        }

        return data

    @message
    def sendVideo(self,
                  chat_id,
                  video,
                  duration=None,
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
                'file_unique_id': video
            }
        }

        if duration:
            data['duration'] = duration
            data['video2']['duration'] = duration
        if caption:
            data['caption'] = caption

        return data

    @message
    def sendVoice(self,
                  chat_id,
                  voice,
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
                'file_unique_id': voice
            }
        }

        if duration:
            data['duration'] = duration
            data['voice2']['duration'] = duration
        if caption:
            data['caption'] = caption

        return data

    @message
    def sendLocation(self,
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

    @message
    def sendVenue(self,
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
        data = {
            'chat_id': chat_id,
            'latitude': latitude,
            'longitude': longitude,
            'address': address,
            'title': title,
            'venue': {
                'latitude': latitude,
                'longitude': longitude,
                'address': address,
                'title': title
            }
        }

        if foursquare_id:
            data['foursquare_id'] = foursquare_id
            data['venue']['foursquare_id'] = foursquare_id

        return data

    @message
    def sendContact(self,
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

    @message
    def sendGame(self, chat_id, game_short_name, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'game_short_name': game_short_name}

        return data

    @message
    def sendChatAction(self, chat_id, action, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'action': action}

        return data

    def answerInlineQuery(self,
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
        data['method'] = "answerInlineQuery"

        self._sendmessages.append(data)

    def getUserProfilePhotos(self,
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

        data['method'] = "getUserProfilePhotos"

        self._sendmessages.append(data)

    def getFile(self, file_id, timeout=None, **kwargs):
        data = {'file_id': file_id}

        data['method'] = "getFile"
        self._sendmessages.append(data)

    def kickChatMember(self, chat_id, user_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'user_id': user_id}

        data['method'] = "kickChatMember"

        self._sendmessages.append(data)

    def unbanChatMember(self, chat_id, user_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'user_id': user_id}

        data['method'] = "unbanChatMember"

        self._sendmessages.append(data)

    def answerCallbackQuery(self,
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

        data['method'] = "answerCallbackQuery"

        self._sendmessages.append(data)

    @message
    def editMessageText(self,
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

    @message
    def editMessageCaption(self,
                           chat_id=None,
                           message_id=None,
                           inline_message_id=None,
                           caption=None,
                           reply_markup=None,
                           timeout=None,
                           **kwargs):
        if inline_message_id is None and (chat_id is None
                                          or message_id is None):
            raise TelegramError(
                'editMessageCaption: Both chat_id and message_id are required when '
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

    @message
    def editMessageReplyMarkup(self,
                               chat_id=None,
                               message_id=None,
                               inline_message_id=None,
                               reply_markup=None,
                               timeout=None,
                               **kwargs):
        if inline_message_id is None and (chat_id is None
                                          or message_id is None):
            raise TelegramError(
                'editMessageCaption: Both chat_id and message_id are required when '
                'inline_message_id is not specified')

        data = {}

        if chat_id:
            data['chat_id'] = chat_id
        if message_id:
            data['message_id'] = message_id
        if inline_message_id:
            data['inline_message_id'] = inline_message_id

        return data

    def insertUpdate(self, update):
        """
        This inserts an update into the the bot's storage. these will be retreived on a call to
        getUpdates which is used by the :py:class:`telegram.Updater`. This way the updater can function without any
        modifications.

        Args:
            update (telegram.Update): The update to insert in the queue.
        """
        self._updates.append(update)
        time.sleep(.3)

    def getUpdates(self,
                   offset=None,
                   limit=100,
                   timeout=0,
                   network_delay=None,
                   read_latency=2.,
                   **kwargs):
        return self.updates

    def setWebhook(self,
                   webhook_url=None,
                   certificate=None,
                   timeout=None,
                   **kwargs):
        return None

    def delete_webhook(self, timeout=None, **kwargs):
        return None

    def leaveChat(self, chat_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id}

        data['method'] = "leaveChat"

        self._sendmessages.append(data)

    def getChat(self, chat_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id}

        data['method'] = "getChat"

        self._sendmessages.append(data)

    def getChatAdministrators(self, chat_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id}

        data['method'] = "getChatAdministrators"

        self._sendmessages.append(data)

    def getChatMembersCount(self, chat_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id}

        data['method'] = "getChatMembersCount"

        self._sendmessages.append(data)

    def getChatMember(self, chat_id, user_id, timeout=None, **kwargs):
        data = {'chat_id': chat_id, 'user_id': user_id}

        data['method'] = "getChatMember"

        self._sendmessages.append(data)

    def setGameScore(self,
                     user_id,
                     score,
                     chat_id=None,
                     message_id=None,
                     inline_message_id=None,
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

        data['method'] = "setGameScore"
        self._sendmessages.append(data)

    def getGameHighScores(self,
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

        data['method'] = "getGameHighScores"

        self._sendmessages.append(data)

    @staticmethod
    def de_json(data, bot):
        data = super(Mockbot, Mockbot).de_json(data, bot)

        return Mockbot(**data.__dict__)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'first_name': self.username
        }

        if self.last_name:
            data['last_name'] = self.last_name

        return data

    # snake_case (PEP8) aliases

    get_me = getMe
    send_message = sendMessage
    forward_message = forwardMessage
    send_photo = sendPhoto
    send_audio = sendAudio
    send_document = sendDocument
    send_sticker = sendSticker
    send_video = sendVideo
    send_voice = sendVoice
    send_location = sendLocation
    send_venue = sendVenue
    send_contact = sendContact
    send_game = sendGame
    send_chat_action = sendChatAction
    answer_inline_query = answerInlineQuery
    get_user_profile_photos = getUserProfilePhotos
    get_file = getFile
    kick_chat_member = kickChatMember
    unban_chat_member = unbanChatMember
    answer_callback_query = answerCallbackQuery
    edit_message_text = editMessageText
    edit_message_caption = editMessageCaption
    edit_message_reply_markup = editMessageReplyMarkup
    get_updates = getUpdates
    set_webhook = setWebhook
    leave_chat = leaveChat
    get_chat = getChat
    get_chat_administrators = getChatAdministrators
    get_chat_member = getChatMember
    get_chat_members_count = getChatMembersCount
    set_game_score = setGameScore
    get_game_high_scores = getGameHighScores
