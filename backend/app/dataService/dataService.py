# -*- coding: utf-8 -*-
import copy
import time
import json
import os
import sys

import sqlite3
import pandas as pd

try:
    import globalVariable as GV
    import sqlParser as sp
except ImportError:
    import app.dataService.globalVariable as GV
    import app.dataService.sqlParser as sp

from app.dataService.utils import helpers
from app.dataService.utils.visRecos import vis_design_combos
from app.dataService.vlgenie import VLGenie


class DataService(object):
    def __init__(self, dataset="spider"):
        print("=== begin loading model ===")
        self.sql_parser = sp.SmBop()
        self.dataset = dataset
        if self.dataset == "spider":
            db_lists = []
            db_meta_dict = {}
            for db_meta in json.load(open(os.path.join(GV.SPIDER_FOLDER, "tables.json"), "r")):
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
        return sql

    def data2vl(self, data):
        """Get VegaLite specifications from tabular-style data.
        data: pd.DataFrame, data to be presented
        """
        data_types = {column: helpers.get_attr_type(data[column].tolist()) for column in data}

        attr_list, attr_type_str = helpers.get_attr_datatype_shorthand(data_types)
        if attr_type_str not in vis_design_combos or not \
                vis_design_combos[attr_type_str]["support"]:
            raise ValueError("Unsupported data combinations")

        vl_specs = []

        for d_counter in range(len(vis_design_combos[attr_type_str]["designs"])):

            # Create reference to a design that matches the attribute combination.
            design = copy.deepcopy(vis_design_combos[attr_type_str]["designs"][d_counter])

            vl_genie_instance = VLGenie()

            # MAP the attributes to the DESIGN spec.
            for index, attr in enumerate(attr_list):
                dim = design["priority"][index]  # Dimension: x, y, color, size, tooltip, ...
                agg = design[dim]["agg"]  # Aggregate: sum, mean, ...
                datatype = data_types[attr]

                # Update the design with the attribute. It could be referenced later.
                design[dim]["attr"] = attr
                design[dim]["is_defined"] = True

                # Set the default VIS mark type. Note: Can be overridden later.
                vl_genie_instance.set_vis_type(design["vis_type"])

                # Set the encoding Note: Can be overridden later.
                vl_genie_instance.set_encoding(dim, attr, datatype, agg)

            # If an attribute is dual-encoded e.g. x axis as well as count of y axis,
            # the attribute is supposed to be encoded to both channels.
            for encoding in design["mandatory"]:
                if not design[encoding]["is_defined"]:
                    attr_reference = design[encoding]["attr_ref"]
                    attr = design[attr_reference]["attr"]
                    datatype = data_types[attr]
                    agg = design[encoding]["agg"]
                    vl_genie_instance.set_encoding(encoding, attr, datatype, agg)

            # AESTHETICS
            # ------------------
            # Format ticks (e.g. 10M, 1k, ... ) for Quantitative axes
            vl_genie_instance.add_tick_format()
            # ------------------

            # Enable Tooltips
            # ------------------
            # vl_genie_instance.add_tooltip()
            # ------------------

            # Combine the data
            vl_genie_instance.vl_spec['data'] = {'values': data.to_dict('records')}
            vl_specs.append(vl_genie_instance.vl_spec)

        return vl_specs
    
    def sql2data(self, sql, db_id):
        identifiers = helpers.get_sql_identifiers(sql)

        db_path = os.path.join(GV.SPIDER_FOLDER, f"database/{db_id}/{db_id}.sqlite")
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        data = [list(d) for d in cur.execute(sql).fetchall()]
        con.close()

        data = pd.DataFrame(data, columns=identifiers)
        return data

    
    def sql2vl(self, sql, db_id):
        return self.data2vl(self.sql2data(sql, db_id))


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
