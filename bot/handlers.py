import os
from datetime import datetime
from functools import wraps
from pathlib import Path
from bot.common import GET_DOCUMENT, DOWNLOAD_FILE, TARGET_CHAT, DATABASE_URL
from excel_tables.downloads_table import DownloadsTable
from menu import Menu, MenuList
from telegram import InlineKeyboardMarkup, Chat
import re
from postgress.downloads_db import DownloadsDb


def restricted(func):
    """check that user is in list of admins for bot before run command."""
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in map(int, os.environ.get("LIST_OF_ADMINS").split(',')):
            update.message.reply_text(text='У тебя нет прав для этого действия.')
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


def check_chat_type(func):
    """Check is chat PRIVATE."""
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        chat_type = update.effective_chat.type
        if chat_type == Chat.PRIVATE:
            return func(bot, update, *args, **kwargs)
        update.message.reply_text(text='Можно выполнить только в личном чате с ботом.')
    return wrapped


@check_chat_type
def start(bot, update):
    bot.send_message(chat_id=update.effective_chat.id, text='Приветствую тебя, ' + update.effective_user.username +
                                                            '. Напиши команду /upload чтобы начать загрузку.')


@check_chat_type
@restricted
def reset(bot, update):
    bot.send_message(chat_id=update.effective_chat.id, text='Что-то пошло не так, ' + update.effective_user.username)
    start(bot=bot, update=update)


@restricted
def get_chat_id(bot, update):
    bot.send_message(chat_id=update.effective_chat.id, text='This chat_id is ' + str(update.effective_chat.id))


@check_chat_type
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
        text='file: <b>{}</b>\nsize: {}\nauthor: {}\nID{}'.format(
            msg.to_dict()['document']['file_name'],
            msg.to_dict()['document']['file_size'],
            msg.to_dict()['from']['username'],
            msg.to_dict()['document']['file_id'][::-1]),
        parse_mode='HTML',
        reply_markup=reply_markup)

    start(bot=bot, update=update)


def call_handler(bot, update):
    query = update.callback_query
    qdata = query.data
    from_user = query.from_user

    if qdata == DOWNLOAD_FILE:
        from_user.send_document(document=re.findall(r'ID(.*)', query.message.text)[0][::-1])

        downloads_db = DownloadsDb(connection_string=DATABASE_URL)
        downloads_db.insert(first_name=from_user.first_name,
                            last_name=from_user.last_name,
                            username=from_user.username,
                            is_bot=from_user.is_bot,
                            download_date=datetime.now(),
                            filename=re.findall(r'file: (.*\n)', query.message.text)[0])

        count_rows = downloads_db.count_rows()
        if count_rows > int(os.environ.get("MAX_DB_COUNT", "9000")):
            excel = DownloadsTable()
            all_records = downloads_db.load_all()
            for record in all_records:
                excel.insert_data_into_table(data=record)

            excel.to_excel(str(Path(__file__).parent.parent.absolute()) + os.sep + 'reports' + os.sep,
                           filename='report ' + str(datetime.now().strftime('%d-%m %H-%M-%S')))

            for admin_id in map(int, os.environ.get("LIST_OF_ADMINS").split(',')):
                try:
                    bot.send_message(
                        chat_id=admin_id,
                        text='Количество записей в БД={count_rows}. Текущее состояние БД сохранено в отчет, '
                             'который отправлен всем администраторам. БД очищена и будет заполняться заново'.format(
                                count_rows=count_rows))
                    bot.send_document(chat_id=admin_id, document=open(excel.filename, 'rb'))
                except:
                    pass
                finally:
                    os.remove(excel.filename)
        downloads_db.close()


@check_chat_type
@restricted
def get_stats(bot, update):
    user = update.effective_user
    excel = DownloadsTable()

    downloads_db = DownloadsDb(connection_string=DATABASE_URL)
    all_records = downloads_db.load_all()

    for record in all_records:
        excel.insert_data_into_table(data=record)

    excel.to_excel(str(Path(__file__).parent.parent.absolute()) + os.sep + 'reports' + os.sep,
                   filename='report ' + str(datetime.now().strftime('%d-%m %H-%M-%S')))
    user.send_document(document=open(excel.filename, 'rb'))
    os.remove(excel.filename)
    downloads_db.close()
