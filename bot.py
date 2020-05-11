import logging
import os
from functools import wraps
from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler)

from common import GET_DOCUMENT, START, RESET, UPLOAD, GET_CHAT_ID
from handlers import start, get_chat_id, upload, get_document, call_handler, reset

TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
LIST_OF_ADMINS = map(int, os.environ.get("LIST_OF_ADMINS").split(','))
TARGET_CHAT = int(os.environ.get("TARGET_CHATS"))
DATABASE_URL = os.getenv("DATABASE_URL")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def error(bot, update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def restricted(func):
    """check that user is in list of admins for bot before run command."""
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            update.message.reply_text(text='У тебя нет прав для этого действия.')
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def run(updater_instance):
    updater_instance.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater_instance.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    start_handler = CommandHandler(START, start)
    dp.add_handler(start_handler)

    chat_id_handler = CommandHandler(GET_CHAT_ID, get_chat_id)
    dp.add_handler(chat_id_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(UPLOAD, upload)],

        states={
            GET_DOCUMENT: [MessageHandler(filters=Filters.document, callback=get_document)],
        },

        fallbacks=[CommandHandler(RESET, reset)]
    )
    dp.add_handler(conv_handler)

    updater.dispatcher.add_handler(CallbackQueryHandler(callback=call_handler))

    # log all errors
    dp.add_error_handler(error)
    run(updater)
