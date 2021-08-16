import re
import sqlparse
import json
import numpy as np

from datetime import date, datetime
from flask.json import JSONDecoder

try:
    from app.dataService.utils import constants
    from app.dataService.utils.processSQL import select_unit2text
except ImportError:
    from utils import constants
    from utils.processSQL import select_unit2text




# Copied from NL4DV
def isfloat(datum):
    try:
        if datum == '' or str(datum).isspace():
            return False
        float(datum)
    except AttributeError:
        return False
    except ValueError:
        return False
    except OverflowError:
        return False
    return True


# Copied from NL4DV
def isint(datum):
    try:
        if datum == '' or str(datum).isspace():
            return False
        a = float(datum)
        b = int(a)
    except AttributeError:
        return False
    except ValueError:
        return False
    except OverflowError:
        return False
    return a == b


# Copied from NL4DV
def isdate(datum):
    try:
        if datum == '' or str(datum).isspace():
            return False, None

        for idx, regex_list in enumerate(constants.date_regexes):
            regex = re.compile(regex_list[1])
            match = regex.match(str(datum))
            if match is not None:
                dateobj = dict()
                dateobj["regex_id"] = idx
                dateobj["regex_matches"] = list(match.groups())
                return True, dateobj

    except Exception as e:
        pass

    return False, None


def get_attr_datatype_shorthand(data_types):
    # Attribute-Datatype pair
    unsorted_attr_datatype = [(attr, attr_type) for attr, attr_type in data_types.items()]

    # Since the `vis_combo` mapping keys are in a specific order [Q,N,O,T],
    # we will order the list of attributes in this order
    default_sort_order = ['Q', 'N', 'O', 'T']
    sorted_attr_datatype = [(attr, attr_type) for x in default_sort_order for (attr, attr_type) in
                            unsorted_attr_datatype if attr_type == x]

    sorted_attributes = [x[0] for x in sorted_attr_datatype]
    # e.g. ['Rotten Tomatoes Rating', 'Worldwide Gross']
    sorted_attribute_datatypes = ''.join([x[1] for x in sorted_attr_datatype])  # e.g. 'QQ'

    return sorted_attributes, sorted_attribute_datatypes


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, (date, datetime)):
            return obj.strftime("%Y/%m/%d")
        return json.JSONEncoder.default(self, obj)


# -------------------------------------New Edition---------------------------------------

def is_numeric(obj):
    attrs = ['__add__', '__sub__', '__mul__', '__truediv__', '__pow__']
    return all(hasattr(obj, attr) for attr in attrs)


def get_sql_identifiers(select_decoded):
    return [select_unit2text(select_unit, with_style=False) for select_unit in select_decoded[1]]


# TODO: this function cannot distinguish between O(rdinal) and Q(uantitative)
def get_attr_type(data):
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("SQL returns should be a non-empty list.")
    if all([is_numeric(datum) for datum in data]):
        return "Q"  # Q is for Quantitive
    elif all([isdate(datum)[0] for datum in data]):
        return "T"  # T is for Time
    else:
        return "N"  # N is for Nominal


# From https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not
# -json-serializable
class NpEncoder(JSONDecoder):
    def default(self, obj, **kwargs):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.datetime64):
            return str(obj)
        else:
            return super(NpEncoder, self).default(obj, **kwargs)
