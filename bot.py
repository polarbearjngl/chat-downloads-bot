import logging
import os
from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler, Filters)

TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
MASTER_PSW = os.environ.get("MASTER_PSW")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


PASSWORD_CHECK, DOCUMENT = range(2)


def error(bot, update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(bot, update):
    bot.send_message(chat_id=update.effective_chat.id, text='Hello there, ' + update.effective_user.username +
                                                            '. Call /upload command to start upload.')


def upload(bot, update):
    update.message.reply_text(text='Enter password for proceed upload process')
    return PASSWORD_CHECK


def check_pass(bot, update):
    if MASTER_PSW == update.effective_message.text:
        return DOCUMENT
    else:
        return start(bot=bot, update=update)


def get_document(bot, update):
    msg = update.effective_message
    update.message.reply_text(text=msg.to_dict())


def run(updater_instance):
    updater_instance.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater_instance.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dp.add_handler(start_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('upload', upload)],

        states={
            PASSWORD_CHECK: [MessageHandler(filters=Filters.text, callback=check_pass)],

            DOCUMENT: [MessageHandler(filters=Filters.document, callback=get_document)],
        },

        fallbacks=[CommandHandler('reset', start)]
    )

    dp.add_handler(conv_handler)
    # log all errors
    dp.add_error_handler(error)
    run(updater)
