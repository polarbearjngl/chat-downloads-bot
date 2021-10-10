import json
import os
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from bot.common import GET_DOCUMENT, DOWNLOAD_FILE, TARGET_CHAT, DATABASE_URL, convert_size, COUNTER_DAYS_INTERVAL, \
    MAX_DOWNLOADS_COUNT, PARSE_MSGS_HISTORY, build_download_message, TARGET_CHAT_FOR_EXPORT, ABORT_PARSING, \
    PROCEED_PARSING
from excel_tables.downloads_table import DownloadsTable
from menu import Menu, MenuList
from telegram import InlineKeyboardMarkup, Chat
import re

from postgress.counter_db import CounterDb
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


def check_downloads_counter(func):
    @wraps(func)
    def wrapped(bot, from_user, query, *args, **kwargs):
        if from_user.id in map(int, os.environ.get("LIST_OF_ADMINS").split(',')):
            return func(bot, from_user, query, *args, **kwargs)

        counter_db = CounterDb(connection_string=DATABASE_URL)
        current_counter = counter_db.get_counter(user_id=from_user.id)
        # bot.send_message(chat_id=from_user.id, text=f'{current_counter}')

        datetime_now = datetime.now().replace(microsecond=0, second=0)

        if not current_counter:
            # bot.send_message(chat_id=from_user.id,
            #                  text=f'create new rec')
            counter_db.insert(user_id=from_user.id,
                              username=from_user.username,
                              is_bot=from_user.is_bot,
                              counter_update_date=datetime_now,
                              next_counter_update_date=datetime_now + timedelta(minutes=COUNTER_DAYS_INTERVAL))
            return func(bot, from_user, query, *args, **kwargs)

        next_counter_update_date = current_counter[0]["next_counter_update_date"].replace(microsecond=0, second=0)
        count_num = current_counter[0]["count_num"]

        if datetime_now >= next_counter_update_date:
            # bot.send_message(chat_id=from_user.id,
            #                  text=f'{datetime_now} >= {next_counter_update_date}')
            counter_db.update(user_id=from_user.id,
                              counter_update_date=datetime_now,
                              next_counter_update_date=datetime_now + timedelta(minutes=COUNTER_DAYS_INTERVAL),
                              count=1)
            return func(bot, from_user, query, *args, **kwargs)

        if datetime_now < next_counter_update_date:
            # bot.send_message(chat_id=from_user.id,
            #                  text=f'{datetime_now} < {next_counter_update_date}')

            if count_num < MAX_DOWNLOADS_COUNT:
                # bot.send_message(chat_id=from_user.id,
                #                  text=f'{count_num} < {MAX_DOWNLOADS_COUNT}')
                counter_db.update(user_id=from_user.id,
                                  count=count_num + 1)
                return func(bot, from_user, query, *args, **kwargs)

            if count_num >= MAX_DOWNLOADS_COUNT:
                # bot.send_message(chat_id=from_user.id,
                #                  text=f'{count_num} >= {MAX_DOWNLOADS_COUNT}')
                bot.send_message(chat_id=from_user.id,
                                 text=f'Ты нажал(а) на кнопку "Скачать" <b>{count_num}</b> раз(а).\n'
                                      f'Дальнейшее скачивание ограничено!\n'
                                      f'Ограничение пропадет <b>{next_counter_update_date} GMT</b>.\n',
                                 parse_mode='HTML')
                return

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
    text = build_download_message(file_name=msg.to_dict()['document']['file_name'],
                                  file_size=convert_size(msg.to_dict()['document']['file_size']),
                                  file_id=msg.to_dict()['document']['file_id'][::-1])
    bot.send_message(chat_id=TARGET_CHAT,
                     text=text,
                     parse_mode='HTML',
                     reply_markup=reply_markup)

    start(bot=bot, update=update)


def call_handler(bot, update, user_data):
    query = update.callback_query
    qdata = query.data
    from_user = query.from_user

    if qdata == DOWNLOAD_FILE:
        send_document_to_user(bot, from_user, query)

    if qdata == ABORT_PARSING:
        abort_parsing(bot, from_user, query)

    if qdata == PROCEED_PARSING:
        proceed_parsing(bot, from_user, query, user_data)


@check_downloads_counter
def send_document_to_user(bot, from_user, query):
    from_user.send_document(document=re.findall(r'ID(.*)', query.message.text)[0][::-1])

    downloads_db = DownloadsDb(connection_string=DATABASE_URL)
    counter_db = CounterDb(connection_string=DATABASE_URL)
    downloads_db.insert(first_name=from_user.first_name,
                        last_name=from_user.last_name,
                        username=from_user.username,
                        is_bot=from_user.is_bot,
                        download_date=datetime.now(),
                        filename=re.findall(r'file: (.*\n)', query.message.text)[0])

    count_rows = downloads_db.count_rows() + counter_db.count_rows()
    if count_rows > int(os.environ.get("MAX_DB_COUNT", "9000")):
        excel = DownloadsTable()
        all_records = downloads_db.load_all()
        for record in all_records:
            excel.insert_data_into_table(data=record)

        excel.to_excel(str(Path(__file__).parent.parent.absolute()) + os.sep + 'reports' + os.sep,
                       filename='report ' + str(datetime.now().strftime('%d-%m %H-%M-%S')))

        try:
            for admin_id in map(int, os.environ.get("LIST_OF_ADMINS").split(',')):
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
            downloads_db.truncate()

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


# region IMPORT MSGS
@check_chat_type
@restricted
def start_msgs_import(bot, update):
    bot.send_message(chat_id=update.effective_chat.id,
                     text='Now will be started messages export. Upload JSON with history data')
    return PARSE_MSGS_HISTORY


def parse_msgs_history(bot, update, user_data):
    user = update.effective_user
    msg = update.effective_message

    file_obj = msg.document.get_file()
    filename = file_obj.download()
    file_data = Path(filename)
    with file_data.open() as f:
        dictionary = json.loads(f.read())
    file_data.unlink()

    user_data['dictionary'] = dictionary
    parse_menu = Menu(buttons=MenuList.PARSING_BTN, col_num=2).build_menu()
    reply_markup = InlineKeyboardMarkup(parse_menu)
    user.send_message(
        text=f"WARNING!!! DANGER ZONE!!!"
             f" {len(dictionary)} will be exported to target chat {TARGET_CHAT_FOR_EXPORT}",
        reply_markup=reply_markup)


def abort_parsing(bot, from_user, query):
    bot.delete_message(chat_id=from_user.id, message_id=query.message.message_id)
    bot.send_message(chat_id=from_user.id, text='Export was aborted')


def proceed_parsing(bot, from_user, query, user_data):
    bot.send_message(chat_id=from_user.id,
                     text=f'Here would be an export actions for {len(user_data["dictionary"])} msgs')

    for message in user_data["dictionary"][:5]:
        start_menu = Menu(buttons=MenuList.DOWNLOAD_BTN, col_num=1).build_menu()
        reply_markup = InlineKeyboardMarkup(start_menu)
        text = build_download_message(file_name=message["name"],
                                      file_size=message.get("size", "NaN"),
                                      file_id=message["id"])
        bot.send_message(chat_id=TARGET_CHAT_FOR_EXPORT,
                         text=text,
                         parse_mode='HTML',
                         reply_markup=reply_markup)

    bot.send_message(chat_id=from_user.id,
                     text=f'{len(user_data["dictionary"])} msgs exported')

    bot.delete_message(chat_id=from_user.id, message_id=query.message.message_id)

# endregion
