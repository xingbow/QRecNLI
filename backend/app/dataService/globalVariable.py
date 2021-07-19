# Global variables
# ##############################
import os

test = os.getcwd()

_current_dir = os.path.dirname(os.path.abspath(__file__))

# data folder
DATA_FOLDER = os.path.join(_current_dir, '../data/')
SPIDER_FOLDER = os.path.join(DATA_FOLDER, "dataset/spider")
NVBENCH_FOLDER = os.path.join(DATA_FOLDER, "dataset/nvBench")

# model folder
MODEL_FOLDER = os.path.join(DATA_FOLDER, 'model')
SMBOP_PATH = os.path.join(DATA_FOLDER, 'model/smbop.tar.gz')
SMBOP_FOLDER = os.path.join(MODEL_FOLDER, "SmBop")
