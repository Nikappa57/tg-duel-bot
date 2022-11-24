import os
import logging
from dotenv import load_dotenv

from inspect import getmembers, isfunction

from telegram.ext import Defaults, Updater, CommandHandler, MessageHandler, \
    Filters, CallbackQueryHandler, InlineQueryHandler
from telegram import ParseMode

from Bot import command
from Bot.dice import dice
from Bot.errors import unknown
from Bot.buttons import button
from Bot.inlinemode import inline_mode

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

if __name__ == "__main__":
    print("loading...")

    TOKEN = os.environ.get('TOKEN')

    defaults = Defaults(parse_mode=ParseMode.HTML)
    updater = Updater(token=TOKEN, defaults=defaults, use_context=True)
    dispatcher = updater.dispatcher

    # Commands #
    for name, handler in [o for o in getmembers(command) if isfunction(o[1])]:
        dispatcher.add_handler(CommandHandler(name, handler))

    # Buttons #
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Unknown Command #
    dispatcher.add_handler(
        MessageHandler(Filters.command & Filters.chat_type.private, unknown)
    )

    # Inline Mode #
    dispatcher.add_handler(InlineQueryHandler(inline_mode))

    #Dice
    dispatcher.add_handler(MessageHandler(Filters.dice, dice))


    updater.start_polling()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    print("Bot started")