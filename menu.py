from telegram import InlineKeyboardButton


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

    DOWNLOAD_BTN = [InlineKeyboardButton(text=u"Download file", callback_data='download_file')]
