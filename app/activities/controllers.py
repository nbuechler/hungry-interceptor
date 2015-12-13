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

@activities.route('/<database>/public')
def get_public_activities(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_activities = remoteDB1.activities.find({'privacy': 1})
    else:
        database = 'default'
        all_activities = mongo3.db.activities.find({'privacy': 1})
    return render_template('activities.html',
        all_activities=all_activities, database=database)

@activities.route('/<database>/all')
def get_activities(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_activities = remoteDB1.activities.find({})
    else:
        database = 'default'
        all_activities = mongo3.db.activities.find({})
    return render_template('activities.html',
        all_activities=all_activities, database=database)

# This is the method that starts the processing of the activities, and it will change
# over time as I get better and think more about the dependecy structure.

@activities.route('/overview/<user>')
def process_activities_overview(user=None):
        cursor = mongo3.db.activities.find({"user": ObjectId(user)}) #works! React User id

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a list to hold the time counts (in seconds)
        importance_counts_dict = []
        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)

            # Append the second count to the second_counts_dict
            importance_counts_dict.append(json_dict.get('importance'))

            # Append the entire json_dict dictionary
            data_dict['data'].append(json_dict)

        main_return_dict['all'].append(data_dict) # last json dict, and needs refactoring
        main_return_dict['all'].append({'importanceCounts': importance_counts_dict})
        main_return_dict['all'].append({'description_primary': 'The activity information for every log you have written.'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Activity Summary'})

        return jsonify(**main_return_dict)
