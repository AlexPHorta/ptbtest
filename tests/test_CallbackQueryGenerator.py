#!/usr/bin/env python
# pylint: disable=E0611,E0213,E1102,C0103,E1101,W0613,R0913,R0904
#
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
import pytest
from telegram import (CallbackQuery, Message, Update, User)

from ptbtest import (BadBotException, BadCallbackQueryException,
                     BadUserException, BadMessageException)
from ptbtest import (CallbackQueryGenerator, MessageGenerator, Mockbot,
                     UserGenerator)


class TestCallbackQueryGenerator:
    def test_invalid_calls(self):
        with pytest.raises(BadCallbackQueryException) as exc:
            CallbackQueryGenerator().get_callback_query()

        assert "message and inline_message_id" in str(exc.value)

        with pytest.raises(BadCallbackQueryException) as exc:
            CallbackQueryGenerator().get_callback_query(message=True, inline_message_id=True)

        assert "message and inline_message_id" in str(exc.value)

        with pytest.raises(BadCallbackQueryException) as exc:
            CallbackQueryGenerator().get_callback_query(message=True)

        assert "data and game_short_name" in str(exc.value)

        with pytest.raises(BadCallbackQueryException) as exc:
            CallbackQueryGenerator().get_callback_query(
                message=True, data="test-data", game_short_name="mygame")

        assert "data and game_short_name" in str(exc.value)

    def test_required_auto_set(self):

        u = CallbackQueryGenerator().get_callback_query(
            inline_message_id=True, data="test-data")

        assert isinstance(u.callback_query.from_user, User)
        assert isinstance(u.callback_query.chat_instance, str)

        bot = Mockbot(username="testbot")
        cqg2 = CallbackQueryGenerator(bot=bot)

        assert bot.username == cqg2.bot.username

        with pytest.raises(BadBotException):
            CallbackQueryGenerator(bot="bot")

    def test_message(self):
        mg = MessageGenerator()
        message = mg.get_message().message
        u = CallbackQueryGenerator().get_callback_query(message=message, data="test-data")

        assert isinstance(u, Update)
        assert isinstance(u.callback_query, CallbackQuery)
        assert u.callback_query.message.message_id == message.message_id

        u = CallbackQueryGenerator().get_callback_query(message=True, data="test-data")
        assert isinstance(u.callback_query.message, Message)
        assert u.callback_query.message.from_user.username == CallbackQueryGenerator().bot.username

        with pytest.raises(BadMessageException):
            CallbackQueryGenerator().get_callback_query(message="message", data="test-data")

    def test_inline_message_id(self):
        u = CallbackQueryGenerator().get_callback_query(
            inline_message_id="myidilike", data="test-data")

        assert u.callback_query.inline_message_id == "myidilike"

        u = CallbackQueryGenerator().get_callback_query(
            inline_message_id=True, data="test-data")
        assert isinstance(u.callback_query.inline_message_id, str)

        with pytest.raises(BadCallbackQueryException) as exc:
            CallbackQueryGenerator().get_callback_query(inline_message_id=3.98, data="test-data")

        assert "string or True" in str(exc.value)

    def test_user(self):
        ug = UserGenerator()
        user = ug.get_user()
        u = CallbackQueryGenerator().get_callback_query(user=user, message=True, data="test-data")

        assert user.id == u.callback_query.from_user.id
        assert user.id != u.callback_query.message.from_user.id

        with pytest.raises(BadUserException):
            CallbackQueryGenerator().get_callback_query(
                user="user", inline_message_id=True, data="test-data")
