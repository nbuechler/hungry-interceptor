from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.databases import mongo1, mongo2, mongo3, remoteDB1, secure_graph1

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
# over time as I get better and think more about the dependency structure.

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

@activities.route('/statistics/<user>')
def process_activities_statistics(user=None):
        cursor = mongo3.db.activities.find({"user": ObjectId(user)}) #works! React User id

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a list to hold the time counts (in seconds)
        word_length_dict = []

        # Create a list to hold the time counts (in seconds)
        importance_counts_dict = []

        # Create an empty array to hold the data I care about, in this case
        # the data is an array of privacy info
        privacy_dict = [0, 0]

        # Totals
        totals_dict = {
                'totalImportance' : 0,
                'totalWords' : 0,
                'totalActivities' : 0,
                }

        # Averages
        averages_dict = {
                'avgImportance' : 0,
                'avgWords' : 0,
                }

        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Count total Experiences
            totals_dict['totalActivities'] += 1

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)

            # Append the second count to the second_counts_dict
            importance_counts_dict.append(json_dict.get('importance'))

            # Count total importance
            totals_dict['totalImportance'] += json_dict.get('importance')

            # Append the second count to the second_counts_dict
            word_length_dict.append(json_dict.get('descriptionArrayLength'))

            # Count total words
            totals_dict['totalWords'] += json_dict.get('descriptionArrayLength')

            # Append the entire json_dict dictionary
            data_dict['data'].append(json_dict)

            # Count the different privacies
            if json_dict.get('privacy') < 1:
                privacy_dict[0] += 1
            else:
                privacy_dict[1] += 1

        # Average total Importance
        averages_dict['avgImportance'] = totals_dict['totalImportance'] / len(importance_counts_dict)
        averages_dict['avgWords'] = totals_dict['totalWords'] / len(word_length_dict)

        main_return_dict['all'].append(data_dict) # last json dict, and needs refactoring
        main_return_dict['all'].append(
            {'importanceCounts': importance_counts_dict,
             'wordLengths': word_length_dict,
             'privacyCounts': privacy_dict,
             'totals': totals_dict,
             'averages': averages_dict,
             })
        main_return_dict['all'].append({'description_primary': 'The activity Statistics for every log you have written.'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Activity Statistics'})

        return jsonify(**main_return_dict)

'''
Activity has word
MATCH ()-[r:DID]->(e)-[h:HAS]->(w) RETURN e, w
'''

@activities.route('/has/word/<user>')
def query_activities_contains_words(user=None):
        cypher = secure_graph1.cypher
        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a data dictionary to set up the building of data intended for different charts.
        agr_data_dict = {'aggregateData': []}

        # Create a dictionary to hold all the nodes
        all_nodes_dict = {'allNodes': []}

        # Create a dictionary to hold all the nodes
        # source - the source node (an element in all_nodes_dict).
        # target - the target node (an element in all_nodes_dict).
        all_links_dict = {'allLinks': []}

        # Create a dictionary to hold all the nodes
        activity_nodes_dict = {'activityNodes': []}

        # Create a dictionary to hold all the nodes
        word_nodes_dict = {'wordNodes': []}

        node_number = 0

        ## Assuming that all the activities are queried only when each of the words are then queried
        current_activity_id_for_word_nodes = ''
        current_node_number_for_activity_id = node_number
        for record in cypher.execute("MATCH (u:User {user_id: '" + user + "'})-[r:DID]->(activity)-[h:HAS]->(word) RETURN activity,word"):
            if(current_activity_id_for_word_nodes != record[0].properties.get('activity_id')):
                current_node_number_for_activity_id = node_number
                node_number += 1
                print '======='+ str(node_number) +'======='
                all_nodes_dict['allNodes'].append(record[0].properties)
                activity_nodes_dict['activityNodes'].append(record[0].properties)
                current_activity_id_for_word_nodes = record[0].properties.get('activity_id')
            all_links_dict['allLinks'].append({"source": current_node_number_for_activity_id, "target":  node_number})
            all_nodes_dict['allNodes'].append(record[1].properties)
            print record[0].properties.get('activity_id') # activity properties
            print record[1].properties # word properties
            word_nodes_dict['wordNodes'].append(record[1].properties)
            node_number += 1

        main_return_dict['all'].append(data_dict)
        main_return_dict['all'].append(agr_data_dict)
        main_return_dict['all'].append({'description_primary': 'This information is to show the clusters of words and their relationship to the activities'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Activity Clusters'})
        main_return_dict['all'].append(all_links_dict)
        main_return_dict['all'].append(all_nodes_dict)
        main_return_dict['all'].append(activity_nodes_dict)
        main_return_dict['all'].append(word_nodes_dict)
        main_return_dict['all'].append({'totalLinks': len(all_links_dict['allLinks'])})
        main_return_dict['all'].append({'totalNodes': len(all_nodes_dict['allNodes'])})
        main_return_dict['all'].append({'totalActivities': len(activity_nodes_dict['activityNodes'])})
        main_return_dict['all'].append({'totalWords': len(word_nodes_dict['wordNodes'])})

        return jsonify(**main_return_dict)
