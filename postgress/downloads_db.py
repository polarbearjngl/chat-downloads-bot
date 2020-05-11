from postgress.pg_client import PgClient


class DownloadsDb(PgClient):

    def __init__(self, connection_string):
        super().__init__(connection_string)

    def load_all(self):
        sql_load_all = """SELECT id,
                                 first_name,
                                 last_name,
                                 username,
                                 is_bot,
                                 download_date,
                                 filename
                          FROM   downloads"""
        return self.execute_sql_statement_mapped(sql=sql_load_all)

    def insert(self, first_name, last_name, username, is_bot, download_date, filename):
        sql_insert = """INSERT INTO downloads
                                    (id,
                                     first_name,
                                     last_name,
                                     username,
                                     is_bot,
                                     download_date,
                                     filename)
                        VALUES      (DEFAULT,
                                     :first_name,
                                     :last_name,
                                     :username,
                                     :is_bot,
                                     :download_date,
                                     :filename)"""
        self.execute_sql_statement_with_commit(sql=sql_insert,
                                               first_name=first_name,
                                               last_name=last_name,
                                               username=username,
                                               is_bot=is_bot,
                                               download_date=download_date,
                                               filename=filename)

    def count_rows(self):
        sql_count_rows = """select COUNT(*) from downloads"""
        return self.execute_sql_statement_mapped(sql=sql_count_rows)[0]['count']

    def truncate(self):
        sql_truncate = """truncate downloads"""
        self.execute_sql_statement_with_commit(sql=sql_truncate)
