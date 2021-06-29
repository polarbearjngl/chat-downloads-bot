from postgress.pg_client import PgClient


class CounterDb(PgClient):

    def __init__(self, connection_string):
        super().__init__(connection_string)

    def get_counter(self, user_id):
        sql_get_counter = """SELECT id,
                                    user_id,
                                    username,
                                    is_bot,
                                    counter_update_date,
                                    next_counter_update_date,
                                    count_num
                             FROM   counter
                             WHERE  user_id = :user_id"""
        return self.execute_sql_statement_mapped(sql=sql_get_counter,
                                                 user_id=user_id)

    def update(self, user_id, count, counter_update_date=None, next_counter_update_date=None):
        sql_insert = """UPDATE counter
                           SET counter_update_date = COALESCE(:counter_update_date, counter_update_date),
                               next_counter_update_date = COALESCE(:next_counter_update_date, next_counter_update_date),
                               count_num = :count
                         WHERE user_id = :user_id"""
        self.execute_sql_statement_with_commit(sql=sql_insert,
                                               user_id=user_id,
                                               counter_update_date=counter_update_date,
                                               next_counter_update_date=next_counter_update_date,
                                               count_num=count)

    def insert(self, user_id, username, is_bot, counter_update_date, next_counter_update_date):
        sql_insert = """INSERT INTO counter
                                    (id,
                                     user_id,
                                     username,
                                     is_bot,
                                     counter_update_date,
                                     next_counter_update_date,
                                     count_num)
                        VALUES      (DEFAULT,
                                     :user_id,
                                     :username,
                                     :is_bot,
                                     :counter_update_date,
                                     :next_counter_update_date,
                                     1)"""
        self.execute_sql_statement_with_commit(sql=sql_insert,
                                               user_id=user_id,
                                               username=username,
                                               is_bot=is_bot,
                                               counter_update_date=counter_update_date,
                                               next_counter_update_date=next_counter_update_date)

    def count_rows(self):
        sql_count_rows = """select COUNT(*) as count from counter"""
        return self.execute_sql_statement_mapped(sql=sql_count_rows)[0]['count']

    def truncate(self):
        sql_truncate = """truncate counter"""
        self.execute_sql_statement_with_commit(sql=sql_truncate)
