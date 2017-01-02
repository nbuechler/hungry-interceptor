from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.databases import mongo1, mongo2, mongo3, remoteDB1, secure_graph1

# mongo dependecies
from flask.ext.pymongo import ObjectId

# bson
import json
from bson import json_util

nlp = Blueprint('nlp', __name__)

@nlp.route('/')
def tester():
    return 'nlp!'

@nlp.route('/<database>/save/')
def save_record(database=None):
    # TODO: Add logic to save a record
    return "Not Implemented"
