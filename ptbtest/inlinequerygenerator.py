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
"""This module provides a class to generate telegram callback queries"""
import uuid

from telegram import ChosenInlineResult
from .updategenerator import update
from .ptbgenerator import PtbGenerator
from ptbtest import (Mockbot, UserGenerator)
from ptbtest.errors import (BadBotException, BadUserException)
from telegram import (InlineQuery, Location, User)


class InlineQueryGenerator(PtbGenerator):
    """
        Callback query generator class.

        Attributes:
            bot (ptbtest.Mockbot): Bot to encode with the messages

        Args:
            bot (Optional[ptbtest.Mockbot]): supply your own for a custom botname
    """

    def __init__(self, bot=None):
        PtbGenerator.__init__(self)
        self.ug = UserGenerator()
        if not bot:
            self.bot = Mockbot()
        elif isinstance(bot, Mockbot):
            self.bot = bot
        else:
            raise BadBotException

    @update("inline_query")
    def get_inline_query(self,
                         user=None,
                         query=None,
                         offset=None,
                         location=None):
        """

        Returns a telegram.Update object containing a inline_query.


        Parameters:
            location (Optional[telegram.Location or True]): simulates a location
            offset (Optional[str]):
            query (Optional[str]):
            user (Optional[telegram.User): If omitted will be randomly generated

        Returns:
            telegram.Update: an update containing a :py:class:`telegram.InlineQuery`

        """

        if user:
            if not isinstance(user, User):
                raise BadUserException
        else:
            user = self.ug.get_user()

        if query:
            if not isinstance(query, str):
                raise AttributeError("query must be string")

        if offset:
            if not isinstance(offset, str):
                raise AttributeError("offset must be string")

        if location:
            if isinstance(location, Location):
                pass
            elif isinstance(location, bool):
                import random
                location = Location(random.uniform(-180, 180),
                                    random.uniform(-90, 90))
            else:
                raise AttributeError(
                    "Location must be either telegram.Location or True")

        return InlineQuery(self._gen_id(),
                           from_user=user,
                           query=query,
                           offset=offset,
                           location=location,
                           bot=self.bot)

    @update("chosen_inline_result")
    def get_chosen_inline_result(self,
                                 result_id=None,
                                 query=None,
                                 user=None,
                                 location=None,
                                 inline_message_id=None):
        """
        Returns a telegram.Update object containing a inline_query.

        Parameters:
            result_id (str): The result_id belonging to this chosen result
            inline_message_id (Optional[str]): Of omitted will be generated
            location (Optional[telegram.Location or True]): simulates a location
            query (Optional[str]): The query used to send this query
            user (Optional[telegram.User): If omitted will be randomly generated

        Returns:
            telegram.Update: an update containing a :py:class:`telegram.ChosenInlineResult`

        """
        if not result_id:
            raise AttributeError(
                "result_id must be present for chosen_inline_result")

        if user:
            if not isinstance(user, User):
                raise BadUserException
        else:
            user = self.ug.get_user()

        if not query:
            query = ""

        if location:
            if isinstance(location, Location):
                pass
            elif isinstance(location, bool):
                import random
                location = Location(random.uniform(-180, 180),
                                    random.uniform(-90, 90))
            else:
                raise AttributeError(
                    "Location must be either telegram.Location or True")

        if not inline_message_id:
            inline_message_id = self._gen_id()

        return ChosenInlineResult(result_id=result_id,
                                  from_user=user,
                                  query=query,
                                  location=location,
                                  inline_message_id=inline_message_id)

    def _gen_id(self):
        return str(uuid.uuid4())
