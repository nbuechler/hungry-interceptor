from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.database import mongo1, mongo2, mongo3, remoteDB1

# mongo dependecies
from flask.ext.pymongo import ObjectId

# bson
import json
from bson import json_util

logs = Blueprint('logs', __name__)

@logs.route('/')
def tester():
    return 'Logs!'
