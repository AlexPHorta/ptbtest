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

from telegram import ChosenInlineResult, InlineQuery, Location, Update, User

from ptbtest import InlineQueryGenerator, Mockbot, UserGenerator
from ptbtest.errors import BadBotException, BadUserException


class TestInlineQueryGenerator:
    def test_standard(self):
        u = InlineQueryGenerator().get_inline_query()
        assert isinstance(u, Update)
        assert isinstance(u, Update)
        assert isinstance(u.inline_query, InlineQuery)
        assert isinstance(u.inline_query.from_user, User)

        bot = Mockbot(username="testbot")
        iqg2 = InlineQueryGenerator(bot=bot)
        assert bot.username == iqg2.bot.username

        with pytest.raises(BadBotException):
            InlineQueryGenerator(bot="bot")

    def test_with_user(self):
        user = UserGenerator().get_user()
        u = InlineQueryGenerator().get_inline_query(user=user)
        assert u.inline_query.from_user.id == user.id

        with pytest.raises(BadUserException):
            InlineQueryGenerator().get_inline_query(user="user")

    def test_query(self):
        u = InlineQueryGenerator().get_inline_query(query="test")
        assert u.inline_query.query == "test"

        with pytest.raises(AttributeError, match="query"):
            InlineQueryGenerator().get_inline_query(query=True)

    def test_offset(self):
        u = InlineQueryGenerator().get_inline_query(offset="44")
        assert u.inline_query.offset == "44"

        with pytest.raises(AttributeError, match="offset"):
            InlineQueryGenerator().get_inline_query(offset=True)

    def test_location(self):
        u = InlineQueryGenerator().get_inline_query(location=True)
        assert isinstance(u.inline_query.location, Location)

        loc = Location(23.0, 90.0)
        u = InlineQueryGenerator().get_inline_query(location=loc)
        assert u.inline_query.location.longitude == 23.0

        with pytest.raises(AttributeError, match=r"telegram\.Location"):
            InlineQueryGenerator().get_inline_query(location="location")


class TestChosenInlineResult:
    def test_chosen_inline_result(self):
        u = InlineQueryGenerator().get_chosen_inline_result("testid")
        assert isinstance(u, Update)
        assert isinstance(u.chosen_inline_result, ChosenInlineResult)
        assert isinstance(u.chosen_inline_result.from_user, User)
        assert u.chosen_inline_result.result_id == "testid"

        with pytest.raises(AttributeError, match="chosen_inline_result"):
            InlineQueryGenerator().get_chosen_inline_result()

    def test_with_location(self):
        u = InlineQueryGenerator().get_chosen_inline_result("testid", location=True)
        assert isinstance(u.chosen_inline_result.location, Location)

        loc = Location(23.0, 90.0)
        u = InlineQueryGenerator().get_chosen_inline_result("testid", location=loc)
        assert u.chosen_inline_result.location.longitude == 23.0

        with pytest.raises(AttributeError, match=r"telegram\.Location"):
            InlineQueryGenerator().get_chosen_inline_result("test_id", location="loc")

    def test_inline_message_id(self):
        u = InlineQueryGenerator().get_chosen_inline_result("test")
        assert isinstance(u.chosen_inline_result.inline_message_id, str)

        u = InlineQueryGenerator().get_chosen_inline_result(
            "test", inline_message_id="myidilike")
        assert u.chosen_inline_result.inline_message_id == "myidilike"

    def test_user(self):
        user = UserGenerator().get_user()
        u = InlineQueryGenerator().get_chosen_inline_result("test", user=user)
        assert u.chosen_inline_result.from_user.id == user.id

        with pytest.raises(BadUserException):
            InlineQueryGenerator().get_chosen_inline_result("test", user="user")
