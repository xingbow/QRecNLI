# -*- coding: utf-8 -*-
import time
import json
import os
import sys

try:
    import globalVariable as GV
    import sqlParser as sp
except ImportError:
    import app.dataService.globalVariable as GV
    import app.dataService.sqlParser as sp

class DataService(object):
    def __init__(self):
        print("=== begin loading model ===")
        self.sql_parser = sp.SmBop()
        print("=== finish loading model ===")
        return

    def text2sql(self, q, db_id):
        sql = self.sql_parser.predict(q, db_id)
        return sql



if __name__ == '__main__':
    print('start')
    dataService = DataService()
    sql = dataService.text2sql("films and film prices that cost below 10 dollars", "cinema")
    print("sql: {}".format(sql))




