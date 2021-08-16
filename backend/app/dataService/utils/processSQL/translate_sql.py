agg_dict = {
    'none': '',
    'max': 'the maximum of ',
    'min': 'the minimum of ',
    'count': 'the number of ',
    'sum': 'the sum of ',
    'avg': 'the average of '
}


where_dict = {
    '=': 'equals to',
    '>': 'is larger than',
    '<': 'is smaller than',
    '>=': 'is larger than or equals to',
    '<=': 'is smaller than or equals to',
    '!=': 'not equals to',
    'between': 'is between',
    'where': 'where',
    'in': 'in',
    'like': 'like',
    'is': 'is',
    'exists': 'exists',
}


def is_none(token):
    return token is None or token == 'none' or token == ''


def col_id2text(col_id, with_style=True):
    table_id = col_id.split(': ')[0]
    real_col_id = col_id.split(': ')[1]
    if real_col_id == '*':
        real_col_id = 'all information'
    if with_style:
        text = '<span class="entity-id">{}</span>\'s \
            <span class="column-id">{}</span>'.format(table_id, real_col_id)
    else:
        text = '{}\'s {}'.format(table_id, real_col_id)
    return text


def col_unit2text(col_unit, with_style=True):
    if is_none(col_unit):
        return ''
    agg_id, col_id, isDistinct = col_unit
    # TODO: isDistinct is ignored
    return agg_dict[agg_id]+col_id2text(col_id, with_style)


def val_unit2text(val_unit, with_style=True):
    if is_none(val_unit):
        return ''
    unit_op, col_unit1, col_unit2 = val_unit
    if is_none(unit_op):
        return col_unit2text(col_unit1, with_style)
    else:
        return col_unit2text(col_unit1, with_style)+\
            " {} ".format(unit_op)+col_unit2text(col_unit2, with_style)


def cond_unit2text(cond_unit, with_style=True):
    if is_none(cond_unit):
        return ''
    not_op, op_id, val_unit, val1, val2 = cond_unit
    not_text = " not " if is_none(not_op) else ''
    val2_text = "" if is_none(val2) else ' and {}'.format(val2)
    return "{}{} {} {}{}".format(val_unit2text(val_unit, with_style), not_text,
                                 where_dict[op_id], val1, val2_text)


def where2text(condition, with_style=True):
    where_sentence = ""
    for i, cond_unit in enumerate(condition):
        if i % 2 == 1:
            where_sentence += " {} ".format(cond_unit)
        else:
            where_sentence += cond_unit2text(cond_unit, with_style)
    return where_sentence


def select_unit2text(select_unit, with_style=True):
    if is_none(select_unit):
        return ''
    agg_id, val_unit = select_unit
    return "{}{}".format(agg_dict[agg_id], val_unit2text(val_unit, with_style))


def select2text(select, with_style=True):
    return ', '.join([select_unit2text(select_unit, with_style) \
        for select_unit in select[1]])


def sql2text(decoded_sql, with_style=True):
    select_sentence = select2text(decoded_sql["select"], with_style)
    where_sentence = where2text(decoded_sql["where"], with_style)
    if where_sentence == "":
        sentence = "Find {}.".format(select_sentence)
    else:
        sentence = "Find {} where {}.".format(select_sentence, where_sentence)
    return sentence
