'''
    The RESTful style api server
'''
from pprint import pprint

from app import app
from app import dataService

import json
import os
import re
import logging
import mimetypes
import subprocess

from flask import send_file, request, jsonify, render_template, send_from_directory, Response

LOG = logging.getLogger(__name__)

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
@app.route('/')
def index():
    print('main url!')
    return json.dumps('/')
    # return render_template('index.html')


@app.route('/initialization/<dataset>')
def initialization(dataset):
    if dataset == "spider":
        db_lists = dataService.db_lists
        return json.dumps(db_lists)
    else:
        raise Exception("currently only support spider dataset")


@app.route("/get_tables/<db_id>")
def get_tables(db_id):
    return json.dumps(dataService.get_tables(db_id))


@app.route("/get_cols/<table_name>")
def get_cols(table_name):
    return json.dumps(dataService.get_cols(table_name))


@app.route("/load_tables/<table_name>")
def load_tables(table_name):
    return json.dumps(dataService.load_table_content(table_name))


@app.route("/text2sql/<user_text>/<db_id>")
def text2sql(user_text="films and film prices that cost below 10 dollars", db_id="cinema", execuate=True):
    sql = dataService.text2sql(user_text, db_id)
    result = {'sql': sql}
    if execuate:
        result['data'] = dataService.sql2data(sql, db_id).values.tolist()
    return json.dumps(result)


@app.route("/sql2vis/<sql_text>/<db_id>")
def sql2vis(sql, db_id="cinema"):
    specs = dataService.sql2vl(sql, db_id)
    return json.dumps(specs)

if __name__ == '__main__':
    pass
