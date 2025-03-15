# ruff: noqa: PT009
import re
import unittest
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.constants import ParseMode
from telegram.ext import InlineQueryHandler, Updater

from ptbtest import InlineQueryGenerator, Mockbot

"""
This is an example to show how the ptbtest suite can be used.
This example follows the timerbot example at:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinebot.py
We will skip the start and help callbacks and focus on the inline query.

"""


class TestInlineBot(unittest.TestCase):
    def setUp(self):
        # For use within the tests we nee some stuff. Starting with a Mockbot
        self.bot = Mockbot()
        # And an InlineQueryGenerator and updater (for use with the bot.)
        self.iqg = InlineQueryGenerator(self.bot)
        self.updater = Updater(bot=self.bot)

    def test_inline_bot(self):
        # create some handlers and add them
        def escape_markdown(text):
            """Helper function to escape telegram markup symbols"""
            escape_chars = r"\*_`\["
            return re.sub(r"([%s])" % escape_chars, r"\\\1", text)  # noqa: UP031

        def inlinequery(update):
            query = update.inline_query.query
            results = []

            results.append(
                InlineQueryResultArticle(
                    id=uuid4(), title="Caps", input_message_content=InputTextMessageContent(query.upper())
                )
            )
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="Bold",
                    input_message_content=InputTextMessageContent(
                        f"*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN
                    ),
                )
            )
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title="Italic",
                    input_message_content=InputTextMessageContent(
                        f"_{escape_markdown(query)}_", parse_mode=ParseMode.MARKDOWN
                    ),
                )
            )
            update.inline_query.answer(results)

        dp = self.updater.dispatcher
        dp.add_handler(InlineQueryHandler(inlinequery))
        self.updater.start_polling()

        # Now test the handler
        u1 = self.iqg.get_inline_query(query="test data")
        self.bot.insert_update(u1)

        data = self.bot.sent_messages[-1]
        self.assertEqual(len(data["results"]), 3)
        results = data["results"]
        self.assertEqual(results[0]["title"], "Caps")
        self.assertEqual(results[0]["input_message_content"]["message_text"], "TEST DATA")
        self.assertEqual(results[1]["title"], "Bold")
        self.assertEqual(results[1]["input_message_content"]["message_text"], "*test data*")
        self.assertEqual(results[2]["title"], "Italic")
        self.assertEqual(results[2]["input_message_content"]["message_text"], "_test data_")

        self.updater.stop()


if __name__ == "__main__":
    unittest.main()
