from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.databases import mongo1, mongo2, mongo3, remoteDB1, secure_graph1

# mongo dependecies
from flask.ext.pymongo import ObjectId

# neo4j dependecies
from py2neo.cypher import RecordList

# bson
import json
from bson import json_util

logs = Blueprint('logs', __name__)

@logs.route('/')
def tester():
    return 'Logs!'

@logs.route('/<database>/public')
def get_public_logs(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_logs = remoteDB1.logs.find({'privacy': 1})
    else:
        database = 'default'
        all_logs = mongo3.db.logs.find({'privacy': 1})
    return render_template('logs.html',
        all_logs=all_logs, database=database)

@logs.route('/<database>/all')
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

@logs.route('/overview/<user>')
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

@logs.route('/character_lengths/<user>')
def process_logs_character_lengths(user=None):
        cursor = mongo3.db.logs.find({"user": ObjectId(user)}) #works! React User id

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a list to hold the time counts (in seconds)
        character_lengths_counts_dict = []
        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)

            # Append the second count to the second_counts_dict
            character_lengths_counts_dict.append([
                json_dict.get('physicContentLength'),
                json_dict.get('emotionContentLength'),
                json_dict.get('academicContentLength'),
                json_dict.get('communeContentLength'),
                json_dict.get('etherContentLength'),
                ])

            # Append the entire json_dict dictionary
            data_dict['data'].append(json_dict)

        main_return_dict['all'].append(data_dict) # last json dict, and needs refactoring
        main_return_dict['all'].append({'characterLengthCounts': character_lengths_counts_dict})
        main_return_dict['all'].append({'description_primary': 'The character length information for every log you have written.'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Character Lengths'})

        return jsonify(**main_return_dict)

@logs.route('/word_lengths/<user>')
def process_logs_word_lengths(user=None):
        cursor = mongo3.db.logs.find({"user": ObjectId(user)}) #works! React User id

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a list to hold the time counts (in seconds)
        word_lengths_counts_dict = []
        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)

            # Append the second count to the second_counts_dict
            word_lengths_counts_dict.append([
                json_dict.get('physicArrayLength'),
                json_dict.get('emotionArrayLength'),
                json_dict.get('academicArrayLength'),
                json_dict.get('communeArrayLength'),
                json_dict.get('etherArrayLength'),
                ])

            # Append the entire json_dict dictionary
            data_dict['data'].append(json_dict)

        main_return_dict['all'].append(data_dict) # last json dict, and needs refactoring
        main_return_dict['all'].append({'wordLengthCounts': word_lengths_counts_dict})
        main_return_dict['all'].append({'description_primary': 'The word length information for every log you have written.'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Word Lengths'})

        return jsonify(**main_return_dict)

@logs.route('/has/word/<user>')
def query_logs_contains_sub_logs(user=None):
        cypher = secure_graph1.cypher
        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a dictionary to hold all the nodes
        all_nodes_dict = {'allNodes': []}

        # Create a dictionary to hold all the nodes
        log_nodes_dict = {'logNodes': []}

        # Create a dictionary to hold all the nodes
        word_nodes_dict = {'wordNodes': []}

        node_number = 0

        ## Assuming that all the logs are queried only when each of the words are then queried
        current_log_id_for_word_nodes = ''
        for record in cypher.execute("MATCH (u:User {user_id: '" + user + "'})-[r:LOGGED]->(log)-[h:HAS]->(word) RETURN log,word"):
            if(current_log_id_for_word_nodes != record[0].properties.get('log_id')):
                print '======='+ str(node_number) +'======='
                all_nodes_dict['allNodes'].append(record[0].properties)
                log_nodes_dict['logNodes'].append(record[0].properties)
                current_log_id_for_word_nodes = record[0].properties.get('log_id')
            all_nodes_dict['allNodes'].append(record[1].properties)
            print record[0].properties.get('log_id') # log properties
            print record[1].properties # word properties
            word_nodes_dict['wordNodes'].append(record[1].properties)
            node_number += 1

        main_return_dict['all'].append(all_nodes_dict)
        # main_return_dict['all'].append(log_nodes_dict)
        # main_return_dict['all'].append(word_nodes_dict)
        main_return_dict['all'].append({'totalNodes': len(all_nodes_dict['allNodes'])})
        main_return_dict['all'].append({'totalLogs': len(log_nodes_dict['logNodes'])})
        main_return_dict['all'].append({'totalWords': len(word_nodes_dict['wordNodes'])})

        return jsonify(**main_return_dict)
