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
"""This module provides a class to generate telegram chats"""
import random

from .ptbgenerator import PtbGenerator
from ptbtest import UserGenerator
from telegram import (Chat, User)


class ChatGenerator(PtbGenerator):
    """
        Chat generator class. placeholder for random names and mainly used
        via it's get_chat() method
    """
    GROUPNAMES = [
        "Frustrated Vagabonds", "Heir Apparents", "Walky Talky",
        "Flirty Crowns", "My Amigos"
    ]

    def __init__(self):
        PtbGenerator.__init__(self)

    def get_chat(self,
                 cid=None,
                 chat_type="private",
                 title=None,
                 username=None,
                 user=None,
                 all_members_are_administrators=False):
        """
        Returns a telegram.Chat object with the optionally given type or username
        If any of the arguments are omitted the names will be chosen randomly and the
        username will be generated as first_name + last_name.

        When called without arguments will return a telegram.Chat object for a private chat with a randomly
        generated user.

        Args:
            chat_type (str): Type of chat can be private, group, supergroup or channel.
            title (Optional[str]): Title  for the group/supergroup/channel/
            username (Optional[str]): Username for the private/supergroup/channel.
            user (Optional[telegram.User]): If given a private chat for the supplied user will be generated.
            all_members_are_administrators: set's this flag for a group.

        Returns:
            telegram.Chat: A telegram Chat object.

        """
        if cid and chat_type == 'private':
            if cid < 0:
                chat_type = "group"
        if user:
            if isinstance(user, User):
                u = user
                return Chat(cid or u.id,
                            chat_type,
                            username=u.username,
                            first_name=u.first_name,
                            last_name=u.last_name)
        elif chat_type == "private":
            u = UserGenerator().get_user(username=username)
            return Chat(cid or u.id,
                        chat_type,
                        username=u.username,
                        first_name=u.first_name,
                        last_name=u.last_name)
        elif chat_type == "group":
            if not title:
                title = random.choice(self.GROUPNAMES)
            return Chat(
                cid or self.gen_id(group=True),
                chat_type,
                title=title,
                all_members_are_administrators=all_members_are_administrators)
        elif chat_type == "supergroup" or chat_type == "channel":
            if not title:
                gn = random.choice(self.GROUPNAMES)
            else:
                gn = title
            if not username:
                username = "".join(gn.split(" "))
            return Chat(cid or self.gen_id(group=True),
                        chat_type,
                        title=gn,
                        username=username)
