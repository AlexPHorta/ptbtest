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
"""This module provides a class to generate telegram users"""
import random

from .ptbgenerator import PtbGenerator
from telegram import User


class UserGenerator(PtbGenerator):
    """User generator class. placeholder for random names and mainly used
        via it's get_user() method"""
    FIRST_NAMES = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
        "Elizabeth", "William", "Linda", "David", "Barbara", "Richard",
        "Susan", "Joseph", "Jessica", "Thomas", "Margaret", "Charles", "Sarah"
    ]
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller",
        "Wilson", "Moore", "Taylor"
    ]

    def __init__(self):
        PtbGenerator.__init__(self)

    def get_user(self, first_name=None, last_name=None, username=None,
                 id=None, is_bot=False):
        """
        Returns a telegram.User object with the optionally given name(s) or username
        If any of the arguments are omitted the names will be chosen randomly and the
        username will be generated as first_name + last_name.

        Args:
            first_name (Optional[str]): First name for the returned user.
            last_name (Optional[str]): Lst name for the returned user.
            username (Optional[str]): Username for the returned user.
            is_bot (Optional[bool]): Whether the user is a bot.

        Returns:
            telegram.User: A telegram user object

        """
        if not first_name:
            first_name = random.choice(self.FIRST_NAMES)
        if not last_name:
            last_name = random.choice(self.LAST_NAMES)
        if not username:
            username = first_name + last_name
        return User(
            id or self.gen_id(),
            first_name,
            last_name=last_name,
            username=username,
            is_bot=is_bot)
