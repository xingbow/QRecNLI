################################
# Copied from https://github.com/taoyds/spider/blob/7036cf422b1da08a907acbdc062e598bb0761bf7/process_sql.py
################################
# Assumptions:
#   1. sql is correct
#   2. only table name has alias
#   3. only one intersect/union/except
#
# val: number(float)/string(str)/sql(dict)
# col_unit: (agg_id, col_id, isDistinct(bool))
# val_unit: (unit_op, col_unit1, col_unit2)
# table_unit: (table_type, col_unit/sql)
# cond_unit: (not_op, op_id, val_unit, val1, val2)
# condition: [cond_unit1, 'and'/'or', cond_unit2, ...]
# sql {
#   'select': (isDistinct(bool), [(agg_id, val_unit), (agg_id, val_unit), ...])
#   'from': {'table_units': [table_unit1, table_unit2, ...], 'conds': condition}
#   'where': condition
#   'groupBy': [col_unit1, col_unit2, ...]
#   'orderBy': ('asc'/'desc', [val_unit1, val_unit2, ...])
#   'having': condition
#   'limit': None/limit value
#   'intersect': None/sql
#   'except': None/sql
#   'union': None/sql
# }
################################
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
import globalVariable as GV


def decode_val_unit(val_unit, table):
    # val_unit: (unit_op, col_unit1, col_unit2)
    unit_op = GV.UNIT_OPS[val_unit[0]]
    col_unit1 = val_unit[1]
    col_unit1_decoded = decode_col_unit(col_unit1, table)
    col_unit2 = val_unit[2]
    col_unit2_decoded = decode_col_unit(col_unit2, table)
    return (unit_op, col_unit1_decoded, col_unit2_decoded)


def decode_col_unit(col_unit, table):
    # col_unit: (agg_id, col_id, isDistinct(bool))
    if col_unit == None:
        return None
    else:
        agg_id = GV.AGG_OPS[col_unit[0]]
        col = table["column_names"][col_unit[1]]
        # TODO: handle * with from clause
        if col[1] != "*":
            col_name = table["table_names"][col[0]] + ": " + col[1]
        else:
            col_name = col[1]
        distinct_flag = "distinct" if col_unit[2] else ""
        return (agg_id, col_name, distinct_flag)


def decode_val(val, table):
    if isinstance(val, float) or isinstance(val, str):
        return val
    elif isinstance(val, dict):
        return decode_sql(val, table)


def decode_table_unit(table_unit, table):
    table_type = table_unit[0]
    if table_type == "table_unit":
        return (table_type, table["table_names"][table_unit[1]])
    elif table_type == "sql":
        return (table_type, decode_sql(table_unit[1], table))


def decode_condition(cond, table):
    if cond not in ["and", "or"] and len(cond) > 0:
        not_op = cond[0]
        op_id = GV.WHERE_OPS[cond[1]]
        val_unit = decode_val_unit(cond[2], table)
        val1 = decode_val(cond[3], table)
        val2 = decode_val(cond[4], table)
        # print(type(cond[3]), type(cond[4]), cond[3], cond[4])
        return (not_op, op_id, val_unit, val1, val2)
    else:
        return cond


def decode_from(from_data, table):
    table_units = from_data["table_units"]
    conds = from_data["conds"]
    table_units_decoded = [decode_table_unit(table_unit, table) for table_unit in table_units]
    return {
        "table_units": table_units_decoded,
        "conds": [decode_condition(cond, table) for cond in conds]
    }


def decode_select(sql_data, table, from_data=None):
    # NOTICE: here we use whole sql_data as input since * may be used in the select clause, 
    # we need from clause to identify the corresponding tables
    # 'select': (isDistinct(bool), [(agg_id, val_unit), (agg_id, val_unit), ...])
    distinct_flag = "distinct" if sql_data[0] else ""
    select_units = []
    for s in sql_data[1]:
        agg_id = GV.AGG_OPS[s[0]]
        u, col1, col2 = decode_val_unit(s[1], table)
        if from_data is not None:
            if col1[1] == "*":
                get_table_name = " ".join(
                    [t[1] for t in from_data["table_units"] if t[0] == "table_unit"])
                col1 = (col1[0], get_table_name + ": " + col1[1], col1[2])
            if col2 is not None:
                if col2[1] == "*":
                    get_table_name = " ".join(
                        [t[1] for t in from_data["table_units"] if t[0] == "table_unit"])
                    col2 = (col2[0], get_table_name + ": " + col2[1], col2[2])
        select_units.append((agg_id, (u, col1, col2)))
    return distinct_flag, select_units


def decode_where(where_data, table):
    if len(where_data) == 0:
        return []
    else:
        return [decode_condition(cond, table) for cond in where_data]


def decode_groupby(groupby_data, table):
    return [decode_col_unit(col_unit, table) for col_unit in groupby_data]


def decode_orderby(orderby_data, table):
    if len(orderby_data) > 0:
        order = orderby_data[0]
        val_units = [decode_val_unit(val_unit, table) for val_unit in orderby_data[1]]
        return (order, val_units)
    else:
        return []


def decode_having(having_data, table):
    if len(having_data) == 0:
        return []
    else:
        return [decode_condition(cond, table) for cond in having_data]


def decode_limit(limit_data, table):
    return limit_data


def decode_intersect(intersect_data, table):
    if intersect_data is None:
        return None
    else:
        return decode_sql(intersect_data, table)


def decode_except(except_data, table):
    if except_data is None:
        return None
    else:
        return decode_sql(except_data, table)


def decode_union(union_data, table):
    if union_data is None:
        return None
    else:
        return decode_sql(union_data, table)


def decode_sql(sql_data, table):
    from_data = decode_from(sql_data["from"], table)
    select_data = decode_select(sql_data["select"], table, from_data)
    where_data = decode_where(sql_data["where"], table)
    groupby_data = decode_groupby(sql_data["groupBy"], table)
    orderby_data = decode_orderby(sql_data["orderBy"], table)
    having_data = decode_having(sql_data["having"], table)
    limit_data = decode_limit(sql_data["limit"], table)
    intersect_data = decode_intersect(sql_data["intersect"], table)
    except_data = decode_except(sql_data["except"], table)
    union_data = decode_union(sql_data["union"], table)
    return {
        'select': select_data,
        "from": from_data,
        "where": where_data,
        "groupBy": groupby_data,
        "orderBy": orderby_data,
        "having": having_data,
        "limit": limit_data,
        "intersect": intersect_data,
        "except": except_data,
        "union": union_data
    }
