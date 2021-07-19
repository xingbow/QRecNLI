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
        self.sql_parser = sp.SmBop()
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
        table_names = self.db_meta_dict[db_id]["table_names_original"]
        return table_names

    def get_cols(self, table_name):
        table_names = self.db_meta_dict[self.db_id]["table_names_original"]
        all_col_names = self.db_meta_dict[self.db_id]["column_names_original"]
        all_col_types = self.db_meta_dict[self.db_id]["column_types"]
        table_idx = table_names.index(table_name)
        cols_info = []
        for col_idx, col_name in enumerate(all_col_names):
            if col_name[0] == table_idx:
                cols_info.append([col_name[1], all_col_types[col_idx]])
        return cols_info

    def get_col_names(self, file_name, table_name):
        conn = sqlite3.connect(file_name)
        col_data = conn.execute(f'PRAGMA table_info({table_name});').fetchall()
        conn.close()
        return [entry[1] for entry in col_data]
    
    def load_table_content(self, table_name):
        db_path = os.path.join(GV.SPIDER_FOLDER, f"database/{self.db_id}/{self.db_id}.sqlite")
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.row_factory = sqlite3.Row
        col_names = self.get_col_names(db_path, table_name)
        table_data = []
        for rowid, row in enumerate(cur.execute(f"select * from {table_name}").fetchall()):
            row_dict = {}
            for eleidx, ele in enumerate(row):
                row_dict[col_names[eleidx]] = ele
            row_dict["id"] = rowid
            table_data.append(row_dict)
        return table_data

    def text2sql(self, q, db_id):
        sql = self.sql_parser.predict(q, db_id)
        print("sql: ", sql)
        db_path = os.path.join(GV.SPIDER_FOLDER, f"database/{db_id}/{db_id}.sqlite")
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        data = [list(d) for d in cur.execute(sql).fetchall()]
        con.close()
        return [sql, data]


if __name__ == '__main__':
    print('dataService:')
    dataService = DataService("spider")
    # 1. text2sql
    result = dataService.text2sql("films and film prices that cost below 10 dollars", "cinema")
    print("test2sql: {}".format(result))
    # 2. db lists
    # print(dataService.db_lists)
    # dataService.get_tables("cinema")
    # print(dataService.get_cols("film"))
    # print(dataService.load_table_content("film"))




