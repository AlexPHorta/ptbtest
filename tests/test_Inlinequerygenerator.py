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

from telegram import ChosenInlineResult, InlineQuery, Location, Update, User

from ptbtest import InlineQueryGenerator, Mockbot, UserGenerator
from ptbtest.errors import BadBotException, BadUserException


class TestInlineQueryGenerator(unittest.TestCase):

    def setUp(self):
        self.iqg = InlineQueryGenerator()

    def test_standard(self):
        u = self.iqg.get_inline_query()
        self.assertIsInstance(u, Update)
        self.assertIsInstance(u.inline_query, InlineQuery)
        self.assertIsInstance(u.inline_query.from_user, User)

        bot = Mockbot(username="testbot")
        iqg2 = InlineQueryGenerator(bot=bot)
        self.assertEqual(bot.username, iqg2.bot.username)

        with self.assertRaises(BadBotException):
            iqg3 = InlineQueryGenerator(bot="bot")

    def test_with_user(self):
        ug = UserGenerator()
        user = ug.get_user()
        u = self.iqg.get_inline_query(user=user)
        self.assertEqual(u.inline_query.from_user.id, user.id)

        with self.assertRaises(BadUserException):
            self.iqg.get_inline_query(user="user")

    def test_query(self):
        u = self.iqg.get_inline_query(query="test")
        self.assertEqual(u.inline_query.query, "test")

        with self.assertRaisesRegex(AttributeError, "query"):
            self.iqg.get_inline_query(query=True)

    def test_offset(self):
        u = self.iqg.get_inline_query(offset="44")
        self.assertEqual(u.inline_query.offset, "44")

        with self.assertRaisesRegex(AttributeError, "offset"):
            self.iqg.get_inline_query(offset=True)

    def test_location(self):
        u = self.iqg.get_inline_query(location=True)
        self.assertIsInstance(u.inline_query.location, Location)

        loc = Location(23.0, 90.0)
        u = self.iqg.get_inline_query(location=loc)
        self.assertEqual(u.inline_query.location.longitude, 23.0)

        with self.assertRaisesRegex(AttributeError, "telegram\.Location"):
            self.iqg.get_inline_query(location="location")


class TestChosenInlineResult(unittest.TestCase):

    def setUp(self):
        self.iqc = InlineQueryGenerator()

    def test_chosen_inline_result(self):
        u = self.iqc.get_chosen_inline_result("testid")
        self.assertIsInstance(u, Update)
        self.assertIsInstance(u.chosen_inline_result, ChosenInlineResult)
        self.assertIsInstance(u.chosen_inline_result.from_user, User)
        self.assertEqual(u.chosen_inline_result.result_id, "testid")

        with self.assertRaisesRegex(AttributeError, "chosen_inline_result"):
            self.iqc.get_chosen_inline_result()

    def test_with_location(self):
        u = self.iqc.get_chosen_inline_result("testid", location=True)
        self.assertIsInstance(u.chosen_inline_result.location, Location)
        loc = Location(23.0, 90.0)
        u = self.iqc.get_chosen_inline_result("testid", location=loc)
        self.assertEqual(u.chosen_inline_result.location.longitude, 23.0)

        with self.assertRaisesRegex(AttributeError, "telegram\.Location"):
            self.iqc.get_chosen_inline_result("test_id", location="loc")

    def test_inline_message_id(self):
        u = self.iqc.get_chosen_inline_result("test")
        self.assertIsInstance(u.chosen_inline_result.inline_message_id, str)

        u = self.iqc.get_chosen_inline_result("test",
                                              inline_message_id="myidilike")
        self.assertEqual(u.chosen_inline_result.inline_message_id, "myidilike")

    def test_user(self):
        ug = UserGenerator()
        user = ug.get_user()
        u = self.iqc.get_chosen_inline_result("test", user=user)
        self.assertEqual(u.chosen_inline_result.from_user.id, user.id)

        with self.assertRaises(BadUserException):
            self.iqc.get_chosen_inline_result("test", user="user")


if __name__ == '__main__':
    unittest.main()
