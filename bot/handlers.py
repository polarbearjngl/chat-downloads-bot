from datetime import datetime
from functools import wraps

from bot.common import GET_DOCUMENT, DOWNLOAD_FILE, TARGET_CHAT, LIST_OF_ADMINS, DATABASE_URL
from menu import Menu, MenuList
from telegram import InlineKeyboardMarkup
import re
from postgress.downloads_db import DownloadsDb


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


def start(bot, update):
    bot.send_message(chat_id=update.effective_chat.id, text='Приветствую тебя, ' + update.effective_user.username +
                                                            '. Напиши команду /upload чтобы начать загрузку.')


def reset(bot, update):
    bot.send_message(chat_id=update.effective_chat.id, text='Что-то пошло не так, ' + update.effective_user.username)
    start(bot=bot, update=update)


@restricted
def get_chat_id(bot, update):
    bot.send_message(chat_id=update.effective_chat.id, text='This chat_id is ' + str(update.effective_chat.id))


@restricted
def upload(bot, update):
    update.message.reply_text(text='Теперь ты можешь загрузить файл в сообщения боту.')
    return GET_DOCUMENT


def get_document(bot, update):
    msg = update.effective_message

    start_menu = Menu(buttons=MenuList.DOWNLOAD_BTN, col_num=1).build_menu()
    reply_markup = InlineKeyboardMarkup(start_menu)
    bot.send_message(
        chat_id=TARGET_CHAT,
        text='Скачать файл: <b>{}</b>\nФайл загружен: {}\nID={}'.format(
            msg.to_dict()['document']['file_name'],
            msg.to_dict()['from']['username'],
            msg.to_dict()['document']['file_id']),
        parse_mode='HTML',
        reply_markup=reply_markup)

    start(bot=bot, update=update)


def call_handler(bot, update):
    query = update.callback_query
    query_id = update.callback_query.id
    qdata = query.data
    message_id = query.message.message_id
    chat_id = query.message.chat_id
    from_user = query.from_user

    if qdata == DOWNLOAD_FILE:
        from_user.send_document(document=re.findall(r'ID=(.*)', query.message.text)[0])
        downloads_db = DownloadsDb(connection_string=DATABASE_URL)
        downloads_db.insert(first_name=from_user.first_name,
                            last_name=from_user.last_name,
                            username=from_user.username,
                            is_bot=from_user.is_bot,
                            download_date=datetime.now(),
                            filename="test")
        downloads_db.close()

        from_user.send_message(text=query.message.to_json())
