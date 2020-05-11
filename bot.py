import logging
from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler)
from bot.common import GET_DOCUMENT, START, RESET, UPLOAD, GET_CHAT_ID, TOKEN, PORT, HEROKU_APP_NAME
from bot.handlers import start, get_chat_id, upload, get_document, call_handler, reset


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def error(bot, update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


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
