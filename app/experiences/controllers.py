from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.database import mongo1, mongo2, mongo3, remoteDB1

# mongo dependecies
from flask.ext.pymongo import ObjectId

# bson
import json
from bson import json_util

experiences = Blueprint('experiences', __name__)

@experiences.route('/')
def tester():
    return 'Experiences!'

@experiences.route('/<database>/public')
def get_public_experiences(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_experiences = remoteDB1.experiences.find({'privacy': 1})
    else:
        database = 'default'
        all_experiences = mongo3.db.experiences.find({'privacy': 1})
    return render_template('experiences.html',
        all_experiences=all_experiences, database=database)


@experiences.route('/<database>/all')
def get_experiences(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_experiences = remoteDB1.experiences.find({})
    else:
        database = 'default'
        all_experiences = mongo3.db.experiences.find({})
    return render_template('experiences.html',
        all_experiences=all_experiences, database=database)

# This is the method that starts the processing of the experiences, and it will change
# over time as I get better and think more about the dependecy structure.

@experiences.route('/overview/<user>')
def process_experiences_overview(user=None):
        cursor = mongo3.db.experiences.find({"user": ObjectId('562d722a3f1f9f541814a3e8')}) #works! React User id

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        main_return_dict = {'all' : []}
        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)
            data_dict['data'].append(json_dict)
            
        main_return_dict['all'].append(data_dict) # last json dict, and needs refactoring
        main_return_dict['all'].append({'another_data': 'No Data'})
        main_return_dict['all'].append({'description_primary': 'The experience information for every log you have written.'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Experience Summary'})

        return jsonify(**main_return_dict)
