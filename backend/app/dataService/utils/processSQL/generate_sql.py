
agg_opts_to_nl = {
    'max': "the maximum of ", 
    'min': "the mininum of ", 
    'count': "the number of ", 
    'sum': "the sum of ", 
    'avg': "the average of "
}

def compile_select_from(s, db_meta):
    table_names = db_meta["table_names"]
    table_names_original = db_meta["table_names_original"]

    table_l = [] # table name list
    sel_l = [] # select enetity list
    
    for s_el in s:
        # table name checking
        s_table = s_el.split(":")[0].strip()
        s_table_idx = table_names.index(s_table)
        s_table_name = table_names_original[s_table_idx]
        if s_table_name not in table_l:
            table_l.append(s_table_name)
        # column name checking
        s_col = s_el.split(":")[1].strip()
        s_col_name = "*"
        if s_col != "*":
            for cidx, c in enumerate(db_meta["column_names"]):
                if c[0] == s_table_idx and c[1] == s_col:
                    s_col_name = db_meta["column_names_original"][cidx][1]
        cur_sel = s_table_name + "." + s_col_name
        sel_l.append(cur_sel)
    
    #### forerign keys
    # TODO: optimize `join` operations
    fks = db_meta["foreign_keys"]

    for fk in fks:
        fk0 = fk[0]
        fk1 = fk[1]
        table0 = table_names_original[db_meta["column_names_original"][fk0][0]]
        colname0 = db_meta["column_names_original"][fk0][1]
        table1 = table_names_original[db_meta["column_names_original"][fk1][0]]
        colname1 = db_meta["column_names_original"][fk1][1]
        print(table0, colname0)
        print(table1, colname1)
        if set([table0, table1]).issubset(set(table_l)):
            print("table0, table1: ", table0, table1)

    return


def compile_nl_from_sql_parts(s, g, a):
    """
    generate sql based on sql suggestions
    - input: 
        - s: `select` entities
        - g: `groupby` entities
        - a: `agg` {operation: [entities]}
    - output: nl (str)
    """
    s_set = set(s)
    opt_nls = []
    # print("s_set (before): ", s_set)
    for opt in a.keys():
        for ent in a[opt]:
            s_set.discard(ent)
        opt_nl = [agg_opts_to_nl[opt] + ent.split(":")[1] + " of " + ent.split(":")[0] for ent in a[opt]]
        opt_nls.extend(opt_nl)
    # print(opt_nls)
    # sel_nl_l = [ent.replace(":", "") for ent in list(s_set)] + opt_nls
    sel_nl_l = [ent.split(":")[1] + " of " + ent.split(":")[0] for ent in list(s_set)] + opt_nls
    sel_nl = "Find " + (", ".join(sel_nl_l)).strip()
    if len(g) > 0:
        g_nl = " of " + (", ".join(["each " + ent.replace(":", "") for ent in g])).strip()
    # print(sel_nl + g_nl)
        return sel_nl + g_nl
    else:
        return sel_nl


def compile_sql(nl_dict):
    """
    generate sql based on sql suggestions
    - input: 
        - nl_dict {"select": [], "groupby": [], "agg": [] }
        - db_meta {}, keys: ['column_names', 'column_names_original', 'column_types', 
        'db_id', 'foreign_keys', 'primary_keys', 'table_names', 'table_names_original']
    - output: sql (str)
    """
    # print(db_meta.keys())
    select = nl_dict["select"]
    groupby = nl_dict["groupby"]
    agg = nl_dict["agg"]

    nls = []
    for s, g, a in zip(select, groupby, agg):
        # print(s, g, a)
        nl = compile_nl_from_sql_parts(s, g, a)
        nls.append(nl)
    # print(len(nls))
    # print(nls)
    return nls
