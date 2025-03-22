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
"""This module provides a class to generate telegram chats"""
import random
import warnings
from typing import Optional, Union

from telegram import Chat, User
from telegram.constants import ChatType

from ptbtest import UserGenerator
from ptbtest.ptbgenerator import PtbGenerator


class ChatGenerator(PtbGenerator):
    """
        Chat generator class. Placeholder for random names and mainly used
        via it's get_chat() method.
    """
    GROUPNAMES = (
        "Frustrated Vagabonds", "Heir Apparents", "Walky Talky",
        "Flirty Crowns", "My Amigos"
    )

    def __init__(self):
        super().__init__()

    def get_chat(self,
                 id: Optional[int] = None,
                 type: Optional[Union[ChatType, str]] = None,
                 title: Optional[str] = None,
                 username: Optional[str] = None,
                 user: Optional[User] = None,
                 is_forum: bool = False,
                 *,
                 all_members_are_administrators: bool = False) -> Chat:
        """
        Returns a telegram.Chat object with the optionally given type or username
        If any of the arguments are omitted the names will be chosen randomly and the
        username will be generated as first_name + last_name.

        When called without arguments will return a telegram.Chat object for a private chat with a randomly
        generated user.

        Args:
            id (Optional[int]): ID of the returned chat.
            type (Optional[Union[ChatType, str]]): Type of the chat can be either
                telegram.constants.ChatType or the string literal ("private", "group", "supergroup", "channel").
            title (Optional[str]): Title  for the group/supergroup/channel.
            username (Optional[str]): Username for the private/supergroup/channel.
            user (Optional[telegram.User]): If given, a private chat for the supplied user will be generated.
            is_forum (bool): True, if the supergroup chat is a forum (has topics enabled). Default is False.
            all_members_are_administrators (Optional[bool]): Sets this flag for a group.

        Returns:
            telegram.Chat: A telegram.Chat object.
        """
        if id:
            if type:
                if id < 0 and type not in (ChatType.GROUP, ChatType.SUPERGROUP):
                    raise ValueError("Only groups and supergroups can have the negative 'id'")
                elif id > 0 and type not in (ChatType.PRIVATE, ChatType.CHANNEL):
                    raise ValueError("Only private chats and channels can have the positive 'id'")
        else:
            is_group = True if type in (ChatType.GROUP, ChatType.SUPERGROUP) else False
            id = self.gen_id(is_group)
        chat_id = id

        chat_type = type
        if not chat_type:
            chat_type = ChatType.GROUP if id < 0 else ChatType.PRIVATE

        if is_forum and chat_type not in (ChatType.GROUP, ChatType.SUPERGROUP):
            raise ValueError("'is_forum' can be True for groups and supergroups only")

        if user:
            if not isinstance(user, User):
                raise TypeError("user must be a telegram.User instance")
            elif chat_type != ChatType.PRIVATE:
                if chat_type is not None:
                    warnings.warn(f"'type' was forcibly changed to 'private' instead of "
                                  f"'{chat_type}' because you set 'user' parameter")
                chat_type = ChatType.PRIVATE

        chat_user = user
        if not chat_user and chat_type == ChatType.PRIVATE:
            chat_user = UserGenerator().get_user(username=username, user_id=id)

        chat_title = title
        chat_username = username
        chat_first_name = None
        chat_last_name = None
        chat_api_kwargs = None

        # Configuring private chats.
        if chat_user:
            chat_id = chat_user.id
            chat_username = chat_user.username
            chat_first_name = chat_user.first_name
            chat_last_name = chat_user.last_name
        # Configuring channels, groups and supergroups.
        else:
            chat_title = chat_title if chat_title else random.choice(self.GROUPNAMES)  # noqa: S311
            if not chat_username and chat_type != ChatType.GROUP:
                chat_username = "".join(chat_title.split(" "))
            chat_api_kwargs = {"all_members_are_administrators": all_members_are_administrators}

        return Chat(chat_id,
                    chat_type,
                    username=chat_username,
                    first_name=chat_first_name,
                    last_name=chat_last_name,
                    title=chat_title,
                    is_forum=is_forum,
                    api_kwargs=chat_api_kwargs)

    def get_private_chat(self,
                         id: Optional[int] = None,
                         user: Optional[User] = None,
                         username: Optional[str] = None,
                         first_name: Optional[str] = None,
                         last_name: Optional[str] = None) -> Chat:
        """
        The convenient method for generating private chats.
        If any of the arguments are omitted the values will be chosen randomly.

        Parameters:
            id (Optional[int]): ID of the returned chat.
            user (Optional[telegram.User]): If given, a private chat for the supplied user will be generated.
            username (Optional[str]): A username for the user.
            first_name (Optional[str]): The first name for the user.
            last_name (Optional[str]): The last name for the user.

        Returns:
            telegram.Chat: A telegram.Chat object with the 'private' ChatType.
        """
        # The 'get_chat' method doesn't allow to send `first_name` and `last_name` parameters.
        # If it is necessary to set these parameters we must generate new User object.
        # If the `user` parameter is set then the parameters will be taken from it.
        chat_user = user
        if not chat_user and (first_name or last_name):
            chat_user = UserGenerator().get_user(user_id=id,
                                                 username=username,
                                                 first_name=first_name,
                                                 last_name=last_name)

        return self.get_chat(id=id, user=chat_user, username=username, type=ChatType.PRIVATE)

    def get_channel_chat(self,
                         id: Optional[int] = None,
                         title: Optional[str] = None,
                         username: Optional[str] = None) -> Chat:
        """
        The convenient method for generating channel chats.
        If any of the arguments are omitted the values will be chosen randomly.

        Args:
            id (Optional[int]): ID of the returned chat.
            title (Optional[str]): Title  for the group/supergroup/channel.
            username (Optional[str]): Username for the private/supergroup/channel.

        Returns:
            telegram.Chat: A telegram.Chat object with 'channel' ChatType.
        """

        return self.get_chat(id=id, title=title, username=username, type=ChatType.CHANNEL)

    def get_group_chat(self,
                       id: Optional[int] = None,
                       title: Optional[str] = None,
                       username: Optional[str] = None,
                       is_forum: bool = False,
                       is_supergroup: bool = False,
                       *,
                       all_members_are_administrators: bool = False) -> Chat:
        """
        The convenient method for generating [super]group chats.
        If any of the arguments are omitted the values will be chosen randomly.

        Args:
            id (Optional[int]): ID of the returned chat.
            title (Optional[str]): Title  for the group/supergroup/channel.
            username (Optional[str]): Username for the private/supergroup/channel.
            is_forum (bool): True, if the supergroup chat is a forum (has topics enabled). Default is False.
            is_supergroup (bool): True, if the chat must be supergroup. Default is False.
            all_members_are_administrators (Optional[bool]): Sets this flag for a group.

        Returns:
            telegram.Chat: A telegram.Chat object.
        """
        chat_type = ChatType.SUPERGROUP if is_supergroup else ChatType.GROUP
        return self.get_chat(id=id,
                             type=chat_type,
                             title=title,
                             username=username,
                             is_forum=is_forum,
                             all_members_are_administrators=all_members_are_administrators)

    def get_random_chat(self) -> Chat:
        """
        The convenient method for generating a chat of random type.

        Returns:
            telegram.Chat: A telegram.Chat object with random type.
        """

        def get_supergroup_chat():
            return self.get_group_chat(is_supergroup=True)

        methods = [
            self.get_private_chat,
            self.get_channel_chat,
            self.get_group_chat,
            get_supergroup_chat
        ]

        return random.choice(methods)()
