# -*- coding: utf-8 -*-
import copy
import time
import json
import os
import warnings

import sqlite3
import pandas as pd
import random
import traceback

try:
    from luxRec import  lux_rec_test,multiDF_rec
    import globalVariable as GV
    import sqlParser as sp
    import queryRec as qr
    from utils import helpers
    from utils.visRecos import vis_design_combos
    from vlgenie import VLGenie
    from utils.processSQL import decode_sql, generate_sql
    from utils.processSQL.decode_sql import  extract_select_names, extract_agg_opts, extract_groupby_names
except ImportError:

    import app.dataService.globalVariable as GV
    import app.dataService.sqlParser as sp
    import app.dataService.queryRec as qr
    from app.dataService.luxRec import lux_run_test
    from app.dataService.utils import helpers
    from app.dataService.utils.visRecos import vis_design_combos
    from app.dataService.vlgenie import VLGenie
    from app.dataService.utils.processSQL import decode_sql, generate_sql
    from app.dataService.utils.processSQL.decode_sql import  extract_select_names, extract_agg_opts, extract_groupby_names


class DataService(object):
    def __init__(self, dataset="spider"):
        self.text2sql_model_loaded = True
        self.sql_parser_loaded = True

        self.sqlsugg_model_loaded = True
        self.sql2text_model_loaded = True
        self.dataset = dataset
        self.global_variable = GV
        if self.dataset == "spider":
            db_lists = []
            db_meta_dict = {}
            for db_meta in json.load(open(os.path.join(GV.SPIDER_FOLDER, "tables.json"), "r")):
                db_lists.append(db_meta["db_id"])
                db_meta_dict[db_meta["db_id"]] = db_meta
            self.db_lists = db_lists
            self.db_meta_dict = db_meta_dict
            self.db_id = ""
            self.cur_q = None
            self.h_q = {}
            self.u_q_lux={}
            self.e_q_lux={}
            self.c_lux={}

            self.table_cols = []
        else:
            raise Exception("currently only support spider dataset")
        return

    def _load_text2sql_model(self, verbose=True):
        if self.text2sql_model_loaded:
            return
        if verbose:
            print("=== begin loading text2sql model ===")
        self.text2sql_model = sp.SmBop()
        self.text2sql_model_loaded = True
        if verbose:
            print("=== finish loading text2sql model ===")
    
    def _load_sql2text_model(self, verbose=True):
        if self.sql2text_model_loaded:
            return
        if verbose:
            print("=== begin loading sql2text model ===")
        self.sql2text_model = sp.SQL2NL()
        self.sql2text_model_loaded = True
        if verbose:
            print("=== finish loading sql2text model ===")
        return

    def _load_sql_parser(self, verbose=True):
        if self.sql_parser_loaded:
            return
        if verbose:
            print("=== begin loading sql parser ===")
        self.sql_parser = sp.SQLParser()
        self.sql_parser_loaded = True
        if verbose:
            print("=== finish loading sql parser ===")

    def _load_sqlsugg_model(self, verbose=True):
        if self.sqlsugg_model_loaded:
            return
        if verbose:
            print("=== begin loading sql suggestion model ===")
        self.sqlsugg_model = qr.queryRecommender()
        self.sqlsugg_model_loaded = True
        if verbose:
            print("=== finish loading sql suggestion model ===")

    def get_db_info(self, db_id):
        db_info = self.db_meta_dict[db_id]
        table_info_list = []
        for i, tabel_name in enumerate(db_info['table_names_original']):
            table_info = {
                'id': tabel_name,
                'name': db_info['table_names'][i],
                'primary_key': db_info['primary_keys'][i],
                'columns': []
            }
            for col_i, col in enumerate(db_info['column_names_original']):
                if col[0] == i:
                    table_info['columns'].append({
                        'id': col[1],
                        'name': db_info['column_names'][col_i][1],
                        'type': db_info['column_types'][col_i]
                    })
            table_info_list.append(table_info)
        return table_info_list

    def get_tables(self, db_id):
        self.db_id = db_id
        db_info = self.db_meta_dict[db_id]
        #print(db_info.keys())
        tkeys = set(db_info["primary_keys"]).union(set([k for kp in db_info["foreign_keys"] for k in kp]))
        table_names = db_info["table_names"]
        db_dict = {}
        for cidx, (colname, coltype) in enumerate(zip(db_info["column_names"], db_info["column_types"])):
            # print(cidx, colname, coltype)
            cname = colname[1]
            table_idx = colname[0]
            if table_idx != -1:
                table_name = table_names[table_idx]
                if table_name not in db_dict:
                    db_dict[table_name] = []
                if cidx in tkeys:
                    db_dict[table_name].append([cname, "key"])
                else:
                    db_dict[table_name].append([cname, coltype])
        # sort column names according to column types
        for dk in db_dict.keys():
            db_dict[dk] = sorted(db_dict[dk], key=lambda x: x[1])
        print('get_tables//')
        print('db_dict.keys',db_dict.keys())
        return db_dict

    def get_tables_original(self, db_id):
        self.db_id = db_id
        db_info = self.db_meta_dict[db_id]
        print('db_info.keys()',db_info.keys())
        tkeys = set(db_info["primary_keys"]).union(set([k for kp in db_info["foreign_keys"] for k in kp]))
        table_names = db_info["table_names_original"]
        db_dict = {}
        for cidx, (colname, coltype) in enumerate(zip(db_info["column_names_original"], db_info["column_types"])):
            # print(cidx, colname, coltype)
            cname = colname[1]
            table_idx = colname[0]
            if table_idx != -1:
                table_name = table_names[table_idx]
                if table_name not in db_dict:
                    db_dict[table_name] = []
                if cidx in tkeys:
                    db_dict[table_name].append([cname, "key"])
                else:
                    db_dict[table_name].append([cname, coltype])
        # sort column names according to column types
        for dk in db_dict.keys():
            db_dict[dk] = sorted(db_dict[dk], key=lambda x: x[1])
        print('get_tables_original//')
        print('db_dict.keys',db_dict.keys())
        return db_dict

    def get_cols(self, table_name):
        table_names = self.db_meta_dict[self.db_id]["table_names_original"]
        all_col_names = self.db_meta_dict[self.db_id]["column_names_original"]
        all_col_types = self.db_meta_dict[self.db_id]["column_types"]
        print('table names',table_names)
        table_idx = table_names.index(table_name)
        cols_info = []
        for col_idx, col_name in enumerate(all_col_names):
            if col_name[0] == table_idx:
                cols_info.append([col_name[1], all_col_types[col_idx]])
        return cols_info

    def get_db_cols(self, db_id):
        """
        get all table cols in the database.
        - Input: 
            - db_id: database name
        - Output: 
            - table col names: ["table name: col names", ...]
        """
        if db_id not in self.h_q.keys():
            db_info = self.db_meta_dict[db_id]
            pk = db_info["primary_keys"] # primary keys
            fk = db_info["foreign_keys"] # foreign keys
            k_set = set(pk)
            for f in fk:
                for e in f:
                    k_set.add(e)
            # print("k_set: ", k_set)
            table_names = db_info["table_names"]
            # remove columns that included in primary keys and foreign keys since they usually do not carry many meanings
            table_cols = [table_names[col[0]] + ": " + col[1] for colidx, col in enumerate(db_info["column_names"]) if col[0]!=-1 and colidx not in list(k_set)]
            self.table_cols = table_cols
            # print(table_cols)
            
        return self.table_cols

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
        print('tabel_data',table_data)
        return table_data

    def text2sql(self, q, db_id):
        self._load_text2sql_model()
        sql = self.text2sql_model.predict(q, db_id)
        return sql

    def parsesql(self, sql, db_id):
        """parse sql data based on spider database
        sql: sql query
        db_id: db name in Spider database
        return: {"sql_parse": sql_label, "table": table}
        """
        if self.dataset == "spider":
            self._load_sql_parser()
            parsed = self.sql_parser.parse_sql(sql, db_id)
            return parsed
        else:
            raise Exception(f"Can not support {self.dataset} dataset")

    def init_query_context(self, db_id):
        self.h_q[db_id] = {}
        self.h_q[db_id]["select"] = []
        self.h_q[db_id]["groupby"] = []
        self.h_q[db_id]["agg"] = []

    def get_all_rec(self,rec_dict):
        all_rec = []
        for each in rec_dict:
            all_rec += rec_dict[each]
        return all_rec
    def init_query_context_lux(self,db_id):

        df_list=self.get_df_list(db_id)
        print("lenlenlen",len(df_list))

        self.u_q_lux[db_id]=[[]for i in range(len(df_list))]
        for i in range(len(df_list)):
            try:
                self.u_q_lux[db_id][i]=self.get_all_rec(df_list[i].recommendation)
            except:
                traceback.print_exc()




        self.e_q_lux[db_id]=[[] for i in range(len(df_list))]
        print('init_e',self.e_q_lux)
        self.c_lux[db_id]=['NULL' for i in range(len(df_list))]

    def set_query_context(self, sql, db_id):
        """
        set query context
        ### Input
        - sql: sql (str)
        - db_id: database name (str)
        """
        # TODO: dont update context if already exists in the history
        sql_parse = self.parsesql(sql, db_id)
        sql_decoded = decode_sql(sql_parse["sql_parse"], sql_parse["table"])
        select_ents = extract_select_names(sql_decoded["select"])
        groupby_ents = extract_groupby_names(sql_decoded["groupBy"])
        agg_dict = extract_agg_opts(sql_decoded["select"])
        table_cols = self.get_db_cols(db_id) # meaningful columns
        # print("select ents: ", select_ents)
        # print("groupby ents: ", groupby_ents)
        # print("agg dict: ", agg_dict)
        # print(f"table_cols: {table_cols}")

        self.cur_q = [sql, db_id]
        if db_id not in self.h_q.keys():
            self.init_query_context(db_id)
        # ensure entities are in the table columns (exclude the foreig/primary keys)
        self.h_q[db_id]["select"].append([ent for ent in select_ents if ent in table_cols])
        self.h_q[db_id]["groupby"].append([ent for ent in groupby_ents if ent in table_cols])
        for ag_opt in agg_dict.keys():
            agg_dict[ag_opt] = [attr for attr in agg_dict[ag_opt] if attr in table_cols]
        self.h_q[db_id]["agg"].append(agg_dict)

        # print(json.dumps(self.h_q, indent=2))

    def set_query_context_lux(self,vis,db_id):

        index = vis['df_index']
        print('index',index)
        C_vis_obj = vis['vis_obj']
        self.e_q_lux[db_id][index].append(str(C_vis_obj))
        print('set_E',self.e_q_lux[db_id])
        self.u_q_lux[db_id][index] = [x for x in self.u_q_lux[db_id][index] if str(x) != str(C_vis_obj)]
        print('set_u',self.u_q_lux[db_id][index])
        self.c_lux[db_id][index]=C_vis_obj

    def sql_suggest(self, db_id, table_cols, min_support = 0.6, context_dict = {"select": [], "groupby": [], "agg": []}):
        """
        recommend sql queries based on sqls
        ### Input
        - db_id: database name (str)
        - table_cols: column names of all tables in the selected database
        - context_dict: history queries
        ### Output:
        - suggestion
        """
        if db_id in self.h_q.keys():
            context_dict = self.h_q[db_id]

        # database meta data
        db_meta = self.db_meta_dict[db_id]
        # print("db_meta: ", db_meta.keys()])

        # load sql suggestion model
        self._load_sqlsugg_model()
        # print("db id, table_cols: ", db_id.replace("_", " ").strip(), table_cols)
        db_bin = self.sqlsugg_model.search_sim_dbs(db_id.replace("_", " ").strip(), table_cols)
        # print(db_bin.head())
        sugg_dict = self.sqlsugg_model.query_suggestion(db_bin, context_dict, min_support)
        # print("sugg_dict: ", sugg_dict)
        

        nls_prompts = generate_sql.compile_sql(sugg_dict)
        # print("nls: {}".format(nls))
        sqls = [self.text2sql(nl, db_id) for nl in nls_prompts]
        sql2nls =  [self.sql2nl(sql) for sql in sqls]      
        # print("sql2nls: {}, type: {}".format(sql2nls, type(sql2nls[0])))
        return {
            "sql": sqls,
            "nl": sql2nls
        }
    def get_df_list(self,db_id):
        db_dict=self.get_tables_original(db_id)
        print('db_dict',db_dict)
        df_list=[self.load_table_content(x) for x in db_dict.keys()]
        print('df_list',df_list)
        df_list=[pd.DataFrame(x) for x in df_list]
        print('df_list_df',df_list)
        return df_list

    def lux_suggest(self,db_id,unexplored_intents=0, explored_intents=0, current_choice=0, top_k1=5, top_k2=5):
        df_list = self.get_df_list(db_id)
        if db_id in self.u_q_lux.keys():
            unexplored_intents=self.u_q_lux[db_id]
            explored_intents=self.e_q_lux[db_id]
            current_choice=self.c_lux[db_id]
        else:
            unexplored_intents = [self.get_all_rec(df_list[i].recommendation) for i in range(len(df_list))]
            explored_intents= [[] for i in range(len(df_list))]
            current_choice = ['NULL' for i in range(len(df_list))]

        #print('df_list',df_list)
        print('unexplored_intents',unexplored_intents)
        print('current',current_choice)
        rec=multiDF_rec(df_list,unexplored_intents,explored_intents, current_choice, top_k1, top_k2)


        return rec


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
        sql_parsed = self.parsesql(sql, db_id)
        sql_decoded = decode_sql(sql_parsed["sql_parse"], sql_parsed["table"])
        identifiers = [ident.replace('\'s', '') \
                       for ident in helpers.get_sql_identifiers(sql_decoded["select"])]

        db_path = os.path.join(GV.SPIDER_FOLDER, f"database/{db_id}/{db_id}.sqlite")
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        data = [list(d) for d in cur.execute(sql).fetchall()]
        con.close()

        data = pd.DataFrame(data, columns=identifiers)
        return data

    def sql2vl(self, sql, db_id, return_data=False):
        data = self.sql2data(sql, db_id)
        if data.shape == (1, 1):
            response = data.values[0][0]
        else:
            try:
                response = self.data2vl(data)
            except ValueError:
                warnings.warn("Unsupported data type. Show the results in tables instead.")
                response = data
        if return_data:
            return {'data': data, 'vl': response}
        else:
            return response

    def sql2nl(self, sql: str):
        self._load_sql2text_model()
        nl = self.sql2text_model.sql2text(sql)
        return nl

if __name__ == '__main__':
    print('dataService:')
    dataService = DataService("spider")
    db_id = 'customers_and_addresses'
    print('df_lists',dataService.db_lists)
    '''
    for each_db in dataService.db_lists:
        db_id=each_db
        print('db_id')
        df = dataService.get_df_list(db_id)
        for i in range(len(df)):
            print('type', df[i].data_type)
        dataService.init_query_context_lux(db_id)
        lux_rec_result = dataService.lux_suggest(db_id)
        print('first lux rec', lux_rec_result)
        if lux_rec_result[0] + lux_rec_result[1]!=[]:
            C = random.choice(lux_rec_result[0] + lux_rec_result[1])
            print('C', C)
            dataService.set_query_context_lux(C, db_id)
            second_lux_rec_result = dataService.lux_suggest(db_id)
            print('second lux rec', second_lux_rec_result)
        else:
            continue
            
    '''
    #db_id='cinema'

    #db_dict = dataService.get_tables(db_id)

    #db_cols = dataService.get_db_cols("customers_and_addresses")
    #print("db_cols: ", db_cols)

    #lux_test
    df=dataService.get_df_list(db_id)
    for i in range(len(df)):

        print('type',df[i].data_type)
    dataService.init_query_context_lux(db_id)
    lux_rec_result =dataService.lux_suggest(db_id)
    print('first lux rec',lux_rec_result)
    if lux_rec_result[0] + lux_rec_result[1] != []:
        C = random.choice(lux_rec_result[0] + lux_rec_result[1])
        print('C', C)
        dataService.set_query_context_lux(C, db_id)
        second_lux_rec_result = dataService.lux_suggest(db_id)
        print('second lux rec', second_lux_rec_result)
    else:
        pass


    # 1. text2sql
    result = dataService.text2sql("What are the dates when the customers became customers?", "customers_and_addresses")
    print("test2sql: {}".format(result))

    
    #2. db lists
    print(dataService.db_lists)
    dataService.get_tables("cinema")
    print(dataService.get_cols("film"))
    print(dataService.load_table_content("film"))
    
    #3. query suggestion
    print(dataService.db_meta_dict["cinema"])
    db_info = dataService.db_meta_dict[db_id]
    print(db_info["primary_keys"], db_info["foreign_keys"])
    table_names = db_info["table_names"]
    table_cols = [table_names[col[0]] + ": " + col[1] for col in db_info["column_names"] if col[0]!=-1]
    print(table_cols)
    dataService.set_query_context("SELECT title ,  directed_by FROM film", "cinema")
    ############### test sql suggestions
    sql_suggest = dataService.sql_suggest(db_id, db_cols)
    print("sql_suggest: ", sql_suggest)

    ############### test sql2nl 
    sql = "SELECT addresses.other_address_details FROM addresses"
    nl = dataService.sql2nl(sql)
    print("sql: {} \n nl: {}".format(sql, nl))

