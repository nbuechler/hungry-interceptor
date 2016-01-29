from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.databases import mongo1, mongo2, mongo3, remoteDB1, secure_graph1

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
# over time as I get better and think more about the dependency structure.

@experiences.route('/overview/<user>')
def process_experiences_overview(user=None):
        cursor = mongo3.db.experiences.find({"user": ObjectId(user)}) #works! React User id

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a list to hold the time counts (in seconds)
        second_counts_dict = []
        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)

            # Append the second count to the second_counts_dict
            second_counts_dict.append(json_dict.get('seconds'))

            # Append the entire json_dict dictionary
            data_dict['data'].append(json_dict)

        main_return_dict['all'].append(data_dict) # last json dict, and needs refactoring
        main_return_dict['all'].append({'secondCounts': second_counts_dict})
        main_return_dict['all'].append({'description_primary': 'The experience information for every experience you have written.'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Experience Summary'})

        return jsonify(**main_return_dict)

@experiences.route('/statistics/<user>')
def process_experiences_statistics(user=None):
        cursor = mongo3.db.experiences.find({"user": ObjectId(user)}) #works! React User id

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a list to hold the time counts (in seconds)
        word_length_dict = []

        # Create a list to hold the time counts (in seconds)
        second_counts_dict = []

        # Create an empty array to hold the data I care about, in this case
        # the data is an array of privacy info
        privacy_dict = [0, 0]

        # Create an empty array to hold the data I care about, in this case
        # the data is an array of privacy info
        pronoun_dict = {
                    'singular1stPerson': 0,
                    'singular2ndPerson': 0,
                    'masculine3rdPerson': 0,
                    'femine3rdPerson': 0,
                    'neuter3rdPerson': 0,
                    'plural2ndPerson': 0,
                    'plural1stPerson': 0,
                    'plural3rdPerson': 0,
                    }

        # Create an empty array to hold the data I care about, in this case
        # the data is an array of experience time info
        experience_time_dict = {
                    'before': 0,
                    'while': 0,
                    'after': 0,
                    }

        # Totals
        totals_dict = {
                'totalSeconds' : 0,
                'totalWords' : 0,
                'totalExperiences' : 0,
                }

        # Averages
        averages_dict = {
                'avgSeconds' : 0,
                'avgWords' : 0,
                }

        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Count total Experiences
            totals_dict['totalExperiences'] += 1

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)

            # Append the second count to the second_counts_dict
            second_counts_dict.append(json_dict.get('seconds'))

            # Count total seconds
            totals_dict['totalSeconds'] += json_dict.get('seconds')

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

            # Count the different pronouns
            if json_dict.get('pronoun') == 'I':
                pronoun_dict['singular1stPerson'] += 1
            elif json_dict.get('pronoun') == 'You':
                pronoun_dict['singular2ndPerson'] += 1
            elif json_dict.get('pronoun') == 'He':
                pronoun_dict['masculine3rdPerson'] += 1
            elif json_dict.get('pronoun') == 'She':
                pronoun_dict['femine3rdPerson'] += 1
            elif json_dict.get('pronoun') == 'It':
                pronoun_dict['neuter3rdPerson'] += 1
            elif json_dict.get('pronoun') == 'You all':
                pronoun_dict['plural2ndPerson'] += 1
            elif json_dict.get('pronoun') == 'We':
                pronoun_dict['plural1stPerson'] += 1
            elif json_dict.get('pronoun') == 'They':
                pronoun_dict['plural3rdPerson'] += 1
            else:
                print 'pronoun not found'

            # Count the different pronouns
            if json_dict.get('experienceTime') == 'Before':
                experience_time_dict['before'] += 1
            elif json_dict.get('experienceTime') == 'While':
                experience_time_dict['while'] += 1
            elif json_dict.get('experienceTime') == 'After':
                experience_time_dict['after'] += 1
            else:
                print 'pronoun not found'

        # Average total Importance
        averages_dict['avgSeconds'] = totals_dict['totalSeconds'] / len(second_counts_dict)
        averages_dict['avgWords'] = totals_dict['totalWords'] / len(word_length_dict)

        main_return_dict['all'].append(data_dict) # last json dict, and needs refactoring
        main_return_dict['all'].append(
            {'secondCounts': second_counts_dict,
             'wordLengths': word_length_dict,
             'privacyCounts': privacy_dict,
             'pronouns': pronoun_dict,
             'experienceTimes': experience_time_dict,
             'totals': totals_dict,
             'averages': averages_dict,
             })
        main_return_dict['all'].append({'description_primary': 'The experience statistics for every experience you have written.'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Experience Statistics'})

        return jsonify(**main_return_dict)

'''
Experience has word
MATCH ()-[r:EXPERIENCED]->(e)-[h:HAS]->(w) RETURN e, w
'''

@experiences.route('/has/word/<user>')
def query_experiences_contains_words(user=None):
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
        experience_nodes_dict = {'experienceNodes': []}

        # Create a dictionary to hold all the nodes
        word_nodes_dict = {'wordNodes': []}

        node_number = 0

        ## Assuming that all the experiences are queried only when each of the words are then queried
        current_experience_id_for_word_nodes = ''
        current_node_number_for_experience_id = node_number
        for record in cypher.execute("MATCH (u:User {user_id: '" + user + "'})-[r:EXPERIENCED]->(experience)-[h:HAS]->(word) RETURN experience,word"):
            if(current_experience_id_for_word_nodes != record[0].properties.get('experience_id')):
                current_node_number_for_experience_id = node_number
                node_number += 1
                print '======='+ str(node_number) +'======='
                all_nodes_dict['allNodes'].append(record[0].properties)
                experience_nodes_dict['experienceNodes'].append(record[0].properties)
                current_experience_id_for_word_nodes = record[0].properties.get('experience_id')
            all_links_dict['allLinks'].append({"source": current_node_number_for_experience_id, "target":  node_number})
            all_nodes_dict['allNodes'].append(record[1].properties)
            print record[0].properties.get('experience_id') # experience properties
            print record[1].properties # word properties
            word_nodes_dict['wordNodes'].append(record[1].properties)
            node_number += 1

        main_return_dict['all'].append(data_dict)
        main_return_dict['all'].append(agr_data_dict)
        main_return_dict['all'].append({'description_primary': 'This information is to show the clusters of words and their relationship to the experiences'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Experience Clusters'})
        main_return_dict['all'].append(all_links_dict)
        main_return_dict['all'].append(all_nodes_dict)
        main_return_dict['all'].append(experience_nodes_dict)
        main_return_dict['all'].append(word_nodes_dict)
        main_return_dict['all'].append({'totalLinks': len(all_links_dict['allLinks'])})
        main_return_dict['all'].append({'totalNodes': len(all_nodes_dict['allNodes'])})
        main_return_dict['all'].append({'totalExperiences': len(experience_nodes_dict['experienceNodes'])})
        main_return_dict['all'].append({'totalWords': len(word_nodes_dict['wordNodes'])})

        return jsonify(**main_return_dict)

'''
Method to get all Logs contained by experience:

Experience contains log
MATCH ()-[r:EXPERIENCED]->(e)-[c:CONTAINS]->(l) RETURN e, l
'''

@experiences.route('/contains/log/<user>')
def query_experiences_contains_logs(user=None):
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
        experience_nodes_dict = {'experienceNodes': []}

        # Create a dictionary to hold all the nodes
        log_nodes_dict = {'logNodes': []}

        node_number = 0

        ## Assuming that all the experiences are queried only when each of the logs are then queried
        current_experience_id_for_log_nodes = ''
        current_node_number_for_experience_id = node_number
        for record in cypher.execute("MATCH (u:User {user_id: '" + user + "'})-[r:EXPERIENCED]->(experience)-[c:CONTAINS]->(log) RETURN experience,log"):
            if(current_experience_id_for_log_nodes != record[0].properties.get('experience_id')):
                current_node_number_for_experience_id = node_number
                node_number += 1
                print '======='+ str(node_number) +'======='
                all_nodes_dict['allNodes'].append(record[0].properties)
                experience_nodes_dict['experienceNodes'].append(record[0].properties)
                current_experience_id_for_log_nodes = record[0].properties.get('experience_id')
            all_links_dict['allLinks'].append({"source": current_node_number_for_experience_id, "target":  node_number})
            all_nodes_dict['allNodes'].append(record[1].properties)
            print record[0].properties.get('experience_id') # experience properties
            print record[1].properties # log properties
            log_nodes_dict['logNodes'].append(record[1].properties)
            node_number += 1

        main_return_dict['all'].append(data_dict)
        main_return_dict['all'].append(agr_data_dict)
        main_return_dict['all'].append({'description_primary': 'This information is to show the clusters of logs and their relationship to the experiences'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Experience Clusters'})
        main_return_dict['all'].append(all_links_dict)
        main_return_dict['all'].append(all_nodes_dict)
        main_return_dict['all'].append(experience_nodes_dict)
        main_return_dict['all'].append(log_nodes_dict)
        main_return_dict['all'].append({'totalLinks': len(all_links_dict['allLinks'])})
        main_return_dict['all'].append({'totalNodes': len(all_nodes_dict['allNodes'])})
        main_return_dict['all'].append({'totalExperiences': len(experience_nodes_dict['experienceNodes'])})
        main_return_dict['all'].append({'totalLogs': len(log_nodes_dict['logNodes'])})

        return jsonify(**main_return_dict)
