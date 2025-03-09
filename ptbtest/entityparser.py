#!/usr/bin/env python
# pylint: disable=E0611,E0213,E1102,C0103,E1101,W0613,R0913,R0904
#
# A library that provides a testing suite fot python-telegram-bot
# wich can be found on https://github.com/python-telegram-bot/python-telegram-bot
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
"""This module provides a helperclass to transform marked_up messages to plaintext with entities"""
import re

from ptbtest.errors import BadMarkupException
from telegram import MessageEntity


class EntityParser():
    """
    Placeholder class for the static parser methods
    """

    def __init__(self):
        pass

    @staticmethod
    def parse_markdown(message):
        """

        Args:
            message (str): Message with Markdown text to be transformed

        Returns:
            (message(str), entities(list(telegram.MessageEntity))): The entities found in the message and
            the message after parsing.
        """
        invalids = re.compile(
            r'''(\*_|\*```|\*`|\*\[.*?\]\(.*?\)|_\*|_```|_`|_\[.*?\]\(.*?\)|```\*|```_|
                                  ```\[.*?\]\(.*?\)|`\*|`_|`\[.*?\]\(.*?\)|\[.*?\]\(.*?\)\*|
                                  \[.*?\]\(.*?\)_|\[.*?\]\(.*?\)```|\[.*?\]\(.*?\)`)'''
        )
        tags = re.compile(r'(([`]{3}|\*|_|`)(.*?)(\2))')
        text_links = re.compile(r'(\[(?P<text>.*?)\]\((?P<url>.*?)\))')

        return EntityParser.__parse_text("Markdown", message, invalids, tags,
                                         text_links)

    @staticmethod
    def parse_html(message):
        """

        Args:
            message (str): Message with HTML text to be transformed

        Returns:
            (message(str), entities(list(telegram.MessageEntity))): The entities found in the message and
            the message after parsing.
        """
        invalids = re.compile(r'''(<b><i>|<b><pre>|<b><code>|<b>(<a.*?>)|
                                   <i><b>|<i><pre>|<i><code>|<i>(<a.*?>)|
                                   <pre><b>|<pre><i>|<pre><code>|<pre>(<a.*?>)|
                                   <code><b>|<code><i>|<code><pre>|<code>(<a.*?>)|
                                   (<a.*>)?<b>|(<a.*?>)<i>|(<a.*?>)<pre>|(<a.*?>)<code>)'''
                              )
        tags = re.compile(r'(<(b|i|pre|code)>(.*?)<\/\2>)')
        text_links = re.compile(
            r'<a href=[\'\"](?P<url>.*?)[\'\"]>(?P<text>.*?)<\/a>')

        return EntityParser.__parse_text("HTML", message, invalids, tags,
                                         text_links)

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
                f"nested {ptype} is not supported. your text: {inv.groups()[0]}"
            )
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
                    entities[x].offset -= link.end() - start - length
            entities.append(MessageEntity('text_link', start, length, url=url))
            message = text_links.sub(r'\g<text>', message, count=1)
        for mention in mentions.finditer(message):
            entities.append(
                MessageEntity('mention', mention.start(),
                              mention.end() - mention.start()))
        for hashtag in hashtags.finditer(message):
            entities.append(
                MessageEntity('hashtag', hashtag.start(),
                              hashtag.end() - hashtag.start()))
        for botcommand in botcommands.finditer(message):
            entities.append(
                MessageEntity('bot_command', botcommand.start(),
                              botcommand.end() - botcommand.start()))
        for url in urls.finditer(message):
            entities.append(
                MessageEntity('url', url.start(),
                              url.end() - url.start()))
        return message, entities
