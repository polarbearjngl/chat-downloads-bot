from telegram import InlineKeyboardButton

from bot.common import DOWNLOAD_FILE, ABORT_PARSING, PROCEED_PARSING


class Menu(object):
    """Class for creating inline menu for telegram"""

    def __init__(self, buttons, col_num):
        self.buttons = buttons
        self.col_num = col_num

    def build_menu(self, header_buttons=None, footer_buttons=None):
        """Generating array that used in inline menu creating"""
        menu = [self.buttons[i:i + self.col_num] for i in range(0, len(self.buttons), self.col_num)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return menu


class MenuList(object):
    """List of menu for this bot"""

    DOWNLOAD_BTN = [InlineKeyboardButton(text=u"Скачать файл", callback_data=DOWNLOAD_FILE)]
    PARSING_BTN = [InlineKeyboardButton(text=u"Прервать", callback_data=ABORT_PARSING),
                   InlineKeyboardButton(text=u"Продолжить", callback_data=PROCEED_PARSING)]
