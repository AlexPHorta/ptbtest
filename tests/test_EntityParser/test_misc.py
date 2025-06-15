import re

import pytest
from telegram import MessageEntity, User
from telegram.constants import MessageEntityType

from ptbtest.entityparser import (_get_utf16_length,
                                  get_item,
                                  _check_and_normalize_url,
                                  _split_and_sort_intersected_entities,
                                  _get_id_from_telegram_url,
                                  EntityParser,
                                  get_hash,
                                  _is_hashtag_letter,
                                  _fix_url,
                                  _is_email_address)


def test_get_utf16_length():
    assert _get_utf16_length("a") == 1  # ASCII
    assert _get_utf16_length("hello") == 5  # Multiple ASCII symbols
    assert _get_utf16_length("€") == 1  # Euro (part of the BPM)
    assert _get_utf16_length("𐍈") == 2  # UTF-16 surrogate pair
    assert _get_utf16_length("👨‍👩‍👧‍👦") == 11 # Emoji with ZWJ (Zero Width Joiner)
    assert _get_utf16_length("") == 0  # Empty string
    assert _get_utf16_length("👀🔥") == 4  # Two emojis (each has 2 UTF-16 units)


class TestGetItem:
    seq = [10, 20, 40, 50, 60]

    def test_good_positive_indexes(self):
        assert get_item(self.seq, 0) == 10
        assert get_item(self.seq, 2) == 40
        assert get_item(self.seq, 4) == 60

    def test_good_negative_indexes(self):
        assert get_item(self.seq, -1) == 60
        assert get_item(self.seq, -3) == 40
        assert get_item(self.seq, -5) == 10

    def test_positive_indexes_out_of_range(self):
        assert get_item(self.seq, 5) is None
        assert get_item(self.seq, 10, "default") == "default"
        assert get_item(self.seq, 6, 0) == 0

    def test_negative_indexes_out_of_range(self):
        assert get_item(self.seq, -6) is None
        assert get_item(self.seq, -10, "default") == "default"
        assert get_item(self.seq, -8, 0) == 0

    def test_empty_sequence(self):
        assert get_item([], 0) is None
        assert get_item([], 3, "empty") == "empty"

    def test_allow_negative_indexing_argument(self):
        text = "Hello world!"

        assert get_item(text, 0, allow_negative_indexing=False) == "H"
        assert get_item(text, -1, allow_negative_indexing=False) is None
        assert get_item(text, 1, allow_negative_indexing=False) == "e"


class TestCheckAndNormalizeUrl:

    def test_empty_string(self):
        assert not _check_and_normalize_url("")

    def test_leading_and_trailing_whitespaces(self):
        assert not _check_and_normalize_url(" http://example.com")
        assert not _check_and_normalize_url("http://example.com ")
        assert not _check_and_normalize_url(" http://example.com ")

    def test_valid_protocols(self):
        assert _check_and_normalize_url("http://example.com") == "http://example.com/"
        assert _check_and_normalize_url("https://example.com/") == "https://example.com/"
        assert _check_and_normalize_url("ton://example.com") == "ton://example.com/"
        assert _check_and_normalize_url("tg://example.com") == "tg://example.com/"
        assert _check_and_normalize_url("tonsite://example.com") == "tonsite://example.com/"

    def test_no_protocol(self):    # No protocol
        assert _check_and_normalize_url("example.com") == "http://example.com/"

    def test_wrong_protocol_failing(self):
        assert not _check_and_normalize_url("ftp://example.com")
        assert not _check_and_normalize_url("htts://example.com")
        assert not _check_and_normalize_url("ws://example.com")

    def test_trailing_slash(self):
        assert _check_and_normalize_url("http://example.com") == "http://example.com/"
        assert _check_and_normalize_url("http://example.com/") == "http://example.com/"
        assert _check_and_normalize_url("http://example.com/path") == "http://example.com/path"
        assert _check_and_normalize_url("http://example.com/path/") == "http://example.com/path/"

    def test_with_newline_inside_failing(self):
        assert not _check_and_normalize_url("https://example\n.com")

    def test_http_urls_without_path_and_params(self):
        assert _check_and_normalize_url("http://example.com/") == "http://example.com/"
        assert _check_and_normalize_url("http://www.example.com/") == "http://www.example.com/"
        assert _check_and_normalize_url("http://www.example.com") == "http://www.example.com/"
        assert _check_and_normalize_url("www.example.com") == "http://www.example.com/"
        assert _check_and_normalize_url("www.example.com/") == "http://www.example.com/"

    def test_https_urls_without_path_and_params(self):
        assert _check_and_normalize_url("https://example.com/") == "https://example.com/"
        assert _check_and_normalize_url("https://www.example.com/") == "https://www.example.com/"
        assert _check_and_normalize_url("https://www.example.com") == "https://www.example.com/"

    def test_no_slash_at_the_end_of_the_url_with_params(self):
        assert _check_and_normalize_url("www.example.com/login") == "http://www.example.com/login"
        assert _check_and_normalize_url("https://example.com/login/") == "https://example.com/login/"


class TestGetIdFromTelegramUrl:
    def test_user_id(self):
        result = _get_id_from_telegram_url("user",
                                           "tg://user?id=12345")

        assert result == 12345

    def test_emoji_id(self):
        result = _get_id_from_telegram_url("emoji",
                                           "tg://emoji?id=67890")

        assert result == 67890

    def test_invalid_type_failing(self):
        with pytest.raises(ValueError, match="Wrong type - mention"):
            _get_id_from_telegram_url("mention", "tg://mention?id=123")

    def test_mismatched_type_and_url(self):
        result = _get_id_from_telegram_url("emoji",
                                           "tg://user?id=222222")

        assert result is None


class TestGetHash:
    def test_urls(self):
        example_com = MessageEntity(MessageEntityType.URL, offset=2,
                                    length=5, url="https://example.com")

        wikipedia_org = MessageEntity(MessageEntityType.URL, offset=2,
                                      length=5, url="https://wikipedia.org")

        assert get_hash(example_com) != get_hash(wikipedia_org)

        # Builtin hashes are the same.
        assert hash(example_com) == hash(wikipedia_org)

    def test_user(self):
        user_a = MessageEntity(MessageEntityType.MENTION, offset=11, length=12,
                               user=User(123, "UserA", False))
        user_b = MessageEntity(MessageEntityType.MENTION, offset=11, length=12,
                               user=User(789, "UserBot", True))

        assert get_hash(user_a) != get_hash(user_b)

        # Builtin hashes are the same.
        assert hash(user_a) == hash(user_b)

    def test_code_languages(self):
        java = MessageEntity(MessageEntityType.PRE, offset=2,
                             length=50, language="java")

        python = MessageEntity(MessageEntityType.PRE, offset=2,
                               length=50, language="python")


        assert get_hash(java) != get_hash(python)

        # Builtin hashes are the same.
        assert hash(java) == hash(python)

    def test_custom_emoji_id(self):
        emoji_a = MessageEntity(MessageEntityType.CUSTOM_EMOJI, offset=2,
                                length=5, custom_emoji_id="1234125")

        emoji_b = MessageEntity(MessageEntityType.CUSTOM_EMOJI, offset=2,
                                length=5, custom_emoji_id="789789789")

        assert get_hash(emoji_a) != get_hash(emoji_b)

        # Builtin hashes are the same.
        assert hash(emoji_a) == hash(emoji_b)


class TestSplitAndSortIntersectedEntities:
    def test_empty_entities(self):
        assert _split_and_sort_intersected_entities(()) == list()

    def test_non_intersected_entities(self):
        # The input string is "<b>bold</b> <i>italic</i> <u>underline</u>"
        in_seq = (MessageEntity(length=4, offset=0, type=MessageEntityType.BOLD),
                  MessageEntity(length=6, offset=5, type=MessageEntityType.ITALIC),
                  MessageEntity(length=9, offset=12, type=MessageEntityType.UNDERLINE))

        result = _split_and_sort_intersected_entities(in_seq)

        assert result == [MessageEntity(length=4, offset=0, type=MessageEntityType.BOLD),
                          MessageEntity(length=6, offset=5, type=MessageEntityType.ITALIC),
                          MessageEntity(length=9, offset=12, type=MessageEntityType.UNDERLINE)]

    def test_intersected_entities_case(self):
        # The input string is "<b>hello <i>italic <u>underlined <s>nested</s> entities</u> wo</i>rld</b>"
        in_seq = (MessageEntity(length=45, offset=0, type=MessageEntityType.BOLD),
                  MessageEntity(length=36, offset=6, type=MessageEntityType.ITALIC),
                  MessageEntity(length=26, offset=13, type=MessageEntityType.UNDERLINE),
                  MessageEntity(length=6, offset=24, type=MessageEntityType.STRIKETHROUGH))

        result = _split_and_sort_intersected_entities(in_seq)

        assert result == [MessageEntity(length=6, offset=0, type=MessageEntityType.BOLD),
                          MessageEntity(length=7, offset=6, type=MessageEntityType.BOLD),
                          MessageEntity(length=7, offset=6, type=MessageEntityType.ITALIC),
                          MessageEntity(length=11, offset=13, type=MessageEntityType.BOLD),
                          MessageEntity(length=11, offset=13, type=MessageEntityType.ITALIC),
                          MessageEntity(length=11, offset=13, type=MessageEntityType.UNDERLINE),
                          MessageEntity(length=21, offset=24, type=MessageEntityType.BOLD),
                          MessageEntity(length=18, offset=24, type=MessageEntityType.ITALIC),
                          MessageEntity(length=15, offset=24, type=MessageEntityType.UNDERLINE),
                          MessageEntity(length=6, offset=24, type=MessageEntityType.STRIKETHROUGH)]


def test_is_hashtag_letter():
    # Valid.
    assert _is_hashtag_letter("_")
    assert _is_hashtag_letter("·")
    assert _is_hashtag_letter("\u200c")
    assert _is_hashtag_letter("W")
    assert _is_hashtag_letter("Ж")
    assert _is_hashtag_letter("1")

    # Invalid.
    assert not _is_hashtag_letter("")
    assert not _is_hashtag_letter("-")
    assert not _is_hashtag_letter(".")
    assert not _is_hashtag_letter(" ")
    assert not _is_hashtag_letter("\t")


class TestFixUrl:
    def test_valid_urls_with_protocol(self):
        assert _fix_url("http://example.com") == "http://example.com"
        assert _fix_url("https://example.org/path") == "https://example.org/path"
        assert _fix_url("ftp://sub.domain.co.uk?query=1") == "ftp://sub.domain.co.uk?query=1"
        assert _fix_url("tonsite://example.ton") == "tonsite://example.ton"
        assert _fix_url("https://example.com:8080") == "https://example.com:8080"

    def test_valid_urls_without_protocol(self):
        assert _fix_url("example.com") == "example.com"
        assert _fix_url("domain.org/path/page.html") == "domain.org/path/page.html"
        assert _fix_url("sub_.example.com") == "sub_.example.com"

    def test_domain_path_dividers(self):
        assert _fix_url("http://example.com/path") == "http://example.com/path"
        assert _fix_url("http://example.com#path") == "http://example.com#path"
        assert _fix_url("http://example.com?path") == "http://example.com?path"

    def test_url_with_basic_auth(self):
        assert _fix_url("https://user:pass@example.com") == "https://user:pass@example.com"

    def test_url_with_port(self):
        url = "https://example.com:8080"
        assert _fix_url(url) == url

    def test_fake_domain_teiegram_org(self):
        assert _fix_url("teiegram.org") == ""
        assert _fix_url("https://teiegram.org") == ""
        assert _fix_url("http://teiegram.org") == ""
        assert _fix_url("ftp://teiegram.org") == ""
        assert _fix_url("tonsite://teiegram.org") == ""

    def test_valid_brackets_balance(self):
        assert _fix_url("http://site.com/path(sub[1]{2})") == "http://site.com/path(sub[1]{2})"

    def test_invalid_brackets_balance(self):
        assert _fix_url("http://broken.com/test)") == "http://broken.com/test"

    def test_striping_invalid_symbols_at_the_end(self):
        assert _fix_url("https://example.com/path);") == "https://example.com/path"
        assert _fix_url("http://example.com/test!") == "http://example.com/test"
        assert _fix_url("http://example.com/test.:;,('?!`") == "http://example.com/test"

    def test_valid_ipv4(self):
        assert _fix_url("http://192.168.1.1") == "http://192.168.1.1"
        assert _fix_url("http://192.168.1.1/path") == "http://192.168.1.1/path"
        assert _fix_url("http://192.168.1.1/?param=value") == "http://192.168.1.1/?param=value"
        assert _fix_url("192.168.1.1/?param=value") == "192.168.1.1/?param=value"

    def test_invalid_ip_addresses(self):
        assert _fix_url("http://127.00.0.1") == ""
        assert _fix_url("http://256.100.0.1") == ""

    def test_invalid_urls(self):
        assert _fix_url("localhost") == ""
        assert _fix_url("custom.domainzzz") == ""
        assert _fix_url("bad_domain.com") == ""
        assert _fix_url("https://bad-.com") == ""
        assert _fix_url("https://example.c_m") == ""

    def test_valid_punycode(self):
        assert _fix_url("https://xn--e1afmkfd.xn--80asehdb/") == "https://xn--e1afmkfd.xn--80asehdb/"
        assert _fix_url("xn--80afpi2a3c.xn--p1ai") == "xn--80afpi2a3c.xn--p1ai"

    def test_invalid_punycode(self):
        assert _fix_url("https://xn--a.xn--8/") == ""

    def test_is_common_tld(self):
        """This is a test for the inner function."""
        assert _fix_url("example.Com") == ""
        assert _fix_url("тест.Онлайн") == ""

    def test_url_with_all_parts(self):
        url = "https://user:pass@example.com:8080/path?param1=val&param2=val2#anchor"
        assert _fix_url(url) == url


def test_is_email_address():
    # FAILING
    assert not _is_email_address("")
    assert not _is_email_address("telegram.org")
    assert not _is_email_address("security.telegram.org")
    assert not _is_email_address("@")
    assert not _is_email_address("test.abd")
    assert not _is_email_address("a.ab")

    # SUCCESS
    assert _is_email_address("security@telegram.org")
    assert _is_email_address("A@a.a.a.ab")
    assert _is_email_address("A@a.ab")
    assert _is_email_address("Test@aa.aa.aa.aa")
    assert _is_email_address("Test@test.abd")
    assert _is_email_address("a@a.a.a.ab")
    assert _is_email_address("test@test.abd")
    assert _is_email_address("test@test.com")
    assert _is_email_address("a.bc@d.ef")

    bad_userdata = ("",
                    "a.a.a.a.a.a.a.a.a.a.a.a",
                    "+.+.+.+.+.+",
                    "*.a.a",
                    "a.*.a",
                    "a.a.*",
                    "a.a.",
                    "a.abcdefghijklmnopqrstuvwxyz0.a",
                    "a.a.abcdefghijklmnopqrstuvwxyz0123456789",
                    "abcdefghijklmnopqrstuvwxyz0.a.a")

    good_userdata = ("a.a.a.a.a.a.a.a.a.a.a",
                     "a+a+a+a+a+a+a+a+a+a+a",
                     "+.+.+.+.+._",
                     "aozAQZ0-5-9_+-aozAQZ0-5-9_.aozAQZ0-5-9_.-._.+-",
                     "a.a.a",
                     "a.a.abcdefghijklmnopqrstuvwxyz012345678",
                     "a.abcdefghijklmnopqrstuvwxyz.a",
                     "a..a",
                     "abcdefghijklmnopqrstuvwxyz.a.a",
                     ".a.a")

    bad_domains = ("",
                   ".",
                   "abc",
                   "localhost",
                   "a.a.a.a.a.a.a.ab",
                   ".......",
                   "a.a.a.a.a.a+ab",
                   "a+a.a.a.a.a.ab",
                   "a.a.a.a.a.a.a",
                   "a.a.a.a.a.a.abcdefghi",
                   "a.a.a.a.a.a.ab0yz",
                   "a.a.a.a.a.a.ab9yz",
                   "a.a.a.a.a.a.ab-yz",
                   "a.a.a.a.a.a.ab_yz",
                   "a.a.a.a.a.a.ab*yz",
                   ".ab",".a.ab",
                   "a..ab",
                   "a.a.a..a.ab",
                   ".a.a.a.a.ab",
                   "abcdefghijklmnopqrstuvwxyz01234.ab",
                   "ab0cd.abd.aA*sd.0.9.0-9.ABOYZ",
                   "ab*cd.abd.aAasd.0.9.0-9.ABOYZ",
                   "ab0cd.abd.aAasd.0.9.0*9.ABOYZ",
                   "*b0cd.ab_d.aA-sd.0.9.0-9.ABOYZ",
                   "ab0c*.ab_d.aA-sd.0.9.0-9.ABOYZ",
                   "ab0cd.ab_d.aA-sd.0.9.0-*.ABOYZ",
                   "ab0cd.ab_d.aA-sd.0.9.*-9.ABOYZ",
                   "-b0cd.ab_d.aA-sd.0.9.0-9.ABOYZ",
                   "ab0c-.ab_d.aA-sd.0.9.0-9.ABOYZ",
                   "ab0cd.ab_d.aA-sd.-.9.0-9.ABOYZ",
                   "ab0cd.ab_d.aA-sd.0.9.--9.ABOYZ",
                   "ab0cd.ab_d.aA-sd.0.9.0--.ABOYZ",
                   "_b0cd.ab_d.aA-sd.0.9.0-9.ABOYZ",
                   "ab0c_.ab_d.aA-sd.0.9.0-9.ABOYZ",
                   "ab0cd.ab_d.aA-sd._.9.0-9.ABOYZ",
                   "ab0cd.ab_d.aA-sd.0.9._-9.ABOYZ",
                   "ab0cd.ab_d.aA-sd.0.9.0-_.ABOYZ",
                   "-.ab_d.aA-sd.0.9.0-9.ABOYZ",
                   "ab0cd.ab_d.-.0.9.0-9.ABOYZ",
                   "ab0cd.ab_d.aA-sd.0.9.-.ABOYZ",
                   "_.ab_d.aA-sd.0.9.0-9.ABOYZ",
                   "ab0cd.ab_d._.0.9.0-9.ABOYZ",
                   "ab0cd.ab_d.aA-sd.0.9._.ABOYZ")

    good_domains = ("a.a.a.a.a.a.ab",
                    "a.a.a.a.a.a.abcdef",
                    "a.a.a.a.a.a.aboyz",
                    "a.a.a.a.a.a.ABOYZ",
                    "a.a.a.a.a.a.AbOyZ",
                    "abcdefghijklmnopqrstuvwxyz0123.ab",
                    "ab0cd.ab_d.aA-sd.0.9.0-9.ABOYZ",
                    "A.Z.aA-sd.a.z.0-9.ABOYZ")

    for b_userdata in bad_userdata:
        for b_domain in bad_domains:
            assert not _is_email_address(f"{b_userdata}@{b_domain}"), f"{b_userdata}@{b_domain}"
            assert not _is_email_address(f"{b_userdata}{b_domain}"), f"{b_userdata}{b_domain}"

        for g_domain in good_domains:
            assert not _is_email_address(f"{b_userdata}@{g_domain}"), f"{b_userdata}@{g_domain}"
            assert not _is_email_address(f"{b_userdata}{g_domain}"), f"{b_userdata}{g_domain}"

    for g_userdata in good_userdata:
        for b_domain in bad_domains:
            assert not _is_email_address(f"{g_userdata}@{b_domain}"), f"{g_userdata}@{b_domain}"
            assert not _is_email_address(f"{g_userdata}{b_domain}"), f"{g_userdata}{b_domain}"

        for g_domain in good_domains:
            assert _is_email_address(f"{g_userdata}@{g_domain}"), f"{g_userdata}@{g_domain}"
            assert not _is_email_address(f"{g_userdata}{g_domain}"), f"{g_userdata}{g_domain}"


class TestEntityParserExtractEntities:
    ep = EntityParser()

    def test_str_pattern(self):
        pattern = r"(?<=\B)@([a-zA-Z0-9_]{2,32})(?=\b)"
        result = self.ep._extract_entities("@mention", pattern)

        assert result[0].start == 0
        assert result[0].end == 8
        assert result[0].utf16_length == 8
        assert result[0].utf16_offset == 0

    def test_compiled_pattern(self):
        pattern = re.compile(r"(?<=\B)@([a-zA-Z0-9_]{2,32})(?=\b)")
        result = self.ep._extract_entities("@mention", pattern)

        assert result[0].start == 0
        assert result[0].end == 8
        assert result[0].utf16_length == 8
        assert result[0].utf16_offset == 0

    def test_empty_string(self):
        pattern = re.compile(r"(?<=\B)@([a-zA-Z0-9_]{2,32})(?=\b)")
        result = self.ep._extract_entities("", pattern)

        assert result == ()
