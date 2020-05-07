import logging
import os
from functools import wraps

from telegram import InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler)

from menu import Menu, MenuList

TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
LIST_OF_ADMINS = map(int, os.environ.get("LIST_OF_ADMINS").split(','))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


CHECK_ACCESS, GET_DOCUMENT = range(2)


def error(bot, update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            update.message.reply_text(text='You unauthorized for this action. Stop there your criminal scum.')
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def start(bot, update):
    bot.send_message(chat_id=update.effective_chat.id, text='Hello there, ' + update.effective_user.username +
                                                            '. Call /upload command to start upload.')


def upload(bot, update):
    update.message.reply_text(text='Enter password for proceed upload process')
    return CHECK_ACCESS


@restricted
def check_access(bot, update):
    update.message.reply_text(text='You have access for this action. Upload document to bot')
    return GET_DOCUMENT


def get_document(bot, update):
    msg = update.effective_message

    start_menu = Menu(buttons=MenuList.DOWNLOAD_BTN, col_num=1).build_menu()
    reply_markup = InlineKeyboardMarkup(start_menu)
    update.message.reply_html(text='Download file {}, uploaded by {}, ID={}'.format(
        msg.to_dict()['document']['file_name'],
        msg.to_dict()['from']['username'], msg.to_dict()['document']['file_id']),
        reply_markup=reply_markup)

    start(bot=bot, update=update)


def call_handler(bot, update, user_data):
    query = update.callback_query
    query_id = update.callback_query.id
    qdata = query.data
    message_id = query.message.message_id
    chat_id = query.message.chat_id
    from_user = query.from_user.to_json()
    user_data['from_user'], user_data['query'] = from_user, query.to_json()

    if qdata == 'download_file':
        bot.send_message(chat_id=update.effective_chat.id,
                         text=user_data)

        # bot.send_document(document=)


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
            CHECK_ACCESS: [MessageHandler(filters=Filters.text, callback=check_access)],

            GET_DOCUMENT: [MessageHandler(filters=Filters.document, callback=get_document)],
        },

        fallbacks=[CommandHandler('reset', start)]
    )
    dp.add_handler(conv_handler)

    updater.dispatcher.add_handler(CallbackQueryHandler(callback=call_handler, pass_user_data=True))

    # log all errors
    dp.add_error_handler(error)
    run(updater)
