# ruff: noqa: C901, RUF001
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
"""
This module provides a helper class to transform
marked-up messages to plain text and a :obj:`tuple` of
:class:`entities <telegram.MessageEntity>`.

`Telegram Docs <https://core.telegram.org/bots/api#formatting-options>`_
"""
import html
import ipaddress
import re
import string
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal, Optional, Union
from urllib.parse import urlparse

from telegram import MessageEntity, TelegramObject
from telegram.constants import MessageEntityType

from ptbtest.errors import BadMarkupException

# These priorities are used for sorting purpose.
# https://github.com/tdlib/td/blob/f1b7500310baa496c0b779e4273a3aff0f14f42f/td/telegram/MessageEntity.cpp#L38
PRIORITIES = {
    MessageEntityType.MENTION: 50,
    MessageEntityType.HASHTAG: 50,
    MessageEntityType.BOT_COMMAND: 50,
    MessageEntityType.URL: 50,
    MessageEntityType.EMAIL: 50,
    MessageEntityType.BOLD: 90,
    MessageEntityType.ITALIC: 91,
    MessageEntityType.CODE: 20,
    MessageEntityType.PRE: 10,
    MessageEntityType.TEXT_LINK: 49,
    MessageEntityType.TEXT_MENTION: 49,
    MessageEntityType.CASHTAG: 50,
    MessageEntityType.PHONE_NUMBER: 50,
    MessageEntityType.UNDERLINE: 92,
    MessageEntityType.STRIKETHROUGH: 93,
    MessageEntityType.BLOCKQUOTE: 0,
    MessageEntityType.SPOILER: 94,
    MessageEntityType.CUSTOM_EMOJI: 99,
    MessageEntityType.EXPANDABLE_BLOCKQUOTE: 0
}

ALLOWED_HTML_TAG_NAMES = ("a", "b", "strong", "i", "em", "s", "strike", "del",
                          "u", "ins", "tg-spoiler", "tg-emoji", "span", "pre",
                          "code", "blockquote")

COMMON_TLDS = ("aaa", "aarp", "abb", "abbott", "abbvie", "abc", "able", "abogado",
                "abudhabi", "ac", "academy", "accenture", "accountant", "accountants",
                "aco", "actor", "ad", "ads", "adult", "ae", "aeg", "aero", "aetna",
                "af", "afl", "africa", "ag", "agakhan", "agency", "ai", "aig",
                "airbus", "airforce", "airtel", "akdn", "al", "alibaba", "alipay",
                "allfinanz", "allstate", "ally", "alsace", "alstom", "am", "amazon",
                "americanexpress", "americanfamily", "amex", "amfam", "amica",
                "amsterdam", "analytics", "android", "anquan", "anz", "ao", "aol",
                "apartments", "app", "apple", "aq", "aquarelle", "ar", "arab",
                "aramco", "archi", "army", "arpa", "art", "arte", "as", "asda",
                "asia", "associates", "at", "athleta", "attorney", "au", "auction",
                "audi", "audible", "audio", "auspost", "author", "auto", "autos", "aw",
                "aws", "ax", "axa", "az", "azure", "ba", "baby", "baidu", "banamex",
                "band", "bank", "bar", "barcelona", "barclaycard", "barclays", "barefoot",
                "bargains", "baseball", "basketball", "bauhaus", "bayern", "bb", "bbc",
                "bbt", "bbva", "bcg", "bcn", "bd", "be", "beats", "beauty", "beer",
                "bentley", "berlin", "best", "bestbuy", "bet", "bf", "bg", "bh", "bharti",
                "bi", "bible", "bid", "bike", "bing", "bingo", "bio", "biz", "bj",
                "black", "blackfriday", "blockbuster", "blog", "bloomberg", "blue",
                "bm", "bms", "bmw", "bn", "bnpparibas", "bo", "boats", "boehringer",
                "bofa", "bom", "bond", "boo", "book", "booking", "bosch", "bostik",
                "boston", "bot", "boutique", "box", "br", "bradesco", "bridgestone",
                "broadway", "broker", "brother", "brussels", "bs", "bt", "build", "builders",
                "business", "buy", "buzz", "bv", "bw", "by", "bz", "bzh", "ca", "cab",
                "cafe", "cal", "call", "calvinklein", "cam", "camera", "camp", "canon",
                "capetown", "capital", "capitalone", "car", "caravan", "cards", "care",
                "career", "careers", "cars", "casa", "case", "cash", "casino", "cat",
                "catering", "catholic", "cba", "cbn", "cbre", "cc", "cd", "center", "ceo",
                "cern", "cf", "cfa", "cfd", "cg", "ch", "chanel", "channel", "charity",
                "chase", "chat", "cheap", "chintai", "christmas", "chrome", "church", "ci",
                "cipriani", "circle", "cisco", "citadel", "citi", "citic", "city", "ck",
                "cl", "claims", "cleaning", "click", "clinic", "clinique", "clothing",
                "cloud", "club", "clubmed", "cm", "cn", "co", "coach", "codes", "coffee",
                "college", "cologne", "com", "commbank", "community", "company", "compare",
                "computer", "comsec", "condos", "construction", "consulting", "contact",
                "contractors", "cooking", "cool", "coop", "corsica", "country", "coupon",
                "coupons", "courses", "cpa", "cr", "credit", "creditcard", "creditunion",
                "cricket", "crown", "crs", "cruise", "cruises", "cu", "cuisinella", "cv",
                "cw", "cx", "cy", "cymru", "cyou", "cz", "dabur", "dad", "dance", "data",
                "date", "dating", "datsun", "day", "dclk", "dds", "de", "deal", "dealer",
                "deals", "degree", "delivery", "dell", "deloitte", "delta", "democrat",
                "dental", "dentist", "desi", "design", "dev", "dhl", "diamonds", "diet",
                "digital", "direct", "directory", "discount", "discover", "dish", "diy",
                "dj", "dk", "dm", "dnp", "do", "docs", "doctor", "dog", "domains", "dot",
                "download", "drive", "dtv", "dubai", "dunlop", "dupont", "durban", "dvag",
                "dvr", "dz", "earth", "eat", "ec", "eco", "edeka", "edu", "education", "ee",
                "eg", "email", "emerck", "energy", "engineer", "engineering", "enterprises",
                "epson", "equipment", "er", "ericsson", "erni", "es", "esq", "estate", "et",
                "eu", "eurovision", "eus", "events", "exchange", "expert", "exposed", "express",
                "extraspace", "fage", "fail", "fairwinds", "faith", "family", "fan", "fans",
                "farm", "farmers", "fashion", "fast", "fedex", "feedback", "ferrari", "ferrero",
                "fi", "fidelity", "fido", "film", "final", "finance", "financial", "fire",
                "firestone", "firmdale", "fish", "fishing", "fit", "fitness", "fj", "fk",
                "flickr", "flights", "flir", "florist", "flowers", "fly", "fm", "fo", "foo",
                "food", "football", "ford", "forex", "forsale", "forum", "foundation", "fox",
                "fr", "free", "fresenius", "frl", "frogans", "frontier", "ftr", "fujitsu", "fun",
                "fund", "furniture", "futbol", "fyi", "ga", "gal", "gallery", "gallo", "gallup",
                "game", "games", "gap", "garden", "gay", "gb", "gbiz", "gd", "gdn", "ge", "gea",
                "gent", "genting", "george", "gf", "gg", "ggee", "gh", "gi", "gift", "gifts",
                "gives", "giving", "gl", "glass", "gle", "global", "globo", "gm", "gmail", "gmbh",
                "gmo", "gmx", "gn", "godaddy", "gold", "goldpoint", "golf", "goo", "goodyear",
                "goog", "google", "gop", "got", "gov", "gp", "gq", "gr", "grainger", "graphics",
                "gratis", "green", "gripe", "grocery", "group", "gs", "gt", "gu", "gucci", "guge",
                "guide", "guitars", "guru", "gw", "gy", "hair", "hamburg", "hangout", "haus",
                "hbo", "hdfc", "hdfcbank", "health", "healthcare", "help", "helsinki", "here",
                "hermes", "hiphop", "hisamitsu", "hitachi", "hiv", "hk", "hkt", "hm", "hn",
                "hockey", "holdings", "holiday", "homedepot", "homegoods", "homes", "homesense",
                "honda", "horse", "hospital", "host", "hosting", "hot", "hotels", "hotmail",
                "house", "how", "hr", "hsbc", "ht", "hu", "hughes", "hyatt", "hyundai", "ibm",
                "icbc", "ice", "icu", "id", "ie", "ieee", "ifm", "ikano", "il", "im", "imamat",
                "imdb", "immo", "immobilien", "in", "inc", "industries", "infiniti", "info",
                "ing", "ink", "institute", "insurance", "insure", "int", "international", "intuit",
                "investments", "io", "ipiranga", "iq", "ir", "irish", "is", "ismaili", "ist",
                "istanbul", "it", "itau", "itv", "jaguar", "java", "jcb", "je", "jeep", "jetzt",
                "jewelry", "jio", "jll", "jm", "jmp", "jnj", "jo", "jobs", "joburg", "jot", "joy",
                "jp", "jpmorgan", "jprs", "juegos", "juniper", "kaufen", "kddi", "ke", "kerryhotels",
                "kerrylogistics", "kerryproperties", "kfh", "kg", "kh", "ki", "kia", "kids", "kim",
                "kindle", "kitchen", "kiwi", "km", "kn", "koeln", "komatsu", "kosher", "kp", "kpmg",
                "kpn", "kr", "krd", "kred", "kuokgroup", "kw", "ky", "kyoto", "kz", "la", "lacaixa",
                "lamborghini", "lamer", "lancaster", "land", "landrover", "lanxess", "lasalle",
                "lat", "latino", "latrobe", "law", "lawyer", "lb", "lc", "lds", "lease", "leclerc",
                "lefrak", "legal", "lego", "lexus", "lgbt", "li", "lidl", "life", "lifeinsurance",
                "lifestyle", "lighting", "like", "lilly", "limited", "limo", "lincoln", "link",
                "lipsy", "live", "living", "lk", "llc", "llp", "loan", "loans", "locker", "locus",
                "lol", "london", "lotte", "lotto", "love", "lpl", "lplfinancial", "lr", "ls", "lt",
                "ltd", "ltda", "lu", "lundbeck", "luxe", "luxury", "lv", "ly", "ma", "madrid",
                "maif", "maison", "makeup", "man", "management", "mango", "map", "market",
                "marketing", "markets", "marriott", "marshalls", "mattel", "mba", "mc", "mckinsey",
                "md", "me", "med", "media", "meet", "melbourne", "meme", "memorial", "men", "menu",
                "merckmsd", "mg", "mh", "miami", "microsoft", "mil", "mini", "mint", "mit",
                "mitsubishi", "mk", "ml", "mlb", "mls", "mm", "mma", "mn", "mo", "mobi", "mobile",
                "moda", "moe", "moi", "mom", "monash", "money", "monster", "mormon", "mortgage",
                "moscow", "moto", "motorcycles", "mov", "movie", "mp", "mq", "mr", "ms", "msd",
                "mt", "mtn", "mtr", "mu", "museum", "music", "mv", "mw", "mx", "my", "mz", "na",
                "nab", "nagoya", "name", "navy", "nba", "nc", "ne", "nec", "net", "netbank",
                "netflix", "network", "neustar", "new", "news", "next", "nextdirect", "nexus",
                "nf", "nfl", "ng", "ngo", "nhk", "ni", "nico", "nike", "nikon", "ninja", "nissan",
                "nissay", "nl", "no", "nokia", "norton", "now", "nowruz", "nowtv", "np", "nr",
                "nra", "nrw", "ntt", "nu", "nyc", "nz", "obi", "observer", "office", "okinawa",
                "olayan", "olayangroup", "ollo", "om", "omega", "one", "ong", "onion", "onl",
                "online", "ooo", "open", "oracle", "orange", "org", "organic", "origins", "osaka",
                "otsuka", "ott", "ovh", "pa", "page", "panasonic", "paris", "pars", "partners",
                "parts", "party", "pay", "pccw", "pe", "pet", "pf", "pfizer", "pg", "ph", "pharmacy",
                "phd", "philips", "phone", "photo", "photography", "photos", "physio", "pics",
                "pictet", "pictures", "pid", "pin", "ping", "pink", "pioneer", "pizza", "pk", "pl",
                "place", "play", "playstation", "plumbing", "plus", "pm", "pn", "pnc", "pohl",
                "poker", "politie", "porn", "post", "pr", "pramerica", "praxi", "press", "prime",
                "pro", "prod", "productions", "prof", "progressive", "promo", "properties",
                "property", "protection", "pru", "prudential", "ps", "pt", "pub", "pw", "pwc",
                "py", "qa", "qpon", "quebec", "quest", "racing", "radio", "re", "read",
                "realestate", "realtor", "realty", "recipes", "red", "redstone", "redumbrella",
                "rehab", "reise", "reisen", "reit", "reliance", "ren", "rent", "rentals", "repair",
                "report", "republican", "rest", "restaurant", "review", "reviews", "rexroth",
                "rich", "richardli", "ricoh", "ril", "rio", "rip", "ro", "rocks", "rodeo", "rogers",
                "room", "rs", "rsvp", "ru", "rugby", "ruhr", "run", "rw", "rwe", "ryukyu", "sa",
                "saarland", "safe", "safety", "sakura", "sale", "salon", "samsclub", "samsung",
                "sandvik", "sandvikcoromant", "sanofi", "sap", "sarl", "sas", "save", "saxo", "sb",
                "sbi", "sbs", "sc", "scb", "schaeffler", "schmidt", "scholarships", "school",
                "schule", "schwarz", "science", "scot", "sd", "se", "search", "seat", "secure",
                "security", "seek", "select", "sener", "services", "seven", "sew", "sex", "sexy",
                "sfr", "sg", "sh", "shangrila", "sharp", "shell", "shia", "shiksha", "shoes",
                "shop", "shopping", "shouji", "show", "si", "silk", "sina", "singles", "site",
                "sj", "sk", "ski", "skin", "sky", "skype", "sl", "sling", "sm", "smart", "smile",
                "sn", "sncf", "so", "soccer", "social", "softbank", "software", "sohu", "solar",
                "solutions", "song", "sony", "soy", "spa", "space", "sport", "spot", "sr", "srl",
                "ss", "st", "stada", "staples", "star", "statebank", "statefarm", "stc", "stcgroup",
                "stockholm", "storage", "store", "stream", "studio", "study", "style", "su",
                "sucks", "supplies", "supply", "support", "surf", "surgery", "suzuki", "sv",
                "swatch", "swiss", "sx", "sy", "sydney", "systems", "sz", "tab", "taipei", "talk",
                "taobao", "target", "tatamotors", "tatar", "tattoo", "tax", "taxi", "tc", "tci",
                "td", "tdk", "team", "tech", "technology", "tel", "temasek", "tennis", "teva",
                "tf", "tg", "th", "thd", "theater", "theatre", "tiaa", "tickets", "tienda", "tips",
                "tires", "tirol", "tj", "tjmaxx", "tjx", "tk", "tkmaxx", "tl", "tm", "tmall",
                "tn", "to", "today", "tokyo", "ton", "tools", "top", "toray", "toshiba", "total",
                "tours", "town", "toyota", "toys", "tr", "trade", "trading", "training", "travel",
                "travelers", "travelersinsurance", "trust", "trv", "tt", "tube", "tui", "tunes",
                "tushu", "tv", "tvs", "tw", "tz", "ua", "ubank", "ubs", "ug", "uk", "unicom", "university",
                "uno", "uol", "ups", "us", "uy", "uz", "va", "vacations", "vana", "vanguard",
                "vc", "ve", "vegas", "ventures", "verisign", "vermögensberater", "vermögensberatung",
                "versicherung", "vet", "vg", "vi", "viajes", "video", "vig", "viking", "villas",
                "vin", "vip", "virgin", "visa", "vision", "viva", "vivo", "vlaanderen", "vn", "vodka",
                "volvo", "vote", "voting", "voto", "voyage", "vu", "wales", "walmart", "walter",
                "wang", "wanggou", "watch", "watches", "weather", "weatherchannel", "webcam",
                "weber", "website", "wed", "wedding", "weibo", "weir", "wf", "whoswho", "wien",
                "wiki", "williamhill", "win", "windows", "wine", "winners", "wme", "wolterskluwer",
                "woodside", "work", "works", "world", "wow", "ws", "wtc", "wtf", "xbox", "xerox",
                "xihuan", "xin", "ελ", "ευ", "бг", "бел", "дети", "ею", "католик", "ком", "мкд",
                "мон", "москва", "онлайн", "орг", "рус", "рф", "сайт", "срб", "укр", "қаз", "հայ",
                "ישראל", "קום", "ابوظبي", "ارامكو", "الاردن", "البحرين", "الجزائر", "السعودية",
                "العليان", "المغرب", "امارات", "ایران", "بارت", "بازار", "بيتك", "بھارت", "تونس",
                "سودان", "سورية", "شبكة", "عراق", "عرب", "عمان", "فلسطين", "قطر", "كاثوليك", "كوم",
                "مصر", "مليسيا", "موريتانيا", "موقع", "همراه", "پاکستان", "ڀارت", "कॉम", "नेट", "भारत",
                "भारतम्", "भारोत", "संगठन", "বাংলা", "ভারত", "ভাৰত", "ਭਾਰਤ", "ભારત", "ଭାରତ", "இந்தியா",
                "இலங்கை", "சிங்கப்பூர்", "భారత్", "ಭಾರತ", "ഭാരതം", "ලංකා", "คอม", "ไทย", "ລາວ",
                "გე", "みんな", "アマゾン", "クラウド", "グーグル", "コム", "ストア", "セール", "ファッション",
                "ポイント", "世界", "中信", "中国", "中國", "中文网", "亚马逊", "企业", "佛山", "信息",
                "健康", "八卦", "公司", "公益", "台湾", "台灣", "商城", "商店", "商标", "嘉里", "嘉里大酒店",
                "在线", "大拿", "天主教", "娱乐", "家電", "广东", "微博", "慈善", "我爱你", "手机", "招聘",
                "政务", "政府", "新加坡", "新闻", "时尚", "書籍", "机构", "淡马锡", "游戏", "澳門", "点看",
                "移动", "组织机构", "网址", "网店", "网站", "网络", "联通", "谷歌", "购物", "通販", "集团",
                "電訊盈科", "飞利浦", "食品", "餐厅", "香格里拉", "香港", "닷넷", "닷컴", "삼성", "한국",
                "xxx", "xyz", "yachts", "yahoo", "yamaxun", "yandex", "ye", "yodobashi", "yoga",
                "yokohama", "you", "youtube", "yt", "yun", "za", "zappos", "zara", "zero", "zip",
                "zm", "zone", "zuerich", "zw")


class _EntityMatch:
    """
    Args
        start_pos (int): The start position of the entity.
        end_pos (int): The end position of the entity.
        text (str): The text entities are parsed from. It is used for calculating
            utf16 offset.
        match (re.Match): The raw regex match object.
    """
    def __init__(self, match: re.Match, text:str):
        self._match = match
        self._start = self._match.start()
        self._end = self._match.end()

        self._utf16_offset = _get_utf16_length(text[:self._start])
        self._length = _get_utf16_length(text[self._start:self._end])

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def utf16_offset(self):
        return self._utf16_offset

    @property
    def utf16_length(self):
        return self._length

    def group(self, value: Any):
        return self._match.group(value)


def _get_utf16_length(text: str) -> int:
    """
    Return the length of the ``text`` in UTF-16 code units.

    Telegram `uses UTF-16 <https://core.telegram.org/api/entities#utf-16>`_
    for message entities

    A simple way of computing the entity length is converting the text to UTF-16,
    and then taking the byte length divided by 2 (number of UTF-16 code units).
    `Source <https://core.telegram.org/api/entities#computing-entity-length>`_

    Args:
       text (str): A string to calculate the length for.

    Returns:
        int: The length of the given string.
    """
    return len(text.encode("utf-16-le")) // 2


def get_item(seq: Sequence, index: int, default: Any = None, *,
             allow_negative_indexing: bool = True) -> Any:
    """
    Safely gets item from the sequence by its index.
    If the ``index`` is out of the range, then the ``default`` value is returned.

    Args:
        seq(~collections.abc.Sequence) : A sequence to get the item from.
        index (int): An item's index.
        default (~typing.Any, optional):  The value to be returned if the ``index``
            is out of the range, defaults to :obj:`None`.
        allow_negative_indexing (bool): if ``False`` then negative ``index``es (-1, -22, -113, etc.)
            will be considered as invalid, and the ``default`` value will be returned.

    Returns:
        ~typing.Any: An item under the given ``index`` or the ``default`` value.
    """
    # An empty sequence.
    if not seq:
        return default

    # The positive index, but it is out of the range.
    if index > 0 and index >= len(seq):
        return default

    # The negative index, but it is out of the range.
    if index < 0 and (not allow_negative_indexing or abs(index) > len(seq)):
        return default

    return seq[index]


def _check_and_normalize_url(url: str) -> str:
    """
    Check whether the ``url`` is valid, according to Telegram rules.

    Args:
        url (str): The ``url`` to be checked.
    Returns:
        str: Empty string if the ``url`` is invalid, normalized URL otherwise.
    """
    # The URL must not start or end with whitespace,
    # and it must not contain the new line character.
    if not url or url.startswith(" ") or url.endswith(" ") or "\n" in url:
        return ""

    result = url

    # If the protocol is not specified, sets 'http' protocol
    if "://" not in result:
        result = "http://" + result

    try:
        parsed_url = urlparse(result)
    except ValueError:
        return ""

    if parsed_url.scheme not in ("http", "https", "ton", "tg", "tonsite"):
        return ""

    # Validate domain name.
    pattern_valid_domain = re.compile(r"^(?=.{1,255}$)(?!-)[A-Za-z0-9\-]{1,63}"
                                      r"(\.[A-Za-z0-9\-]{1,63})*\.?(?<!-)$")
    if not pattern_valid_domain.match(parsed_url.netloc):
        return ""

    # Adding trailing slash only for URLs without a path.
    # E.g., https://www.example.com - adds the slash.
    # https://www.example.com/login - doesn't add the slash.
    if not parsed_url.path and not result.endswith("/"):
        result += "/"

    return result


def _get_id_from_telegram_url(type_: Literal["user", "emoji"], url: str) -> Optional[int]:
    """
    Extract a user or emoji ID from the Telegram URL.

    Examples of URLs: ``tg://user?id=123456789``, ``tg://emoji?id=5368324170671202286``

    Args:
        type_ (str): One of `'user'` or `'emoji'`. Depends on the ID that must be extracted.
        url (str): A URL to extract the ID from.
    Returns:
        int, optional: Extracted ID or :obj:`None` if no ID was found.
    """
    if type_ not in ("user", "emoji"):
        raise ValueError(f"Wrong type - {type_}")

    id_ = None
    if match := re.match(rf"tg://{type_}\?id=(\d+)", url):
        id_ = int(match.group(1))

    return id_


def get_hash(obj: TelegramObject) -> int:
    """
    Generate the unique hash value for objects that are inherited
    from :obj:`~telegram.TelegramObject`.

    The :meth:`telegram.TelegramObject.__hash__` method considers only certain
    attributes described in ``_id_attrs``.

    E.g., the ``_id_attrs`` of :obj:`~telegram.MessageEntity` is
    ``(self.type, self.offset, self.length)``.
    It means that ``MessageEntity("url", 1, 2)``
    and ``MessageEntity("url", 1, 2, url="https://ex.com)`` are equal and get the same hash.

    The ``get_hash`` function transforms ``obj`` into a JSON string
    and then gets hash of that string.

    Args:
        obj (:obj:`~telegram.TelegramObject`): An object to generate hash for.

    Returns:
        int: A hash value for the given object.
    """
    return hash(obj.to_json())


def _split_and_sort_intersected_entities(entities):
    """
    The function splits nested intersected entities.
    Therefore, ``parse_markdown_v2`` and ``parse_html`` functions will
    return the same result as the Telegram server does.

    Example:
        An input string is ``*hello _italic ~world~ italic_ world*``.

        By default, :meth:`~ptbtest.entityparser.EntityParser.parse_markdown_v2` returns:

        .. code:: python

            MessageEntity(length=31, offset=0, type=MessageEntityType.BOLD)
            MessageEntity(length=19, offset=6, type=MessageEntityType.ITALIC)
            MessageEntity(length=5, offset=13, type=MessageEntityType.STRIKETHROUGH)

        For the same string, the Telegram server returns:

        .. code:: python

            MessageEntity(length=6, offset=0, type=MessageEntityType.BOLD)
            MessageEntity(length=7, offset=6, type=MessageEntityType.BOLD)
            MessageEntity(length=7, offset=6, type=MessageEntityType.ITALIC)
            MessageEntity(length=18, offset=13, type=MessageEntityType.BOLD)
            MessageEntity(length=12, offset=13, type=MessageEntityType.ITALIC)
            MessageEntity(length=5, offset=13, type=MessageEntityType.STRIKETHROUGH)

    Args:
        entities (Sequence[~telegram.MessageEntity]): A list of all entities that were found in
            the text.

    Returns:
        (list[~telegram.MessageEntity]):
            A list of sorted and split entities.
    """
    def sort_entities(e):
        return sorted(e, key=lambda m: (m.offset, -m.length, PRIORITIES[m.type]))

    new_entities = list()
    # Sorting the entities in the order in which they appear in the sentence
    entities = sort_entities(entities)
    while entities:
        # Taking the leftmost entities and check all other entities against it.
        base_ent = entities.pop(0)
        # [Expandable]Blockquotes and text links must not be split.
        if base_ent.type in (MessageEntityType.BLOCKQUOTE,
                             MessageEntityType.EXPANDABLE_BLOCKQUOTE,
                             MessageEntityType.TEXT_LINK):
            new_entities.append(base_ent)
            continue

        for e in entities:
            # If the next entity is inside the current one,
            # then the base entity should be split.
            if e.offset < base_ent.offset + base_ent.length:
                d_base = base_ent.to_dict()
                d_new = d_base.copy()

                d_new["length"] = e.offset - d_new["offset"]
                if d_new["length"] > 0:
                    new_entities.append(MessageEntity(**d_new))

                d_base["length"] -=  d_new["length"]
                d_base["offset"] = e.offset
                base_ent = MessageEntity(**d_base)

        new_entities.append(base_ent)

    return sort_entities(new_entities)


def _decode_html_entity(in_text: str, position: int) -> tuple[Optional[str], int]:
    """
    Decode HTML entity that starts at ``position`` in ``in_text``.

    .. note::
        As for April 2025, the API supports only the following named
        HTML entities: ``&lt;``, ``&gt;``, ``&amp;`` and ``&quot;``.

    Examples:
        .. code:: python

            _decode_html_entity("&lt;", 0) == ('<', 4)
            _decode_html_entity("&#69;", 0) == ('E', 5)
            _decode_html_entity("In the middle &amp; of the sentence", 14) == ('&', 19)

    Args:
        in_text (str): A string with an HTML entity.
        position (int): The position where the entity starts from.

    Returns:
        str (optional), int: The entity and new position in text
        (right after the entity).

    Raises:
        ValueError: if the character at the ``position`` is not the '&'.
    """
    if not in_text:
        return None, position

    if position >= len(in_text) or position < 0:
        return None, position

    if in_text[position] != "&":
        raise ValueError(f"The character ('{in_text[position]}') at the "
                         f"position {position} is not '&'")

    end_pos = position + 1
    result = None

    # Numeric character reference.
    if get_item(in_text, position + 1) == "#":
        end_pos += 1
        entity_code = None
        # Hexadecimal numeric character reference
        if get_item(in_text, position + 2, "") in "xX":
            end_pos += 1
            hex_num = ""

            while ch := get_item(in_text, end_pos):
                if ch not in string.hexdigits:
                    break
                hex_num += ch
                end_pos += 1

            # Check whether the 'hex_str' is a valid hex number.
            try:
                entity_code = int(hex_num, 16)
            except ValueError:
                entity_code = None
        # decimal numeric character reference
        else:
            decimal_num = ""
            while ch := get_item(in_text, end_pos):
                # Do not use string.isdigit()/isnumeric()/isdecimal()
                # because those functions considers as digits much wider
                # range of characters than just 0...9 as Telegram does.
                # See this SO answer https://stackoverflow.com/a/54912545/19813684
                if ch not in string.digits:
                    break
                decimal_num += ch
                end_pos += 1

            # Check whether the 'decimal_num' is a valid decimal number.
            try:
                entity_code = int(decimal_num)
            except ValueError:
                entity_code = None

        if entity_code:
            if entity_code >= 0x10FFFF:
                return None, position

            hex_str = str(hex(entity_code)).removeprefix("0x")
            result = html.unescape(f"&#x{hex_str}")
            # 'html.unescape' returns empty string for hex
            # codes that don't have HTML entities.
            # In such cases, Telegram returns hex code with the
            # '\U00' prefix.
            # IN: "&#x10FFFE;", OUT: "\U0010fffe"
            if not result:
                result = r"\U00" + hex_str.lower()

        # If received an invalid entity,
        # or numeric entity was out of Unicode range (>= 0x10ffff),
        # or entity is enormously large.
        if result is None or result == "�" or end_pos - position >= 10:
            return None, position

        result = str(result)
    else:
        while ch := get_item(in_text, end_pos):
            if ch not in string.ascii_letters:
                break
            end_pos += 1
        mapping = {"lt": "<", "gt": ">", "amp": "&", "quot": "\""}
        entity = in_text[position + 1:end_pos]
        if entity not in mapping:
            return None, position

        result = mapping[entity]

    position = end_pos + 1 if get_item(in_text, end_pos) == ";" else end_pos

    return result, position


def _is_hashtag_letter(letter: str) -> bool:
    """
    Check if the ``letter`` can be a part of the hashtag entity.

    The character is considered valid if it fits one of the requirements:
     - underscore
     - middle dot
     - Zero Width Non-Joiner (ZWNJ)
     - alphabetic (the Unicode category is one of the “Lm”, “Lt”, “Lu”, “Ll”, or “Lo”
     - decimal (the Unicode category is "Nd")

    Args:
        letter: A letter that must be validated.

    Returns:
        bool: True if the ``letter`` is the valid hashtag character, False otherwise.
    """
    if letter and (letter in "_·" or letter == "\u200c" or letter.isalpha() or letter.isdecimal()):
        return True
    else:
        return False


def _fix_url(full_url: str) -> str:
    has_protocol = False
    url = full_url
    protocols_pattern = re.compile(r"^(https?|ftp|tonsite)://", flags=re.IGNORECASE)

    if match := protocols_pattern.match(full_url):
        has_protocol = True
        url = url[match.end():]

    domain_end = len(url)
    # Looking for the leftmost position of
    # the one of the given chars (these chars divide
    # the domain and the path).
    for ch in "/?#":
        pos = url.find(ch)
        if pos > -1 and pos < domain_end:
            domain_end = pos
    domain, path = url[:domain_end], url[domain_end:]

    if (at_pos := domain.find("@")) > -1:
        domain = domain[at_pos+1:]

    if (colon_pos := domain.rfind(":")) > -1:
        domain = domain[:colon_pos]

    if domain.lower() == "teiegram.org":
        return ""

    parentheses_cnt, square_br_cnt, curly_br_cnt = 0, 0, 0

    path_pos = 0
    for ch in path:
        if ch == "(":
            parentheses_cnt += 1
        elif ch == ")":
            parentheses_cnt -= 1
        elif ch == "[":
            square_br_cnt += 1
        elif ch == "]":
            square_br_cnt -= 1
        elif ch == "{":
            curly_br_cnt += 1
        elif ch == "}":
            curly_br_cnt -= 1

        if parentheses_cnt < 0 or square_br_cnt < 0 or curly_br_cnt < 0:
            break

        path_pos += 1

    bad_path_end_chars = ".:;,('?!`"

    while path_pos > 0 and path[path_pos-1] in bad_path_end_chars:
        path_pos -= 1

    full_url = full_url[:len(full_url) - (len(path) - path_pos)]

    is_ipv4 = True
    try:
        ipaddress.ip_address(domain)
    except ValueError:
        is_ipv4 = False

    domain_parts = domain.split(".")
    if len(domain_parts) <= 1:
        return ""

    def validator(text):
        return not text or len(text) >= 64 or text.endswith("-")

    if any(map(validator, domain_parts)):
        return ""

    if is_ipv4:
        return full_url

    # The "google" part in "google.com".
    second_level_domain = domain_parts[-2]
    # Skip the URL if there are no subdomains and domain starts with a underscore.
    if len(domain_parts) == 2 and second_level_domain.startswith("_"):
        return ""

    # If the 2nd level domain consists of whitespaces only.
    if not second_level_domain.strip():
        return ""
    # Telegram considers the underscore as an invalid symbol
    # only in the second level domain, while for all subdomains
    # it is perfectly OK.
    elif "_" in second_level_domain:
        return ""

    # .com, .net, .org, etc.
    tld = domain_parts[-1].rstrip("…")
    if len(tld) <= 1:
        return ""

    def is_common_tld(tld: str) -> bool:
        if tld.islower():
            return tld in COMMON_TLDS

        lowered = tld.lower()
        if lowered != tld and lowered[1:] == tld[1:]:
            return False

        return lowered in COMMON_TLDS

    if tld.startswith("xn--"):
        if len(tld) <= 5 or re.search(r"[^0-9a-zA-Z]", tld[4:]):
            return ""
    else:
        if tld.count("_") + tld.count("-") > 0:
            return ""

        if not has_protocol and not is_common_tld(tld):
            return ""

    return full_url


def _is_email_address(text: str) -> bool:
    """
    Check if the given ``text`` is a valid email address.
    """
    pattern = re.compile(r"^([a-z0-9_-]{0,26}[.+:]){0,10}"
                         r"[a-z0-9_-]{1,35}"
                         r"@(([a-z0-9][a-z0-9_-]{0,28})?[a-z0-9][.]){1,6}"
                         r"[a-z]{2,8}$", flags=re.IGNORECASE)

    return bool(pattern.search(text))


class EntityParser:
    @staticmethod
    def parse_markdown(text: str) -> tuple[str, tuple[MessageEntity, ...]]:
        """
        Extract :obj:`~telegram.MessageEntity` from ``text`` with the
        `Markdown V1 <https://core.telegram.org/bots/api#markdown-style>`_ markup.

        Examples:
            An input string: ``*hello* _world_ `!```

            Result:

            .. code:: python

                ('hello world !',
                 (MessageEntity(length=5, offset=0, type=<MessageEntityType.BOLD>),
                  MessageEntity(length=5, offset=6, type=<MessageEntityType.ITALIC>),
                  MessageEntity(length=1, offset=12, type=<MessageEntityType.CODE>)))

        Args:
            text (str): A string with Markdown V1 markup.

        Returns:
            (str, tuple[~telegram.MessageEntity]): The clean string without entity
            symbols, and tuple with :obj:`~telegram.MessageEntity`.
            The tuple might be empty if no entities were found.

        Raises:
            ~ptbtest.errors.BadMarkupException: If find unclosed entity or empty string
                is sent.
        """
        entities = list()
        striped_text = text.strip()
        text_size = len(striped_text)
        utf16_offset = 0
        new_text = list()

        # https://github.com/TelegramMessenger/libprisma#supported-languages
        pre_code_language_pattern = re.compile(r"^([a-z0-9-]+)\s+")

        i = 0
        while i < text_size:
            ch = striped_text[i]
            if ch == "\\" and get_item(striped_text, i+1) in "_*`[":
                # Skip the escape symbol (\).
                i += 1
                new_text.append(striped_text[i])
                # Go to the next char in the given string.
                i += 1
                utf16_offset += 1
                continue

            # Current char is NOT an entity beginning.
            # Save it 'as is' and go on to the next char
            if ch not in "_*`[":
                # Here it might be any symbol, and it can have any length.
                # E.g. 'A' has 1 code unit, '©' has 1 code unit, '😊' has 2 code units.
                utf16_offset += _get_utf16_length(ch)
                new_text.append(ch)
                i += 1
                continue

            # Telegram returns error messages with the offset specified in bytes.
            # The length of strings and byte strings might be different. E.g.:
            # len('A©😊') == 3, while len('A©😊'.encode()) == 7.
            # This value is used only for the error message.
            begin_index_utf16 = len(striped_text[:i].encode())
            end_character = ch

            if ch == "[":
                end_character = "]"

            # Skipping the entity's opening char.
            i += 1
            language = ""

            is_pre = False
            if ch == "`" and i + 2 < text_size and striped_text[i:i+2] == "``":
                # The code entity has three chars (```).
                # The first one was skipped the few lines above
                # (`i += 1` just above this `if`).
                # Increasing the counter by 2 to skip the rest of the entity's
                # symbols and jump to the text.
                i += 2
                is_pre = True
                # Trying to get language name.
                # E.g.:
                # ```python <- this name
                # code snippet here
                # ```
                if lang_match := pre_code_language_pattern.match(striped_text[i:]):
                    # .group(0) contains trailing space too.
                    # .group(1) contains the language name only.
                    language = lang_match.group(1)
                    i += len(language)

                if striped_text[i] in "\r\n":
                    i += 1

            entity_offset = utf16_offset

            entity_content_pattern = fr"^(.*?)\{end_character}"
            if is_pre:
                entity_content_pattern = r"^(.*?)```"

            # Here we parse all content inside the entity
            # up to closing symbol (which is not included).
            if entity_content_match := re.match(entity_content_pattern,
                                                striped_text[i:],
                                                re.DOTALL):
                entity_end_char = "```" if is_pre else end_character
                entity_content = (entity_content_match.group()
                                  .removesuffix(entity_end_char))
                i += len(entity_content)

                # If this is the end of the message, then remove ALL trailing
                # whitespaces and new line characters.
                if i + len(entity_end_char) == text_size:
                    entity_content = entity_content.rstrip()

                # If the current entity is a link (starts with '[')...
                if ch == "[":
                    # ... and there is a whitespace or a newline between
                    # square brackets and parentheses
                    if re.match(r"^]\s+\([^)]+\)", striped_text[i:]):
                        # Saving the content of the square brackets 'as is'.
                        new_text.append(entity_content)
                        # `+1` here is the length of the entity's end char (`]`).
                        i += 1
                        continue
                    # ... or if there is nothing after the entity or there are
                    # only whitespaces, then remove all whitespaces at the end
                    # of the string.
                    # Here the trailing whitespace WON'T be striped:
                    # `[inline URL ](http://www.example.com) with trailing text.`
                    # While here the whitespace WILL be striped:
                    # `[inline URL ](http://www.example.com)`
                    elif (get_item(striped_text, i + 1) == "(" and
                            not re.match(r"^]\(.*?\)\s*\S.*", striped_text[i:])):
                        entity_content = entity_content.rstrip()

                utf16_offset += _get_utf16_length(entity_content)
                new_text.append(entity_content)
            # The code reached the end of the text, but the end
            # of the entity wasn't found.
            if i == text_size or not entity_content_match:
                # `telegram.Bot` raises `telegram.error.BadRequest` error.
                raise BadMarkupException(f"Can't parse entities: can't find end of the entity "
                                         f"starting at byte offset {begin_index_utf16}")

            if entity_offset != utf16_offset:
                entity_length = utf16_offset - entity_offset
                if ch == "_":
                    entities.append(MessageEntity(MessageEntity.ITALIC,
                                                  entity_offset,
                                                  entity_length))
                elif ch == "*":
                    entities.append(MessageEntity(MessageEntity.BOLD,
                                                  entity_offset,
                                                  entity_length))
                elif ch == "[":
                    url = ""
                    if get_item(striped_text, i + 1) == "(":
                        i += 2
                        while i < text_size and striped_text[i] != ")":
                            url += striped_text[i]
                            i += 1
                    # If there is no part with the URL (only square brackets:
                    # `[no URL part here]`) and the current entity is the only
                    # entity for now (the left most in the text), then we must strip
                    # all whitespaces at the beginning of the string.
                    else:
                        if len(new_text) == 1:
                            new_text[-1] = new_text[-1].lstrip()

                    if checked_url := _check_and_normalize_url(url):
                        # As for April 2025, inline mentioning doesn't work (from the server side).
                        # If mentioning was found, skip it.
                        # E.g.: [inline mention of a user](tg://user?id=123456789)
                        if not checked_url.startswith("tg://"):
                            entities.append(MessageEntity(MessageEntity.TEXT_LINK,
                                                          entity_offset,
                                                          entity_length,
                                                          url=checked_url))
                elif ch == "`":
                    if is_pre:
                        entities.append(MessageEntity(MessageEntity.PRE,
                                                      entity_offset,
                                                      entity_length,
                                                      language=language))

                    else:
                        entities.append(MessageEntity(MessageEntity.CODE,
                                                      entity_offset,
                                                      entity_length))

            if is_pre:
                i += 2
            i += 1

        result_str = "".join(new_text).rstrip()
        if not result_str:
            raise BadMarkupException("Text must be non-empty")

        return result_str, tuple(entities)

    @staticmethod
    def parse_markdown_v2(text: str) -> tuple[str, tuple[MessageEntity, ...]]:
        """
        Extract :obj:`~telegram.MessageEntity` from ``text`` with the
        `Markdown V2 <https://core.telegram.org/bots/api#markdownv2-style>`_ markup.

        Examples:
            An input string: ``*hello _nested __entities__ beautiful_ world*``

            Result:

            .. code:: python

                ('hello nested entities beautiful world',
                 (MessageEntity(length=6, offset=0, type=<MessageEntityType.BOLD>),
                  MessageEntity(length=7, offset=6, type=<MessageEntityType.BOLD>),
                  MessageEntity(length=7, offset=6, type=<MessageEntityType.ITALIC>),
                  MessageEntity(length=24, offset=13, type=<MessageEntityType.BOLD>),
                  MessageEntity(length=18, offset=13, type=<MessageEntityType.ITALIC>),
                  MessageEntity(length=8, offset=13, type=<MessageEntityType.UNDERLINE>)))

        Args:
            text (str): A string with Markdown V2 markup.

        Returns:
            (str, tuple[~telegram.MessageEntity]): The clean string without entity
            symbols, and tuple with :obj:`~telegram.MessageEntity`.
            The tuple might be empty if no entities were found.

        Raises:
            ~ptbtest.errors.BadMarkupException: If find unclosed entity, unescaped
             reserved character or empty string is sent.
        """
        err_msg_entity = ("Can't parse entities: can't find end of "
                          "{entity_type} entity at byte offset {offset}")
        err_msg_reserved = ("Can't parse entities: character '{0}' is reserved "
                            "and must be escaped with the preceding '\\'")
        err_empty_text = "Message text is empty"

        have_blockquote = False
        can_start_blockquote = True

        striped_text = text.strip()

        offset = 0
        utf16_offset = 0
        text_size = len(striped_text)

        entities: list[MessageEntity] = list()
        nested_entities: list[MessageEntity] = list()
        result_text = ""
        # In this dict, the raw byte offset (the entity's start position
        # in the original string) of the entity will be stored.
        # The key is the entity's hash, and the value is the byte offset.
        # This dict will be used for error messages.
        raw_offset: dict[int, int] = dict()
        while offset < text_size:
            cur_ch = striped_text[offset]
            next_ch = get_item(striped_text, offset+1)
            # Processing escaped ASCII characters.
            if cur_ch == "\\" and 0 < ord(next_ch) <= 126:
                offset += 1
                result_text += striped_text[offset]
                utf16_offset += 1
                if striped_text[offset] != "\r":
                    can_start_blockquote = (striped_text[offset] == "\n")
                offset += 1
                continue

            reserved_characters = "_*[]()~`>#+-=|{}.!\n"
            if nested_entities:
                if nested_entities[-1].type in (MessageEntityType.CODE, MessageEntityType.PRE):
                    reserved_characters = "`"

            # Processing regular characters.
            if cur_ch not in reserved_characters:
                utf16_offset += _get_utf16_length(cur_ch)
                if cur_ch != "\r":
                    can_start_blockquote = False
                result_text += cur_ch
                offset += 1
                continue

            def is_end_of_entity() -> bool:
                """
                Check whether the current character is the one that closes the entity.
                """
                nonlocal text_size, offset, striped_text, cur_ch, have_blockquote, nested_entities

                if not nested_entities:
                    return False
                if (have_blockquote and cur_ch == "\n" and
                        (offset + 1 == text_size or get_item(striped_text, offset + 1) != ">")):
                    return True

                last_nested_entity_type = nested_entities[-1].type
                if last_nested_entity_type == MessageEntityType.BOLD:
                    is_end = (cur_ch == "*")
                elif last_nested_entity_type == MessageEntityType.ITALIC:
                    is_end = (cur_ch == "_" and get_item(striped_text, offset + 1) != "_")
                elif last_nested_entity_type == MessageEntityType.CODE:
                    is_end = (cur_ch == "`")
                elif last_nested_entity_type == MessageEntityType.PRE:
                    is_end = (cur_ch == "`"
                                        and get_item(striped_text, offset + 1) == "`"
                                        and get_item(striped_text, offset + 2) == "`")
                elif last_nested_entity_type == MessageEntityType.TEXT_LINK:
                    is_end = (cur_ch == "]")
                elif last_nested_entity_type == MessageEntityType.UNDERLINE:
                    is_end = (cur_ch == "_" and get_item(striped_text, offset + 1) == "_")
                elif last_nested_entity_type == MessageEntityType.STRIKETHROUGH:
                    is_end = (cur_ch == "~")
                elif last_nested_entity_type == MessageEntityType.SPOILER:
                    is_end = (cur_ch == "|" and get_item(striped_text, offset + 1) == "|")
                elif last_nested_entity_type == MessageEntityType.CUSTOM_EMOJI:
                    is_end = (cur_ch == "]")
                elif last_nested_entity_type == MessageEntityType.BLOCKQUOTE:
                    is_end = False
                else:
                    is_end = False

                return is_end

            user_id = None
            custom_emoji_id = None
            language = None
            url = None

            if not is_end_of_entity():
                entity_type: MessageEntityType = None
                entity_raw_begin_pos = offset
                if cur_ch == "_":
                    if get_item(striped_text, offset+1) == "_":
                        entity_type = MessageEntityType.UNDERLINE
                        offset += 1
                    else:
                        entity_type = MessageEntityType.ITALIC
                elif cur_ch == "*":
                    entity_type = MessageEntityType.BOLD
                elif cur_ch == "~":
                    entity_type = MessageEntityType.STRIKETHROUGH
                elif cur_ch == "|":
                    if get_item(striped_text, offset+1) == "|":
                        offset += 1
                        entity_type = MessageEntityType.SPOILER
                    else:
                        raise BadMarkupException(err_msg_reserved.format("|"))
                elif cur_ch == "[":
                    entity_type = MessageEntityType.TEXT_LINK
                elif cur_ch == "`":
                    if get_item(striped_text, offset+1) == "`" and get_item(striped_text, offset+2) == "`":
                        offset += 3
                        entity_type = MessageEntityType.PRE
                        # Trying to get language name.
                        # E.g.:
                        # ```python <- this name
                        # code snippet here
                        # ```
                        if lang_match := re.match(r"^([^\s`]+)\s+", striped_text[offset:]):
                            # .group(0) contains trailing space too.
                            # .group(1) contains the language name only.
                            language = lang_match.group(1)
                            offset += len(language)

                        # Without this condition, a whitespace right after the language
                        # name will be eaten.
                        if get_item(striped_text, offset, "") not in "\r\n":
                            offset -= 1
                    else:
                        entity_type = MessageEntityType.CODE
                elif cur_ch == "!":
                    if get_item(striped_text, offset+1) == "[":
                        offset += 1
                        entity_type = MessageEntityType.CUSTOM_EMOJI
                    else:
                        raise BadMarkupException(err_msg_reserved.format("!"))
                elif cur_ch == "\n":
                    utf16_offset += 1
                    result_text += cur_ch
                    can_start_blockquote = True
                elif cur_ch == ">":
                    if can_start_blockquote:
                        if not have_blockquote:
                            entity_type = MessageEntityType.BLOCKQUOTE
                            have_blockquote = True
                    else:
                        raise BadMarkupException(err_msg_reserved.format(">"))
                else:
                    raise BadMarkupException(err_msg_reserved.format(striped_text[offset]))

                if entity_type is None:
                    offset += 1
                    continue

                me = MessageEntity(type=entity_type, offset=utf16_offset,
                                   length=len(result_text) - utf16_offset,
                                   url=url, user=user_id, language=language,
                                   custom_emoji_id=custom_emoji_id)

                # By default, the error message for an empty string
                # is "Message text is empty", but if there was at least
                # one entity, the text changes to "text must be non-empty".
                if err_empty_text == "Message text is empty":
                    err_empty_text = "Text must be non-empty"

                nested_entities.append(me)

                raw_offset[get_hash(me)] = len(striped_text[:entity_raw_begin_pos].encode())

            else:
                # lne stands for last_nested_entity
                lne = nested_entities[-1]
                e_type = lne.type

                if cur_ch == "\n" and e_type != MessageEntityType.BLOCKQUOTE:
                    if (e_type != MessageEntityType.SPOILER or
                            not (lne.offset == offset - 2 or
                                    (lne.offset == offset - 3 and len(result_text) != 0 and result_text[-1] == "\r"))):
                        raise BadMarkupException(err_msg_entity.format(entity_type=e_type, offset=lne.offset))
                    nested_entities.pop()

                    lne = nested_entities[-1]
                    if lne.type != MessageEntityType.BLOCKQUOTE:
                        raise BadMarkupException(err_msg_entity.format(entity_type=lne.type,
                                                                       offset=lne.offset))
                    e_type = MessageEntityType.EXPANDABLE_BLOCKQUOTE

                skip_entity = (utf16_offset == lne.offset)
                if e_type in (MessageEntityType.BOLD, MessageEntityType.ITALIC,
                              MessageEntityType.CODE, MessageEntityType.STRIKETHROUGH):
                    pass
                elif e_type in (MessageEntityType.UNDERLINE, MessageEntityType.SPOILER):
                    offset += 1
                elif e_type == MessageEntityType.PRE:
                    offset += 2
                elif e_type == MessageEntityType.TEXT_LINK:
                    url = ""
                    if get_item(striped_text, offset+1) != "(":
                        url = result_text[lne.offset: len(result_text) - lne.offset]
                    else:
                        offset += 2
                        url_begin_pos = len(striped_text[:offset].encode())
                        while offset < text_size and striped_text[offset] != ")":
                            if cur_ch == "\\" and 0 < ord(next_ch) <= 126:
                                url += striped_text[offset + 1]
                                offset += 2
                                continue
                            url += striped_text[offset]
                            offset += 1
                        if get_item(striped_text, offset) != ")":
                            msg = "Can't parse entities: can't find end of a url at byte offset %s"
                            raise BadMarkupException(msg % url_begin_pos)

                    user_id = _get_id_from_telegram_url("user", url)
                    # As for April 2025, inline mentioning doesn't work (from the server side).
                    # If mentioning was found, skip it.
                    if user_id is not None:
                        user_id = None
                        skip_entity = True
                    else:
                        url = _check_and_normalize_url(url)
                        if not url:
                            skip_entity = True
                elif e_type == MessageEntityType.CUSTOM_EMOJI:
                    if get_item(striped_text, offset+1) != "(":
                        raise BadMarkupException("Custom emoji entity must contain a tg://emoji URL")
                    offset += 2
                    url = ""
                    url_begin_pos = offset

                    while offset < text_size and striped_text[offset] != ")":
                        if cur_ch == "\\" and 0 < ord(next_ch) <= 126:
                            url += striped_text[offset + 1]
                            offset += 2
                            continue
                        url += striped_text[offset]
                        offset += 1
                    if striped_text[offset] != ")":
                        raise BadMarkupException(f"Can't find end of a custom emoji URL at byte offset {url_begin_pos}")

                    custom_emoji_id = _get_id_from_telegram_url("emoji", url)
                elif e_type in (MessageEntityType.BLOCKQUOTE, MessageEntityType.EXPANDABLE_BLOCKQUOTE):
                    have_blockquote = False
                    result_text += striped_text[offset]
                    can_start_blockquote = True
                    utf16_offset += 1
                    skip_entity = False
                else:
                    raise BadMarkupException(f"Unknown entity '{e_type}' type is received.")

                if not skip_entity:
                    entity_offset = nested_entities[-1].offset
                    entity_length = utf16_offset - entity_offset
                    if user_id:
                        e_type = MessageEntityType.MENTION
                    elif custom_emoji_id:
                        e_type = MessageEntityType.CUSTOM_EMOJI

                    entities.append(MessageEntity(e_type,
                                                  entity_offset,
                                                  entity_length,
                                                  user=user_id,
                                                  custom_emoji_id=custom_emoji_id,
                                                  url=url,
                                                  language=lne.language))

                nested_entities.pop()

            offset += 1

        if have_blockquote:
            e_type = MessageEntityType.BLOCKQUOTE
            if nested_entities:
                lne = nested_entities[-1]
                if lne.type == MessageEntityType.SPOILER and lne.offset == len(result_text.encode()):
                    nested_entities.pop()
                    del lne
                    e_type = MessageEntityType.EXPANDABLE_BLOCKQUOTE

                lne = nested_entities[-1]
                if lne.type == MessageEntityType.BLOCKQUOTE:
                    entity_offset = lne.offset
                    entity_length = utf16_offset - entity_offset
                    if entity_length > 0:
                        entities.append(MessageEntity(e_type,
                                                      entity_offset,
                                                      entity_length))
                    nested_entities.pop(-1)

        if nested_entities:
            byte_offset = raw_offset[get_hash(nested_entities[-1])]
            entity_type = nested_entities[-1].type
            # Telegram has two different entities which are 'pre' and 'precode',
            # while PTB has only 'pre'.
            # 'pre' for code WITHOUT 'language' specified, and
            # 'precode' for code WITH 'language'
            if entity_type == MessageEntityType.PRE and nested_entities[-1].language:
                entity_type = "precode"
            raise BadMarkupException(err_msg_entity.format(entity_type=entity_type,
                                                           offset=byte_offset))
        len_before_strip = len(result_text)
        result_text = result_text.rstrip()
        # There were trailing new lines or whitespaces.
        if entities and len_before_strip != len(result_text):
            last_entity = entities[-1]
            # Trailing whitespaces were inside an entity, we must subtract
            # the length of striped whitespaces from the length of the entity.
            if len_before_strip == last_entity.offset + last_entity.length:
                d = last_entity.to_dict()
                d["length"] -= (len_before_strip - len(result_text))
                if d["length"] > 0:
                    entities[-1] = MessageEntity(**d)
                else:
                    entities.pop()

        if not result_text:
            raise BadMarkupException(err_empty_text)

        sorted_entities = _split_and_sort_intersected_entities(entities)
        if not sorted_entities:
            result_text = result_text.strip()

        return result_text, tuple(sorted_entities)

    @staticmethod
    def parse_html(text: str) -> tuple[str, tuple[MessageEntity, ...]]:
        """
        Extract :obj:`~telegram.MessageEntity` from ``text`` with the
        `HTML <https://core.telegram.org/bots/api#html-style>`_ markup.

        Examples:
            An input string: ``<b>hello <i>italic <u>underlined <s>nested</s> entities</u> wo</i>rld</b>``

            Result:

            .. code:: python

                ('hello italic underlined nested entities world',
                     (MessageEntity(length=6, offset=0, type=<MessageEntityType.BOLD>),
                      MessageEntity(length=7, offset=6, type=<MessageEntityType.BOLD>),
                      MessageEntity(length=7, offset=6, type=<MessageEntityType.ITALIC>),
                      MessageEntity(length=11, offset=13, type=<MessageEntityType.BOLD>),
                      MessageEntity(length=11, offset=13, type=<MessageEntityType.ITALIC>),
                      MessageEntity(length=11, offset=13, type=<MessageEntityType.UNDERLINE>),
                      MessageEntity(length=21, offset=24, type=<MessageEntityType.BOLD>),
                      MessageEntity(length=18, offset=24, type=<MessageEntityType.ITALIC>),
                      MessageEntity(length=15, offset=24, type=<MessageEntityType.UNDERLINE>),
                      MessageEntity(length=6, offset=24, type=<MessageEntityType.STRIKETHROUGH>)))

        Args:
            text (str): A string with HTML markup.

        Returns:
            (str, tuple[~telegram.MessageEntity]): The clean string without tags
            and tuple with :obj:`~telegram.MessageEntity`.
            The tuple might be empty if no entities were found.

        Raises:
            ~ptbtest.errors.BadMarkupException
        """
        err_msg_prefix = "Can't parse entities:"
        err_msg_empty_string = "Message text is empty"

        @dataclass
        class EntityInfo:
            tag_name: str
            argument: str
            entity_offset: int
            entity_begin_pos: int

        striped_text = text.strip()
        text_size = len(striped_text)
        offset = 0
        utf16_offset = 0

        entities: list[MessageEntity] = list()
        nested_entities: list[EntityInfo] = list()
        result_text = ""

        def get_byte_offset(begin_pos):
            """
            Return the length of the string in bytes starting from
            the beginning ann up to ``begin_pos``.
            """
            nonlocal striped_text
            return len(striped_text[:begin_pos].encode())

        while offset < text_size:
            cur_ch = striped_text[offset]
            # Processing HTML entities, like '&gt;', '&#65;'.
            if cur_ch == "&":
                decoded_entity, offset = _decode_html_entity(striped_text, offset)
                if decoded_entity:
                    utf16_offset += _get_utf16_length(decoded_entity)
                    result_text += decoded_entity
                    continue

            # Save regular characters as-is.
            if cur_ch != "<":
                result_text += cur_ch
                utf16_offset += _get_utf16_length(cur_ch)
                offset += 1
                continue

            offset += 1
            begin_pos = offset
            # The beginning of an entity.
            if (next_ch := get_item(striped_text, offset)) != "/":
                # Collecting the name of the tag.
                while next_ch is not None and not next_ch.isspace() and next_ch != ">":
                    offset += 1
                    next_ch = get_item(striped_text, offset)

                if offset >= text_size:
                    raise BadMarkupException(f"{err_msg_prefix} unclosed start tag at "
                                             f"byte offset {get_byte_offset(begin_pos - 1)}")

                tag_name = striped_text[begin_pos:offset].lower()

                if tag_name not in ALLOWED_HTML_TAG_NAMES:
                    raise BadMarkupException(f"{err_msg_prefix} unsupported start tag \"{tag_name}\" "
                                             f"at byte offset {get_byte_offset(begin_pos - 1)}")

                argument = None
                while striped_text[offset] != ">":
                    # Skip whitespaces between the tag name and the attribute name.
                    while offset < text_size and striped_text[offset].isspace():
                        offset += 1
                    if striped_text[offset] == ">":
                        break
                    attr_begin_pos = offset
                    while (get_item(striped_text, offset) and
                           not striped_text[offset].isspace() and
                           striped_text[offset] not in "=>/\"'"):
                        offset += 1

                    attr_name = striped_text[attr_begin_pos:offset]
                    if not attr_name:
                        raise BadMarkupException(f"{err_msg_prefix} empty attribute name in the tag \"{tag_name}\" "
                                                 f"at byte offset {get_byte_offset(begin_pos - 1)}")

                    while offset < text_size and striped_text[offset].isspace():
                        offset += 1

                    if get_item(striped_text, offset) != "=":
                        if offset >= text_size:
                            raise BadMarkupException(f"{err_msg_prefix} unclosed start tag \"{tag_name}\" "
                                                     f"at byte offset {get_byte_offset(begin_pos - 1)}")
                        if tag_name == "blockquote" and attr_name == "expandable":
                            argument = 1
                        continue
                    offset += 1

                    while offset < text_size and striped_text[offset].isspace():
                        offset += 1

                    if offset >= text_size:
                        raise BadMarkupException(f"{err_msg_prefix} unclosed start tag \"{tag_name}\" "
                                                 f"at byte offset {get_byte_offset(begin_pos - 1)}")

                    attr_value = ""
                    # Processing attr values without quotes.
                    # E.g., '<span class=tg-spoiler>spoiler</span>'
                    if striped_text[offset] not in "\"'":
                        token_begin_pos = offset
                        while striped_text[offset] in string.ascii_letters + string.digits + ".-":
                            offset += 1
                        attr_value = striped_text[token_begin_pos:offset].lower()

                        if not striped_text[offset].isspace() and striped_text[offset] != ">":
                            raise BadMarkupException(f"{err_msg_prefix} unexpected end of name token "
                                                     f"at byte offset {get_byte_offset(token_begin_pos)}")
                    # Attr values inside quotes.
                    else:
                        end_char = striped_text[offset]
                        offset += 1

                        while offset < text_size and striped_text[offset] != end_char:
                            if striped_text[offset] == "&":
                                html_entity, offset = _decode_html_entity(striped_text, offset)
                                if html_entity:
                                    attr_value += html_entity
                                    continue

                            attr_value += striped_text[offset]
                            offset += 1

                        if get_item(striped_text, offset) == end_char:
                            offset += 1

                    if offset >= text_size:
                        raise BadMarkupException(f"{err_msg_prefix} unclosed start tag at "
                                                 f"byte offset {get_byte_offset(begin_pos - 1)}")

                    if tag_name == "a" and attr_name == "href":
                        argument = attr_value
                    elif tag_name == "code" and attr_name == "class" and attr_value.startswith("language-"):
                        argument = attr_value.removeprefix("language-")
                    elif tag_name == "span" and attr_name == "class" and attr_value.startswith("tg-"):
                        argument = attr_value.removeprefix("tg-")
                    elif tag_name == "tg-emoji" and attr_name == "emoji-id":
                        argument = attr_value
                    elif tag_name == "blockquote" and attr_name == "expandable":
                        argument = "1"

                if tag_name == "span" and argument != "spoiler":
                    raise BadMarkupException(f"{err_msg_prefix} tag \"span\" must have class"
                                             f" \"tg-spoiler\" at byte offset "
                                             f"{get_byte_offset(begin_pos - 1)}")

                nested_entities.append(EntityInfo(
                    tag_name=tag_name,
                    argument=argument,
                    entity_offset=utf16_offset,
                    entity_begin_pos=begin_pos
                ))
                if err_msg_empty_string == "Message text is empty":
                    err_msg_empty_string = "Text must be non-empty"
            # The end of an entity
            else:
                if not nested_entities:
                    raise BadMarkupException(f"{err_msg_prefix} unexpected end tag at "
                                             f"byte offset {get_byte_offset(begin_pos - 1)}")
                while (get_item(striped_text, offset) and
                       not striped_text[offset].isspace()
                       and striped_text[offset] != ">"):
                    offset += 1
                end_tag_name = striped_text[begin_pos+1:offset]
                while offset < text_size and striped_text[offset].isspace():
                    offset += 1

                if get_item(striped_text, offset) != ">":
                    raise BadMarkupException(f"{err_msg_prefix} unclosed end tag at "
                                             f"byte offset {get_byte_offset(begin_pos - 1)}")

                tag_name = nested_entities[-1].tag_name
                if end_tag_name and end_tag_name != tag_name:
                    raise BadMarkupException(f"{err_msg_prefix} unmatched end tag at byte offset "
                                             f"{get_byte_offset(begin_pos - 1)}, expected \"</"
                                             f"{tag_name}>\", found \"</{end_tag_name}>\"")

                if utf16_offset > nested_entities[-1].entity_offset:
                    e_offset = nested_entities[-1].entity_offset
                    e_length = utf16_offset - e_offset

                    if tag_name in ("i", "em"):
                        entities.append(MessageEntity(MessageEntityType.ITALIC,
                                                      e_offset, e_length))
                    elif tag_name in ("b", "strong"):
                        entities.append(MessageEntity(MessageEntityType.BOLD,
                                                      e_offset, e_length))
                    elif tag_name in ("s", "strike", "del"):
                        entities.append(MessageEntity(MessageEntityType.STRIKETHROUGH,
                                                      e_offset, e_length))
                    elif tag_name in ("u", "ins"):
                        entities.append(MessageEntity(MessageEntityType.UNDERLINE,
                                                      e_offset, e_length))
                    elif tag_name == "tg-spoiler" or (tag_name == "span" and
                                                      nested_entities[-1].argument == "spoiler"):
                        entities.append(MessageEntity(MessageEntityType.SPOILER,
                                                      e_offset, e_length))
                    elif tag_name == "tg-emoji":
                        try:
                            emoji_id = int(nested_entities[-1].argument)
                        except ValueError:
                            raise BadMarkupException(f"{err_msg_prefix} invalid custom "
                                                     f"emoji identifier specified")

                        entities.append(MessageEntity(MessageEntityType.CUSTOM_EMOJI,
                                                      e_offset, e_length,
                                                      custom_emoji_id=str(emoji_id)))
                    elif tag_name == "a":
                        url = nested_entities[-1].argument
                        if not url:
                            begin = nested_entities[-1].entity_begin_pos
                            url = striped_text[begin+2:offset-3]

                        user_id = _get_id_from_telegram_url("user", url)
                        if user_id:
                            # As for April 2025, inline mentioning doesn't work (from the server side).
                            # If mentioning was found, then ignoring it.
                            # entities.append(MessageEntity(MessageEntityType.MENTION,
                            #                               e_offset, e_length,
                            #                               user=user_id))
                            pass
                        else:
                            url = _check_and_normalize_url(url)
                            if url:
                                entities.append(MessageEntity(MessageEntityType.TEXT_LINK,
                                                              e_offset, e_length, url=url))
                    elif tag_name == "pre":
                        if (entities and entities[-1].type == MessageEntityType.CODE
                                and entities[-1].offset == e_offset
                                and entities[-1].length == e_length):
                                # and entities[-1].language):
                            dict_e = entities[-1].to_dict()
                            dict_e["type"] = MessageEntityType.PRE
                            entities[-1] = MessageEntity(**dict_e)
                        else:
                            entities.append(MessageEntity(MessageEntityType.PRE,
                                                          e_offset, e_length))
                    elif tag_name == "code":
                        if (entities and entities[-1].type == MessageEntityType.PRE
                                and entities[-1].offset == e_offset
                                and entities[-1].length == e_length):
                            dict_e = entities[-1].to_dict()
                            dict_e["type"] = MessageEntityType.PRE
                            if nested_entities[-1].argument:
                                dict_e["language"] = nested_entities[-1].argument
                            entities[-1] = MessageEntity(**dict_e)
                        else:
                            entities.append(MessageEntity(MessageEntityType.CODE,
                                                          e_offset, e_length,
                                                          language=nested_entities[-1].argument))
                    elif tag_name == "blockquote":
                        if nested_entities[-1].argument:
                            entities.append(MessageEntity(MessageEntityType.EXPANDABLE_BLOCKQUOTE,
                                                          e_offset, e_length))
                        else:
                            entities.append(MessageEntity(MessageEntityType.BLOCKQUOTE,
                                                          e_offset, e_length))
                    else:
                        raise BadMarkupException(f"Unexpected tag name '{tag_name}'")
                nested_entities.pop()

            # End of the outermost while loop.
            offset += 1

        if nested_entities:
            raise BadMarkupException(f"{err_msg_prefix} can't find end tag corresponding to "
                                     f"start tag \"{nested_entities[-1].tag_name}\"")

        len_before_strip = len(result_text)
        result_text = result_text.rstrip()
        # There were trailing new lines or whitespaces.
        if entities and len_before_strip != len(result_text):
            last_entity = entities[-1]
            # Trailing whitespaces were inside an entity, we must subtract
            # the length of striped whitespaces from the length of the entity.
            if len_before_strip == last_entity.offset + last_entity.length:
                d = last_entity.to_dict()
                d["length"] -= (len_before_strip - len(result_text))
                if d["length"] > 0:
                    entities[-1] = MessageEntity(**d)
                else:
                    entities.pop()

        sorted_entities = _split_and_sort_intersected_entities(entities)

        if not sorted_entities:
            result_text = result_text.strip()

        for i, en in enumerate(sorted_entities):
            if en.type == MessageEntityType.CODE and en.language:
                d = en.to_dict()
                d["language"] = None
                sorted_entities[i] = MessageEntity(**d)

        if not result_text:
            raise BadMarkupException(err_msg_empty_string)

        return result_text, tuple(sorted_entities)

    @staticmethod
    def _extract_entities(text: str, pattern: Union[str, re.Pattern]) -> tuple[_EntityMatch, ...]:
        """
        Parse entities from text with the given regular expression.

        .. TODO: add all methods where this method is used.

            Used by:
                :meth:`parse_mentions`

        Args:
            text (str): Text that must be parsed.
            pattern (str | ~typing.Pattern): A regular expression.

        Returns:
            tuple[_EntityMatch]: A tuple of ``_EntityPosition`` with the offset and
            the length of the found entities.
            """
        if isinstance(pattern, str):
            pattern = re.compile(pattern)

        result = list()
        for match in pattern.finditer(text):
            result.append(_EntityMatch(match, text))

        return tuple(result)

    @staticmethod
    def parse_mentions(text: str) -> tuple[MessageEntity, ...]:
        """
        Extract :obj:`~telegram.MessageEntity` representing
        ``@mentions`` from ``text``.

        Examples:
            An input string: ``text with @multiple @mentions``

            Result:

            .. code:: python

                (MessageEntity(length=9, offset=10, type=MessageEntityType.MENTION),
                 MessageEntity(length=9, offset=20, type=MessageEntityType.MENTION))

        Args:
            text (str): A message that must be parsed.

        Returns:
            tuple[~telegram.MessageEntity]: Tuple of :obj:`~telegram.MessageEntity` with
            type :obj:`~telegram.constants.MessageEntityType.MENTION`.
            The tuple might be empty if no entities were found.
        """

        pattern = r"(?<=\B)@([a-zA-Z0-9_]{2,32})(?=\b)"

        points = EntityParser._extract_entities(text, pattern)

        allowed_3_char_mentions = ("@gif", "@vid", "@pic")
        entities: list[MessageEntity] = list()
        for entity_position in points:
            if entity_position.utf16_length < 4 or entity_position.utf16_length > 33:
                continue
            elif (entity_position.utf16_length == 4 and
                  text[entity_position.start:entity_position.end] not in allowed_3_char_mentions):
                continue

            entities.append(MessageEntity(MessageEntityType.MENTION,
                                          offset=entity_position.utf16_offset,
                                          length=entity_position.utf16_length))

        return tuple(entities)

    @staticmethod
    def parse_bot_commands(text: str) -> tuple[MessageEntity, ...]:
        """
        Extract :obj:`~telegram.MessageEntity` representing
        bot ``/commands`` from the given ``text``.

        Examples:
            An input string: ``/start``

            Result:

            .. code:: python

                (MessageEntity(length=6, offset=0, type=<MessageEntityType.BOT_COMMAND>),)

        Args:
            text (str): A message that must be parsed.

        Returns:
            tuple[~telegram.MessageEntity]: Tuple of :obj:`~telegram.MessageEntity` with
            type :obj:`~telegram.constants.MessageEntityType.BOT_COMMAND`.
            The tuple might be empty if no entities were found.
        """
        pattern = re.compile("(?<!\b|[/<>])/([a-zA-Z0-9_]{1,64})"
                             r"(?:@([a-zA-Z0-9_]{3,32}))?(?!\B|[/<>])")

        entities = list()
        for entity_position in EntityParser._extract_entities(text, pattern):
            entities.append(MessageEntity(MessageEntityType.BOT_COMMAND,
                                          offset=entity_position.utf16_offset,
                                          length=entity_position.utf16_length))

        return tuple(entities)

    @staticmethod
    def parse_hashtags(text: str) -> tuple[MessageEntity, ...]:
        """
        Extract :obj:`~telegram.MessageEntity` representing
        bot ``#hashtags`` from the given ``text``.

        Examples:
            An input string: ``#hashtag``

            Result:

            .. code:: python

                (MessageEntity(length=8, offset=0, type=<MessageEntityType.HASHTAG>),)

        Args:
            text (str): A message that must be parsed.

        Returns:
            tuple[~telegram.MessageEntity]: Tuple of :obj:`~telegram.MessageEntity` with
            type :obj:`~telegram.constants.MessageEntityType.HASHTAG`.
            The tuple might be empty if no entities were found.
        """
        cur_pos = 0

        entities = list()

        while (start_position := text.find("#", cur_pos)) >= 0:
            # Shift from the '#' character to the next one in the hashtag.
            cur_pos = start_position + 1
            has_letter = False

            if not (ch:=get_item(text, cur_pos, "")) or not _is_hashtag_letter(ch):
                continue
            # The hash sign ('#') is in the middle of the string.
            elif _is_hashtag_letter(get_item(text, start_position-1, "", allow_negative_indexing=False)):
                continue

            while _is_hashtag_letter(get_item(text, cur_pos, "")):
                # The length of a #hashtag must be less than or equal to 256
                # (excluding the '#' character).
                if (cur_pos + 1 - start_position) > 257:
                    break

                if not has_letter and text[cur_pos].isalpha():
                    has_letter = True

                cur_pos += 1

            # If the hashtag consists of digits only.
            if not has_letter:
                continue
            # If there is the '#' character right after the hashtag
            # (e.g., '#hashtag#'), then the hashtag must be ignored.
            if get_item(text, cur_pos) == "#":
                continue

            length = cur_pos - start_position

            if length < 257:
                # There is a '@mention' right after the hashtag.
                if get_item(text, cur_pos) == "@":
                    match = re.match(r"@[a-zA-Z0-9_]{3,32}", text[cur_pos:])
                    if match:
                        next_ch = get_item(text, length + match.end())
                        # If there is the '#' character right after the mention,
                        # then the mention must be ignored, otherwise the mention
                        # must be included in the entity.
                        if next_ch != "#":
                            length += match.end()

            if length > 1:
                utf16_offset = _get_utf16_length(text[:start_position])
                utf16_length = _get_utf16_length(text[start_position:start_position+length])
                entities.append(MessageEntity(MessageEntityType.HASHTAG,
                                              offset=utf16_offset,
                                              length=utf16_length))

        return tuple(entities)

    @staticmethod
    def parse_cashtags(text: str) -> tuple[MessageEntity, ...]:
        """
        Extract :obj:`~telegram.MessageEntity` representing
        cashtags (``$ABC``) from the given ``text``.

        Examples:
            An input string: ``$ABC``

            Result:

            .. code:: python

                (MessageEntity(length=4, offset=0, type=<MessageEntityType.CASHTAG>), )

        Args:
            text (str): A message that must be parsed.

        Returns:
            tuple[~telegram.MessageEntity]: Tuple of :obj:`~telegram.MessageEntity` with
            type :obj:`~telegram.constants.MessageEntityType.CASHTAG`.
            The tuple might be empty if no entities were found.
        """
        entities = list()
        # A cashtag can contain from 1 to 8 capital letter (the only exception is '1INCH'),
        # with optional @mention (3 to 32 characters).
        pattern = re.compile(r'\$(1INCH|[A-Z]+)(?:@([a-zA-Z0-9_]{3,}))?')

        matches = pattern.finditer(text)

        for match in matches:
            # If the input string is "$ABC@mention", then
            # group 0 is '$ABC@mention'
            # group 1 is 'ABC'
            # group 2 is 'mention' (optional)
            cashtag = match.group(1)
            mention = match.group(2)

            # The character right before the cashtag.
            prev_ch = get_item(text, match.start()-1, "", allow_negative_indexing=False)
            # The character right after the cashtag (including an optional @mention).
            next_ch = get_item(text, match.end(), "", allow_negative_indexing=False)
            if len(cashtag) > 8:
                continue
            elif _is_hashtag_letter(prev_ch) or prev_ch == "$":
                continue
            elif not mention and _is_hashtag_letter(next_ch):
                continue
            # If there is '$' right after the cashtag, then the cashtag
            # must be ignored.
            elif get_item(text, match.start() + len(cashtag) + 1, "") == "$":
                continue

            # The length including mention and '$@' symbols.
            full_length = match.end() - match.start()
            # The mention must be ignored if it is too long
            # or there is '$' symbol right after the mention
            if mention and (len(mention) > 32 or next_ch == "$"):
                full_length = len(cashtag) + 1

            entities.append(MessageEntity(MessageEntityType.CASHTAG,
                                          offset=_get_utf16_length(text[:match.start()]),
                                          length=full_length))

        return tuple(entities)

    @staticmethod
    def parse_urls_and_emails(text: str) -> tuple[MessageEntity, ...]:
        """
        Extract :obj:`~telegram.MessageEntity` representing
        URLs (``https://example.com``) from the given ``text``.

        Examples:
            An input string: ``https://example.com``

            Result:

            .. code:: python

                (MessageEntity(length=19, offset=0, type=MessageEntityType.URL),)

        Args:
            text (str): A message that must be parsed.

        Returns:
            tuple[~telegram.MessageEntity]: Tuple of :obj:`~telegram.MessageEntity` with
            type :obj:`~telegram.constants.MessageEntityType.URL`.
            The tuple might be empty if no entities were found.
        """
        # Allowed characters in the username and in the password in the basic auth.
        user_pass_chars = "a-z0-9._―‑!%-"

        host_domain_symbols = "a-z0-9\u00a1-\uffff―_‑-"
        # This pattern is based on this one https://gist.github.com/dperini/729294
        pattern = re.compile(
            # Optional protocol.
            r"(?:[a-z]+://)?"
            # 'user:pass' basic auth (optional)
            fr"(?:[:{user_pass_chars}]+(?::[{user_pass_chars}]+)?@)?"
            r"(?:"
                # IP address
                r"(?:(?:\d{1,3})\.){3}(?:\d{1,3})\b"
            r"|"
                # host & domain names
                r"(?:"
                    r"(?:"
                        rf"[{host_domain_symbols}]"
                        rf"[{host_domain_symbols}]{{0,62}}"
                    r")?"
                    rf"[{host_domain_symbols}]\."
                r")+"
                # TLD identifier name
                r"(?:[a-z0-9\u00a1-\uffff`‑―-]{2,})"
            r")"
            # port number (optional)
            r"(?P<port>:[0-9]+)?"
            # resource path (optional)
            r"(?P<path>[/?#]\S*)?", flags=re.IGNORECASE)

        def is_url_path_symbol(ch):
            """
            Check if the given symbol is a valid symbol for the path.
            """
            if ch in "\n<>\"«»":
                return False

            int_ch = ord(ch)
            if 0x206f >= int_ch >= 0x2000:  # General Punctuation.
                # Zero Width Non-Joiner/Joiner and various dashes
                return int_ch == 0x200c or int_ch == 0x200d or (0x2015 >= int_ch >= 0x2010)

            # The char is not a Separator.
            return not unicodedata.category(ch).startswith("Z")

        entities = list()
        matches = EntityParser._extract_entities(text, pattern)
        for match in matches:
            entity_length = match.utf16_length
            url = text[match.start:match.end]
            protocol = urlparse(url).scheme if "://" in url else None
            prev_ch: str = get_item(text, match.start - 1, "", allow_negative_indexing=False)

            # Skip if there is a dot or a latin letter right before the url or ...
            if (prev_ch and prev_ch in string.ascii_letters + "." or
                    # ... there is '@' symbol without user:pass or ...
                    "://@" in url or
                    # ... there is no protocol, but '://' at the beginning or the URL startswith '@'.
                    url.startswith("@") or url.startswith("://")):
                continue
            # if there is a dot(s) followed by a non-whitespace symbol right after the
            # TLD, then ignore such an URL.
            elif re.search(r"^\.+[^.\s]", text[match.end:]):
                continue
            elif protocol and protocol.lower() not in ("http", "https", "ftp", "tonsite"):
                continue

            path = match.group("path")

            # Checking for invalid symbols in the path.
            valid_symbols_in_path_counter = 1  # Skip the leading slash in the path.
            while (path and
                   valid_symbols_in_path_counter < len(path) and
                   is_url_path_symbol(path[valid_symbols_in_path_counter])):
                valid_symbols_in_path_counter+=1

            if path and valid_symbols_in_path_counter != len(path):
                invalid_symbols_counter = len(path) - valid_symbols_in_path_counter
                url = url[:len(url) - invalid_symbols_counter]
                entity_length -= _get_utf16_length(path[valid_symbols_in_path_counter:])
                path = path[:valid_symbols_in_path_counter]

            fixed_url = _fix_url(url)
            if not fixed_url:
                continue
            elif (url_length_diff := len(url) - len(fixed_url)) > 0:
                entity_length -= _get_utf16_length(url[-url_length_diff:])

            # The 'raw_port' will contain the colon symbol.
            # E.g., ':8080'.
            if raw_port := match.group("port"):
                # If the port is bigger than 65535, than ignore everything
                # in the url after the tld.
                port = int(raw_port[1:])
                if port == 0 or port > 65535:
                    entity_length -= len(raw_port + (path or ""))

            # Ignore trailing '#' symbol if there are no preceding '#', '?' or '/' symbols.
            if re.search(r"(?<![#?/])#$", fixed_url):
                entity_length -= 1

            if not path and fixed_url.endswith("…"):
                entity_length -= 1

            entity_type = MessageEntityType.URL
            offset = match.utf16_offset
            entity_text = text[match.start:match.start + entity_length]

            if _is_email_address(entity_text):
                entity_type = MessageEntityType.EMAIL
                if entity_text.startswith(":"):
                    offset += 1
                    entity_length -= 1
                elif entity_text.startswith("mailto:"):
                    offset += 7
                    entity_length -= 7

            entities.append(MessageEntity(entity_type, offset=offset, length=entity_length))

        return tuple(entities)

    @staticmethod
    def __parse_text(ptype, message, invalids, tags, text_links):
        entities = []
        mentions = re.compile(r'@[a-zA-Z0-9]{1,}\b')
        hashtags = re.compile(r'#[a-zA-Z0-9]{1,}\b')
        botcommands = re.compile(r'(?<!\/|\w)\/[a-zA-Z0-0_\-]{1,}\b')
        urls = re.compile(
            r'(([hHtTpP]{4}[sS]?|[fFtTpP]{3})://)?([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'
        )
        inv = invalids.search(message)
        if inv:
            raise BadMarkupException(
                "nested {} is not supported. your text: {}".format(
                    ptype, inv.groups()[0]))
        while tags.search(message):
            tag = tags.search(message)
            text = tag.groups()[2]
            start = tag.start()
            if tag.groups()[1] in ["b", "*"]:
                parse_type = "bold"
            elif tag.groups()[1] in ["i", "_"]:
                parse_type = "italic"
            elif tag.groups()[1] in ["code", "`"]:
                parse_type = "code"
            elif tag.groups()[1] in ["pre", "```"]:
                parse_type = "pre"
            entities.append(MessageEntity(parse_type, start, len(text)))
            message = tags.sub(r'\3', message, count=1)
        while text_links.search(message):
            link = text_links.search(message)
            url = link.group('url')
            text = link.group('text')
            start = link.start()
            length = len(text)
            for x, ent in enumerate(entities):
                if ent.offset > start:
                    # The previous solution subtracted link.end()-start-length
                    # from entities[x].offset. That's why the -1 multiplication.
                    shift_to = (link.end() - start - length) * -1
                    entities[x] = MessageEntity.shift_entities(shift_to, [entities[x]])[0]
            entities.append(MessageEntity('text_link', start, length, url=url))
            message = text_links.sub(r'\g<text>', message, count=1)
        for mention in mentions.finditer(message):
            entities.append(
                MessageEntity('mention',
                              mention.start(), mention.end() - mention.start(
                    )))
        for hashtag in hashtags.finditer(message):
            entities.append(
                MessageEntity('hashtag',
                              hashtag.start(), hashtag.end() - hashtag.start(
                    )))
        for botcommand in botcommands.finditer(message):
            entities.append(
                MessageEntity('bot_command',
                              botcommand.start(),
                              botcommand.end() - botcommand.start()))
        for url in urls.finditer(message):
            entities.append(
                MessageEntity('url', url.start(), url.end() - url.start()))

        return message, entities
