#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from app import app
from app.routes.app import create_app
from gevent.pywsgi import WSGIServer

app = create_app()

http_server = WSGIServer(('0.0.0.0', 5012), app)
http_server.serve_forever()
