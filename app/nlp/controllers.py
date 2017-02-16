from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify, request

import requests, operator, math, json, csv, os

from datetime import datetime

#databases
from config.databases import mongo1, mongo2, mongo3, remoteDB1, secure_graph1

# mongo dependecies
from flask.ext.pymongo import ObjectId

# bson
import json
from bson import json_util

utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
utc_datetime = datetime.utcnow()
api_ip = '0.0.0.0'
port = '7000'

nlp = Blueprint('nlp', __name__)

@nlp.route('/')
def tester():
    return 'nlp!'

@nlp.route('/<database>/save/')
def save_record(database=None):
    # TODO: Add logic to save a record
    return "Not Implemented"

@nlp.route('/analyze_emotion_set/big_6/', methods=['POST'])
def analyze_emotion_set(database=None):

    request_body = {
      "doc": " Sadness is an emotional pain associated with, or characterized by, feelings of disadvantage, loss, despair, grief, helplessness, disappointment and sorrow. An individual experiencing sadness may become quiet or lethargic, and withdraw themselves from others. An example of severe sadness is depression. Crying is often an indication of sadness",
      "lang": "english",
      "natural": "1",
      "stemmer": "1",
      "lemma": "1",
      "ub": 2,
      "lb": 2
    }

    print request.get_json()

    data = request_body
    endpoint = 'http://' + api_ip + ':' + port + '/helpers/analyze_emotion_set/big_6/'
    r = requests.post(endpoint, json=data)
    # return jsonify(r.content)
    return jsonify(status="success", data=json.loads(r.content))
