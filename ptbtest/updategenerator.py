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
"""This module provides a decorator to generate telegram updates"""
import functools

from telegram import Update


def _gen_id():
    x = 1
    while True:
        yield x
        x += 1


idgen = _gen_id()


def update(messtype):
    """
    Decorator used by the generatorclasses to wrap the produced method in an update.
    """

    def _update(func):

        @functools.wraps(func)
        def decorated_func(self, *args, **kwargs):
            tmp = dict(message=None,
                       edited_message=None,
                       inline_query=None,
                       chosen_inline_result=None,
                       callback_query=None,
                       channel_post=None,
                       edited_channel_post=None)
            tmp[messtype] = func(self, *args, **kwargs)
            return Update(next(idgen),
                          message=tmp['message'],
                          edited_message=tmp['edited_message'],
                          inline_query=tmp['inline_query'],
                          chosen_inline_result=tmp['chosen_inline_result'],
                          callback_query=tmp['callback_query'],
                          channel_post=tmp['channel_post'],
                          edited_channel_post=tmp['edited_channel_post'])

        return decorated_func

    return _update
