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
from ptbtest import ChatGenerator
from ptbtest import UserGenerator


class TestChatGenerator(unittest.TestCase):

    def setUp(self):
        self.cg = ChatGenerator()

    def test_without_parameter(self):
        c = self.cg.get_chat()

        self.assertIsInstance(c.id, int)
        self.assertTrue(c.id > 0)
        self.assertEqual(c.username, c.first_name + c.last_name)
        self.assertEqual(c.type, "private")

    def test_group_chat(self):
        c = self.cg.get_chat(chat_type="group")

        self.assertTrue(c.id < 0)
        self.assertEqual(c.type, "group")
        self.assertFalse(c.all_members_are_administrators)
        self.assertIsInstance(c.title, str)

    def test_group_all_members_are_administrators(self):
        c = self.cg.get_chat(chat_type="group",
                             all_members_are_administrators=True)
        self.assertEqual(c.type, "group")
        self.assertTrue(c.all_members_are_administrators)

    def test_group_chat_with_group_name(self):
        c = self.cg.get_chat(chat_type="group", title="My Group")

        self.assertEqual(c.title, "My Group")

    def test_private_from_user(self):
        u = UserGenerator().get_user()
        c = self.cg.get_chat(user=u)

        self.assertEqual(u.id, c.id)
        self.assertEqual(c.username, c.first_name + c.last_name)
        self.assertEqual(u.username, c.username)
        self.assertEqual(c.type, "private")

    def test_supergroup(self):
        c = self.cg.get_chat(chat_type="supergroup")

        self.assertTrue(c.id < 0)
        self.assertEqual(c.type, "supergroup")
        self.assertIsInstance(c.title, str)
        self.assertTrue(c.username, "".join(c.title.split()))

    def test_supergroup_with_title(self):
        c = self.cg.get_chat(chat_type="supergroup", title="Awesome Group")

        self.assertEqual(c.title, "Awesome Group")
        self.assertEqual(c.username, "AwesomeGroup")

    def test_supergroup_with_username(self):
        c = self.cg.get_chat(chat_type="supergroup", username="mygroup")

        self.assertEqual(c.username, "mygroup")

    def test_supergroup_with_username_title(self):
        c = self.cg.get_chat(chat_type="supergroup",
                             username="mygroup",
                             title="Awesome Group")

        self.assertEqual(c.title, "Awesome Group")
        self.assertEqual(c.username, "mygroup")

    def test_channel(self):
        c = self.cg.get_chat(chat_type="channel")

        self.assertIsInstance(c.title, str)
        self.assertEqual(c.type, "channel")
        self.assertTrue(c.username, "".join(c.title.split()))

    def test_channel_with_title(self):
        c = self.cg.get_chat(chat_type="channel", title="Awesome Group")
        self.assertEqual(c.title, "Awesome Group")
        self.assertEqual(c.username, "AwesomeGroup")

    def test_channel_with_username(self):
        c = self.cg.get_chat(chat_type="channel", username="mygroup")

        self.assertEqual(c.username, "mygroup")

    def test_channel_with_username_title(self):
        c = self.cg.get_chat(chat_type="channel",
                             username="mygroup",
                             title="Awesome Group")

        self.assertEqual(c.title, "Awesome Group")
        self.assertEqual(c.username, "mygroup")


if __name__ == '__main__':
    unittest.main()
