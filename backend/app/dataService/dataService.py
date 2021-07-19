# -*- coding: utf-8 -*-
import time
import json
import os
import sys
import sqlite3

try:
    import globalVariable as GV
    import sqlParser as sp
except ImportError:
    import app.dataService.globalVariable as GV
    import app.dataService.sqlParser as sp

class DataService(object):
    def __init__(self, dataset = "spider"):
        print("=== begin loading model ===")
        # self.sql_parser = sp.SmBop()
        self.dataset = dataset
        if self.dataset == "spider":
            db_lists = []
            db_meta_dict = {}
            for db_meta in json.load(open(os.path.join(GV.SPIDER_FOLDER,"tables.json"), "r")):
                db_lists.append(db_meta["db_id"])
                db_meta_dict[db_meta["db_id"]] = db_meta
            self.db_lists = db_lists
            self.db_meta_dict = db_meta_dict
            self.db_id = ""
        else:
            raise Exception("currently only support spider dataset")
        print("=== finish loading model ===")
        return
    
    def get_tables(self, db_id):
        self.db_id = db_id
        table_names = self.db_meta_dict[db_id]["table_names"]
        return table_names

    def get_cols(self, table_name):
        table_names = self.db_meta_dict[self.db_id]["table_names"]
        all_col_names = self.db_meta_dict[self.db_id]["column_names"]
        all_col_types = self.db_meta_dict[self.db_id]["column_types"]
        table_idx = table_names.index(table_name)
        cols_info = []
        for col_idx, col_name in enumerate(all_col_names):
            if col_name[0] == table_idx:
                cols_info.append([col_name[1], all_col_types[col_idx]])
        return cols_info

    def text2sql(self, q, db_id):
        sql = self.sql_parser.predict(q, db_id)
        return sql
        


if __name__ == '__main__':
    print('dataService:')
    dataService = DataService("spider")
    # 1. text2sql
    # sql = dataService.text2sql("films and film prices that cost below 10 dollars", "cinema")
    # print("sql: {}".format(sql))
    # 2. db lists
    print(dataService.db_lists)
    dataService.get_tables("cinema")
    print(dataService.get_cols("film"))




