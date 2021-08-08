agg_dict = {
    'none': '',
    'max': 'the maximum of ',
    'min': 'the minimum of ',
    'count': 'the number of ',
    'sum': 'the sum of ',
    'avg': 'the average number of '
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


def col_id2text(col_id, agg_id=None):
    col_text = col_id.replace(':', '\'s')
    if agg_id == 'count' and '*' in col_text:
        col_text = col_text.replace('*', 'entries')
    else:
        col_text = col_text.replace('*', 'all information')
    return col_text


def col_unit2text(col_unit):
    if is_none(col_unit):
        return ''
    agg_id, col_id, isDistinct = col_unit
    # TODO: isDistinct is ignored
    return agg_dict[agg_id]+col_id2text(col_id, agg_id)


def val_unit2text(val_unit):
    if is_none(val_unit):
        return ''
    unit_op, col_unit1, col_unit2 = val_unit
    if is_none(unit_op):
        return col_unit2text(col_unit1)
    else:
        return col_unit2text(col_unit1)+" {} ".format(unit_op)+col_unit2text(col_unit2)


def cond_unit2text(cond_unit):
    if is_none(cond_unit):
        return ''
    not_op, op_id, val_unit, val1, val2 = cond_unit
    not_text = " not " if is_none(not_op) else ''
    val2_text = "" if is_none(val2) else ' and {}'.format(val2)
    return "{}{} {} {}{}".format(val_unit2text(val_unit), not_text,
                                 where_dict[op_id], val1, val2_text)


def where2text(condition):
    where_sentence = ""
    for i, cond_unit in enumerate(condition):
        if i % 2 == 1:
            where_sentence += " {} ".format(cond_unit)
        else:
            where_sentence += cond_unit2text(cond_unit)
    return where_sentence


def select_unit2text(select_unit):
    if is_none(select_unit):
        return ''
    agg_id, val_unit = select_unit
    return "{}{}".format(agg_dict[agg_id], val_unit2text(val_unit))


def select2text(select):
    return ', '.join([select_unit2text(select_unit) for select_unit in select[1]])


def sql2text(decoded_sql):
    select_sentence = select2text(decoded_sql["select"])
    where_sentence = where2text(decoded_sql["where"])
    if where_sentence == "":
        sentence = "Find {}.".format(select_sentence)
    else:
        sentence = "Find {} where {}.".format(select_sentence, where_sentence)
    return sentence

