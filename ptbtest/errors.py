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
"""This module provides exceptions to raise in tests"""


class BadUserException(Exception):

    def __init__(self, error=None):
        super(BadUserException,
              self).__init__(error or 'Invalid telegram.User object')


class BadChatException(Exception):

    def __init__(self, error=None):
        super(BadChatException,
              self).__init__(error or 'Invalid telegram.Chat object')


class BadMessageException(Exception):

    def __init__(self, error=None):
        super(BadMessageException,
              self).__init__(error or 'Invalid telegram.Message object')


class BadBotException(Exception):

    def __init__(self, error=None):
        super(BadBotException,
              self).__init__(error or 'Invalid ptbtest.Mockbot object')


class BadCallbackQueryException(Exception):

    def __init__(self, error=None):
        super(BadCallbackQueryException,
              self).__init__(error or 'Invalid telegram.CallbackQuery object')


class BadMarkupException(Exception):

    def __init__(self, error=None):
        super(BadMarkupException, self).__init__(error or 'Bad markup error')
