import os

from excel_tables.excel_table import ExcelTable


class DownloadsTable(ExcelTable):
    COLUMNS = ['id',
               'first_name',
               'last_name',
               'username',
               'is_bot',
               'download_date',
               'filename']

    DIR_NAME = 'DownloadsTable' + os.sep

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key in self.COLUMNS:
            setattr(self, key, [])

    def insert_data_into_table(self, data):
        self.get('id').append(data['id'])
        self.get('first_name').append(data['first_name'])
        self.get('last_name').append(data['last_name'])
        self.get('username').append(data['username'])
        self.get('is_bot').append(data['is_bot'])
        self.get('download_date').append(data['download_date'])
        self.get('filename').append(data['filename'])
