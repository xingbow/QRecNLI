# -*- coding: UTF-8 -*-
from flask import Flask
from flask_cors import CORS
from app.dataService.dataService import DataService
from app.dataService.utils.helpers import NpEncoder

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.json_encoder = NpEncoder

# flask_cors: Cross Origin Resource Sharing (CORS), making cross-origin AJAX possible.
CORS(app)

dataService = DataService("spider")

from app.routes import index