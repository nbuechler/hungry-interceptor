from flask import Flask
from flask import render_template, redirect, url_for, jsonify


# bson
import json
from bson import json_util

# mongo dependecies
from flask.ext.pymongo import ObjectId

# CORS dependecies
from flask.ext.cors import CORS

#databases
# from config.database import mongo1, mongo2, mongo3, remoteDB1

# mongo dependecies
# from flask.ext.pymongo import ObjectId

# bson
import json
from bson import json_util

app = Flask(__name__)

#CORS instance
cors = CORS(app, resources={r"/*": {"origins": "*"}}) #CORS :WARNING everything!


#TODO: List out more apis for specific calls I need
@app.route('/')
def home_page():
    return 'hello world'

@app.route('/secret')
def secret_page():
    return 'shhh..this is a secret'




@app.route('/<database>/experiences/public')
def get_public_experiences(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_experiences = remoteDB1.experiences.find({'privacy': 1})
    else:
        database = 'default'
        all_experiences = mongo3.db.experiences.find({'privacy': 1})
    return render_template('experiences.html',
        all_experiences=all_experiences, database=database)


@app.route('/<database>/experiences')
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

@app.route('/process-experiences-overview/<user>')
def process_experiences_overview(user=None):
        cursor = mongo3.db.experiences.find({"user": ObjectId('562d722a3f1f9f541814a3e8')}) #works! React User id

        main_return_dict = {'all' : []}
        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)
            main_return_dict['all'].append(json_dict)

        return jsonify(**main_return_dict)

# This is the method that starts the processing of the experiences, and it will change
# over time as I get better and think more about the dependecy structure.

@app.route('/process-activities-overview/<user>')
def process_activities_overview(user=None):
        cursor = mongo3.db.activities.find({"user": ObjectId('562d722a3f1f9f541814a3e8')}) #works! React User id

        main_return_dict = {'all' : []}
        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)
            main_return_dict['all'].append(json_dict)

        return jsonify(**main_return_dict)

@app.route('/dummyold')
def get_all_dummy():
    allOfIt = dict(
    {'all' : [
        {'pies': [
                  {'key': 'P1', 'data': [2, 4, 5, 4, 7]},
                  {'key': 'P2', 'data': [3, 2, 9, 1, 8]},
                  {'key': 'P3', 'data': [3, 4, 0, 7, 8]},
                  {'key': 'P4', 'data': [3, 5, 5, 0, 4]},
                  {'key': 'P5', 'data': [3, 8, 3, 2, 3]}
                ]},
        {'logCounts': [14, 23, 22, 14, 30]},
        {'description_primary': 'The main desciption is going to detail that this is one view of the data'},
        {'description_secondary': 'The secondary description is going to detail that this is really a lot more information'},
        {'title': 'Something'}
    ]})

    return jsonify(**allOfIt)

@app.route('/altdummy')
def get_all_altdummy():
    allOfIt = dict(
    {'all' : [
        {'pies': [
                  {'key': 'P1', 'data': [6, 5, 8, 8, 7]},
                  {'key': 'P2', 'data': [3, 6, 9, 1, 8]},
                  {'key': 'P3', 'data': [3, 0, 8, 6, 3]},
                  {'key': 'P4', 'data': [3, 5, 5, 0, 4]},
                  {'key': 'P5', 'data': [8, 0, 3, 5, 6]}
                ]},
        {'logCounts': [14, 23, 22, 14, 30]},
        {'description_primary': 'The main desciption --- look it is different!'},
        {'description_secondary': 'The secondary description --- look at the data below, it should be, too!'},
        {'title': 'Something'}
    ]})

    return jsonify(**allOfIt)

# if __name__ == '__main__':
    # app.run()
    # app.run(debug=True)
