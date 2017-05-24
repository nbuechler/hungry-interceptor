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
import pymongo
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

def save_record(collection_name, data):

    try:
        affect_analysis.db.create_collection(collection_name)
    except Exception as e:
        pass

    collection = affect_analysis.db[collection_name]
    # TODO: Add the user (id/username) who ran this analysis
    print 'data'
    print data
    collection.insert(data)
    return "Success"


@nlp.route('/analyze_emotion_set/', methods=['POST'])
def analyze_emotion_set():

    data = request.get_json()
    endpoint = 'http://' + api_ip + ':' + port + '/helpers/analyze_emotion_set/' + data.get('emotion_set') + '/'
    r = requests.post(endpoint, json=data)

    # save content
    save_record('all_records', json.loads(r.content))
    # return content
    return jsonify(status="success", data=json.loads(r.content))

def get_total_analysis_count(collection):

    cursor = affect_analysis.db[collection].find().sort('_id', pymongo.DESCENDING); #find all
    data = {}
    data['corpus_length'] = cursor.count()

    return data

@nlp.route('/analyses/<collection>/<page>/<count_per_page>/', methods=['GET'])
def retrieve_all_run_analyses(collection=None, page=None, count_per_page=None):

    x = (int(page) - 1) * int(count_per_page)
    y = int(page) * int(count_per_page)

    cursor = affect_analysis.db[collection].find().sort('_id', pymongo.DESCENDING); #find all
    data = []
    for i in cursor[x:y]:
        truncated_emotion_set = []
        for affect in i['emotion_set']:
            truncated_emotion_set.append({
                "emotion": affect['emotion'],
                "normalized_r_score": affect['normalized_r_score'],
            })
        # Improve run time by only returning back a subset of the emotion_set scoring
        i['emotion_set'] = truncated_emotion_set
        # Return back only the first 100 at most characters
        if len(i['doc']) > 400:
            i['doc'] = i['doc'][0:400] + '...'
        data.append(i)

    total_analyses = get_total_analysis_count(collection)['corpus_length']

    # TODO: Fix the janky dumps loads syntax for the data here
    return jsonify(
                status="success",
                stats='stats',
                total_analyses=total_analyses,
                count_per_page=count_per_page,
                data=json.loads(json.dumps(data, default=json_util.default)),
                )

@nlp.route('/analyses/<collection>/stats/', methods=['GET'])
def retrieve_all_run_analyses_statistics(collection=None):

    data = get_total_analysis_count(collection)

    return jsonify(
                status="success",
                data=json.loads(json.dumps(data, default=json_util.default)),
                )
