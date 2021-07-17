# Global variables
# ##############################
import os

test = os.getcwd()

_current_dir = os.path.dirname(os.path.abspath(__file__))

# data folder
DATA_FOLDER = os.path.join(_current_dir, '../data/')  