import json
import os
import logging
import pandas as pd
from time import time
from sql_metadata import Parser

from flask import Blueprint, current_app, request, jsonify
from app.dataService.utils import processSQL
import numpy as np

LOG = logging.getLogger(__name__)

api = Blueprint('api', __name__)


@api.route('/')
def index():
    print('main url!')
    return json.dumps('/')


@api.route('/initialization/<dataset>')
def initialization(dataset):
    if dataset == "spider":
        db_lists = current_app.dataService.db_lists
        return jsonify(db_lists)
    else:
        raise Exception("currently only support spider dataset")


@api.route("/get_tables/<db_id>")
def get_tables(db_id):
    # TODO: initialize the query context when the db is (re)selected
    current_app.dataService.init_query_context(db_id)
    print("query cache init.")
    return jsonify(current_app.dataService.get_tables(db_id))


@api.route("/get_database_meta/<db_id>")
def get_database_meta(db_id):
    return jsonify(current_app.dataService.get_db_info(db_id))


@api.route("/load_tables/<table_name>")
def load_tables(table_name):
    return jsonify(current_app.dataService.load_table_content(table_name))


# @api.route("/text2sql/<user_text>/<db_id>", methods=['GET'])
# def text2sql(user_text="films and film prices that cost below 10 dollars", db_id="cinema"):
@api.route("/text2sql", methods=['POST'])
def text2sql():
    text2sql_data = request.json
    user_text = text2sql_data["user_text"]
    db_id = text2sql_data["db_id"]
    sql = current_app.dataService.text2sql(user_text, db_id)
    sql = sql.replace("\n", "\n ")
    print(f"sql: {sql}")
    current_app.dataService.set_query_context(sql, db_id)  # set query context
    result = {'sql': sql, 'data': current_app.dataService.sql2data(sql, db_id).values.tolist()}
    print("text2sql: ", result)
    return jsonify(result)


@api.route("/sql2vis/<sql_text>/<db_id>", methods=['GET'])
def sql2vis(sql_text, db_id="cinema"):
    response = current_app.dataService.sql2vl(sql_text, db_id, return_data=True)
    data = response['data'].to_dict('records')
    content = response['vl']
    if isinstance(content, list):
        # TODO: vega-vue only supports the following mark types
        content = [s for s in content if s['mark']['type'] in
                   ["bar", "circle", "square", "tick", "line", "area", "point", "rule", "text"]]
        returnType = 'vega-lite'
    elif isinstance(content, pd.DataFrame):
        content = content.to_dict('records')
        returnType = 'table'
    else:
        if isinstance(content, np.integer):
            content = int(content)
        if isinstance(content, np.floating):
            content = float(content)
        if isinstance(content, np.ndarray):
            content = content.tolist()
        returnType = 'data'

    return jsonify({'type': returnType, 'content': content, 'data': data})


@api.route("/sql2text/<sql_text>/<db_id>", methods=['GET'])
def sql2text(sql_text, db_id="cinema"):
    text = current_app.dataService.sql2nl(sql_text)
    return jsonify({'text': text, 'sqlDecoded': {}})
    # old version
    sql_parsed = current_app.dataService.parsesql(sql_text, db_id)
    sql_decoded = processSQL.decode_sql(sql_parsed["sql_parse"], sql_parsed["table"])
    text = processSQL.sql2text(sql_decoded)
    response = {'sqlDecoded': sql_decoded, 'text': text}
    return jsonify(response)


@api.route("/sql_sugg/<db_id>", methods=['GET'])
def sql_sugg(db_id):
    table_cols = current_app.dataService.get_db_cols(db_id)
    sugg = current_app.dataService.sql_suggest(db_id, table_cols)
    # print(f"sugg: {sugg}")
    return jsonify(sugg)


@api.route("/user_data", methods=['POST'])
def get_user_data():
    user_data = request.json
    # print(f"user_data: {user_data}")
    user_data_folder = current_app.dataService.global_variable.USER_DATA_FOLDER
    userid = user_data["userid"]
    username = user_data["username"]
    systype = user_data["systype"]
    timestamp = int(time())
    print(os.path.join(user_data_folder, f"{userid}-{username}-{systype}-{timestamp}.json"))
    with open(os.path.join(user_data_folder, f"{userid}-{username}-{systype}-{timestamp}.json"),
              "w") as f:
        json.dump(user_data, f)
    return jsonify("successfully save user data!")


if __name__ == '__main__':
    pass
