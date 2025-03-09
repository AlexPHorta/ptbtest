# Pylint has problems in recognizing proper type of get_message() function
# because of decorator used. To clear those errors it is required
# to disable "maybe-no-member".
# pylint: disable=E1101

from __future__ import absolute_import

import unittest

from telegram import (Audio, Contact, Document, Location, Message, PhotoSize,
                      Sticker, Update, User, Venue, Video, Voice)

from ptbtest import (BadBotException, BadChatException, BadMarkupException,
                     BadMessageException, BadUserException, ChatGenerator,
                     MessageGenerator, Mockbot, UserGenerator)


class TestMessageGeneratorCore(unittest.TestCase):

    def setUp(self):
        self.mg = MessageGenerator()

    def test_is_update(self):
        u = self.mg.get_message()
        self.assertIsInstance(u, Update)
        self.assertIsInstance(u.message, Message)

    def test_bot(self):
        u = self.mg.get_message()
        self.assertIsInstance(u.message.bot, Mockbot)
        self.assertEqual(u.message.bot.username, "MockBot")

        b = Mockbot(username="AnotherBot")
        mg2 = MessageGenerator(bot=b)
        u = mg2.get_message()
        self.assertEqual(u.message.bot.username, "AnotherBot")

        with self.assertRaises(BadBotException):
            mg3 = MessageGenerator(bot="Yeah!")

    def test_private_message(self):
        u = self.mg.get_message(private=True)
        self.assertEqual(u.message.from_user.id, u.message.chat.id)

    def test_not_private(self):
        u = self.mg.get_message(private=False)
        self.assertEqual(u.message.chat.type, "group")
        self.assertNotEqual(u.message.from_user.id, u.message.chat.id)

    def test_with_user(self):
        ug = UserGenerator()
        us = ug.get_user()
        u = self.mg.get_message(user=us, private=False)
        self.assertEqual(u.message.from_user.id, us.id)
        self.assertNotEqual(u.message.from_user.id, u.message.chat.id)

        u = self.mg.get_message(user=us)
        self.assertEqual(u.message.from_user, us)
        self.assertEqual(u.message.from_user.id, u.message.chat.id)

        with self.assertRaises(BadUserException):
            us = "not a telegram.User"
            u = self.mg.get_message(user=us)

    def test_with_chat(self):
        cg = ChatGenerator()
        c = cg.get_chat()
        u = self.mg.get_message(chat=c)
        self.assertEqual(u.message.chat.id, u.message.from_user.id)
        self.assertEqual(u.message.chat.id, c.id)

        c = cg.get_chat(chat_type="group")
        u = self.mg.get_message(chat=c)
        self.assertNotEqual(u.message.from_user.id, u.message.chat.id)
        self.assertEqual(u.message.chat.id, c.id)

        with self.assertRaisesRegex(BadChatException, "get_channel_post"):
            c = cg.get_chat(chat_type="channel")
            self.mg.get_message(chat=c)

        with self.assertRaises(BadChatException):
            c = "Not a telegram.Chat"
            self.mg.get_message(chat=c)

    def test_with_chat_and_user(self):
        cg = ChatGenerator()
        ug = UserGenerator()
        us = ug.get_user()
        c = cg.get_chat()
        u = self.mg.get_message(user=us, chat=c)
        self.assertNotEqual(u.message.from_user.id, u.message.chat.id)
        self.assertEqual(u.message.from_user.id, us.id)
        self.assertEqual(u.message.chat.id, c.id)

        us = "not a telegram.User"
        with self.assertRaises(BadUserException):
            u = self.mg.get_message(user=us)
        with self.assertRaises(BadUserException):
            u = self.mg.get_message(chat=c, user="user")

        c = "Not a telegram.Chat"
        with self.assertRaises(BadChatException):
            self.mg.get_message(chat=c)
        with self.assertRaises(BadChatException):
            self.mg.get_message(user=u, chat="chat")


class TestMessageGeneratorText(unittest.TestCase):

    def setUp(self):
        self.mg = MessageGenerator()

    def test_simple_text(self):
        u = self.mg.get_message(text="This is a test")
        self.assertEqual(u.message.text, "This is a test")

    def test_text_with_markdown(self):
        teststr = "we have *bold* `code` [google](www.google.com) @username #hashtag _italics_ ```pre block``` " \
                  "ftp://snt.utwente.nl /start"
        u = self.mg.get_message(text=teststr)
        self.assertEqual(u.message.text, teststr)

        u = self.mg.get_message(text=teststr, parse_mode="Markdown")
        self.assertEqual(len(u.message.entities), 9)
        for ent in u.message.entities:
            if ent.type == "bold":
                self.assertEqual(ent.offset, 8)
                self.assertEqual(ent.length, 4)
            elif ent.type == "code":
                self.assertEqual(ent.offset, 13)
                self.assertEqual(ent.length, 4)
            elif ent.type == "italic":
                self.assertEqual(ent.offset, 44)
                self.assertEqual(ent.length, 7)
            elif ent.type == "pre":
                self.assertEqual(ent.offset, 52)
                self.assertEqual(ent.length, 9)
            elif ent.type == "text_link":
                self.assertEqual(ent.offset, 18)
                self.assertEqual(ent.length, 6)
                self.assertEqual(ent.url, "www.google.com")
            elif ent.type == "mention":
                self.assertEqual(ent.offset, 25)
                self.assertEqual(ent.length, 9)
            elif ent.type == "hashtag":
                self.assertEqual(ent.offset, 35)
                self.assertEqual(ent.length, 8)
            elif ent.type == "url":
                self.assertEqual(ent.offset, 62)
                self.assertEqual(ent.length, 20)
            elif ent.type == "bot_command":
                self.assertEqual(ent.offset, 83)
                self.assertEqual(ent.length, 6)

        with self.assertRaises(BadMarkupException):
            self.mg.get_message(text="bad *_double_* markdown",
                                parse_mode="Markdown")

    def test_with_html(self):
        teststr = "we have <b>bold</b> <code>code</code> <a href='www.google.com'>google</a> @username #hashtag " \
                  "<i>italics</i> <pre>pre block</pre> ftp://snt.utwente.nl /start"
        u = self.mg.get_message(text=teststr)
        self.assertEqual(u.message.text, teststr)

        u = self.mg.get_message(text=teststr, parse_mode="HTML")
        self.assertEqual(len(u.message.entities), 9)
        for ent in u.message.entities:
            if ent.type == "bold":
                self.assertEqual(ent.offset, 8)
                self.assertEqual(ent.length, 4)
            elif ent.type == "code":
                self.assertEqual(ent.offset, 13)
                self.assertEqual(ent.length, 4)
            elif ent.type == "italic":
                self.assertEqual(ent.offset, 44)
                self.assertEqual(ent.length, 7)
            elif ent.type == "pre":
                self.assertEqual(ent.offset, 52)
                self.assertEqual(ent.length, 9)
            elif ent.type == "text_link":
                self.assertEqual(ent.offset, 18)
                self.assertEqual(ent.length, 6)
                self.assertEqual(ent.url, "www.google.com")
            elif ent.type == "mention":
                self.assertEqual(ent.offset, 25)
                self.assertEqual(ent.length, 9)
            elif ent.type == "hashtag":
                self.assertEqual(ent.offset, 35)
                self.assertEqual(ent.length, 8)
            elif ent.type == "url":
                self.assertEqual(ent.offset, 62)
                self.assertEqual(ent.length, 20)
            elif ent.type == "bot_command":
                self.assertEqual(ent.offset, 83)
                self.assertEqual(ent.length, 6)

        with self.assertRaises(BadMarkupException):
            self.mg.get_message(text="bad <b><i>double</i></b> markup",
                                parse_mode="HTML")

    def test_wrong_markup(self):
        with self.assertRaises(BadMarkupException):
            self.mg.get_message(text="text", parse_mode="htmarkdownl")


class TestMessageGeneratorReplies(unittest.TestCase):

    def setUp(self):
        self.mg = MessageGenerator()

    def test_reply(self):
        u1 = self.mg.get_message(text="this is the first")
        u2 = self.mg.get_message(text="This is the second",
                                 reply_to_message=u1.message)
        self.assertEqual(u1.message.text, u2.message.reply_to_message.text)

        with self.assertRaises(BadMessageException):
            u = "This is not a Messages"
            self.mg.get_message(reply_to_message=u)


class TestMessageGeneratorForwards(unittest.TestCase):

    def setUp(self):
        self.mg = MessageGenerator()
        self.ug = UserGenerator()
        self.cg = ChatGenerator()

    def test_forwarded_message(self):
        u1 = self.ug.get_user()
        u2 = self.ug.get_user()
        c = self.cg.get_chat(chat_type="group")
        u = self.mg.get_message(user=u1,
                                chat=c,
                                forward_from=u2,
                                text="This is a test")
        self.assertEqual(u.message.from_user.id, u1.id)
        self.assertEqual(u.message.forward_from.id, u2.id)
        self.assertNotEqual(u.message.from_user.id, u.message.forward_from.id)
        self.assertEqual(u.message.text, "This is a test")
        self.assertIsInstance(u.message.forward_date, int)
        import datetime
        self.mg.get_message(forward_from=u2,
                            forward_date=datetime.datetime.now())

        with self.assertRaises(BadUserException):
            u3 = "This is not a User"
            u = self.mg.get_message(user=u1,
                                    chat=c,
                                    forward_from=u3,
                                    text="This is a test")

    def test_forwarded_channel_message(self):
        c = self.cg.get_chat(chat_type="channel")
        us = self.ug.get_user()
        u = self.mg.get_message(text="This is a test",
                                forward_from=us,
                                forward_from_chat=c)
        self.assertNotEqual(u.message.chat.id, c.id)
        self.assertNotEqual(u.message.from_user.id, us.id)
        self.assertEqual(u.message.forward_from.id, us.id)
        self.assertEqual(u.message.text, "This is a test")
        self.assertIsInstance(u.message.forward_from_message_id, int)
        self.assertIsInstance(u.message.forward_date, int)

        u = self.mg.get_message(text="This is a test", forward_from_chat=c)
        self.assertNotEqual(u.message.from_user.id, u.message.forward_from.id)
        self.assertIsInstance(u.message.forward_from, User)
        self.assertIsInstance(u.message.forward_from_message_id, int)
        self.assertIsInstance(u.message.forward_date, int)

        with self.assertRaises(BadChatException):
            c = "Not a Chat"
            u = self.mg.get_message(text="This is a test", forward_from_chat=c)

        with self.assertRaises(BadChatException):
            c = self.cg.get_chat(chat_type="group")
            u = self.mg.get_message(text="This is a test", forward_from_chat=c)


class TestMessageGeneratorStatusMessages(unittest.TestCase):

    def setUp(self):
        self.mg = MessageGenerator()
        self.ug = UserGenerator()
        self.cg = ChatGenerator()

    def test_new_chat_member(self):
        user = self.ug.get_user()
        chat = self.cg.get_chat(chat_type="group")
        u = self.mg.get_message(chat=chat, new_chat_members=[user])
        self.assertEqual(len(u.message.new_chat_members), 1)
        self.assertEqual(u.message.new_chat_members[0].id, user.id)

        with self.assertRaises(BadChatException):
            self.mg.get_message(new_chat_members=[user])
        with self.assertRaises(BadUserException):
            self.mg.get_message(chat=chat, new_chat_members=["user"])

    def test_left_chat_member(self):
        user = self.ug.get_user()
        chat = self.cg.get_chat(chat_type='group')
        u = self.mg.get_message(chat=chat, left_chat_member=user)
        self.assertEqual(u.message.left_chat_member.id, user.id)

        with self.assertRaises(BadChatException):
            self.mg.get_message(left_chat_member=user)
        with self.assertRaises(BadUserException):
            self.mg.get_message(chat=chat, left_chat_member="user")

    def test_new_chat_title(self):
        chat = self.cg.get_chat(chat_type="group")
        u = self.mg.get_message(chat=chat, new_chat_title="New title")
        self.assertEqual(u.message.chat.title, "New title")
        self.assertEqual(u.message.chat.title, chat.title)

        with self.assertRaises(BadChatException):
            self.mg.get_message(new_chat_title="New title")

    def test_new_chat_photo(self):
        chat = self.cg.get_chat(chat_type="group")
        u = self.mg.get_message(chat=chat, new_chat_photo=True)
        self.assertIsInstance(u.message.new_chat_photo, list)
        self.assertIsInstance(u.message.new_chat_photo[0], PhotoSize)
        photo = [PhotoSize("2", "2", 1, 1, file_size=3)]
        u = self.mg.get_message(chat=chat, new_chat_photo=photo)
        self.assertEqual(len(u.message.new_chat_photo), 1)

        with self.assertRaises(BadChatException):
            self.mg.get_message(new_chat_photo=True)

        photo = "foto's!"
        with self.assertRaises(BadMessageException):
            self.mg.get_message(chat=chat, new_chat_photo=photo)
        with self.assertRaises(BadMessageException):
            self.mg.get_message(chat=chat, new_chat_photo=[1, 2, 3])

    def test_pinned_message(self):
        chat = self.cg.get_chat(chat_type="supergroup")
        message = self.mg.get_message(chat=chat,
                                      text="this will be pinned").message
        u = self.mg.get_message(chat=chat, pinned_message=message)
        self.assertEqual(u.message.pinned_message.text, "this will be pinned")

        with self.assertRaises(BadChatException):
            self.mg.get_message(pinned_message=message)
        with self.assertRaises(BadMessageException):
            self.mg.get_message(chat=chat, pinned_message="message")

    def test_multiple_statusmessages(self):
        with self.assertRaises(BadMessageException):
            self.mg.get_message(private=False,
                                new_chat_members=[self.ug.get_user()],
                                new_chat_title="New title")


class TestMessageGeneratorAttachments(unittest.TestCase):

    def setUp(self):
        self.mg = MessageGenerator()

    def test_caption_solo(self):
        with self.assertRaisesRegex(BadMessageException, r"caption without"):
            self.mg.get_message(caption="my cap")

    def test_more_than_one(self):
        with self.assertRaisesRegex(BadMessageException, "more than one"):
            self.mg.get_message(photo=True, video=True)

    def test_location(self):
        loc = Location(50.012, -32.11)
        u = self.mg.get_message(location=loc)
        self.assertEqual(loc.longitude, u.message.location.longitude)

        u = self.mg.get_message(location=True)
        self.assertIsInstance(u.message.location, Location)

        with self.assertRaisesRegex(BadMessageException,
                                    r"telegram\.Location"):
            self.mg.get_message(location="location")

    def test_venue(self):
        ven = Venue(Location(1.0, 1.0), "some place", "somewhere")
        u = self.mg.get_message(venue=ven)
        self.assertEqual(u.message.venue.title, ven.title)

        u = self.mg.get_message(venue=True)
        self.assertIsInstance(u.message.venue, Venue)

        with self.assertRaisesRegex(BadMessageException, r"telegram\.Venue"):
            self.mg.get_message(venue="Venue")

    def test_contact(self):
        con = Contact("0612345", "testman")
        u = self.mg.get_message(contact=con)
        self.assertEqual(con.phone_number, u.message.contact.phone_number)

        u = self.mg.get_message(contact=True)
        self.assertIsInstance(u.message.contact, Contact)

        with self.assertRaisesRegex(BadMessageException, r"telegram\.Contact"):
            self.mg.get_message(contact="contact")

    def test_voice(self):
        voice = Voice("idyouknow", "idyouknow", 12)
        u = self.mg.get_message(voice=voice)
        self.assertEqual(voice.file_id, u.message.voice.file_id)

        cap = "voice file"
        u = self.mg.get_message(voice=voice, caption=cap)
        self.assertEqual(u.message.caption, cap)

        u = self.mg.get_message(voice=True)
        self.assertIsInstance(u.message.voice, Voice)

        with self.assertRaisesRegex(BadMessageException, r"telegram\.Voice"):
            self.mg.get_message(voice="voice")

    def test_video(self):
        video = Video("idyouknow", "idyouknow", 200, 200, 10)
        u = self.mg.get_message(video=video)
        self.assertEqual(video.file_id, u.message.video.file_id)

        cap = "video file"
        u = self.mg.get_message(video=video, caption=cap)
        self.assertEqual(u.message.caption, cap)

        u = self.mg.get_message(video=True)
        self.assertIsInstance(u.message.video, Video)

        with self.assertRaisesRegex(BadMessageException, r"telegram\.Video"):
            self.mg.get_message(video="video")

    def test_sticker(self):
        sticker = Sticker("idyouknow", "idyouknow", 30, 30, False, False)
        u = self.mg.get_message(sticker=sticker)
        self.assertEqual(sticker.file_id, u.message.sticker.file_id)

        cap = "sticker file"
        u = self.mg.get_message(sticker=sticker, caption=cap)
        self.assertEqual(u.message.caption, cap)

        u = self.mg.get_message(sticker=True)
        self.assertIsInstance(u.message.sticker, Sticker)

        with self.assertRaisesRegex(BadMessageException, r"telegram\.Sticker"):
            self.mg.get_message(sticker="sticker")

    def test_document(self):
        document = Document("idyouknow", "idyouknow", file_name="test.pdf")
        u = self.mg.get_message(document=document)
        self.assertEqual(document.file_id, u.message.document.file_id)

        cap = "document file"
        u = self.mg.get_message(document=document, caption=cap)
        self.assertEqual(u.message.caption, cap)

        u = self.mg.get_message(document=True)
        self.assertIsInstance(u.message.document, Document)

        with self.assertRaisesRegex(BadMessageException,
                                    r"telegram\.Document"):
            self.mg.get_message(document="document")

    def test_audio(self):
        audio = Audio("idyouknow", "idyouknow", 23)
        u = self.mg.get_message(audio=audio)
        self.assertEqual(audio.file_id, u.message.audio.file_id)

        cap = "audio file"
        u = self.mg.get_message(audio=audio, caption=cap)
        self.assertEqual(u.message.caption, cap)

        u = self.mg.get_message(audio=True)
        self.assertIsInstance(u.message.audio, Audio)

        with self.assertRaisesRegex(BadMessageException, r"telegram\.Audio"):
            self.mg.get_message(audio="audio")

    def test_photo(self):
        photo = [PhotoSize("2", "2", 1, 1, file_size=3)]
        u = self.mg.get_message(photo=photo)
        self.assertEqual(photo[0].file_size, u.message.photo[0].file_size)

        cap = "photo file"
        u = self.mg.get_message(photo=photo, caption=cap)
        self.assertEqual(u.message.caption, cap)

        u = self.mg.get_message(photo=True)
        self.assertIsInstance(u.message.photo, list)
        self.assertIsInstance(u.message.photo[0], PhotoSize)

        with self.assertRaisesRegex(BadMessageException, r"telegram\.Photo"):
            self.mg.get_message(photo="photo")
        with self.assertRaisesRegex(BadMessageException, r"telegram\.Photo"):
            self.mg.get_message(photo=[1, 2, 3])


class TestMessageGeneratorEditedMessage(unittest.TestCase):

    def setUp(self):
        self.mg = MessageGenerator()

    def test_edited_message(self):
        u = self.mg.get_edited_message()
        self.assertIsInstance(u.edited_message, Message)
        self.assertIsInstance(u, Update)

    def test_with_parameters(self):
        u = self.mg.get_edited_message(text="New *text*",
                                       parse_mode="Markdown")
        self.assertEqual(u.edited_message.text, "New text")
        self.assertEqual(len(u.edited_message.entities), 1)

    def test_with_message(self):
        m = self.mg.get_message(text="first").message
        u = self.mg.get_edited_message(message=m, text="second")
        self.assertEqual(m.message_id, u.edited_message.message_id)
        self.assertEqual(m.chat.id, u.edited_message.chat.id)
        self.assertEqual(m.from_user.id, u.edited_message.from_user.id)
        self.assertEqual(u.edited_message.text, "second")

        with self.assertRaises(BadMessageException):
            self.mg.get_edited_message(message="Message")


class TestMessageGeneratorChannelPost(unittest.TestCase):

    def setUp(self):
        self.mg = MessageGenerator()

    def test_channel_post(self):
        u = self.mg.get_channel_post()
        self.assertIsInstance(u, Update)
        self.assertIsInstance(u.channel_post, Message)
        self.assertEqual(u.channel_post.chat.type, "channel")
        self.assertEqual(u.channel_post.from_user, None)

    def test_with_chat(self):
        cg = ChatGenerator()
        group = cg.get_chat(chat_type="group")
        channel = cg.get_chat(chat_type="channel")
        u = self.mg.get_channel_post(chat=channel)
        self.assertEqual(channel.title, u.channel_post.chat.title)

        with self.assertRaisesRegex(BadChatException, "telegram\.Chat"):
            self.mg.get_channel_post(chat="chat")
        with self.assertRaisesRegex(BadChatException, "chat\.type"):
            self.mg.get_channel_post(chat=group)

    def test_with_user(self):
        ug = UserGenerator()
        user = ug.get_user()
        u = self.mg.get_channel_post(user=user)
        self.assertEqual(u.channel_post.from_user.id, user.id)

    def test_with_content(self):
        u = self.mg.get_channel_post(text="this is *bold* _italic_",
                                     parse_mode="Markdown")
        self.assertEqual(u.channel_post.text, "this is bold italic")
        self.assertEqual(len(u.channel_post.entities), 2)


class TestMessageGeneratorEditedChannelPost(unittest.TestCase):

    def setUp(self):
        self.mg = MessageGenerator()

    def test_edited_channel_post(self):
        u = self.mg.get_edited_channel_post()
        self.assertIsInstance(u.edited_channel_post, Message)
        self.assertIsInstance(u, Update)

    def test_with_parameters(self):
        u = self.mg.get_edited_channel_post(text="New *text*",
                                            parse_mode="Markdown")
        self.assertEqual(u.edited_channel_post.text, "New text")
        self.assertEqual(len(u.edited_channel_post.entities), 1)

    def test_with_channel_post(self):
        m = self.mg.get_channel_post(text="first").channel_post
        u = self.mg.get_edited_channel_post(channel_post=m, text="second")
        self.assertEqual(m.message_id, u.edited_channel_post.message_id)
        self.assertEqual(m.chat.id, u.edited_channel_post.chat.id)
        self.assertEqual(u.edited_channel_post.text, "second")

        with self.assertRaises(BadMessageException):
            self.mg.get_edited_channel_post(channel_post="Message")


if __name__ == '__main__':
    unittest.main()
