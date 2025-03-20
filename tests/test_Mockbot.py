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
from __future__ import absolute_import

import unittest

import telegram
from telegram import ChatAction
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import InlineQueryResult
from telegram import TelegramError
from telegram import User, Message, Chat, Update
from telegram.ext import Updater, CommandHandler

from ptbtest import Mockbot


class TestMockbot(unittest.TestCase):
    def setUp(self):
        self.mockbot = Mockbot()

    def test_updater_works_with_mockbot(self):
        # handler method
        def start(bot, update):
            message = bot.sendMessage(update.message.chat_id, "this works")
            self.assertIsInstance(message, Message)

        updater = Updater(workers=2, bot=self.mockbot)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        updater.start_polling()
        user = User(id=1, first_name="test", is_bot=False)
        chat = Chat(45, "group")
        message = Message(
            404, user, None, chat, text="/start", bot=self.mockbot)
        message2 = Message(
            404, user, None, chat, text="start", bot=self.mockbot)
        message3 = Message(
            404, user, None, chat, text="/start@MockBot", bot=self.mockbot)
        message4 = Message(
            404, user, None, chat, text="/start@OtherBot", bot=self.mockbot)
        self.mockbot.insertUpdate(Update(0, message=message))
        self.mockbot.insertUpdate(Update(1, message=message2))
        self.mockbot.insertUpdate(Update(1, message=message3))
        self.mockbot.insertUpdate(Update(1, message=message4))
        data = self.mockbot.sent_messages
        self.assertEqual(len(data), 2)
        data = data[0]
        self.assertEqual(data['method'], 'sendMessage')
        self.assertEqual(data['chat_id'], chat.id)
        updater.stop()

    def test_properties(self):
        self.assertEqual(self.mockbot.id, 0)
        self.assertEqual(self.mockbot.first_name, "Mockbot")
        self.assertEqual(self.mockbot.last_name, "Bot")
        self.assertEqual(self.mockbot.name, "@MockBot")
        mb2 = Mockbot("OtherUsername")
        self.assertEqual(mb2.name, "@OtherUsername")
        self.mockbot.sendMessage(1, "test 1")
        self.mockbot.sendMessage(2, "test 2")
        self.assertEqual(len(self.mockbot.sent_messages), 2)
        self.mockbot.reset()
        self.assertEqual(len(self.mockbot.sent_messages), 0)

    def test_dejson_and_to_dict(self):
        import json
        d = self.mockbot.to_dict()
        self.assertIsInstance(d, dict)
        js = json.loads(json.dumps(d))
        b = Mockbot.de_json(js, None)
        self.assertIsInstance(b, Mockbot)

    def test_answerCallbackQuery(self):
        self.mockbot.answerCallbackQuery(
            1, "done", show_alert=True, url="google.com", cache_time=2)

        data = self.mockbot.sent_messages[-1]
        self.assertEqual(data['method'], "answerCallbackQuery")
        self.assertEqual(data['text'], "done")

    def test_answerInlineQuery(self):
        r = [
            InlineQueryResult("string", "1"), InlineQueryResult("string", "2")
        ]
        self.mockbot.answerInlineQuery(
            1,
            r,
            is_personal=True,
            next_offset=3,
            switch_pm_parameter="asd",
            switch_pm_text="pm")

        data = self.mockbot.sent_messages[-1]
        self.assertEqual(data['method'], "answerInlineQuery")
        self.assertEqual(data['results'][0]['id'], "1")

    def test_editMessageCaption(self):
        self.mockbot.editMessageCaption(chat_id=12, message_id=23)

        data = self.mockbot.sent_messages[-1]
        self.assertEqual(data['method'], "editMessageCaption")
        self.assertEqual(data['chat_id'], 12)
        self.mockbot.editMessageCaption(
            inline_message_id=23, caption="new cap", photo=True)
        data = self.mockbot.sent_messages[-1]
        self.assertEqual(data['method'], "editMessageCaption")
        with self.assertRaises(TelegramError):
            self.mockbot.editMessageCaption()
        with self.assertRaises(TelegramError):
            self.mockbot.editMessageCaption(chat_id=12)
        with self.assertRaises(TelegramError):
            self.mockbot.editMessageCaption(message_id=12)

    def test_editMessageReplyMarkup(self):
        self.mockbot.editMessageReplyMarkup(chat_id=1, message_id=1)
        data = self.mockbot.sent_messages[-1]
        self.assertEqual(data['method'], "editMessageReplyMarkup")
        self.assertEqual(data['chat_id'], 1)
        self.mockbot.editMessageReplyMarkup(inline_message_id=1)
        data = self.mockbot.sent_messages[-1]
        self.assertEqual(data['method'], "editMessageReplyMarkup")
        self.assertEqual(data['inline_message_id'], 1)
        with self.assertRaises(TelegramError):
            self.mockbot.editMessageReplyMarkup()
        with self.assertRaises(TelegramError):
            self.mockbot.editMessageReplyMarkup(chat_id=12)
        with self.assertRaises(TelegramError):
            self.mockbot.editMessageReplyMarkup(message_id=12)

    def test_editMessageText(self):
        self.mockbot.editMessageText("test", chat_id=1, message_id=1)
        data = self.mockbot.sent_messages[-1]
        self.assertEqual(data['method'], "editMessageText")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['text'], "test")
        self.mockbot.editMessageText(
            "test",
            inline_message_id=1,
            parse_mode="Markdown",
            disable_web_page_preview=True)
        data = self.mockbot.sent_messages[-1]
        self.assertEqual(data['method'], "editMessageText")
        self.assertEqual(data['inline_message_id'], 1)

    def test_forwardMessage(self):
        self.mockbot.forwardMessage(1, 2, 3)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "forwardMessage")
        self.assertEqual(data['chat_id'], 1)

    def test_getChat(self):
        self.mockbot.getChat(1)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "getChat")
        self.assertEqual(data['chat_id'], 1)

    def test_getChatAdministrators(self):
        self.mockbot.getChatAdministrators(chat_id=2)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "getChatAdministrators")
        self.assertEqual(data['chat_id'], 2)

    def test_getChatMember(self):
        self.mockbot.getChatMember(1, 3)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "getChatMember")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['user_id'], 3)

    def test_getChatMembersCount(self):
        self.mockbot.getChatMembersCount(1)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "getChatMembersCount")
        self.assertEqual(data['chat_id'], 1)

    def test_getFile(self):
        self.mockbot.getFile("12345")
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "getFile")
        self.assertEqual(data['file_id'], "12345")

    def test_getGameHighScores(self):
        self.mockbot.getGameHighScores(
            1, chat_id=2, message_id=3, inline_message_id=4)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "getGameHighScores")
        self.assertEqual(data['user_id'], 1)

    def test_getMe(self):
        data = self.mockbot.getMe()

        self.assertIsInstance(data, User)
        self.assertEqual(data.name, "@MockBot")

    def test_getUpdates(self):
        data = self.mockbot.getUpdates()

        self.assertEqual(data, [])

    def test_getUserProfilePhotos(self):
        self.mockbot.getUserProfilePhotos(1, offset=2)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "getUserProfilePhotos")
        self.assertEqual(data['user_id'], 1)

    def test_kickChatMember(self):
        self.mockbot.kickChatMember(chat_id=1, user_id=2)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "kickChatMember")
        self.assertEqual(data['user_id'], 2)

    def test_leaveChat(self):
        self.mockbot.leaveChat(1)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "leaveChat")

    def test_sendAudio(self):
        self.mockbot.sendAudio(
            1,
            "123",
            duration=2,
            performer="singer",
            title="song",
            caption="this song")
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendAudio")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['duration'], 2)
        self.assertEqual(data['performer'], "singer")
        self.assertEqual(data['title'], "song")
        self.assertEqual(data['caption'], "this song")

    def test_sendChatAction(self):
        self.mockbot.sendChatAction(1, ChatAction.TYPING)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendChatAction")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['action'], "typing")

    def test_sendContact(self):
        self.mockbot.sendContact(1, "123456", "test", last_name="me")
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendContact")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['phone_number'], "123456")
        self.assertEqual(data['last_name'], "me")

    def test_sendDocument(self):
        self.mockbot.sendDocument(
            1, "45", filename="jaja.docx", caption="good doc")
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendDocument")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['filename'], "jaja.docx")
        self.assertEqual(data['caption'], "good doc")

    def test_sendGame(self):
        self.mockbot.sendGame(1, "testgame")
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendGame")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['game_short_name'], "testgame")

    def test_sendLocation(self):
        self.mockbot.sendLocation(1, 52.123, 4.23)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendLocation")
        self.assertEqual(data['chat_id'], 1)

    def test_sendMessage(self):
        keyb = InlineKeyboardMarkup(
            [[InlineKeyboardButton(
                "test 1", callback_data="test1")],
             [InlineKeyboardButton(
                 "test 2", callback_data="test2")]])
        self.mockbot.sendMessage(
            1,
            "test",
            parse_mode=telegram.ParseMode.MARKDOWN,
            reply_markup=keyb,
            disable_notification=True,
            reply_to_message_id=334,
            disable_web_page_preview=True)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendMessage")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['text'], "test")
        self.assertEqual(
            eval(data['reply_markup'])['inline_keyboard'][1][0][
                'callback_data'], "test2")

    def test_sendPhoto(self):
        self.mockbot.sendPhoto(1, "test.png", caption="photo")
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendPhoto")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['caption'], "photo")

    def test_sendSticker(self):
        self.mockbot.sendSticker(-4231, "test")
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendSticker")
        self.assertEqual(data['chat_id'], -4231)

    def test_sendVenue(self):
        self.mockbot.sendVenue(
            1, 4.2, 5.1, "nice place", "somewherestreet 2", foursquare_id=2)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendVenue")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['foursquare_id'], 2)

    def test_sendVideo(self):
        self.mockbot.sendVideo(1, "some file", duration=3, caption="video")
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendVideo")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['duration'], 3)
        self.assertEqual(data['caption'], "video")

    def test_sendVoice(self):
        self.mockbot.sendVoice(1, "some file", duration=3, caption="voice")
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "sendVoice")
        self.assertEqual(data['chat_id'], 1)
        self.assertEqual(data['duration'], 3)
        self.assertEqual(data['caption'], "voice")

    def test_setGameScore(self):
        self.mockbot.setGameScore(
            1,
            200,
            chat_id=2,
            message_id=3,
            inline_message_id=4,
            force=True,
            disable_edit_message=True)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "setGameScore")
        self.assertEqual(data['user_id'], 1)
        self.mockbot.setGameScore(1, 200, edit_message=True)

    def test_unbanChatMember(self):
        self.mockbot.unbanChatMember(1, 2)
        data = self.mockbot.sent_messages[-1]

        self.assertEqual(data['method'], "unbanChatMember")
        self.assertEqual(data['chat_id'], 1)


if __name__ == '__main__':
    unittest.main()
