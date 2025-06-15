from telegram import MessageEntity
from telegram.constants import MessageEntityType

from ptbtest.entityparser import EntityParser


class TestParseHashtags:
    ep = EntityParser()

    def test_empty_string(self):
        result = self.ep.parse_hashtags("")

        assert result == ()

    def test_text_without_hashtags(self):
        text = "Hello world!"

        result = self.ep.parse_hashtags(text)

        assert result == ()

    def test_one_char_length_hashtag(self):
        result = self.ep.parse_hashtags("#h")

        assert result == (MessageEntity(length=2, offset=0, type=MessageEntityType.HASHTAG),)

    def test_multiple_hash_tags(self):
        result = self.ep.parse_hashtags("#hash #tag")

        assert result == (MessageEntity(length=5, offset=0, type=MessageEntityType.HASHTAG),
                          MessageEntity(length=4, offset=6, type=MessageEntityType.HASHTAG))

    def test_max_length__256_symbols(self):
        result = self.ep.parse_hashtags("#" + "a" * 256)

        assert result == (MessageEntity(length=257, offset=0, type=MessageEntityType.HASHTAG),)

    def test_more_than_max_length__257_symbols(self):
        result = self.ep.parse_hashtags("#" + "a" * 257)

        assert result == (MessageEntity(length=257, offset=0, type=MessageEntityType.HASHTAG),)

    def test_non_ascii_symbols(self):
        text = "#٢٣٤_你好世界"

        result = self.ep.parse_hashtags(text)

        assert result == (MessageEntity(length=9, offset=0, type=MessageEntityType.HASHTAG),)

    def test_with_mention(self):
        text = "#hashtag@mention"

        result = self.ep.parse_hashtags(text)

        assert result == (MessageEntity(length=16, offset=0, type=MessageEntityType.HASHTAG),)

    def test_with_too_small_mention_up_to_3_chars(self):
        expected = (MessageEntity(length=8, offset=0, type=MessageEntityType.HASHTAG),)

        assert self.ep.parse_hashtags("#hashtag@") == expected
        assert self.ep.parse_hashtags("#hashtag@a") == expected
        assert self.ep.parse_hashtags("#hashtag@ab") == expected
        assert self.ep.parse_hashtags("#hashtag@a-b") == expected

    def test_hash_tag_with_middle_dot(self):
        text = "#hash·tag"

        result = self.ep.parse_hashtags(text)

        assert result == (MessageEntity(length=9, offset=0, type=MessageEntityType.HASHTAG),)

    def test_with_max_allowed_length_mention__32_chars(self):
        text = "#hashtag@" + "a" * 32

        result = self.ep.parse_hashtags(text)

        assert result == (MessageEntity(length=41, offset=0, type=MessageEntityType.HASHTAG),)

    def test_with_too_long_mention__33_chars(self):
        text = "#hashtag@" + "a" * 33

        result = self.ep.parse_hashtags(text)

        assert result == (MessageEntity(length=41, offset=0, type=MessageEntityType.HASHTAG),)

    def test_with_mention_and_with_hash_sign_at_the_end_of_mention(self):
        text = "#hashtag@username#"

        result = self.ep.parse_hashtags(text)

        assert result == (MessageEntity(length=8, offset=0, type=MessageEntityType.HASHTAG),)

    def test_string_consists_of_hash_sign_only(self):
        assert self.ep.parse_hashtags("#") == ()
        assert self.ep.parse_hashtags("##") == ()
        assert self.ep.parse_hashtags("##############") == ()

    def test_hash_sign_at_the_end(self):
        assert self.ep.parse_hashtags("hashtag#") == ()
        assert self.ep.parse_hashtags("hashtag #   ") == ()

    def test_with_trailing_and_leading_hash_sign(self):
        assert self.ep.parse_hashtags("#hashtag#") == ()
        assert self.ep.parse_hashtags(" #h# ") == ()

    def test_whitespace_between_hash_sign_and_word(self):
        assert self.ep.parse_hashtags("# hashtag") == ()
        assert self.ep.parse_hashtags("hash# tag") == ()

    def test_hash_sign_in_the_middle_of_the_string(self):
        assert self.ep.parse_hashtags("hash#tag") == ()
        assert self.ep.parse_hashtags("Ж#tag") == ()

    def test_digits_only_in_hash_tag(self):
        result = self.ep.parse_hashtags("#1234567890")

        assert result == ()

    def test_mixed_case(self):
        result = self.ep.parse_hashtags("#HaSh")
        assert result == (MessageEntity(length=5, offset=0, type=MessageEntityType.HASHTAG),)

    def test_utf16_offset_and_length(self):
        result = self.ep.parse_hashtags("😄😄😄😄 😄😄😄#a𒈙")

        assert result == (MessageEntity(length=4, offset=15, type=MessageEntityType.HASHTAG),)

    def test_invalid_symbols_ignored(self):
        expected = (MessageEntity(length=2, offset=0, type=MessageEntityType.HASHTAG),)

        assert self.ep.parse_hashtags("#a\u2122") == expected
        assert self.ep.parse_hashtags("#a൹") == expected
