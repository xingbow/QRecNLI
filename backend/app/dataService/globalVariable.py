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

#################### Save user data
USER_DATA_FOLDER = os.path.join(DATA_FOLDER, 'user')
if not os.path.isdir(USER_DATA_FOLDER):
    os.mkdir(USER_DATA_FOLDER)

#################### SQL parser variables
split_symbol = " ; "
##### adopted from https://github.com/taoyds/spider/blob/88c04b7ee43a4cc58984369de7d8196f55a84fbf/process_sql.py
CLAUSE_KEYWORDS = ('select', 'from', 'where', 'group', 'order', 'limit', 'intersect', 'union', 'except')
JOIN_KEYWORDS = ('join', 'on', 'as')

WHERE_OPS = ('not', 'between', '=', '>', '<', '>=', '<=', '!=', 'in', 'like', 'is', 'exists')
UNIT_OPS = ('none', '-', '+', "*", '/')
AGG_OPS = ('none', 'max', 'min', 'count', 'sum', 'avg')
TABLE_TYPE = {
    'sql': "sql",
    'table_unit': "table_unit",
}

COND_OPS = ('and', 'or')
SQL_OPS = ('intersect', 'union', 'except')
ORDER_OPS = ('desc', 'asc')

#################### SQL2NL model config
SQL2NL_MODEL_NAME = "hkunlp/from_all_T5_base_prefix_sql2text2"
SQL2NL_MODEL_FOLDER = os.path.abspath(os.path.join(MODEL_FOLDER, "UnifiedSKG"))
SQL2NL_MODEL_CONFIG_PATH = os.path.abspath(os.path.join(SQL2NL_MODEL_FOLDER, "configure/Salesforce/T5_base_prefix_sql2text.cfg"))


##################
### test case for query suggestion
# test_topic = "employee_hire_evaluation"
# test_table_cols = ['employee: employee id',
#                    'employee: name',
#                    'employee: age',
#                    'employee: city',
#                    'shop: shop id',
#                    'shop: name',
#                    'shop: location',
#                    'shop: district',
#                    'shop: number products',
#                    'shop: manager name',
#                    'hiring: shop id',
#                    'hiring: employee id',
#                    'hiring: start from',
#                    'hiring: is full time',
#                    'evaluation: employee id',
#                    'evaluation: year awarded',
#                    'evaluation: bonus',
#                    'employee: *',
#                    'shop: *',
#                    'hiring: *',
#                    'evaluation: *']

############
# test_topic = "cinema"
# test_table_cols = ['film: rank in series', 'film: number in season', 
# 'film: title', 'film: directed by', 'film: original air date', 'film: production code', 
# 'cinema: name', 'cinema: openning year', 'cinema: capacity', 
# 'cinema: location', 'schedule: date', 
# 'schedule: show times per day', 'schedule: price']

############
test_topic = "customers_and_addresses"
test_table_cols = ['addresses: address content', 'addresses: city', 'addresses: zip postcode', 
'addresses: state province county', 'addresses: country', 'addresses: other address details', 
'products: product details', 'customers: payment method', 'customers: customer name', 
'customers: date became customer', 'customers: other customer details', 'customer addresses: date address from', 
'customer addresses: address type', 'customer addresses: date address to', 'customer contact channels: channel code', 
'customer contact channels: active from date', 'customer contact channels: active to date', 'customer contact channels: contact number', 
'customer orders: order status', 'customer orders: order date', 'customer orders: order details', 'order items: order quantity']
col_combo = [{'products: product details', 'order items: order quantity'}]

opt_constraints = ['addresses: address content', 'addresses: city', 'addresses: zip postcode', 
'addresses: state province county', 'addresses: country', 'addresses: other address details', 
'products: product details', 'customers: payment method', 'customers: customer name', 
'customers: date became customer', 'customers: other customer details', 'customer addresses: date address from', 
'customer addresses: address type', 'customer addresses: date address to', 'customer contact channels: channel code', 
'customer contact channels: active from date', 'customer contact channels: active to date', 'customer contact channels: contact number', 
'customer orders: order status', 'customer orders: order date', 'customer orders: order details']


