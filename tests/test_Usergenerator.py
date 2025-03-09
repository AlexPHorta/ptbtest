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

from ptbtest import UserGenerator


class TestUserGenerator(unittest.TestCase):

    def setUp(self):
        self.ug = UserGenerator()

    def test_no_specification(self):
        u = self.ug.get_user()
        self.assertIsInstance(u.id, int)
        self.assertTrue(u.id > 0)
        self.assertIsInstance(u.first_name, str)
        self.assertEqual(u.username, u.first_name + u.last_name)

    def test_with_first_name(self):
        u = self.ug.get_user(first_name="Test")
        self.assertEqual(u.first_name, "Test")
        self.assertTrue(u.username.startswith("Test"))

    def test_with_username(self):
        u = self.ug.get_user(username="misterbot")

        self.assertEqual(u.username, "misterbot")


if __name__ == '__main__':
    unittest.main()
