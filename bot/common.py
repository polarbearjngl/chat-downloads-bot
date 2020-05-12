import os

TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", "8443"))
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
LIST_OF_ADMINS = map(int, os.environ.get("LIST_OF_ADMINS").split(','))
TARGET_CHAT = int(os.environ.get("TARGET_CHATS"))
DATABASE_URL = os.getenv("DATABASE_URL")

GET_DOCUMENT = range(1)
START = 'start'
RESET = 'reset'
UPLOAD = 'upload'
GET_CHAT_ID = 'get_chat_id'
DOWNLOAD_FILE = 'download_file'
GET_STATS = 'get_stats'
