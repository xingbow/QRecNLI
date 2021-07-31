import os
import sys
# import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
import torch
import pathlib
import numpy as np

try:
    import globalVariable as GV
except ImportError:
    import app.dataService.globalVariable as GV
sys.path.append(GV.SMBOP_FOLDER)

# allennlp
import torch
from allennlp.models.archival import Archive, load_archive, archive_model
from allennlp.data.vocabulary import Vocabulary
from allennlp.common import Params
from allennlp.models import Model
from allennlp.common.params import *
from allennlp.data import DatasetReader, Instance
from allennlp.predictors import Predictor

# smbop
from smbop.modules.relation_transformer import *
from smbop.models.smbop import SmbopParser
from smbop.modules.lxmert import LxmertCrossAttentionLayer
from smbop.dataset_readers.spider import SmbopSpiderDatasetReader
import smbop.utils.node_util as node_util

# process SQL
try:
    from utils.processSQL import process_sql
except ImportError:
    from app.dataService.utils.processSQL import process_sql

pathlib.Path(f"cache").mkdir(exist_ok=True)

class SQLParser(object):
    def __init__(self):
        self.db = GV.SPIDER_FOLDER
        self.db_schema, self.db_names, self.tables = process_sql.get_schemas_from_json(os.path.join(self.db, "tables.json"))
        
    def parse_sql(self, sql="SELECT name ,  country ,  age FROM singer group by country having count(*) > 2", db_id="concert_singer"):
        schema = self.db_schema[db_id]
        table = self.tables[db_id]
        schema = process_sql.Schema(schema, table)

        sql_label = process_sql.get_sql(schema, sql)
        # print("sql_label: {}".format(sql_label))
        return {"sql_parse": sql_label, "table": table}

class SmBop(object):
    def __init__(self):
        overrides = {
            "dataset_reader": {
                "tables_file": os.path.join(GV.SPIDER_FOLDER, "tables.json"),
                "dataset_path": os.path.join(GV.SPIDER_FOLDER, "database"),
            },
            "validation_dataset_reader": {
                "tables_file": os.path.join(GV.SPIDER_FOLDER, "tables.json"),
                "dataset_path": os.path.join(GV.SPIDER_FOLDER, "database"),
            }
        }
        self.predictor = Predictor.from_path(GV.SMBOP_PATH, cuda_device=-1, overrides=overrides)

    def predict(self, q, db_id):
        instance = self.predictor._dataset_reader.text_to_instance(utterance=q, db_id=db_id)
        self.predictor._dataset_reader.apply_token_indexers(instance)
        with torch.cuda.amp.autocast(enabled=True):
            out = self.predictor._model.forward_on_instances([instance])
            return out[0]["sql_list"]


if __name__=='__main__':
    # smbop = SmBop()
    # result = smbop.predict("films and film prices that cost below 10 dollars", "cinema")
    # print("result: {}".format(result))
    sp = SQLParser()
    sp.parse_sql()
