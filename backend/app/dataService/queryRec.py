import os
import sys
import re
import json
import numpy as np
import pandas as pd
import math

from sentence_transformers import SentenceTransformer, util
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from mlxtend.frequent_patterns import fpmax, fpgrowth
from sklearn.metrics.pairwise import cosine_similarity

try:
    import globalVariable as GV
    from utils.processSQL import process_sql, decode_sql, generate_sql
    from utils.processSQL.decode_sql import extract_select_names, extract_agg_opts, extract_groupby_names
except ImportError:
    import app.dataService.globalVariable as GV
    from app.dataService.utils.processSQL import process_sql, decode_sql, generate_sql
    from app.dataService.utils.processSQL.decode_sql import extract_select_names, extract_agg_opts, extract_groupby_names
# TODO: data type checking and loading before recommendation
class queryRecommender(object):
    # TODO Check: handle change of database
    def __init__(self, topic_sim_th=0.55, item_sim=0.4, alpha=0.9, beta=0.5,
                 groupby_th=0.7, agg_th=0.5, sim=0.7,
                 opt_n = 1,
                 ref_db_meta_path=os.path.join(GV.SPIDER_FOLDER, "train_spider.json")):
        self.GV = GV
        # self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # self.model = SentenceTransformer('paraphrase-MiniLM-L12-v2')

        self.db_schema, self.db_names, self.tables = process_sql.get_schemas_from_json(
            os.path.join(GV.SPIDER_FOLDER, "tables.json"))
        self.db_new_names = [re.sub(r'[0-9]+', '', n.replace("_", " ")).strip().lower() for n in
                             self.db_names]

        # --- parameter setting
        self.topic_sim_th = topic_sim_th
        self.item_sim = item_sim
        self.groupby_th = groupby_th
        self.agg_th = agg_th
        self.sim = sim
        self.alpha = alpha  # relevance decay for seqeuential query
        self.beta = beta
        self.opt_n = opt_n
        # --- reference database
        with open(ref_db_meta_path, "r") as f:
            ref_db_data = pd.DataFrame(json.load(f))
        self.dataset = ref_db_data
        # --- target table to search
        # self.search_cols = search_cols
        self.db_cache = {} # caching search results
        self.g_cols_cache = {}
        # ---- pre-selected
        self.pre_sel = []

    def cal_cosine_sim(self, sen0, sen1):
        """
        - calculate cosine similairty between sen0 and sen1
        - INPUT:
          - sen0: list of str or single str
          - sen1: list of str or single str
        - OUTPUT:
          - cosine similarity between sen0 and sen1
        """
        if isinstance(sen0, list):
            sen0 = ["".join(s.split(":")[1:]) if ":" in s else s for s in sen0]
        elif isinstance(sen0, str):
            sen0 = "".join(sen0.split(":")[1:]) if ":" in sen0 else sen0
        if isinstance(sen1, list):
            sen1 = ["".join(s.split(":")[1:]) if ":" in s else s for s in sen1]
        elif isinstance(sen1, str):
            sen1 = "".join(sen1.split(":")[1:]) if ":" in sen1 else sen1
        embedd0 = self.model.encode(sen0, convert_to_tensor=True)
        embedd1 = self.model.encode(sen1, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(embedd0, embedd1).cpu().numpy()
        return cosine_scores


    def search_sim_dbs(self, topic, search_cols):
        """
        - retrieve similar db according to query table names
        - INPUT:
          - topic: table/db name (str)
          - search_cols: input table columns (list)
        - OUTPUT:
          - dataframe of similar dbs in the dataset
        """
        ############## cluster input columns based on their semantic meanings
        cols_groups = self.get_grouped_cols(search_cols)
        self.g_cols_cache = cols_groups
        #################################################

        if topic in self.db_cache.keys():
            return self.db_cache[topic]

        self.search_cols = search_cols
        sim_scores = self.cal_cosine_sim(topic, self.db_new_names)[0]
        related_db_names = [self.db_names[i] for i in np.where(sim_scores > self.topic_sim_th)[0]]
        print(f"related_db_names: {related_db_names}")
        row_sims = []
        rowids = []
        for rowid, row in self.dataset.iterrows():
            if row["db_id"] in related_db_names:
                rowids.append(rowid)
                # entity in `select` clause
                # print(row["sql"])
                select_decoded = decode_sql(row["sql"], self.tables[row["db_id"]])["select"]
                select_ents = extract_select_names(select_decoded)
                # calculate similarity between `select` items and `select` cols
                row_sim = self.cal_cosine_sim(self.search_cols, select_ents)
                row_sims.append(np.max(row_sim, axis=1))
        db_df_bin = pd.DataFrame(np.where(np.array(row_sims) > self.item_sim, 1, 0),
                                 columns=self.search_cols)
        self.ref_db = (self.dataset.loc[rowids]).reset_index(drop=True)
        sim_sum = [sum(db_df_bin[col]) for col in db_df_bin.columns]
        db_df_bin = db_df_bin[db_df_bin.columns[(-np.array(sim_sum)).argsort()]]
        ######################################################################
        
        self.db_cache[topic] = db_df_bin
        return db_df_bin

    def get_grouped_cols(self, columns, min_size = 2, th = 0.75):
        corpus_embeddings = self.model.encode(columns, convert_to_tensor=True)
        clusters = util.community_detection(corpus_embeddings, min_community_size = min_size, threshold = th)
        col_groups = [set([columns[c] for c in cluster]) for cluster in clusters]
        col_groups += GV.col_combo
        # print("col_groups: ", col_groups)
        return col_groups


    def get_freq_combo(self, df, filter_set=set([]), support=None, max_len = 3):
        """
        - input: dataframe (m * n) => binary values
        - output: frequent combo => columns: support, itemsets, itemlen
        """
        # print("max_len: ", max_len)
        # FIXED: fpmax V.S. fpgrowth 
        # (choose `fpgrowth` for flexible itemset selection based on itemset lengths)
        if support is None:
            support = self.item_sim
        freq_combo = fpmax(df, min_support=support, use_colnames=True)
        # freq_combo = fpgrowth(df, min_support=support, use_colnames=True, max_len = max_len)
        freq_combo["itemlen"] = freq_combo["itemsets"].apply(len)
        # (DONE): adjust ranking according to both itemset lengths AND itemsets support: (log2(item length)+1) * support
        # freq_combo["itemW"] = (np.log2(freq_combo["itemlen"]) +1) * freq_combo["support"]
        freq_combo["itemW"] = freq_combo["itemlen"] * np.square(freq_combo["support"])
        # filter regarding to condition
        if len(filter_set) > 0:
            freq_combo = freq_combo.iloc[
                [rowid for rowid, row in enumerate(freq_combo["itemsets"]) if
                 row.issubset(filter_set) == False]]
        freq_combo = freq_combo.sort_values(["itemlen", "support"], ascending=False).reset_index(
            drop=True)
        # freq_combo = freq_combo.sort_values(["itemW", "support"], ascending=False).reset_index(
        #     drop=True)
        # print(freq_combo.head())
        # exit()
        return freq_combo

    def get_opts(self, df, cols, groupby_contexts=[], agg_contexts=[], top_n = 1):
        """
        recommend  `groupby` & `agg_opt` items
        `agg_opt` items: `avg`, `min`, `max`, `count`, `sum`
        - input: binary feature vectors (size: db_col_num * input_col_num) for input table cols
              - top_n: limit return results
        - output: `groupby` cols ([col1, col2]), `agg_opt` lists ([{"opt": "col"}, {}])
        """
        agg_opts = ['max', 'min', 'count', 'sum', 'avg']
        groupby_sugg = []
        agg_sugg = []

        # `groupby` and `agg` contexts
        # groupby_contexts = np.hstack(
        #     [['shop: manager name'], [], ["shop: district", "shop: location"]]
        # )
        # groupby_contexts = np.hstack(
        #         [['shop: manager name'], [], ["shop: district", "shop: location"]])
        gb_sugg_context = []
        if len(groupby_contexts)>0:
            groupby_contexts = np.hstack(groupby_contexts)
            ##############################
            # calculate `groupby` context relecance (between remaining cols and groupby contexts)
            if len(groupby_contexts)>0:
                df_col_diff = df.columns.difference(set(groupby_contexts))
                groupby_c_sim = np.max(self.cal_cosine_sim(groupby_contexts, df_col_diff), axis=0)
                # print(f"groupby_c_sim: {groupby_c_sim}", groupby_c_sim.shape)
                df_col_diff = df_col_diff[(-groupby_c_sim).argsort()]
                groupby_c_sim = groupby_c_sim[(-groupby_c_sim).argsort()]
                # TODO: original similarity: self.sim
                gb_sugg_context = [gb for gb in list(df_col_diff[groupby_c_sim > self.groupby_th]) if
                                "*" not in gb]  # handle (table_name: *) situations
                # print(f"gb_sugg_context: {gb_sugg_context}")
                # print("*"*10)
            ##############################
        # agg_contexts = [{}, {}, {"count": ["customers: other customer details"]}]
        
        # print(f"groupby_contexts = {groupby_contexts}, agg_contexts = {agg_contexts}")

        for _, col in enumerate(cols):
            col_mul = np.prod(df[col], axis=1)
            col_mul_idx = np.where(col_mul == 1)[0]
            all_groupby_names = []
            agg_list = []
            for rowid, row in self.ref_db.iloc[col_mul_idx].iterrows():
                db_id = row["db_id"]
                table = self.tables[db_id]
                sql = row["sql"]
                # extract `groupby` entities
                # groupby_decoded = decode_sql.decode_groupby(sql["groupBy"], table)
                groupby_decoded = decode_sql(sql, table)["groupBy"]
                groupby_names = extract_groupby_names(groupby_decoded)
                # extract `agg` operations
                select_decoded = decode_sql(sql, table)["select"]
                # select_decoded = decode_sql.decode_select(sql, table)
                agg_dict = extract_agg_opts(select_decoded)
                agg_list.append(agg_dict)
                if len(groupby_names) > 0:
                    all_groupby_names.append(groupby_names)
            # `groupby` entity suggestion
            # TODO: Thresholds `groupby` confidence support and similarity
            # TODO: Whether context/history `groupby` opts should be included in the next `groupby` opt? - Current: remove context/history opt
            ################################################################
            # calculate db `groupby` relevance
            gb_sugg = []
            if len(col_mul_idx) > 0:
                if len(all_groupby_names) / len(
                        col_mul_idx) > self.groupby_th:  # confidence thresholds
                    # print(all_groupby_names)
                    groupby_sim = np.max(
                        self.cal_cosine_sim(np.concatenate(all_groupby_names), df.columns), axis=0)
                    groupby_cols = df.columns[(-groupby_sim).argsort()]
                    groupby_sim = groupby_sim[(-groupby_sim).argsort()]
                    gb_sugg = list(
                        groupby_cols[groupby_sim > self.groupby_th])  # similarity thresholds
            # TODO: (DOING) limit return results of `groupby`
            if len(gb_sugg_context) >0:
                if len(gb_sugg_context) >= top_n:
                    gb_sugg = gb_sugg_context[:top_n]
                else:
                    gb_sugg = gb_sugg[:(top_n - len(gb_sugg_context))] + gb_sugg_context
                # gb_sugg += gb_sugg_context
            else:
                if len(gb_sugg)>=top_n:
                    gb_sugg=gb_sugg[:top_n]
            # print(f"gb_sugg: {gb_sugg}")
            groupby_sugg.append(gb_sugg)
            ################################################################
            # `agg` entity suggestion
            # TODO: Thresholds `agg` confidence support and similarity
            # TODO: (DOING) limit return results of `agg`
            agg_df = pd.DataFrame(agg_list).head()
            # print(agg_df.head())
            agg_sugg_dict = {}
            if len(col_mul_idx) > 0:
                for agg_opt in agg_opts:
                    # print("agg_opt: ", agg_opt)
                    # calculate `agg` context relevance
                    ################################################################
                    agg_l = [agg_c[agg_opt] for agg_c in agg_contexts if agg_opt in agg_c.keys()]
                    agg_l = np.concatenate(agg_l) if len(agg_l) > 0 else agg_l
                    if len(agg_l) > 0:
                        agg_context_sim = np.max(self.cal_cosine_sim(agg_l, col), axis=0)
                        agg_col = [col[aid] for aid, a_sim in enumerate(agg_context_sim) if
                                   a_sim > self.item_sim]
                        if agg_opt != "count":
                            agg_col = [ac for ac in agg_col if ac not in GV.opt_constraints]
                        # print("-*-"*10)
                        # print("agg_col: ", agg_col)
                        # print("-*-"*10)
                        if agg_opt not in agg_sugg_dict.keys():
                            agg_sugg_dict[agg_opt] = []
                        agg_sugg_dict[agg_opt] += (agg_col)
                        # print("type(agg_col)",type(agg_col), agg_col, agg_sugg_dict[agg_opt])
                    ################################################################
                    # calculate db `agg` relevance
                    agg_num = 0
                    a_l = []
                    for agg in agg_df[agg_opt].values:
                        if len(agg) > 0:
                            agg_num += 1
                            a_l += agg
                    # print("---"*10)
                    # print("agg_num, len(col_mul_idx): ", agg_num, len(col_mul_idx))
                    # print("---"*10)
                    # if agg_num / len(col_mul_idx) > self.agg_th:
                    if agg_num > 0:
                        # agg_sugg_dict[agg_opt] = []
                        # print("a_l, col: ", a_l, col)
                        agg_c_sim = np.mean(self.cal_cosine_sim(a_l, col), axis=0)
                        for g_sim, c in zip(agg_c_sim, col):
                            if g_sim > self.agg_th:
                                if agg_opt not in agg_sugg_dict.keys():
                                    agg_sugg_dict[agg_opt] = []
                                if c not in agg_sugg_dict[agg_opt]:
                                    # select top one count
                                    # if agg_opt == "count" and len(agg_sugg_dict[agg_opt])>=1:
                                    if len(agg_sugg_dict[agg_opt])>=1:
                                        break
                                    else:
                                        # agg_sugg_dict[agg_opt].append(c)
                                        if agg_opt == "count":
                                            agg_sugg_dict[agg_opt].append(c)
                                        else:
                                            if c not in GV.opt_constraints:
                                                agg_sugg_dict[agg_opt].append(c)
                                
                                if len(agg_sugg_dict[agg_opt])==0:
                                    agg_sugg_dict.pop(agg_opt)


            agg_sugg.append(agg_sugg_dict)
        # assert len(agg_sugg) == len(cols)
        # print("agg_sugg: ", agg_sugg)
        return groupby_sugg, agg_sugg

    def query_suggestion(self, db_df_bin, context_dict={"select": [], "groupby": [], "agg": []},
                         min_support=None, top_n=5, max_len = 3):
        """
        max_len: max query entity # per query
        TODO: 
        0. drill down and up in existing query items
        1. consider clustering input columns based on their semantics and operate cols on cluster levels
        2. consider user specified (combo of interest) that are not frequently seen in the db
        3. IMPLICIT feedback: selection of recomended items, indicating items that are not selected is not of users' interest,
        consider decreasing the rank of unselected recommended items
        4. ranking considering `groupby` and `opt` items
        """
        support = self.item_sim if min_support is None else min_support
        # `select`, `agg`, `groupby`
        sel_contexts = context_dict["select"]
        agg_contexts = context_dict["agg"]
        groupby_contexts = context_dict["groupby"]
        # STEP ONE: initial recommendation
        if len(sel_contexts) == 0:
            freq_combo = self.get_freq_combo(db_df_bin, set([]), support, max_len = max_len)
            union_set = frozenset().union(*freq_combo["itemsets"].values)
            next_cols = [list(v) for v in freq_combo["itemsets"].values]
            # print("freq_combo: ", freq_combo)
            # print("db_df_bin.columns: ", db_df_bin.columns)
            # print("next cols: ", next_cols, db_df_bin.columns.difference([]))
            
            if len(union_set) < top_n:
                rest_cols = db_df_bin.columns.difference(list(union_set))
                sim_sum = [sum(db_df_bin[col]) for col in rest_cols]
                # sort columns according to their overall database relevance
                cols_supp = []
                #############################################
                ########## recommend similar columns (grouped based on their semantic meaning)
                for col in db_df_bin[rest_cols[(-np.array(sim_sum)).argsort()]].columns:
                    if len(cols_supp) < top_n - len(union_set):
                        if sum([col in c for c in cols_supp]) == 0:
                            curr_set = [col]
                            # check `max_len` constraints
                            for c in self.g_cols_cache:
                                if col in c:
                                    curr_set += list(c.difference([col]))[:max_len-2]
                            # print("curr_set: ", curr_set)
                            cols_supp.append(curr_set) 
                #############################################
                # print("cols_supp: ", cols_supp)
                # cols_supp = [[col] for col in db_df_bin[rest_cols[(-np.array(sim_sum)).argsort()]].columns[:(top_n - len(union_set))]]
                next_cols += cols_supp
            else:
                next_cols = [list(v) for vidx, v in enumerate(freq_combo["itemsets"].values) if vidx<top_n]

            # # get `groupby` and `agg_opt` items
            # groupby_sugg, agg_sugg = self.get_opts(db_df_bin, next_cols, groupby_contexts,
            #                                        agg_contexts, self.opt_n)

            # print("next_cols: ", next_cols)
            return {
                "select": next_cols,
                "groupby": [[] for nc in next_cols], #groupby_sugg,
                "agg": [{} for nc in next_cols] #agg_sugg,
            }

        # STEP TWO: recommendation considering the contexts information
        columns = db_df_bin.columns
        context_cols = np.concatenate(sel_contexts)
        rest_cols = columns.difference(context_cols)
        
        all_sims = np.zeros(len(rest_cols))
        ########################################################################
        # get `groupby` and `agg_opt` items (NEW)
        opt_flag = False
        if len(sel_contexts) > 0:
            if len(sel_contexts[-1]) > 0:
                if set(self.pre_sel) != set(sel_contexts[-1]):
                    groupby_sugg, agg_sugg = self.get_opts(db_df_bin, [sel_contexts[-1]], groupby_contexts,
                                                        agg_contexts, self.opt_n)
                    # print("sel_contexts[-1], self.pre_sel: ", sel_contexts[-1], self.pre_sel)
                    self.pre_sel = sel_contexts[-1]
                    if len(groupby_sugg[0]) > 0 or bool(agg_sugg[0]):
                        opt_flag = True
                        if bool(agg_sugg[0]):
                            sel_pre = [[]]
                        else:
                            sel_pre = [sel_contexts[-1]]
                        print("---"*10)
                        # print("sel_contexts, self.pre_sel: ", sel_contexts, self.pre_sel)
                        print("prev cols, groupby_sugg, agg_sugg: ", sel_contexts[-1], groupby_sugg, agg_sugg)
                        print("---"*10)
        # 
        # if len(context_cols) > 0:
        #     groupby_sugg_, agg_sugg_ = self.get_opts(db_df_bin, [context_cols], groupby_contexts,
        #                                                 agg_contexts, self.opt_n)
        #     print("operations for queried items: ", context_cols, groupby_sugg_, agg_sugg_)
        ########################################################################

        for contextid, context in enumerate(sel_contexts):
            # print()
            # print("context: ", context)
            # print()
            if len(context)>0:
                # 1. consider semantic similarity
                semantic_sim_scores = np.max(self.cal_cosine_sim(rest_cols, context),
                                            axis=1) * math.pow(self.alpha,
                                                                len(sel_contexts) - contextid - 1)
                # print("semantic_sim_scores: ", semantic_sim_scores)
                # 2. consider cosine similarity between feature vectors (relevance vector to the database)
                db_col_feat = db_df_bin[rest_cols].T
                context_feat = db_df_bin[context].T
                db_relevance = np.max(cosine_similarity(db_col_feat, context_feat), axis=1) * math.pow(
                    self.alpha, len(sel_contexts) - contextid - 1)
                # print("db_relevance: ", db_relevance)
                # 3. average similarity based on semantic similarity and db relevance
                all_sims += semantic_sim_scores + self.beta * db_relevance
        # print("all_sims: ", all_sims, rest_cols)
        rest_cols = rest_cols[(-all_sims).argsort()]
        top_n_rest_cols = rest_cols[:top_n]
        # TODO: pay attention to item similarity threshold change & reinitialization
        # support = support * math.pow(self.alpha, len(sel_contexts))
        # print(f"support: {support}")

        # print(self.g_cols_cache)
        # print("top_n_rest_cols: ", top_n_rest_cols)

        freq_combo = self.get_freq_combo(db_df_bin[list(context_cols) + list(top_n_rest_cols)],
                                         filter_set=set(context_cols), support=support, max_len = max_len)
        freq_cols = [list(v) for v in freq_combo["itemsets"].values if len(v) > 0]
        ##########################################
        for col in rest_cols:
            if len(freq_cols) < top_n:
                total_cols = []
                if len(freq_cols) > 0:
                    total_cols = np.concatenate(freq_cols)
                if col not in total_cols:
                    curr_set = [col]
                    for c in self.g_cols_cache:
                        if col in c:
                            curr_set += list(c.difference([col]))[:max_len-2]
                    # print("col not in total cols: ", curr_set)
                    freq_cols.append(curr_set)
            else:
                freq_cols = freq_cols[:top_n]
                break
        ##########################################
        ################### OLD ####################
        # if len(freq_combo["itemsets"].values) < top_n:
        #     for col in top_n_rest_cols:
        #         print(col)

        #     if len(freq_cols) == 0:
        #         freq_cols = [[tn] for tn in top_n_rest_cols]
        #     else:
        #         freq_cols += [[col] for col in top_n_rest_cols if
        #                       col not in np.concatenate(freq_cols)]
        # else:
        #     freq_cols = freq_cols[:top_n]
        ################### OLD ####################
        # print("freq cols: ", freq_cols)

        # get `groupby` and `agg_opt` items (OLD)
        # groupby_sugg, agg_sugg = self.get_opts(db_df_bin, freq_cols, groupby_contexts,
        #                                        agg_contexts, self.opt_n)

        # return {
        #     "select": freq_cols,
        #     "groupby": groupby_sugg,
        #     "agg":  agg_sugg
        # }
        if opt_flag:
            return {
                "select": sel_pre + freq_cols,
                "groupby": groupby_sugg + [[] for fc in freq_cols],
                "agg":  agg_sugg + [{} for fc in freq_cols]
            }
        else:
            return {
                "select": freq_cols,
                "groupby": [[] for fc in freq_cols],#groupby_sugg,
                "agg": [{} for fc in freq_cols] #agg_sugg
            }


if __name__ == "__main__":
    test_topic = GV.test_topic
    test_table_cols = GV.test_table_cols

    qr = queryRecommender()
    db_bin = qr.search_sim_dbs(test_topic.replace("_", " ").strip(), test_table_cols)
    # print(qr.tables[test_topic])

    # initial recommendation
    context_dict = {
        "select": [],
        "groupby": [],
        "agg": []
    }
    # sugg_dict = qr.query_suggestion(db_bin, context_dict, None)
    sugg_dict = qr.query_suggestion(db_bin, context_dict, 0.6)
    # nls = generate_sql.compile_sql(sugg_dict)
    # print("nl for sugg_dict: ", nls)
    freq_combo = sugg_dict["select"]
    groupby_sugg = sugg_dict["groupby"]
    agg_sugg = sugg_dict["agg"]
    # select_items = [freq_combo[2]]
    select_items = [freq_combo[0]]

    print(f"next_cols: {freq_combo}")
    print(f"groupby_sugg: {groupby_sugg}")
    print(f"agg_sugg: {agg_sugg}")
    print(f"select_items: {select_items}")
    print()

    # next query suggestion
    context_dict["select"] = select_items
    sugg_dict = qr.query_suggestion(db_bin, context_dict, 0.6)
    # nls = generate_sql.compile_sql(sugg_dict)
    # print("nl for sugg_dict: ", nls)
    next_cols = sugg_dict["select"]
    groupby_sugg = sugg_dict["groupby"]
    agg_sugg = sugg_dict["agg"]

    print(f"next_cols: {next_cols}")
    print(f"groupby_sugg: {groupby_sugg}")
    print(f"agg_sugg: {agg_sugg}")
    # print(f"select_items: {select_items + [next_cols[3]]}")
    print(f"select_items: {select_items + [next_cols[0]]}")
    print()

    # next query suggestion
    # context_dict["select"] = select_items + [next_cols[3]]
    context_dict["select"] = select_items + [next_cols[0]]
    sugg_dict = qr.query_suggestion(db_bin, context_dict, 0.6)
    # nls = generate_sql.compile_sql(sugg_dict)
    # print("nl for sugg_dict: ", nls)
    next_cols = sugg_dict["select"]
    groupby_sugg = sugg_dict["groupby"]
    agg_sugg = sugg_dict["agg"]
    # print(len(next_cols), len(groupby_sugg))
    print(f"next_cols: {next_cols}")
    print(f"groupby_sugg: {groupby_sugg}")
    print(f"agg_sugg: {agg_sugg}")
    print(f"select_items: {select_items + [next_cols[0]]}")
