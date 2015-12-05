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

@app.route('/<database>/logs')
def get_logs(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_logs = remoteDB1.logs.find({})
    else:
        database = 'default'
        all_logs = mongo3.db.logs.find({})
    return render_template('logs.html',
        all_logs=all_logs, database=database)

# This is the method that starts the processing of the logs, and it will change
# over time as I get better and think more about the dependecy structure.

# The general gist od this is that the logs should be processed like the dummy
# example below so that another service can use this method as a sevice.

# The cursor object gets turned into a json which then in turn gets made into a
# a python dictionary. Then processing can happen on it and be returned ultimately
# --> like so:    return jsonify(**allOfIt)


@app.route('/process-logs-overview/<user>')
def process_logs_overview(user=None):
    if user:
        # Make it take a user id dynamically
        # https://api.mongodb.org/python/current/tutorial.html
        # cursor = mongo3.db.logs.find({"user": ObjectId('562d722a3f1f9f541814a3e8')}) #works! React User id
        cursor = mongo3.db.logs.find({"user": ObjectId(user)}) #works! React User id

        # Create a pie dictionary to set up the building of data intended for pie charts.
        pie_dict = {'pies': []}
        # Create counters for the total lengths of word_arrays
        physicArrayTotal = 0
        emotionArrayTotal = 0
        academicArrayTotal = 0
        communeArrayTotal = 0
        etherArrayTotal = 0
        # Create a main dictionary for the response
        main_return_dict = {'all' : []}

        # http://stackoverflow.com/questions/11280382/python-mongodb-pymongo-json-encoding-and-decoding
        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)
            # Define the json key for the array to hold the
            json_key = json_dict.get('_id').get('$oid')
            # Create an empty array to hold the data I care about, in this case
            # the data is an array of five numbers for each json_dict, the word_array lengths (words)
            word_array_lengths = []
            if json_dict.get('physicArrayLength') > 0:
                word_array_lengths.append(json_dict.get('physicArrayLength'))
            else:
                word_array_lengths.append(0)
            if json_dict.get('emotionArrayLength') > 0:
                word_array_lengths.append(json_dict.get('emotionArrayLength'))
            else:
                word_array_lengths.append(0)
            if json_dict.get('academicArrayLength') > 0:
                word_array_lengths.append(json_dict.get('academicArrayLength'))
            else:
                word_array_lengths.append(0)
            if json_dict.get('communeArrayLength') > 0:
                word_array_lengths.append(json_dict.get('communeArrayLength'))
            else:
                word_array_lengths.append(0)
            if json_dict.get('etherArrayLength') > 0:
                word_array_lengths.append(json_dict.get('etherArrayLength'))
            else:
                word_array_lengths.append(0)
            # Get the content for each of the word array values, and order it correctly in the array
            word_array_contents = []
            word_array_contents.append(json_dict.get('physicContent'))
            word_array_contents.append(json_dict.get('emotionContent'))
            word_array_contents.append(json_dict.get('academicContent'))
            word_array_contents.append(json_dict.get('communeContent'))
            word_array_contents.append(json_dict.get('etherContent'))
            # Assemble a pie_instance_dict
            pie_instance_dict = {
                                'key': json_key,
                                'data': word_array_lengths,
                                'values': word_array_contents,
                                'name': json_dict.get('name')
                                }
            # Assembled pie_instance_dict now gets appended to the end of pies in pie_dict
            pie_dict['pies'].append(pie_instance_dict)
            # Remember, we are also counting the total lengths
            if json_dict.get('physicArrayLength') > 0:
                physicArrayTotal += json_dict.get('physicArrayLength')
            if json_dict.get('emotionArrayLength') > 0:
                emotionArrayTotal += json_dict.get('emotionArrayLength')
            if json_dict.get('academicArrayLength') > 0:
                academicArrayTotal += json_dict.get('academicArrayLength')
            if json_dict.get('communeArrayLength') > 0:
                communeArrayTotal += json_dict.get('communeArrayLength')
            if json_dict.get('etherArrayLength') > 0:
                etherArrayTotal += json_dict.get('etherArrayLength')

        # Append the totals to an array now that the 'for in' loop is done
        counts = []
        counts.append(physicArrayTotal)
        counts.append(emotionArrayTotal)
        counts.append(academicArrayTotal)
        counts.append(communeArrayTotal)
        counts.append(etherArrayTotal)
        # Create an dictionart for all the totals
        word_array_dict = {'logCounts': counts}

        # Assemble the main_return_dict
        main_return_dict['all'].append(pie_dict)
        main_return_dict['all'].append(word_array_dict)
        main_return_dict['all'].append({'description_primary': 'The log information for every log you have written.'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Log Summary'})

        # print the_dict
        return jsonify(**main_return_dict)
        # return json_item
    else:
        # Do nothing
        return 'You get nothing!'

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
