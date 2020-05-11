import re
import psycopg2


class PgClient(object):

    def __init__(self, connection_string):
        self._connection = psycopg2.connect(dsn=connection_string)

    def execute_sql_statement_mapped(self, sql, **query_args):
        u"""Получение результата выполнения SQL запроса в виде словаря.

        Args:
            sql: выполняемый запрос.
            query_args: Словарь содержащий наименования аргументов и их значения для передачи в sql запрос.

        Returns:

        """
        cursor = self.connection.cursor()
        sql = self.format_sql_query(sql=sql, **query_args)
        cursor.execute(sql, query_args)
        results = cursor.fetchall()
        results_list = self.get_all_statements(results=results, cursor=cursor)
        cursor.close()
        return results_list

    @staticmethod
    def format_sql_query(sql, **kwargs):
        u"""Format sql query to psycopg2 format.

        Args:
            sql: sql query

        Returns: Formatted sql.

        """
        for key in kwargs.keys():
            sql = re.sub(pattern=r"(:{})".format(key), repl='%({arg})s'.format(arg=key), string=sql)
        return sql

    def get_all_statements(self, results, cursor):
        u"""Get all records from cursor.

        Args:
            results: Query result.
            cursor: Cursor object.

        Returns: list of dicts with query result.

        """
        results_list = []
        for result in results:
            dictionary = {}
            self.rec_to_dict(cursor.description, result, dictionary)
            results_list.append(dictionary)

        return results_list

    def execute_sql_statement_with_commit(self, sql, **query_args):
        """execute sql with commit.

        Args:
            sql: sql query.

        """
        cursor = self.connection.cursor()
        sql = self.format_sql_query(sql=sql, **query_args)
        cursor.execute(sql, query_args)
        self.connection.commit()

    @property
    def connection(self):
        """Get db connection."""
        return self._connection

    @staticmethod
    def rec_to_dict(description, values, dictionary):
        """DB record to dict."""
        for i in range(len(values)):
            key = description[i][0]
            if key not in dictionary.keys():
                dictionary[description[i][0]] = values[i]

        return dictionary

    def close(self):
        """Close connect to Postgres."""
        self.connection.close()
