from telegram import MessageEntity
from telegram.constants import MessageEntityType

from ptbtest.entityparser import EntityParser


class TestParseBotCommands:
    ep = EntityParser()

    def test_message_consists_of_command_only(self):
        result = self.ep.parse_bot_commands("/command")

        assert result == (MessageEntity(length=8, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_multiple_commands(self):
        result = self.ep.parse_bot_commands("/command and /command2")

        assert result ==  (MessageEntity(length=8, offset=0,
                                         type=MessageEntityType.BOT_COMMAND),
                           MessageEntity(length=9, offset=13,
                                         type=MessageEntityType.BOT_COMMAND))

    def test_at_the_beginning_of_the_text(self):
        result = self.ep.parse_bot_commands("/command with text afterwards")

        assert result == (MessageEntity(length=8, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_in_the_middle_of_the_text(self):
        result = self.ep.parse_bot_commands("A command /inside text")

        assert result == (MessageEntity(length=7, offset=10,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_at_the_end_of_the_text(self):
        result = self.ep.parse_bot_commands("A command at the /end")

        assert result == (MessageEntity(length=4, offset=17,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_one_character_command(self):
        result = self.ep.parse_bot_commands("/c")

        assert result == (MessageEntity(length=2, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_64_characters_command(self):
        text = "/abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz0123456789_1"

        result = self.ep.parse_bot_commands(text)

        assert result == (MessageEntity(length=65, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_65_characters_command(self):
        text = "/abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz0123456789_12"

        result = self.ep.parse_bot_commands(text)

        assert result == ()

    def test_all_allowed_characters(self):
        result = self.ep.parse_bot_commands("/underscored_command_12")

        assert result == (MessageEntity(length=23, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_underscore_in_command_only(self):
        result = self.ep.parse_bot_commands("/_")

        assert result == (MessageEntity(length=2, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_special_characters(self):
        result = self.ep.parse_bot_commands("/%$#!")

        assert result == ()

    def test_trailing_whitespace(self):
        result = self.ep.parse_bot_commands("/command  ")

        assert result == (MessageEntity(length=8, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_leading_whitespace(self):
        result = self.ep.parse_bot_commands("  /command")

        assert result == (MessageEntity(length=8, offset=2,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_whitespaces_around_command(self):
        result = self.ep.parse_bot_commands("  /command  ")

        assert result == (MessageEntity(length=8, offset=2,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_trailing_slash(self):
        result = self.ep.parse_bot_commands("/command/")

        assert result == ()

    def test_with_bot_mention(self):
        result = self.ep.parse_bot_commands("/command@botname")

        assert result == (MessageEntity(length=16, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_with_too_short_bot_mention(self):
        # The minimum length of the mention must be 3 characters.
        result = self.ep.parse_bot_commands("/command@bo")

        assert result == (MessageEntity(length=8, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_with_bot_mention_exactly_32_chars(self):
        result = self.ep.parse_bot_commands("/command@abcdefghijklmnopqrstuvwxyz123456")

        assert result == (MessageEntity(length=41, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_with_too_long_bot_mention(self):
        result = self.ep.parse_bot_commands("/command@abcdefghijklmnopqrstuvwxyz1234567")

        assert result == (MessageEntity(length=8, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_uppercase_command(self):
        result = self.ep.parse_bot_commands("/COMMAND")

        assert result == (MessageEntity(length=8, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_lowercase_command(self):
        result = self.ep.parse_bot_commands("/command")

        assert result == (MessageEntity(length=8, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_mix_cased_command(self):
        result = self.ep.parse_bot_commands("/coMManD")

        assert result == (MessageEntity(length=8, offset=0,
                                        type=MessageEntityType.BOT_COMMAND),)

    def test_utf16_offset(self):
        text = "😄😄😄/command"

        result = self.ep.parse_bot_commands(text)

        assert result == (MessageEntity(length=8, offset=6, type=MessageEntityType.BOT_COMMAND),)

    def test_command_from_numbers_only(self):
        assert self.ep.parse_bot_commands("/1234") == (MessageEntity(length=5, offset=0, type=MessageEntityType.BOT_COMMAND),)
        assert self.ep.parse_bot_commands("rdar:/1234") == (MessageEntity(length=5, offset=5, type=MessageEntityType.BOT_COMMAND),)
