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

from telegram import CallbackQuery, Message, Update, User

from ptbtest import (BadBotException, BadCallbackQueryException,
                     BadMessageException, BadUserException,
                     CallbackQueryGenerator, MessageGenerator, Mockbot,
                     UserGenerator)


class TestMessageGeneratorChannelPost(unittest.TestCase):

    def setUp(self):
        self.cqg = CallbackQueryGenerator()

    def test_invalid_calls(self):
        with self.assertRaisesRegex(BadCallbackQueryException,
                                    "message and inline_message_id"):
            self.cqg.get_callback_query()
        with self.assertRaisesRegex(BadCallbackQueryException,
                                    "message and inline_message_id"):
            self.cqg.get_callback_query(message=True, inline_message_id=True)
        with self.assertRaisesRegex(BadCallbackQueryException,
                                    "data and game_short_name"):
            self.cqg.get_callback_query(message=True)
        with self.assertRaisesRegex(BadCallbackQueryException,
                                    "data and game_short_name"):
            self.cqg.get_callback_query(message=True,
                                        data="test-data",
                                        game_short_name="mygame")

    def test_required_auto_set(self):
        u = self.cqg.get_callback_query(inline_message_id=True,
                                        data="test-data")
        self.assertIsInstance(u.callback_query.from_user, User)
        self.assertIsInstance(u.callback_query.chat_instance, str)
        bot = Mockbot(username="testbot")
        cqg2 = CallbackQueryGenerator(bot=bot)
        self.assertEqual(bot.username, cqg2.bot.username)

        with self.assertRaises(BadBotException):
            cqg3 = CallbackQueryGenerator(bot="bot")

    def test_message(self):
        mg = MessageGenerator()
        message = mg.get_message().message
        u = self.cqg.get_callback_query(message=message, data="test-data")
        self.assertIsInstance(u, Update)
        self.assertIsInstance(u.callback_query, CallbackQuery)
        self.assertEqual(u.callback_query.message.message_id,
                         message.message_id)

        u = self.cqg.get_callback_query(message=True, data="test-data")
        self.assertIsInstance(u.callback_query.message, Message)
        self.assertEqual(u.callback_query.message.from_user.username,
                         self.cqg.bot.username)

        with self.assertRaises(BadMessageException):
            self.cqg.get_callback_query(message="message", data="test-data")

    def test_inline_message_id(self):
        u = self.cqg.get_callback_query(inline_message_id="myidilike",
                                        data="test-data")
        self.assertEqual(u.callback_query.inline_message_id, "myidilike")
        u = self.cqg.get_callback_query(inline_message_id=True,
                                        data="test-data")
        self.assertIsInstance(u.callback_query.inline_message_id, str)

        with self.assertRaisesRegex(BadCallbackQueryException,
                                    "string or True"):
            self.cqg.get_callback_query(inline_message_id=3.98,
                                        data="test-data")

    def test_user(self):
        ug = UserGenerator()
        user = ug.get_user()
        u = self.cqg.get_callback_query(user=user,
                                        message=True,
                                        data="test-data")
        self.assertEqual(user.id, u.callback_query.from_user.id)
        self.assertNotEqual(user.id, u.callback_query.message.from_user.id)

        with self.assertRaises(BadUserException):
            u = self.cqg.get_callback_query(user="user",
                                            inline_message_id=True,
                                            data="test-data")


if __name__ == '__main__':
    unittest.main()
