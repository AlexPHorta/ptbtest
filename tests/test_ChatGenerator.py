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
import re

import pytest
from telegram.constants import ChatType

from ptbtest import ChatGenerator, UserGenerator


@pytest.fixture(scope="function")
def mock_chat():
    return ChatGenerator()


class TestChatGenerator:
    def test_without_parameters(self, mock_chat):
        c = mock_chat.get_chat()

        assert isinstance(c.id, int)
        assert c.id > 0
        assert c.type == "private"
        assert c.username == c.first_name + c.last_name
        assert c.is_forum is False

    @pytest.mark.parametrize(["chat_type"],
                             [
                                 (ChatType.GROUP,),
                                 (ChatType.SUPERGROUP,),
                                 (ChatType.CHANNEL,),
                                 (ChatType.PRIVATE,)
                             ])
    def test_each_chat_type(self, mock_chat, chat_type):
        c = mock_chat.get_chat(type=chat_type)
        assert c.type == chat_type


class TestId:
    def test_positive_id_only(self, mock_chat):
        c = mock_chat.get_chat(id=1)

        assert c.type == "private"
        assert c.username == c.first_name + c.last_name

    def test_negative_id_only(self, mock_chat):
        c = mock_chat.get_chat(id=-1)
        assert c.type == ChatType.GROUP

    def test_zero_id(self, mock_chat):
        c = mock_chat.get_chat(id=0)

        assert c.id > 0
        assert c.type == "private"
        assert c.username == c.first_name + c.last_name

    @pytest.mark.parametrize(["chat_type"], [(ChatType.PRIVATE,), (ChatType.CHANNEL,)])
    def test_negative_id_with_channel_and_private(self, mock_chat, chat_type):
        exc_msg = re.escape("Only groups and supergroups can have the negative 'id'")

        with pytest.raises(ValueError, match=exc_msg):
            mock_chat.get_chat(id=-1, type=chat_type)

    @pytest.mark.parametrize(["chat_type"], [(ChatType.GROUP,), (ChatType.SUPERGROUP,)])
    def test_positive_id_with_group_and_supergroup(self, mock_chat, chat_type):
        exc_msg = re.escape("Only private chats and channels can have the positive 'id'")

        with pytest.raises(ValueError, match=exc_msg):
            mock_chat.get_chat(id=1, type=chat_type)

    def test_with_id_not_private(self, mock_chat):
        c = mock_chat.get_chat(type="group", id=-1)
        assert c.type == "group"

        c = mock_chat.get_chat(type="supergroup", id=-1)
        assert c.type == "supergroup"

    @pytest.mark.parametrize(["chat_type"], [(ChatType.GROUP,), (ChatType.SUPERGROUP,)])
    def test_group_and_supergroup_get_negative_auto_id(self, mock_chat, chat_type):
        c = mock_chat.get_chat(type=chat_type)
        assert c.id < 0

    @pytest.mark.parametrize(["chat_type"], [(ChatType.CHANNEL,), (ChatType.PRIVATE,)])
    def test_private_and_channel_get_positive_auto_id(self, mock_chat, chat_type):
        c = mock_chat.get_chat(type=chat_type)
        assert c.id > 0


class TestPrivateChat:
    def test_private_from_user(self):
        u = UserGenerator().get_user()
        c = ChatGenerator().get_chat(user=u)

        assert u.id == c.id
        assert c.username == c.first_name + c.last_name
        assert u.username == c.username
        assert c.type == "private"

    def test_private_chat_without_user_get_random_user(self):
        c = ChatGenerator().get_chat(type=ChatType.PRIVATE)

        assert c.type == ChatType.PRIVATE
        assert c.username
        # All chat types have 'username' but only private chats have 'first_name' and 'last_name'.
        # So if these attributes are set it means that a random user was generated for the Chat.
        assert c.first_name
        assert c.last_name

    def test_user_id_overrides_chat_id(self, mock_chat):
        """
        If both *user* and *id* are sent then *user* has higher priority.
        """
        user_id = 3141592
        user = UserGenerator().get_user(user_id=user_id)
        chat = mock_chat.get_chat(id=1234, user=user)

        assert chat.id == user_id

    def test_private_chat_without_user_but_with_id_and_username(self, mock_chat):
        """
        Checks that calling *get_chat* without a *user* but with an *id* and a *username*
        will populate corresponding fields in a *user* object.
        """
        username = "ringo_starr"
        chat_id = 771940

        chat = mock_chat.get_chat(id=chat_id, username=username, type="private")
        assert chat.id == chat_id
        assert chat.username == username
        assert chat.type == "private"

    @pytest.mark.parametrize(["chat_type"],[(ChatType.GROUP,), (ChatType.SUPERGROUP,), (ChatType.CHANNEL,)])
    def test_chat_with_user_but_not_private_chat_turns_into_private_and_send_warning(self, mock_chat, chat_type):
        user = UserGenerator().get_user()

        warn_message = re.escape("'type' was forcibly changed to 'private' instead of "
                                 f"'{chat_type}' because you set 'user' parameter")
        with pytest.warns(UserWarning, match=warn_message):
            chat = mock_chat.get_chat(user=user, type=chat_type)

        assert chat.type == ChatType.PRIVATE

    def test_private_no_username(self):
        c = ChatGenerator().get_chat(type="private")

        assert c.id > 0
        assert c.username == c.first_name + c.last_name
        assert c.type == "private"

    def test_with_invalid_user(self):
        """The user argument must be a telegram.User instance"""
        with pytest.raises(TypeError):
            ChatGenerator().get_chat(user="invalid user")


class TestGroupAndSupergroup:
    def test_group_chat(self):
        c = ChatGenerator().get_chat(type="group")

        assert c.id < 0
        assert c.type == "group"
        assert c.api_kwargs.get("all_members_are_administrators") is False
        assert isinstance(c.title, str)

    def test_group_chat_with_group_name(self):
        c = ChatGenerator().get_chat(type="group", title="My Group")

        assert c.id < 0
        assert c.type == "group"
        assert c.api_kwargs.get("all_members_are_administrators") is False
        assert c.title == "My Group"

    def test_group_all_members_are_administrators(self):
        c = ChatGenerator().get_chat(type="group", all_members_are_administrators=True)

        assert c.type == "group"
        assert c.api_kwargs.get("all_members_are_administrators") is True

    def test_supergroup(self):
        c = ChatGenerator().get_chat(type="supergroup")

        assert c.id < 0
        assert c.type == "supergroup"
        assert isinstance(c.title, str)
        assert c.username == "".join(c.title.split())

    def test_supergroup_with_title(self):
        c = ChatGenerator().get_chat(type="supergroup", title="Awesome Group")

        assert c.title == "Awesome Group"
        assert c.username == "AwesomeGroup"

    def test_supergroup_with_username(self):
        c = ChatGenerator().get_chat(type="supergroup", username="mygroup")

        assert c.username == "mygroup"

    def test_supergroup_with_username_and_title(self):
        c = ChatGenerator().get_chat(
            type="supergroup", username="mygroup", title="Awesome Group")

        assert c.title == "Awesome Group"
        assert c.username == "mygroup"


class TestChannel:
    def test_channel(self):
        c = ChatGenerator().get_chat(type="channel")

        assert isinstance(c.title, str)
        assert c.type == "channel"
        assert c.username == "".join(c.title.split())

    def test_channel_with_title(self):
        c = ChatGenerator().get_chat(type="channel", title="Awesome Group")

        assert c.title == "Awesome Group"
        assert c.username == "AwesomeGroup"


class TestTopics:
    def test_topics_enabled_for_groups(self, mock_chat):
        ch = mock_chat.get_chat(type="group", is_forum=True)
        assert ch.is_forum is True

    def test_topics_enabled_for_supergroups(self, mock_chat):
        ch = mock_chat.get_chat(type="supergroup", is_forum=True)
        assert ch.is_forum is True

    def test_topics_disabled(self, mock_chat):
        ch = mock_chat.get_chat(type="group", is_forum=False)
        assert ch.is_forum is False

    @pytest.mark.parametrize(["chat_type"], [(ChatType.PRIVATE,), (ChatType.CHANNEL,)])
    def test_topics_enabled_for_private_and_channel(self, mock_chat, chat_type):
        exc_msg = re.escape("'is_forum' can be True for groups and supergroups only")
        with pytest.raises(ValueError, match=exc_msg):
            mock_chat.get_chat(id=1, type=chat_type, is_forum=True)
