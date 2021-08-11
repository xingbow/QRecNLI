'''
    The RESTful style api server
'''
from pprint import pprint

import json
import os
import re
import logging
import mimetypes

from flask import Blueprint, current_app, request, jsonify, Response
from app.dataService.utils import processSQL

LOG = logging.getLogger(__name__)

api = Blueprint('api', __name__)

MB = 1 << 20
BUFF_SIZE = 10 * MB


def partial_response(path, start, end=None):
    LOG.info('Requested: %s, %s', start, end)
    file_size = os.path.getsize(path)

    # Determine (end, length)
    if end is None:
        end = start + BUFF_SIZE - 1
    end = min(end, file_size - 1)
    end = min(end, start + BUFF_SIZE - 1)
    length = end - start + 1

    # Read file
    with open(path, 'rb') as fd:
        fd.seek(start)
        bytes = fd.read(length)
    assert len(bytes) == length

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    LOG.info('Response: %s', response)
    LOG.info('Response: %s', response.headers)
    return response


def get_range(request):
    range = request.headers.get('Range')
    LOG.info('Requested: %s', range)
    m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', range)
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None

# ################################################################################ route
@api.route('/')
def index():
    print('main url!')
    return json.dumps('/')
    # return render_template('index.html')


@api.route('/initialization/<dataset>')
def initialization(dataset):
    if dataset == "spider":
        db_lists = current_app.dataService.db_lists
        return json.dumps(db_lists)
    else:
        raise Exception("currently only support spider dataset")


@api.route("/get_tables/<db_id>")
def get_tables(db_id):
    return json.dumps(current_app.dataService.get_tables(db_id))


@api.route("/get_cols/<table_name>")
def get_cols(table_name):
    return json.dumps(current_app.dataService.get_cols(table_name))


@api.route("/load_tables/<table_name>")
def load_tables(table_name):
    return json.dumps(current_app.dataService.load_table_content(table_name))


@api.route("/text2sql/<user_text>/<db_id>", methods=['GET'])
def text2sql(user_text="films and film prices that cost below 10 dollars", db_id="cinema"):
    sql = current_app.dataService.text2sql(user_text, db_id)
    result = {'sql': sql}
    result['data'] = current_app.dataService.sql2data(sql, db_id).values.tolist()
    return json.dumps(result)


@api.route("/sql2vis/<sql_text>/<db_id>", methods=['GET'])
def sql2vis(sql_text, db_id="cinema"):
    specs = current_app.dataService.sql2vl(sql_text, db_id)
    # TODO: vega-vue only supports the following mark types
    specs = [s for s in specs if s['mark']['type'] in ["bar", "circle", "square", \
        "tick", "line", "area", "point", "rule", "text"]]
    return json.dumps(specs)


@api.route("/sql2text/<sql_text>/<db_id>", methods=['GET'])
def sql2text(sql_text, db_id="cinema"):
    print("sql_text", sql_text)
    sql_parsed = current_app.dataService.parsesql(sql_text, db_id)
    sql_decoded = processSQL.decode_sql(sql_parsed["sql_parse"], sql_parsed["table"])
    text = processSQL.sql2text(sql_decoded)
    return json.dumps(text)


if __name__ == '__main__':
    pass
