import os
import sys
import re
import json
import numpy as np
import pandas as pd
import math

from sentence_transformers import SentenceTransformer, util

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, fpmax

try:
    import globalVariable as GV
    from utils.processSQL import process_sql, decode_sql
except ImportError:
    import app.dataService.globalVariable as GV
    from app.dataService.utils.processSQL import process_sql, decode_sql

test_topic = "employee_hire_evaluation"
test_table_cols = ['employee: employee id',
 'employee: name',
 'employee: age',
 'employee: city',
 'shop: shop id',
 'shop: name',
 'shop: location',
 'shop: district',
 'shop: number products',
 'shop: manager name',
 'hiring: shop id',
 'hiring: employee id',
 'hiring: start from',
 'hiring: is full time',
 'evaluation: employee id',
 'evaluation: year awarded',
 'evaluation: bonus',
 'employee: *',
 'shop: *',
 'hiring: *',
 'evaluation: *']

class queryRecommender(object):
    def __init__(self, search_cols, topic_sim_th = 0.4, item_sim = 0.4, alpha = 0.9, ref_db_meta_path = os.path.join(GV.SPIDER_FOLDER, "train_spider.json")):
        self.GV = GV
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

        self.db_schema, self.db_names, self.tables = process_sql.get_schemas_from_json(os.path.join(GV.SPIDER_FOLDER, "tables.json"))
        self.db_new_names = [re.sub(r'[0-9]+', '', n.replace("_", " ")).strip().lower() for n in self.db_names]

        # --- parameter setting
        self.topic_sim_th = topic_sim_th
        self.item_sim = item_sim
        self.alpha = alpha # relevance decay for seqeuential query
        # --- reference database
        with open(ref_db_meta_path, "r") as f:
            ref_db_data = pd.DataFrame(json.load(f))
        self.dataset = ref_db_data
        # --- target table to search
        self.search_cols = search_cols
    

    def cal_cosine_sim(self, sen0, sen1):
        # calculate cosine similairty between sen0 and sen1
        # sen0: list of str or single str
        # sen1: list of str or single str
        embedd0 = self.model.encode(sen0, convert_to_tensor=True)
        embedd1 = self.model.encode(sen1, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(embedd0, embedd1).cpu().numpy()
        return cosine_scores
    

    def search_sim_dbs(self, topic):
        sim_scores = self.cal_cosine_sim(topic, self.db_new_names)[0]
        related_db_names = [self.db_names[i] for i in np.where(sim_scores>self.topic_sim_th)[0]]
        row_sims = []
        for _, row in self.dataset.iterrows():
            if row["db_id"] in related_db_names:
                select_decoded = decode_sql.decode_select(row["sql"], self.tables[row["db_id"]])
                select_ents = decode_sql.extract_select_names(select_decoded)
                # calculate similarity between select items and select cols
                row_sim = self.cal_cosine_sim(self.search_cols, select_ents)
                row_sims.append(np.max(row_sim, axis=1))
        db_df_bin = pd.DataFrame(np.where(np.array(row_sims)>self.item_sim, 1, 0), columns=self.search_cols)
        sim_sum = [sum(db_df_bin[col]) for col in db_df_bin.columns]
        db_df_bin = db_df_bin[db_df_bin.columns[(-np.array(sim_sum)).argsort()]]
        return db_df_bin

    def get_freq_combo(self, df):
        # input: dataframe (m * n) => binary values
        # output: frequent combo => columns: support, itemsets
        freq_combo = fpmax(df, min_support=self.item_sim, use_colnames=True)\
            .sort_values("support", ascending=False).reset_index(drop=True)
        return freq_combo

    def query_suggestion(self, db_df_bin, contexts=[], top_n = 3):
        # freq_combo = self.get_freq_combo(db_df_bin)
        columns = db_df_bin.columns
        rest_cols = columns.difference(np.concatenate(contexts))
        print(rest_cols)
        all_sims = np.zeros(len(rest_cols))
        for contextid, context in enumerate(contexts):
            sim_scores = np.max(self.cal_cosine_sim(rest_cols, context), axis=1) * math.pow(self.alpha, len(contexts) - contextid - 1)
            all_sims += sim_scores
        all_sims /= len(contexts)
        # TODO: consider cosine similarity between feature vectors (relevance vector to the database)
        return rest_cols[(-all_sims).argsort()[:top_n]]



if __name__ == "__main__":
    qr = queryRecommender(test_table_cols)
    db_bin = qr.search_sim_dbs(test_topic.replace("_"," ").strip())
    freq_combo = qr.get_freq_combo(db_bin)
    select_items = [list(freq_combo.iloc[0]["itemsets"]), list(freq_combo.iloc[1]["itemsets"])]
    next_cols = qr.query_suggestion(db_bin, select_items)
    print(next_cols)
