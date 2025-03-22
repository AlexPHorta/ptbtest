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
import asyncio
import json

import pytest

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import InlineQueryResult
from telegram import User, Message, Chat, Update
from telegram.constants import ChatAction, ParseMode
from telegram.error import TelegramError
from telegram.ext import Updater

from ptbtest import Mockbot

pytestmark = pytest.mark.anyio


class TestMockbot:
    mockbot = Mockbot()

    # This one is passing, but I believe it's wrong and I don't know why. (c) Eldinnie
    @pytest.mark.xfail(reason="The outdated API version")
    async def test_updater_works_with_mockbot(self):
        # handler method
        def start(bot, update):
            message = bot.send_message(update.message.chat_id, "this works")
            assert isinstance(message, Message)

        updater = Updater(bot=self.mockbot, update_queue=asyncio.Queue())
        async with updater:
            user = User(id=1, first_name="test", is_bot=True)
            chat = Chat(45, "group")
            message = Message(
                404, user, None, chat, text="/start", via_bot=self.mockbot)
            message2 = Message(
                404, user, None, chat, text="start", via_bot=self.mockbot)
            message3 = Message(
                404, user, None, chat, text="/start@MockBot", via_bot=self.mockbot)
            message4 = Message(
                404, user, None, chat, text="/start@OtherBot", via_bot=self.mockbot)
            self.mockbot.insert_update(Update(0, message=message))
            self.mockbot.insert_update(Update(1, message=message2))
            self.mockbot.insert_update(Update(1, message=message3))
            self.mockbot.insert_update(Update(1, message=message4))
            data = self.mockbot.sent_messages
            assert len(data) == 2
            data = data[0]
            assert data['method'] == 'send_message'
            assert data['chat_id'] == chat.id

    def test_properties(self):
        assert self.mockbot.id == 0
        assert self.mockbot.first_name == "Mockbot"
        assert self.mockbot.last_name == "Bot"
        assert self.mockbot.name == "@MockBot"
        mb2 = Mockbot("OtherUsername")
        assert mb2.name == "@OtherUsername"
        self.mockbot.send_message(1, "test 1")
        self.mockbot.send_message(2, "test 2")
        assert len(self.mockbot.sent_messages) == 2
        self.mockbot.reset()
        assert len(self.mockbot.sent_messages) == 0

    @pytest.mark.xfail(reason="Mockbot.de_json must be updated")
    def test_dejson_and_to_dict(self):
        d = self.mockbot.to_dict()
        assert isinstance(d, dict)
        js = json.loads(json.dumps(d))
        b = Mockbot.de_json(js, None)
        assert isinstance(b, Mockbot)

    def test_answer_callback_query(self):
        self.mockbot.answer_callback_query(
            1, "done", show_alert=True, url="google.com", cache_time=2)

        data = self.mockbot.sent_messages[-1]
        assert data['method'] == "answer_callback_query"
        assert data['text'] == "done"

    def test_answer_inline_query(self):
        r = [
            InlineQueryResult("string", "1"), InlineQueryResult("string", "2")
        ]
        self.mockbot.answer_inline_query(
            1,
            r,
            is_personal=True,
            next_offset=3,
            switch_pm_parameter="asd",
            switch_pm_text="pm")

        data = self.mockbot.sent_messages[-1]
        assert data['method'] == "answer_inline_query"
        assert data['results'][0]['id'] == "1"

    @pytest.mark.xfail(reason="The outdated API version")
    def test_edit_message_caption(self):
        self.mockbot.edit_message_caption(chat_id=12, message_id=23)

        data = self.mockbot.sent_messages[-1]
        assert data['method'] == "edit_message_caption"
        assert data['chat_id'] == 12
        self.mockbot.edit_message_caption(
            inline_message_id=23, caption="new cap", photo=True)
        data = self.mockbot.sent_messages[-1]
        assert data['method'] == "edit_message_caption"
        with pytest.raises(TelegramError):
            self.mockbot.edit_message_caption()
        with pytest.raises(TelegramError):
            self.mockbot.edit_message_caption(chat_id=12)
        with pytest.raises(TelegramError):
            self.mockbot.edit_message_caption(message_id=12)

    @pytest.mark.xfail(reason="The outdated API version")
    def test_edit_message_reply_markup(self):
        self.mockbot.edit_message_reply_markup(chat_id=1, message_id=1)
        data = self.mockbot.sent_messages[-1]
        assert data['method'] == "edit_message_reply_markup"
        assert data['chat_id'] == 1

        self.mockbot.edit_message_reply_markup(inline_message_id=1)
        data = self.mockbot.sent_messages[-1]
        assert data['method'] == "edit_message_reply_markup"
        assert data['inline_message_id'] == 1

        with pytest.raises(TelegramError):
            self.mockbot.edit_message_reply_markup()
        with pytest.raises(TelegramError):
            self.mockbot.edit_message_reply_markup(chat_id=12)
        with pytest.raises(TelegramError):
            self.mockbot.edit_message_reply_markup(message_id=12)

    def test_edit_message_text(self):
        self.mockbot.edit_message_text("test", chat_id=1)
        data = self.mockbot.sent_messages[-1]
        assert data['method'] == "edit_message_text"
        assert data['chat_id'] == 1
        assert data['text'] == "test"
        self.mockbot.edit_message_text(
            "test",
            inline_message_id=1,
            parse_mode="Markdown",
            disable_web_page_preview=True)
        data = self.mockbot.sent_messages[-1]
        assert data['method'] == "edit_message_text"
        assert data['inline_message_id'] == 1

    @pytest.mark.xfail(reason="The outdated API version")
    def test_forward_message(self):
        self.mockbot.forward_message(1, 2, 3)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "forward_message"
        assert data['chat_id'] == 1

    def test_get_chat(self):
        self.mockbot.get_chat(1)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "get_chat"
        assert data['chat_id'] == 1

    def test_getChatAdministrators(self):
        self.mockbot.get_chat_administrators(chat_id=2)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "get_chat_administrators"
        assert data['chat_id'] == 2

    def test_get_chat_member(self):
        self.mockbot.get_chat_member(1, 3)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "get_chat_member"
        assert data['chat_id'] == 1
        assert data['user_id'] == 3

    def test_get_chat_members_count(self):
        self.mockbot.get_chat_members_count(1)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "get_chat_members_count"
        assert data['chat_id'] == 1

    def test_get_file(self):
        self.mockbot.get_file("12345")
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "get_file"
        assert data['file_id'] == "12345"

    def test_get_game_high_score(self):
        self.mockbot.get_game_high_score(
            1, chat_id=2, message_id=3, inline_message_id=4)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "get_game_high_score"
        assert data['user_id'] == 1

    def test_get_me(self):
        data = self.mockbot.get_me()

        assert isinstance(data, User)
        assert data.name == "@MockBot"

    def test_get_updates(self):
        data = self.mockbot.get_updates()

        assert data == []

    def test_get_user_profile_photos(self):
        self.mockbot.get_user_profile_photos(1, offset=2)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "get_user_profile_photos"
        assert data['user_id'] == 1

    def test_kick_chat_member(self):
        self.mockbot.kick_chat_member(chat_id=1, user_id=2)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "kick_chat_member"
        assert data['user_id'] == 2

    def test_leave_chat(self):
        self.mockbot.leave_chat(1)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "leave_chat"

    def test_send_audio(self):
        self.mockbot.send_audio(
            1,
            "123",
            "audio_unique_id",
            duration=2,
            performer="singer",
            title="song",
            caption="this song")
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_audio"
        assert data['chat_id'] == 1
        assert data['duration'] == 2
        assert data['performer'] == "singer"
        assert data['title'] == "song"
        assert data['caption'] == "this song"

    def test_send_chat_action(self):
        self.mockbot.send_chat_action(1, ChatAction.TYPING)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_chat_action"
        assert data['chat_id'] == 1
        assert data['action'] == "typing"

    def test_send_contact(self):
        self.mockbot.send_contact(1, "123456", "test", last_name="me")
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_contact"
        assert data['chat_id'] == 1
        assert data['phone_number'] == "123456"
        assert data['last_name'] == "me"

    def test_send_document(self):
        self.mockbot.send_document(
            1, "45", "document_unique_id", filename="jaja.docx", caption="good doc")
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_document"
        assert data['chat_id'] == 1
        assert data['filename'] == "jaja.docx"
        assert data['caption'] == "good doc"

    def test_send_game(self):
        self.mockbot.send_game(1, "testgame")
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_game"
        assert data['chat_id'] == 1
        assert data['game_short_name'] == "testgame"

    def test_send_location(self):
        self.mockbot.send_location(1, 52.123, 4.23)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_location"
        assert data['chat_id'] == 1

    def test_send_message(self):
        keyb = InlineKeyboardMarkup(
            [[InlineKeyboardButton(
                "test 1", callback_data="test1")],
             [InlineKeyboardButton(
                 "test 2", callback_data="test2")]])
        self.mockbot.send_message(
            1,
            "test",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyb,
            disable_notification=True,
            reply_to_message_id=334,
            disable_web_page_preview=True)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_message"
        assert data['chat_id'] == 1
        assert data['text'] == "test"
        assert eval(data['reply_markup'])['inline_keyboard'][1][0]['callback_data'] == "test2"

    def test_send_photo(self):
        self.mockbot.send_photo(1, "test.png", caption="photo")
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_photo"
        assert data['chat_id'] == 1
        assert data['caption'] == "photo"

    def test_send_sticker(self):
        self.mockbot.send_sticker(-4231, "test", "sticker_unique_id", 10, 10, True, True, "regular")
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_sticker"
        assert data['chat_id'] == -4231

    def test_send_venue(self):
        self.mockbot.send_venue(
            1, 4.2, 5.1, "nice place", "somewherestreet 2", foursquare_id=2)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_venue"
        assert data['chat_id'] == 1
        assert data['foursquare_id'] == 2

    def test_send_video(self):
        self.mockbot.send_video(1, "some file", "video_unique_id", 10, 10, 3)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_video"
        assert data['chat_id'] == 1
        assert data['video2']['width'] == 10
        assert data['video2']['height'] == 10
        assert data['video2']['duration'] == 3

    def test_send_voice(self):
        self.mockbot.send_voice(1, "some file", "voide_unique_id", duration=3, caption="voice")
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "send_voice"
        assert data['chat_id'] == 1
        assert data['duration'] == 3
        assert data['caption'] == "voice"

    def test_set_game_score(self):
        self.mockbot.set_game_score(
            1,
            200,
            chat_id=2,
            message_id=3,
            inline_message_id=4,
            force=True,
            disable_edit_message=True)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "set_game_score"
        assert data['user_id'] == 1
        self.mockbot.set_game_score(1, 200, edit_message=True)

    def test_unban_chat_member(self):
        self.mockbot.unban_chat_member(1, 2)
        data = self.mockbot.sent_messages[-1]

        assert data['method'] == "unban_chat_member"
        assert data['chat_id'] == 1
