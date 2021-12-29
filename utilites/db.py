import psycopg2
from psycopg2 import Error
import os
import unittest
from datetime import datetime


class PostgreSQL():

    def __init__(self):
        self.dbname = os.environ.get('PARSER_DB_NAME', 'test')
        self.user = os.environ.get('PARSER_DB_USER', 'user')
        self.password = os.environ.get('PARSER_DB_PASS', 'pass')
        self.host = os.environ.get('PARSER_DB_HOST', 'localhost')
        self.port = os.environ.get('PARSER_DB_PORT', '5432')

        self.conn = psycopg2.connect(dbname=self.dbname,
                                     user=self.user,
                                     password=self.password,
                                     host=self.host,
                                     port=self.port)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def status(self):
        self.cur.execute(r"SELECT url FROM xgb_x_zalog8.flat_pagination limit 1")
        self.conn.commit
        return self.conn.status

    def insert_item(self, table_name, item):
        columns_string = ', '.join(item.keys())
        placeholders = ', '.join(['%s'] * len(item))
        sql = """INSERT INTO %s (%s)
                 VALUES (%s)""" % (table_name, columns_string, placeholders)
        self.cur.execute(sql, list(item.values()))
        self.conn.commit()

    def count(self, table, col, value):
        sql = """select count(*) from %s where "%s" = '%s';""" % (table, col, value)
        self.cur.execute(sql)
        return self.cur.fetchone()[0]

    def get_id_from_flat_parser(self, col, value):
        sql = """select id_rec from flat_parser where "%s" = '%s' limit 1;""" % (col, value)
        self.cur.execute(sql)
        res = self.cur.fetchone()
        return res[0] if isinstance(res, tuple) else None

    def update_item(self, table_name, item, col, value):
        values = ' ,'.join([f'{key} = \'{value}\'' for key, value in item.items()])
        sql = """UPDATE %s SET %s WHERE %s = '%s'""" % (table_name, values, col, value)
        self.cur.execute(sql)
        self.conn.commit()

    def delete_from_table(self, table_name, col, value):
        """ delete from table where col equal value"""
        query = """DELETE FROM %s WHERE "%s" = '%s' """ % (table_name, col, value)
        self.cur.execute(query)
        self.conn.commit()

    def close(self):
        self.conn.close()
        self.cur.close()


# class TestParserDB(unittest.TestCase):
#
#     def setUp(self):
#         self.db = PostgreSQL()
#         self.date = datetime.now()
#
#     def test_status(self):
#         self.assertEqual(self.db.status(), 1)
#
#     def test_01_insert_new_items(self):
#         test_item_pagination = {'source': 'test',
#                                 'url': 'test',
#                                 'date_last_view': self.date,
#                                 'need_parse': True,
#                                 'info': 'test',
#                                 'date_change_sign': self.date,
#                                 'date_added': self.date
#                                 }
#         test_item_parser = {'source': 'test',
#                             'url': 'test_url',
#                             'contract_type': 'test'
#                             }
#         self.assertEqual(self.db.insert_item('flat_pagination', test_item_pagination), True)
#         self.assertEqual(self.db.insert_item('flat_parser', test_item_parser), True)
#
#     def test_02_update_item(self):
#         item = {'source': 'test_2'}
#         self.assertTrue(self.db.update_item('flat_parser', item, 'url', 'test_url'))
#
#     def test_04_delete_item(self):
#         self.assertTrue(self.db.delete_from_table('flat_pagination', 'source', 'test'))
#         self.assertTrue(self.db.delete_from_table('flat_parser', 'source', 'test_2'))
#
#     def tearDown(self):
#         self.db.close()
#
#
# if __name__ == '__main__':
#     unittest.main()
