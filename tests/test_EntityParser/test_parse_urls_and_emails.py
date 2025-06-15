# ruff: noqa: RUF001
from telegram import MessageEntity
from telegram.constants import MessageEntityType

from ptbtest.entityparser import EntityParser

class TestParseUrls:
    ep = EntityParser()

    def test_empty_string(self):
        assert self.ep.parse_urls_and_emails("") == ()

    def test_no_urls_in_string(self):
        assert self.ep.parse_urls_and_emails(".") == ()
        assert self.ep.parse_urls_and_emails("Hello world.") == ()

    def test_invalid_urls(self):
        assert self.ep.parse_urls_and_emails("http://  .com") == ()
        assert self.ep.parse_urls_and_emails("URL:     .com") == ()
        assert self.ep.parse_urls_and_emails("URL: .com") == ()
        assert self.ep.parse_urls_and_emails(".com") == ()
        assert self.ep.parse_urls_and_emails("http://  .") == ()
        assert self.ep.parse_urls_and_emails("http://.") == ()
        assert self.ep.parse_urls_and_emails("http://.com") == ()
        assert self.ep.parse_urls_and_emails("http://  .") == ()
        assert self.ep.parse_urls_and_emails("http://1.0") == ()
        assert self.ep.parse_urls_and_emails("http://a.0") == ()
        assert self.ep.parse_urls_and_emails("http://a.a") == ()
        assert self.ep.parse_urls_and_emails("https://t.…") == ()

    def test_valid_domains(self):
        assert self.ep.parse_urls_and_emails("telegram.org") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("(telegram.org)") == (MessageEntity(length=12, offset=1, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("\ntelegram.org)") == (MessageEntity(length=12, offset=1, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails(" telegram.org)") == (MessageEntity(length=12, offset=1, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("\"telegram.org\"") == (MessageEntity(length=12, offset=1, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails(" telegram.org ") == (MessageEntity(length=12, offset=1, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails(" telegram.org. ") == (MessageEntity(length=12, offset=1, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("google.com:᪉᪉᪉᪉᪉") == (MessageEntity(length=10, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("telegram.ton") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("telegram.onion") == (MessageEntity(length=14, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("ТеСт.ОнЛайН") == (MessageEntity(length=11, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("ÀÁ.com. ÀÁ.com.") == (MessageEntity(length=6, offset=0, type=MessageEntityType.URL),
                                                                    MessageEntity(length=6, offset=8, type=MessageEntityType.URL))
        assert self.ep.parse_urls_and_emails("ÀÁ.com,ÀÁ.com.") == (MessageEntity(length=6, offset=0, type=MessageEntityType.URL),
                                                                   MessageEntity(length=6, offset=7, type=MessageEntityType.URL))
        assert self.ep.parse_urls_and_emails("https://a.de`bc") == (MessageEntity(length=15, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("telegram.ORG") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("_.test.com") == (MessageEntity(length=10, offset=0, type=MessageEntityType.URL),)

    def test_invalid_domains(self):
        assert self.ep.parse_urls_and_emails(".telegram.org)") == ()
        assert self.ep.parse_urls_and_emails("telegram.tonsite") == ()
        assert self.ep.parse_urls_and_emails("a.ab") == ()
        assert self.ep.parse_urls_and_emails("test.abd") == ()
        assert self.ep.parse_urls_and_emails("ТеСт.Онлайн") == ()
        # The upper greek letter alpha.
        assert self.ep.parse_urls_and_emails("ТеСт.ОнлΑЙН") == ()
        assert self.ep.parse_urls_and_emails("ТеСт.Онлайнн") == ()
        assert self.ep.parse_urls_and_emails("test.abd") == ()
        assert self.ep.parse_urls_and_emails("telegram.Org") == ()
        assert self.ep.parse_urls_and_emails("telegram.Org") == ()
        assert self.ep.parse_urls_and_emails("a.b.c.com.a.b.c") == ()
        assert self.ep.parse_urls_and_emails("http://test_.com") == ()
        assert self.ep.parse_urls_and_emails("test_.com") == ()
        assert self.ep.parse_urls_and_emails("_test.com") == ()
        assert self.ep.parse_urls_and_emails("bad_domain.com") == ()

    def test_valid_protocols(self):
        assert self.ep.parse_urls_and_emails("https://telegram.org") == (MessageEntity(length=20, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://telegram.org") == (MessageEntity(length=19, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("ftp://telegram.org") == (MessageEntity(length=18, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("tonsite://telegram.ton") == (MessageEntity(length=22, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://ÀТеСт.ОнЛайНн") == (MessageEntity(length=20, offset=0, type=MessageEntityType.URL),)

    def test_invalid_protocols(self):
        assert self.ep.parse_urls_and_emails("sftp://telegram.org") == ()
        assert self.ep.parse_urls_and_emails("ftps://telegram.org") == ()
        assert self.ep.parse_urls_and_emails("invalid://telegram.org") == ()
        assert self.ep.parse_urls_and_emails("sftp://telegram.org") == ()

    def test_without_protocol(self):
        assert self.ep.parse_urls_and_emails("://telegram.org") == (MessageEntity(length=12, offset=3, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("telegram.org") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),)

    def test_slashes_without_protocol(self):
        assert self.ep.parse_urls_and_emails("//telegram.org)") == (MessageEntity(length=12, offset=2, type=MessageEntityType.URL),)

    def test_comma_inside_url(self):
        assert self.ep.parse_urls_and_emails("http://google,.com") == ()

    def test_with_params(self):
        assert self.ep.parse_urls_and_emails("()telegram.org/?q=()") == (MessageEntity(length=18, offset=2, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://telegram.org/?asd=123#123.") == (MessageEntity(length=32, offset=0, type=MessageEntityType.URL),)

    def test_basic_auth_ignoring_mentions(self):
        """
        These tests will fail if they'll be testsed against the Telegram server,
        because mentions extracted before URLs and in this string http://@google.com
        "@google" as a mention will be found, and no URLs.
        """
        assert self.ep.parse_urls_and_emails("http://@google.com") == (MessageEntity(length=10, offset=8, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://@goog.com") == (MessageEntity(length=8, offset=8, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://@@google.com") == (MessageEntity(length=10, offset=9, type=MessageEntityType.URL),)

    def test_basic_auth(self):
        assert self.ep.parse_urls_and_emails("http://a@google.com") == (MessageEntity(length=19, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://test@google.com") == (MessageEntity(length=22, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://user:pass@google.com") == (MessageEntity(length=27, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://a:h.bcde.fg@c.com") == (MessageEntity(length=25, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://bc:defg@c.com") == (MessageEntity(length=21, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://a:hbc:defg@c.com") == (MessageEntity(length=24, offset=0, type=MessageEntityType.URL),)

    def test_uncommon_tld(self):
        # WITHOUT the protocol.
        assert self.ep.parse_urls_and_emails("telegram.tonsite") == ()
        # WITH the protocol.
        assert self.ep.parse_urls_and_emails("http://telegram.tonsite") == (MessageEntity(length=23, offset=0, type=MessageEntityType.URL),)

    def test_mix_cased_protocol(self):
        assert self.ep.parse_urls_and_emails("hTtPs://telegram.org") == (MessageEntity(length=20, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("HTTP://telegram.org") == (MessageEntity(length=19, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://telegram.org") == (MessageEntity(length=20, offset=0, type=MessageEntityType.URL),)

    def test_protocols_with_leading_latin_char(self):
        assert self.ep.parse_urls_and_emails("sHTTP://telegram.org") == ()
        assert self.ep.parse_urls_and_emails(".ahttp://google.com") == ()

    def test_protocols_with_leading_non_latin_char(self):
        # The leading cyrillic letter 'a'.
        assert self.ep.parse_urls_and_emails("аHTTP://telegram.org") == (MessageEntity(length=19, offset=1, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("൹HTTP://telegram.org") == (MessageEntity(length=19, offset=1, type=MessageEntityType.URL),)

    def test_very_long_url(self):
        assert self.ep.parse_urls_and_emails("http://abcdefghijkabcdefghijkabcdefghijkabcdefg"
                                  "hijkabcdefghijkabcdefghijkabcdefghijkabcdefghij"
                                  "kabcdefghijkabcdefghijkabcdefghijkabcdefghijkab"
                                  "cdefghijkabcdefghijkabcdefghijkabcdefghijkabcde"
                                  "fghijkabcdefghijkabcdefghijkabcdefghijkabcdefgh"
                                  "ijkabcdefghijkabcdefghijkabcdefghijkabcdefghijk"
                                  "abcdefghijkabcdefghijkabcdefghijkabcdefghijkabc"
                                  "defghijkabcdefghijkabcdefghijkabcdefghijkabcdef"
                                  "ghijkabcdefghijkabcdefghijkabcdefghijkabcdefghi"
                                  "jkabcdefghijkabcdefghijkabcdefghijkabcdefghijka"
                                  "bcdefghijkabcdefghijkabcdefghijkabcdefghijkabcd"
                                  "efghijkabcdefghijkabcdefghijkabcdefghijkabcdefg"
                                  "hijkabcdefghijkabcdefghijkabcdefghijkabcdefghij"
                                  "kabcdefghijkabcdefghijkabcdefghijkabcdefghijkab"
                                  "cdefghijkabcdefghijkabcdefghijkabcdefghijkabcde"
                                  "fghijkabcdefghijkabcdefghijkabcdefghijkabcdefgh"
                                  "ijkabcdefghijkabcdefghijkabcdefghijkabcdefghijk"
                                  "abcdefghijkabcdefghijkabcdefghijkabcdefghijkabc"
                                  "defghijkabcdefghijkabcdefghijk.com") == ()

    def test_valid_ports(self):
        assert self.ep.parse_urls_and_emails("google.com:1#ab c") == (MessageEntity(length=15, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("google.com:1#") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("google.com:1#1") == (MessageEntity(length=14, offset=0, type=MessageEntityType.URL),)
        # Leading zeros are acceptable (according to the Telegram rules).
        assert self.ep.parse_urls_and_emails("google.com:00000001/abs") == (MessageEntity(length=23, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("google.com:000000065535/abs") == (MessageEntity(length=27, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("google.com:000000080/abs") == (MessageEntity(length=24, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("google.com:65535") == (MessageEntity(length=16, offset=0, type=MessageEntityType.URL),)

    def test_invalid_ports(self):
        # Too big port number (>65535)
        assert self.ep.parse_urls_and_emails("google.com:000000065536/abs") == (MessageEntity(length=10, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("google.com:65536") == (MessageEntity(length=10, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("google.com:100000") == (MessageEntity(length=10, offset=0, type=MessageEntityType.URL),)
        # The port number overflow and invalid symbold in the path.
        assert self.ep.parse_urls_and_emails("google.com:0000000655353/abs>>>>") == (MessageEntity(length=10, offset=0, type=MessageEntityType.URL),)
        # Zero port is not acceptable.
        assert self.ep.parse_urls_and_emails("google.com:0000000/abs") == (MessageEntity(length=10, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("google.com:0/abs") == (MessageEntity(length=10, offset=0, type=MessageEntityType.URL),)
        # Empty port.
        assert self.ep.parse_urls_and_emails("google.com:/abs") == (MessageEntity(length=10, offset=0, type=MessageEntityType.URL),)

    def test_localhost_ip_address(self):
        assert self.ep.parse_urls_and_emails("127.001") == ()
        assert self.ep.parse_urls_and_emails("127.0.0.1") == (MessageEntity(length=9, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("127.0.0.01") == ()
        assert self.ep.parse_urls_and_emails("127.0.0.256") == ()
        assert self.ep.parse_urls_and_emails("127.0.0.300") == ()
        assert self.ep.parse_urls_and_emails("127.0.0.260") == ()
        assert self.ep.parse_urls_and_emails("1.0") == ()
        assert self.ep.parse_urls_and_emails("127.0.0.1000") == ()

    def test_fake_domain_teiegram(self):
        assert self.ep.parse_urls_and_emails("teiegram.org/test") == ()
        assert self.ep.parse_urls_and_emails("TeiegraM.org/test") == ()
        assert self.ep.parse_urls_and_emails("TeiegraM.org") == ()
        assert self.ep.parse_urls_and_emails("teiegram.org") == ()

    def test_parentheses_and_brackets(self):
        assert self.ep.parse_urls_and_emails("http://test.google.com/?q=abc()}[]def") == (MessageEntity(length=31, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://test.google.com/?q=abc([{)]}def") == (MessageEntity(length=38, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://test.google.com/?q=abc(){}]def") == (MessageEntity(length=33, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://test.google.com/?q=abc){}[]def") == (MessageEntity(length=29, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://test.google.com/?q=abc(){}[]def") == (MessageEntity(length=38, offset=0, type=MessageEntityType.URL),)

    def test_underscores(self):
        assert self.ep.parse_urls_and_emails("http://google_.com") == ()
        assert self.ep.parse_urls_and_emails("http://google._com_") == ()
        assert self.ep.parse_urls_and_emails("http://test_.google.com") == (MessageEntity(length=23, offset=0, type=MessageEntityType.URL),)

    def test_hyphen_at_end_of_domain_and_subdomain(self):
        assert self.ep.parse_urls_and_emails("http://test-.google.com") == ()
        assert self.ep.parse_urls_and_emails("http://test.google-.com") == ()

    def test_ipv6_address(self):
        assert self.ep.parse_urls_and_emails("http://[2001:4860:0:2001::68]/") == ()

    def test_tg_domains(self):
        assert self.ep.parse_urls_and_emails("tg://resolve") == ()

    def test_different_url_endings(self):
        assert self.ep.parse_urls_and_emails("http://google.com/") == (MessageEntity(length=18, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://google.com?") == (MessageEntity(length=17, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://google.com#") == (MessageEntity(length=17, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://google.com##") == (MessageEntity(length=19, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://google.com/?") == (MessageEntity(length=18, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://www.google.com/ab,") == (MessageEntity(length=25, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://test.com#a") == (MessageEntity(length=17, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://test.com#") == (MessageEntity(length=15, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://test.com?#") == (MessageEntity(length=17, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://test.com/?#") == (MessageEntity(length=18, offset=0, type=MessageEntityType.URL),)

    def test_at_symbol(self):
        assert self.ep.parse_urls_and_emails("https://a.bc@c.com") == (MessageEntity(length=18, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://a.de/bc@c.com") == (MessageEntity(length=21, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://a.debc@c.com") == (MessageEntity(length=20, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://a.de`bc@c.com") == (MessageEntity(length=15, offset=0, type=MessageEntityType.URL),
                                                                          MessageEntity(length=5, offset=16, type=MessageEntityType.URL))

        assert self.ep.parse_urls_and_emails("https://a.bcde.fg@c.com") == (MessageEntity(length=23, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://abc@c.com") == (MessageEntity(length=17, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://a.bc@test.com:cd.com") == (MessageEntity(length=21, offset=0, type=MessageEntityType.URL),
                                                                                 MessageEntity(length=6, offset=22, type=MessageEntityType.URL))

    def test_filenames_like_urls(self):
        assert self.ep.parse_urls_and_emails("File '/usr/views.py'") == (MessageEntity(length=8, offset=11, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails(".views.py") == ()
        assert self.ep.parse_urls_and_emails("'views.py'") == (MessageEntity(length=8, offset=1, type=MessageEntityType.URL),)

    def test_misc(self):
        assert self.ep.parse_urls_and_emails("telegram. org. www. com... telegram.org... ...google.com...") == (MessageEntity(length=12, offset=27, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("Такой сайт: http://www.google.com или такой telegram.org") == (MessageEntity(length=21, offset=12, type=MessageEntityType.URL),
                                                                                                             MessageEntity(length=12, offset=44, type=MessageEntityType.URL))
        assert self.ep.parse_urls_and_emails("[http://google.com](test)") == (MessageEntity(length=17, offset=1, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("google.com:᪀᪀") == (MessageEntity(length=10, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("/.b/..a    @.....@/. a.ba") == (MessageEntity(length=4, offset=21, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("('http://telegram.org/a-b/?br=ie&lang=en',)") == (MessageEntity(length=38, offset=2, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://ai.telegram.org/bot%20bot/test-...") == (MessageEntity(length=39, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("bbbbbbbbbbbbbb.@.@") == ()
        assert self.ep.parse_urls_and_emails("@.") == ()
        assert self.ep.parse_urls_and_emails("<http://www.ics.uci.edu/pub/ietf/uri/historical.html#WARNING>") == (MessageEntity(length=59, offset=1, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://t.me/abcdef…") == (MessageEntity(length=19, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://t.me…") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://t.m…") == ()
        assert self.ep.parse_urls_and_emails("https://t.…") == ()
        assert self.ep.parse_urls_and_emails("https://t…") == ()
        assert self.ep.parse_urls_and_emails(".?") == ()
        assert self.ep.parse_urls_and_emails("👉http://ab.com/cdefgh-1IJ") == (MessageEntity(length=24, offset=2, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://test―‑@―google―.―com―/―–―‐―/―/―/―?―‑―#―――") == (MessageEntity(length=48, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("a!:b@gmail.com") == (MessageEntity(length=14, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("a:b!@gmail.com") == (MessageEntity(length=14, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("_sip._udp.apnic.net") == (MessageEntity(length=19, offset=0, type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("https://as_sip._udp.apnic.net") == (MessageEntity(length=29, offset=0, type=MessageEntityType.URL),)

    def test_complex(self):
        text = ("a.b.google.com dfsknnfs gsdfgsg http://códuia.de/ dffdg,\" 12)(cpia.de/())(\" http://гришка.рф/ sdufhdf "
                "http://xn--80afpi2a3c.xn--p1ai/ I have a good time.Thanks, guys!\n\n(hdfughidufhgdis) go#ogle.com гришка.рф "
                "hsighsdf gi почта.рф\n\n✪df.ws/123      "
                "xn--80afpi2a3c.xn--p1ai\n\nhttp://foo.com/blah_blah\nhttp://foo.com/blah_blah/\n(Something like "
                "http://foo.com/blah_blah)\nhttp://foo.com/blah_blah_(wikipedi8989a_Вася)\n(Something like "
                "http://foo.com/blah_blah_(Стакан_007))\nhttp://foo.com/blah_blah.\nhttp://foo.com/blah_blah/.\n<http://foo.com/"
                "blah_blah>\n<http://fo@@@@@@@@@^%#*@^&@$#*@#%^*&!^o.com/blah_blah/>\nhttp://foo.com/blah_blah,\nhttp://"
                "www.example.com/wpstyle/?p=364.\nhttp://✪df.ws/123\nrdar://1234\nhttp://"
                "userid:password@example.com:8080\nhttp://userid@example.com\nhttp://userid@example.com:8080\nhttp://"
                "userid:password@example.com\nhttp://example.com:8080 "
                "x-yojimbo-item://6303E4C1-xxxx-45A6-AB9D-3A908F59AE0E\nmessage://"
                "%3c330e7f8409726r6a4ba78dkf1fd71420c1bf6ff@mail.gmail.com%3e\n"
                "<tag>http://example.com</tag>\nJust a www.example.com "
                "link.\n\n➡️.ws/"
                "䨹\n\nabcdefghijklmnopqrstuvwxyz0123456789qwe_sdfsdf.aweawe-sdfs.com\ngoogle.com:"
                "᪉᪉᪉᪉\ngoogle."
                "com:᪀᪀\nhttp://  .com\nURL:     .com\nURL: "
                ".com\n\ngoogle.com?qwe\ngoogle.com#qwe\ngoogle.com/?\ngoogle.com/#\ngoogle.com?\ngoogle.com#\n")

        assert self.ep.parse_urls_and_emails(text) == (MessageEntity(length=14, offset=0, type=MessageEntityType.URL),
                                                       MessageEntity(length=17, offset=32, type=MessageEntityType.URL),
                                                       MessageEntity(length=10, offset=62, type=MessageEntityType.URL),
                                                       MessageEntity(length=17, offset=76, type=MessageEntityType.URL),
                                                       MessageEntity(length=31, offset=102, type=MessageEntityType.URL),
                                                       MessageEntity(length=8, offset=189, type=MessageEntityType.URL),
                                                       MessageEntity(length=9, offset=198, type=MessageEntityType.URL),
                                                       MessageEntity(length=8, offset=220, type=MessageEntityType.URL),
                                                       MessageEntity(length=10, offset=230, type=MessageEntityType.URL),
                                                       MessageEntity(length=23, offset=246, type=MessageEntityType.URL),
                                                       MessageEntity(length=24, offset=271, type=MessageEntityType.URL),
                                                       MessageEntity(length=25, offset=296, type=MessageEntityType.URL),
                                                       MessageEntity(length=24, offset=338, type=MessageEntityType.URL),
                                                       MessageEntity(length=45, offset=364, type=MessageEntityType.URL),
                                                       MessageEntity(length=37, offset=426, type=MessageEntityType.URL),
                                                       MessageEntity(length=24, offset=465, type=MessageEntityType.URL),
                                                       MessageEntity(length=25, offset=491, type=MessageEntityType.URL),
                                                       MessageEntity(length=24, offset=519, type=MessageEntityType.URL),
                                                       MessageEntity(length=16, offset=583, type=MessageEntityType.URL),
                                                       MessageEntity(length=24, offset=601, type=MessageEntityType.URL),
                                                       MessageEntity(length=37, offset=627, type=MessageEntityType.URL),
                                                       MessageEntity(length=17, offset=666, type=MessageEntityType.URL),
                                                       MessageEntity(length=39, offset=696, type=MessageEntityType.URL),
                                                       MessageEntity(length=25, offset=736, type=MessageEntityType.URL),
                                                       MessageEntity(length=30, offset=762, type=MessageEntityType.URL),
                                                       MessageEntity(length=34, offset=793, type=MessageEntityType.URL),
                                                       MessageEntity(length=23, offset=828, type=MessageEntityType.URL),
                                                       MessageEntity(length=18, offset=982, type=MessageEntityType.URL),
                                                       MessageEntity(length=15, offset=1014, type=MessageEntityType.URL),
                                                       MessageEntity(length=7, offset=1037, type=MessageEntityType.URL),
                                                       MessageEntity(length=62, offset=1046, type=MessageEntityType.URL),
                                                       MessageEntity(length=10, offset=1109, type=MessageEntityType.URL),
                                                       MessageEntity(length=10, offset=1125, type=MessageEntityType.URL),
                                                       MessageEntity(length=14, offset=1178, type=MessageEntityType.URL),
                                                       MessageEntity(length=14, offset=1193, type=MessageEntityType.URL),
                                                       MessageEntity(length=11, offset=1208, type=MessageEntityType.URL),
                                                       MessageEntity(length=12, offset=1221, type=MessageEntityType.URL),
                                                       MessageEntity(length=10, offset=1234, type=MessageEntityType.URL),
                                                       MessageEntity(length=10, offset=1246, type=MessageEntityType.URL))

    def test_utf16_length(self):
        assert self.ep.parse_urls_and_emails("example.com/hello=𐐷&hhh=2𐍈") == (MessageEntity(length=28, offset=0,
                                                                                             type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("example.com/hello=𐐷&«hhh=2𐍈") == (MessageEntity(length=21, offset=0,
                                                                                              type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("example.com/hello=𐐷&hhh)=2𐍈") == (MessageEntity(length=24, offset=0,
                                                                                              type=MessageEntityType.URL),)

    def test_percentage_symbol(self):
        assert self.ep.parse_urls_and_emails("http://%3c330e7f8409726r@mail.gmail.com") == (MessageEntity(length=39,
                                                                                                          offset=0,
                                                                                                          type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://%3c330e7f8409726rmail.gmail.com") == (MessageEntity(length=30,
                                                                                                         offset=8,
                                                                                                         type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("%3c330e7f8409726rmail.gmail.com") == (MessageEntity(length=30,
                                                                                                  offset=1,
                                                                                                  type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("%3c330e7f8409726r@mail.gmail.com") == (MessageEntity(length=32,
                                                                                                   offset=0,
                                                                                                   type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("http://%3c330e7f8409726r6a4ba78dkf1fd71420c1bf6ff@mail.gmail.com") == (MessageEntity(length=64,
                                                                                                                                   offset=0,
                                                                                                                                   type=MessageEntityType.URL),)
        assert self.ep.parse_urls_and_emails("message://%3c330e7f8409726r6a4ba78dkf1fd71420c1bf6ff@mail.gmail.com%3e") == ()

    def test_emails(self):
        assert self.ep.parse_urls_and_emails("a.bc@c.com") == (MessageEntity(length=10, offset=0, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("https://a.de[bc@c.com") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),
                                                                          MessageEntity(length=8, offset=13, type=MessageEntityType.EMAIL))
        assert self.ep.parse_urls_and_emails("https://a.de]bc@c.com") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),
                                                                          MessageEntity(length=8, offset=13, type=MessageEntityType.EMAIL))
        assert self.ep.parse_urls_and_emails("https://a.de{bc@c.com") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),
                                                                          MessageEntity(length=8, offset=13, type=MessageEntityType.EMAIL))
        assert self.ep.parse_urls_and_emails("https://a.de}bc@c.com") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),
                                                                          MessageEntity(length=8, offset=13, type=MessageEntityType.EMAIL))
        assert self.ep.parse_urls_and_emails("https://a.de(bc@c.com") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),
                                                                          MessageEntity(length=8, offset=13, type=MessageEntityType.EMAIL))
        assert self.ep.parse_urls_and_emails("https://a.de)bc@c.com") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),
                                                                          MessageEntity(length=8, offset=13, type=MessageEntityType.EMAIL))
        assert self.ep.parse_urls_and_emails("https://a.de'bc@c.com") == (MessageEntity(length=12, offset=0, type=MessageEntityType.URL),
                                                                          MessageEntity(length=8, offset=13, type=MessageEntityType.EMAIL))
        assert self.ep.parse_urls_and_emails("https://de[bc@c.com") == (MessageEntity(length=8, offset=11, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("https://de/bc@c.com") == (MessageEntity(length=8, offset=11, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("https://de[bc@c.com") == (MessageEntity(length=8, offset=11, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("https://de{bc@c.com") == (MessageEntity(length=8, offset=11, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("https://de}bc@c.com") == (MessageEntity(length=8, offset=11, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("https://de(bc@c.com") == (MessageEntity(length=8, offset=11, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("https://de)bc@c.com") == (MessageEntity(length=8, offset=11, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("https://de\\bc@c.com") == (MessageEntity(length=8, offset=11, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("https://de'bc@c.com") == (MessageEntity(length=8, offset=11, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("https://de`bc@c.com") == (MessageEntity(length=8, offset=11, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("a@b@c.com") == (MessageEntity(length=7, offset=2, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("a@b.com:c@1") == (MessageEntity(length=7, offset=0, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("test@test.software") == (MessageEntity(length=18, offset=0, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("abc@c.com@d.com") == (MessageEntity(length=9, offset=0, type=MessageEntityType.EMAIL),
                                                                    MessageEntity(length=5, offset=10, type=MessageEntityType.URL))
        assert self.ep.parse_urls_and_emails("Look :test@example.com") == (MessageEntity(length=16, offset=6, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("a#:b@gmail.com") == (MessageEntity(length=11, offset=3, type=MessageEntityType.EMAIL),)
        assert self.ep.parse_urls_and_emails("Look mailto:test@example.com") == (MessageEntity(length=16, offset=12, type=MessageEntityType.EMAIL),)
