from __future__ import absolute_import
import unittest

from ptbtest import CallbackQueryGenerator
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import Updater

from ptbtest import ChatGenerator
from ptbtest import MessageGenerator
from ptbtest import Mockbot

"""
This is an example to show how the ptbtest suite can be used.
This example follows the timerbot example at:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinekeyboard.py
We will skip the start and help callbacks and focus on the callback query.

"""
class TestInlineKeyboard(unittest.TestCase):
    def setUp(self):
        # For use within the tests we need some stuff. Starting with a Mockbot
        self.bot = Mockbot()
        # Some generators for users and chats
        self.cg = ChatGenerator()
        # And a Messagegenerator, CallbackQueryGenerator and updater (for use with the bot.)
        self.mg = MessageGenerator(self.bot)
        self.cqg = CallbackQueryGenerator(self.bot)
        self.updater = Updater(bot=self.bot)

    def test_callback(self):
        # first insert the callbackhandler, register it and start polling
        def button(bot, update):
            query = update.callback_query

            bot.editMessageText(text="Selected option: %s" % query.data,
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
        dp = self.updater.dispatcher
        dp.add_handler(CallbackQueryHandler(button))
        self.updater.start_polling()

        # the start callback in this example generates a message that will be edited, so let's mimick that message
        # for future reference
        keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                     InlineKeyboardButton("Option 2", callback_data='2')],
                    [InlineKeyboardButton("Option 3", callback_data='3')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        chat = self.cg.get_chat()
        start_message = self.bot.sendMessage(chat_id=chat.id, text='Please choose:', reply_markup=reply_markup)

        # now let's create some callback query's to send
        u1 = self.cqg.get_callback_query(message=start_message, data="1")
        u2 = self.cqg.get_callback_query(message=start_message, data="2")
        u3 = self.cqg.get_callback_query(message=start_message, data="3")

        # And test them one by one
        self.bot.insertUpdate(u1)
        data = self.bot.sent_messages[-1]
        self.assertEqual(data['text'], "Selected option: 1")
        self.assertEqual(data['chat_id'], start_message.chat.id)
        self.assertEqual(data['message_id'], start_message.message_id)
        self.bot.insertUpdate(u2)
        data = self.bot.sent_messages[-1]
        self.assertEqual(data['text'], "Selected option: 2")
        self.assertEqual(data['chat_id'], start_message.chat.id)
        self.assertEqual(data['message_id'], start_message.message_id)
        self.bot.insertUpdate(u3)
        data = self.bot.sent_messages[-1]
        self.assertEqual(data['text'], "Selected option: 3")
        self.assertEqual(data['chat_id'], start_message.chat.id)
        self.assertEqual(data['message_id'], start_message.message_id)

        # stop polling
        self.updater.stop()


if __name__ == '__main__':
    unittest.main()
