import os

from pandas import DataFrame, ExcelWriter
from openpyxl import load_workbook


class ExcelTable(dict):
    """Base class for excel table."""

    # column names for table
    COLUMNS = []
    # dir name for saving file
    DIR_NAME = ''
    EXTENSION = '.xlsx'

    def get(self, key):
        return getattr(self, key, [])

    def to_excel(self, directory, filename, sheet_name='sheet1', startrow=0, startcol=0):
        """Save data to excel."""
        directory = directory + self.DIR_NAME
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = directory + filename + self.EXTENSION

        writer = None
        try:
            book = load_workbook(filename)
            writer = ExcelWriter(filename, engine='openpyxl')
            writer.book = book
        except FileNotFoundError:
            pass

        df = DataFrame(data={k: v for k, v in self.__dict__.items() if k in self.COLUMNS})
        df.to_excel(excel_writer=writer or filename,
                    sheet_name=sheet_name,
                    startrow=startrow, startcol=startcol,
                    index=False)
        if writer:
            writer.save()
            writer.close()

        self.filename = filename
