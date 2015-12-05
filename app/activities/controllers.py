from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.database import mongo1, mongo2, mongo3, remoteDB1

# mongo dependecies
from flask.ext.pymongo import ObjectId

# bson
import json
from bson import json_util

activities = Blueprint('activities', __name__)

@activities.route('/')
def tester():
    print(2+2)
    foo = mongo3.db.users
    print(foo)
    return 'Activities!'

# This is the method that starts the processing of the experiences, and it will change
# over time as I get better and think more about the dependecy structure.

@activities.route('/overview/<user>')
def process_activities_overview(user=None):
        cursor = mongo3.db.activities.find({"user": ObjectId('562d722a3f1f9f541814a3e8')}) #works! React User id

        main_return_dict = {'all' : []}
        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)
            main_return_dict['all'].append(json_dict)

        return jsonify(**main_return_dict)
