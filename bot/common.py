import math
import os

TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
LIST_OF_ADMINS = map(int, os.environ.get("LIST_OF_ADMINS").split(','))
TARGET_CHAT = int(os.environ.get("TARGET_CHATS"))
DATABASE_URL = os.getenv("DATABASE_URL")
COUNTER_DAYS_INTERVAL = int(os.getenv("COUNTER_DAYS_INTERVAL"))
MAX_DOWNLOADS_COUNT = int(os.getenv("MAX_DOWNLOADS_COUNT"))
TARGET_CHAT_FOR_EXPORT = int(os.environ.get("TARGET_CHAT_FOR_EXPORT"))

GET_DOCUMENT = range(1)
START = 'start'
RESET = 'reset'
UPLOAD = 'upload'
GET_CHAT_ID = 'get_chat_id'
DOWNLOAD_FILE = 'download_file'
GET_STATS = 'get_stats'
START_MSGS_IMPORT = 'start_msgs_import'
PARSE_MSGS_HISTORY = 'parse_msgs_history'
ABORT_PARSING = "abort_parsing"
PROCEED_PARSING = "proceed_parsing"


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def build_download_message(file_name, file_size, file_id):
    text = 'file: <b>{}</b>\nsize: {}\nID{}'.format(
        file_name,
        file_size,
        file_id)
    return text
