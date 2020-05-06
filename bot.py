import logging
import os
from telegram.ext import (Updater, CommandHandler)

TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def error(bot, update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def start(bot, update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def run(updater_instance):
    updater_instance.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater_instance.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dp.add_handler(start_handler)

    # log all errors
    dp.add_error_handler(error)
    run(updater)
