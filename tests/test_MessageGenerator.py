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
import datetime
from collections.abc import Sequence

import pytest
from telegram import (Audio, Contact, Document, Location, Sticker, User,
                      Update, Venue, Video, Voice, PhotoSize, Message)

from ptbtest import (BadBotException, BadChatException, BadUserException,
                     BadMarkupException, BadMessageException, Mockbot,
                     UserGenerator, MessageGenerator, ChatGenerator)


class TestMessageGeneratorCore:
    def test_is_update(self):
        u = MessageGenerator().get_message()
        assert isinstance(u, Update)
        assert isinstance(u.message, Message)

    def test_bot(self):
        u = MessageGenerator().get_message()
        assert isinstance(u.message.via_bot, Mockbot)
        assert u.message.via_bot.username == "MockBot"

        b = Mockbot(username="AnotherBot")
        mg2 = MessageGenerator(bot=b)
        u = mg2.get_message()
        assert u.message.via_bot.username == "AnotherBot"

        with pytest.raises(BadBotException):
            MessageGenerator(bot="Yeah!")

    def test_private_message(self):
        u = MessageGenerator().get_message(private=True)
        assert u.message.from_user.id == u.message.chat.id

    def test_not_private(self):
        u = MessageGenerator().get_message(private=False)
        assert u.message.chat.type == "group"
        assert u.message.from_user.id != u.message.chat.id

    def test_with_user(self):
        user = UserGenerator().get_user()
        u = MessageGenerator().get_message(user=user, private=False)

        assert u.message.from_user.id == user.id
        assert u.message.from_user.id != u.message.chat.id

        u = MessageGenerator().get_message(user=user)
        assert u.message.from_user == user
        assert u.message.from_user.id == u.message.chat.id

        with pytest.raises(BadUserException):
            MessageGenerator().get_message(user="not a telegram.User")

    def test_with_chat(self):
        cg = ChatGenerator()
        chat = cg.get_chat()
        u = MessageGenerator().get_message(chat=chat)
        assert u.message.chat.id == u.message.from_user.id
        assert u.message.chat.id == chat.id

        chat = cg.get_chat(type="group")
        u = MessageGenerator().get_message(chat=chat)
        assert u.message.from_user.id != u.message.chat.id
        assert u.message.chat.id == chat.id

        with pytest.raises(BadChatException, match="get_channel_post"):
            chat = cg.get_chat(type="channel")
            MessageGenerator().get_message(chat=chat)

        with pytest.raises(BadChatException):
            MessageGenerator().get_message(chat="Not a telegram.Chat")

    def test_with_chat_and_user(self):
        cg = ChatGenerator()
        ug = UserGenerator()
        us = ug.get_user()
        c = cg.get_chat()
        u = MessageGenerator().get_message(user=us, chat=c)
        assert u.message.from_user.id != u.message.chat.id
        assert u.message.from_user.id == us.id
        assert u.message.chat.id == c.id

        with pytest.raises(BadUserException):
            MessageGenerator().get_message(user="not a telegram.User")
        with pytest.raises(BadUserException):
            MessageGenerator().get_message(chat=c, user="user")

        with pytest.raises(BadChatException):
            MessageGenerator().get_message(chat="Not a telegram.Chat")
        with pytest.raises(BadChatException):
            MessageGenerator().get_message(user=u, chat="chat")


class TestMessageGeneratorText:
    def test_simple_text(self):
        u = MessageGenerator().get_message(text="This is a test")
        assert u.message.text == "This is a test"

    def test_text_with_markdown(self):
        teststr = ("we have *bold* `code` [google](www.google.com) "
                   "@username #hashtag _italics_ ```pre block``` "
                   "ftp://snt.utwente.nl /start")
        u = MessageGenerator().get_message(text=teststr)
        assert u.message.text == teststr

        u = MessageGenerator().get_message(text=teststr, parse_mode="Markdown")
        assert len(u.message.entities) == 9
        for ent in u.message.entities:
            if ent.type == "bold":
                assert ent.offset == 8
                assert ent.length == 4
            elif ent.type == "code":
                assert ent.offset == 13
                assert ent.length == 4
            elif ent.type == "italic":
                assert ent.offset == 44
                assert ent.length == 7
            elif ent.type == "pre":
                assert ent.offset == 52
                assert ent.length == 9
            elif ent.type == "text_link":
                assert ent.offset == 18
                assert ent.length == 6
                assert ent.url == "www.google.com"
            elif ent.type == "mention":
                assert ent.offset == 25
                assert ent.length == 9
            elif ent.type == "hashtag":
                assert ent.offset == 35
                assert ent.length == 8
            elif ent.type == "url":
                assert ent.offset == 62
                assert ent.length == 20
            elif ent.type == "bot_command":
                assert ent.offset == 83
                assert ent.length == 6

        with pytest.raises(BadMarkupException):
            MessageGenerator().get_message(
                text="bad *_double_* markdown", parse_mode="Markdown")

    def test_with_html(self):
        teststr = ("we have <b>bold</b> <code>code</code> "
                   "<a href='www.google.com'>google</a> @username "
                   "#hashtag <i>italics</i> <pre>pre block</pre> "
                   "ftp://snt.utwente.nl /start")
        u = MessageGenerator().get_message(text=teststr)
        assert u.message.text == teststr

        u = MessageGenerator().get_message(text=teststr, parse_mode="HTML")
        assert len(u.message.entities) == 9
        for ent in u.message.entities:
            if ent.type == "bold":
                assert ent.offset == 8
                assert ent.length == 4
            elif ent.type == "code":
                assert ent.offset == 13
                assert ent.length == 4
            elif ent.type == "italic":
                assert ent.offset == 44
                assert ent.length == 7
            elif ent.type == "pre":
                assert ent.offset == 52
                assert ent.length == 9
            elif ent.type == "text_link":
                assert ent.offset == 18
                assert ent.length == 6
                assert ent.url == "www.google.com"
            elif ent.type == "mention":
                assert ent.offset == 25
                assert ent.length == 9
            elif ent.type == "hashtag":
                assert ent.offset == 35
                assert ent.length == 8
            elif ent.type == "url":
                assert ent.offset == 62
                assert ent.length == 20
            elif ent.type == "bot_command":
                assert ent.offset == 83
                assert ent.length == 6

        with pytest.raises(BadMarkupException):
            MessageGenerator().get_message(
                text="bad <b><i>double</i></b> markup", parse_mode="HTML")

    def test_wrong_markup(self):
        with pytest.raises(BadMarkupException):
            MessageGenerator().get_message(text="text", parse_mode="htmarkdownl")


class TestMessageGeneratorReplies:
    def test_reply(self):
        u1 = MessageGenerator().get_message(text="this is the first")
        u2 = MessageGenerator().get_message(
            text="This is the second", reply_to_message=u1.message)
        assert u1.message.text == u2.message.reply_to_message.text

        with pytest.raises(BadMessageException):
            MessageGenerator().get_message(reply_to_message="This is not a Messages")


class TestMessageGeneratorForwards:

    @pytest.fixture(scope="function")
    def mock_group_chat(self):
        return ChatGenerator().get_chat(type="group")

    @pytest.mark.xfail(reason="telegram.Message must be updated to the most recent API version")
    def test_forwarded_message(self):
        """
        The API of the PTB v21.x doesn't have 'forward_from' attribute
        in the Message object.
        """
        u1 = UserGenerator().get_user()
        u2 = UserGenerator().get_user()
        c = ChatGenerator().get_chat(type="group")
        u = MessageGenerator().get_message(
            user=u1, chat=c, forward_from=u2, text="This is a test")
        assert u.message.from_user.id == u1.id
        assert u.message.forward_from.id == u2.id
        assert u.message.from_user.id != u.message.forward_from.id
        assert u.message.text == "This is a test"
        assert isinstance(u.message.forward_date, int)
        MessageGenerator().get_message(
            forward_from=u2, forward_date=datetime.datetime.now())

        with pytest.raises(BadUserException):
            MessageGenerator().get_message(
                user=u1,
                chat=c,
                forward_from="This is not a User",
                text="This is a test")

    @pytest.mark.xfail(reason="telegram.Message must be updated to the most recent API version")
    def test_forwarded_channel_message(self, mock_group_chat):
        """
        The API of the PTB v21.x doesn't have 'forward_from' attribute
        in the Message object.
        """
        c = ChatGenerator().get_chat(type="channel")
        us = UserGenerator().get_user()
        u = MessageGenerator().get_message(
            text="This is a test", forward_from=us, forward_from_chat=c)
        assert u.message.chat.id != c.id
        assert u.message.from_user.id != us.id
        assert u.message.forward_from.id == us.id
        assert u.message.text == "This is a test"
        assert isinstance(u.message.forward_from_message_id, int)
        assert isinstance(u.message.forward_date, int)

        u = MessageGenerator().get_message(text="This is a test", forward_from_chat=c)
        assert u.message.from_user.id != u.message.forward_from.id
        assert isinstance(u.message.forward_from, User)
        assert isinstance(u.message.forward_from_message_id, int)
        assert isinstance(u.message.forward_date, int)

        with pytest.raises(BadChatException):
            u = MessageGenerator().get_message(
                    text="This is a test",
                    forward_from_chat="Not a Chat")

        with pytest.raises(BadChatException):
            u = MessageGenerator().get_message(
                    text="This is a test",
                    forward_from_chat=mock_group_chat)


class TestMessageGeneratorStatusMessages:
    def test_new_chat_member(self):
        user = UserGenerator().get_user()
        chat = ChatGenerator().get_chat(type="group")
        u = MessageGenerator().get_message(chat=chat, new_chat_members=[user])
        assert u.message.new_chat_members[0].id == user.id

        with pytest.raises(BadChatException):
            MessageGenerator().get_message(new_chat_members=[user])

        with pytest.raises(BadUserException):
            MessageGenerator().get_message(chat=chat, new_chat_members="user")

    def test_left_chat_member(self):
        user = UserGenerator().get_user()
        chat = ChatGenerator().get_chat(type='group')
        u = MessageGenerator().get_message(chat=chat, left_chat_member=user)
        assert u.message.left_chat_member.id == user.id

        with pytest.raises(BadChatException):
            MessageGenerator().get_message(left_chat_member=user)
        with pytest.raises(BadUserException):
            MessageGenerator().get_message(chat=chat, left_chat_member="user")

    @pytest.mark.xfail(reason="telegram.Message must be updated to the most recent API version")
    def test_new_chat_title(self):
        """
        This test works with the PTB v13.5 but doesn't work the v21.x
        """
        chat = ChatGenerator().get_chat(type="group")
        u = MessageGenerator().get_message(chat=chat, new_chat_title="New title")
        assert u.message.chat.title == "New title"
        assert u.message.chat.title == chat.title

        with pytest.raises(BadChatException):
            MessageGenerator().get_message(new_chat_title="New title")

    def test_new_chat_photo(self):
        chat = ChatGenerator().get_chat(type="group")
        u = MessageGenerator().get_message(chat=chat, new_chat_photo=True)
        assert isinstance(u.message.new_chat_photo, Sequence)
        assert isinstance(u.message.new_chat_photo[0], PhotoSize)
        photo = [PhotoSize("2", "photo_unique_id", 1, 1, file_size=3)]
        u = MessageGenerator().get_message(chat=chat, new_chat_photo=photo)
        assert len(u.message.new_chat_photo) == 1

        with pytest.raises(BadChatException):
            MessageGenerator().get_message(new_chat_photo=True)

        photo = "foto's!"
        with pytest.raises(BadMessageException):
            MessageGenerator().get_message(chat=chat, new_chat_photo=photo)
        with pytest.raises(BadMessageException):
            MessageGenerator().get_message(chat=chat, new_chat_photo=[1, 2, 3])

    @pytest.mark.xfail(reason="telegram.Message must be updated to the most recent API version")
    def test_pinned_message(self):
        """
        This test works with the PTB v13.5 but doesn't work the v21.x
        """
        chat = ChatGenerator().get_chat(type="supergroup")
        message = MessageGenerator().get_message(
            chat=chat, text="this will be pinned").message
        u = MessageGenerator().get_message(chat=chat, pinned_message=message)
        assert u.message.pinned_message.text == "this will be pinned"

        with pytest.raises(BadChatException):
            MessageGenerator().get_message(pinned_message=message)
        with pytest.raises(BadMessageException):
            MessageGenerator().get_message(chat=chat, pinned_message="message")

    def test_multiple_statusmessages(self):
        with pytest.raises(BadMessageException):
            MessageGenerator().get_message(
                private=False,
                new_chat_members=UserGenerator().get_user(),
                new_chat_title="New title")


class TestMessageGeneratorAttachments:
    def test_caption_solo(self):
        with pytest.raises(BadMessageException, match="caption without"):
            MessageGenerator().get_message(caption="my cap")

    def test_more_than_one(self):
        with pytest.raises(BadMessageException, match="more than one"):
            MessageGenerator().get_message(photo=True, video=True)

    def test_location(self):
        loc = Location(50.012, -32.11)
        u = MessageGenerator().get_message(location=loc)
        assert loc.longitude == u.message.location.longitude

        u = MessageGenerator().get_message(location=True)
        assert isinstance(u.message.location, Location)

        with pytest.raises(BadMessageException, match=r"telegram\.Location"):
            MessageGenerator().get_message(location="location")

    def test_venue(self):
        ven = Venue(Location(1.0, 1.0), "some place", "somewhere")
        u = MessageGenerator().get_message(venue=ven)
        assert u.message.venue.title == ven.title

        u = MessageGenerator().get_message(venue=True)
        assert isinstance(u.message.venue, Venue)

        with pytest.raises(BadMessageException, match=r"telegram.Venue"):
            MessageGenerator().get_message(venue="Venue")

    def test_contact(self):
        con = Contact("0612345", "testman")
        u = MessageGenerator().get_message(contact=con)
        assert con.phone_number == u.message.contact.phone_number

        u = MessageGenerator().get_message(contact=True)
        assert isinstance(u.message.contact, Contact)

        with pytest.raises(BadMessageException, match=r"telegram.Contact"):
            MessageGenerator().get_message(contact="contact")

    def test_voice(self):
        voice = Voice("idyouknow", 12, 1)
        u = MessageGenerator().get_message(voice=voice)
        assert voice.file_id == u.message.voice.file_id

        cap = "voice file"
        u = MessageGenerator().get_message(voice=voice, caption=cap)
        assert u.message.caption == cap

        u = MessageGenerator().get_message(voice=True)
        assert isinstance(u.message.voice, Voice)

        with pytest.raises(BadMessageException, match=r"telegram\.Voice"):
            MessageGenerator().get_message(voice="voice")

    def test_video(self):
        video = Video("idyouknow", "file_unique_id", 200, 200, 10)
        u = MessageGenerator().get_message(video=video)
        assert video.file_id == u.message.video.file_id

        cap = "video file"
        u = MessageGenerator().get_message(video=video, caption=cap)
        assert u.message.caption == cap

        u = MessageGenerator().get_message(video=True)
        assert isinstance(u.message.video, Video)

        with pytest.raises(BadMessageException, match=r"telegram\.Video"):
            MessageGenerator().get_message(video="video")

    def test_sticker(self):
        sticker = Sticker("idyouknow", "sticker_unique_id", 30, 30, True, True, "REGULAR")
        u = MessageGenerator().get_message(sticker=sticker)
        assert sticker.file_id == u.message.sticker.file_id

        cap = "sticker file"
        u = MessageGenerator().get_message(sticker=sticker, caption=cap)
        assert u.message.caption == cap

        u = MessageGenerator().get_message(sticker=True)
        assert isinstance(u.message.sticker, Sticker)

        with pytest.raises(BadMessageException, match=r"telegram\.Sticker"):
            MessageGenerator().get_message(sticker="sticker")

    def test_document(self):
        document = Document("document_id", "idyouknow", file_name="test.pdf")
        u = MessageGenerator().get_message(document=document)
        assert document.file_id == u.message.document.file_id

        cap = "document file"
        u = MessageGenerator().get_message(document=document, caption=cap)
        assert u.message.caption == cap

        u = MessageGenerator().get_message(document=True)
        assert isinstance(u.message.document, Document)

        with pytest.raises(BadMessageException, match=r"telegram\.Document"):
            MessageGenerator().get_message(document="document")

    def test_audio(self):
        audio = Audio("idyouknow", 23, 60)
        u = MessageGenerator().get_message(audio=audio)
        assert audio.file_id == u.message.audio.file_id

        cap = "audio file"
        u = MessageGenerator().get_message(audio=audio, caption=cap)
        assert u.message.caption == cap

        u = MessageGenerator().get_message(audio=True)
        assert isinstance(u.message.audio, Audio)

        with pytest.raises(BadMessageException, match=r"telegram\.Audio"):
            MessageGenerator().get_message(audio="audio")

    def test_photo(self):
        photo = [PhotoSize("2", "photo_unique_id", 1, 1, file_size=3)]
        u = MessageGenerator().get_message(photo=photo)
        assert photo[0].file_size == u.message.photo[0].file_size

        cap = "photo file"
        u = MessageGenerator().get_message(photo=photo, caption=cap)
        assert u.message.caption == cap

        u = MessageGenerator().get_message(photo=True)
        assert isinstance(u.message.photo, tuple)
        assert isinstance(u.message.photo[0], PhotoSize)

        with pytest.raises(BadMessageException, match=r"telegram\.Photo"):
            MessageGenerator().get_message(photo="photo")

        with pytest.raises(BadMessageException, match=r"telegram\.Photo"):
            MessageGenerator().get_message(photo=[1, 2, 3])

class TestMessageGeneratorEditedMessage:
    def test_edited_message(self):
        u = MessageGenerator().get_edited_message()
        assert isinstance(u.edited_message, Message)
        assert isinstance(u, Update)

    def test_with_parameters(self):
        u = MessageGenerator().get_edited_message(
            text="New *text*", parse_mode="Markdown")
        assert u.edited_message.text == "New text"
        assert len(u.edited_message.entities) == 1

    def test_with_message(self):
        m = MessageGenerator().get_message(text="first").message
        u = MessageGenerator().get_edited_message(message=m, text="second")
        assert m.message_id == u.edited_message.message_id
        assert m.chat.id == u.edited_message.chat.id
        assert m.from_user.id == u.edited_message.from_user.id
        assert u.edited_message.text == "second"

        with pytest.raises(BadMessageException):
            MessageGenerator().get_edited_message(message="Message")


class TestMessageGeneratorChannelPost:
    def test_channel_post(self):
        u = MessageGenerator().get_channel_post()
        assert isinstance(u, Update)
        assert isinstance(u.channel_post, Message)
        assert u.channel_post.chat.type == "channel"
        assert u.channel_post.from_user is None

    def test_with_chat(self):
        cg = ChatGenerator()
        group = cg.get_chat(type="group")
        channel = cg.get_chat(type="channel")
        u = MessageGenerator().get_channel_post(chat=channel)
        assert channel.title == u.channel_post.chat.title

        with pytest.raises(BadChatException, match=r"telegram\.Chat"):
            MessageGenerator().get_channel_post(chat="chat")

        with pytest.raises(BadChatException, match=r"chat\.type") as exc2:
            MessageGenerator().get_channel_post(chat=group)

    def test_with_user(self):
        ug = UserGenerator()
        user = ug.get_user()
        u = MessageGenerator().get_channel_post(user=user)
        assert u.channel_post.from_user.id == user.id

    def test_with_content(self):
        u = MessageGenerator().get_channel_post(
            text="this is *bold* _italic_", parse_mode="Markdown")
        assert u.channel_post.text == "this is bold italic"
        assert len(u.channel_post.entities) == 2


class TestMessageGeneratorEditedChannelPost:
    def test_edited_channel_post(self):
        u = MessageGenerator().get_edited_channel_post()
        assert isinstance(u.edited_channel_post, Message)
        assert isinstance(u, Update)

    def test_with_parameters(self):
        u = MessageGenerator().get_edited_channel_post(
            text="New *text*", parse_mode="Markdown")
        assert u.edited_channel_post.text == "New text"
        assert len(u.edited_channel_post.entities) == 1

    def test_with_channel_post(self):
        m = MessageGenerator().get_channel_post(text="first").channel_post
        u = MessageGenerator().get_edited_channel_post(channel_post=m, text="second")
        assert m.message_id == u.edited_channel_post.message_id
        assert m.chat.id == u.edited_channel_post.chat.id
        assert u.edited_channel_post.text == "second"

        with pytest.raises(BadMessageException):
            MessageGenerator().get_edited_channel_post(channel_post="Message")
