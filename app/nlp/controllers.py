from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify, request

import requests, operator, math, json, csv, os

from datetime import datetime

#databases
from config.databases import (mongo1,
                              mongo2,
                              mongo3,
                              remoteDB1,
                              secure_graph1,
                              affect_analysis)

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
def save_record(collection_name, data):

    try:
        affect_analysis.db.create_collection(collection_name)
    except Exception as e:
        pass

    collection = affect_analysis.db[collection_name]
    # TODO: Add the user (id/username) who ran this analysis
    collection.insert(data)
    return "Success"


@nlp.route('/analyze_emotion_set/', methods=['POST'])
def analyze_emotion_set(database=None):

    data = json.loads(request.get_json())
    endpoint = 'http://' + api_ip + ':' + port + '/helpers/analyze_emotion_set/' + data.get('emotion_set') + '/'
    r = requests.post(endpoint, json=data)

    # save content
    save_record('all_records', json.loads(r.content))
    # return content
    return jsonify(status="success", data=json.loads(r.content))
