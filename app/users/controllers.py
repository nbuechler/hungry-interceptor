from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.databases import mongo1, mongo2, mongo3, remoteDB1, secure_graph1

# mongo dependecies
from flask.ext.pymongo import ObjectId

# neo4j dependecies
from py2neo import Node, Relationship

# bson
import json
from bson import json_util

users = Blueprint('users', __name__)

@users.route('/')
def tester():
    print(2+2)
    foo = mongo3.db.users
    print(foo)
    return 'Users!'

@users.route('/<database>/all')
def get_users(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_users = remoteDB1.users.find({})
    else:
        database = 'default'
        all_users = mongo3.db.users.find({})
    return render_template('users.html',
        all_users=all_users, database=database)

#Go to new user create page
@users.route('/<database>/new')
def new_user(database=None):
#    form = DefaultForm()
    if database == 'remote':
        print('Receiving remote data')
    else:
        database = 'default'
    return render_template('newUser.html',
#                           form=form,
                           database=database
                          )

#Find a user by first name for fun!
@users.route('/<database>/<first_name>')
def get_user(database=None, first_name=None):
    print('User is ' + first_name)
    if database == 'remote':
        print('Receiving remote data')
        user = remoteDB1.users.find_one({'firstName': first_name})
        print('==User==')
        print(user)
    else:
        database = 'default'
        user = mongo3.db.users.find_one({'firstName': first_name})
        print('==User==')
        print(user)
    return render_template('userPage.html',
        user=user, database=database)


'''
User SPOKE unique word, count of word usage
MATCH ()-[r:SPOKE]->(n:Word) RETURN DISTINCT n.name, count(n.name)
'''
# TODO: How to make this more interesting??
# MATCH ()-[r:HAS]-(w:Word {name: 'Deep'}) RETURN r


@users.route('/spoke/unique_word/<user>')
def query_users_contains_unique_word(user=None):
        cypher = secure_graph1.cypher
        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a data dictionary to set up the building of data intended for different charts.
        agr_data_dict = {'aggregateData': []}


        all_unique_words_dict = {'allUniqueWords': []}
        l2h_unique_words_dict = {'lowToHighUniqueWords': []}

        # Create a dictionary to hold all the nodes
        experience_nodes_dict = {'experienceNodes': []}

        # Create a dictionary to hold all the nodes
        word_nodes_dict = {'wordNodes': []}

        # Create a dictionary to hold all the nodes
        totals_dict = {'totalUniqueWords': 0}

        for record in cypher.execute("MATCH (u:User {user_id: '" + user + "'})-[r:SPOKE]->(word) RETURN DISTINCT word.name, count(word.name)"):
            # print record
            all_unique_words_dict['allUniqueWords'].append(
                {
                'word': record[0],
                'count': record[1],
                'wordLength': len(record[0]),
                }
            )
            l2h_unique_words_dict['lowToHighUniqueWords'].append(
                {
                'word': record[0],
                'count': record[1],
                'wordLength': len(record[0]),
                }
            )

        all_unique_words_dict['allUniqueWords'].sort(key=lambda x: (x['wordLength'], x['word']), reverse=False)
        l2h_unique_words_dict['lowToHighUniqueWords'].sort(key=lambda x: (x['count'], x['wordLength'], x['word']), reverse=False)

        totals_dict['totalUniqueWords'] = len(all_unique_words_dict['allUniqueWords'])

        main_return_dict['all'].append(data_dict)
        main_return_dict['all'].append(agr_data_dict)
        main_return_dict['all'].append({'description_primary': 'The list of unique words and the number of times the words are used (frequency)'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Unique words'})
        main_return_dict['all'].append(all_unique_words_dict)
        main_return_dict['all'].append(l2h_unique_words_dict)
        main_return_dict['all'].append(totals_dict)

        return jsonify(**main_return_dict)


# Logro perspective? time filtered
# TODO : MATCH ()-[r:DID]->(a)-[c:CONTAINS]->(e)-[cc:CONTAINS]->(l) RETURN a, e, l

'''
Method to get all the Logs contained by Experiences contained by Activities:

Activity contains experience contains log
MATCH ()-[r:DID]->(a)-[c:CONTAINS]->(e)-[cc:CONTAINS]->(l) RETURN a, e, l
'''

@users.route('/did/activity_with_log/<user>')
def query_activities_contains_logs(user=None):
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
        experience_nodes_dict = {'experienceNodes': []}

        # Create a dictionary to hold all the nodes
        log_nodes_dict = {'logNodes': []}

        node_number = 0

        ## Assuming that all the activities are queried only when each of the experiences are then queried
        current_activity_id_for_experience_nodes = ''
        current_experience_id_for_log_nodes = ''
        current_node_number_for_activity_id = node_number
        current_node_number_for_experience_id = node_number
        current_node_number_for_log_id = node_number

        # Each record is the smalles unit of the relationship, in this case logs
        for record in cypher.execute("MATCH (u:User {user_id: '" + user + "'})-[r:DID]->(activity)-[c:CONTAINS]->(experience)-[cc:CONTAINS]->(log) RETURN activity,experience,log"):
            print record

            if(current_experience_id_for_log_nodes != record[1].properties.get('experience_id')):
                current_node_number_for_experience_id = node_number
                node_number += 1
                print '======='+ str(node_number) +'======='


                if(current_activity_id_for_experience_nodes != record[0].properties.get('activity_id')):
                    current_node_number_for_activity_id = node_number
                    node_number += 1
                    print '======='+ str(node_number) +'======='
                    all_nodes_dict['allNodes'].append(record[0].properties)
                    activity_nodes_dict['activityNodes'].append(record[0].properties)
                    current_activity_id_for_experience_nodes = record[0].properties.get('activity_id')
                all_links_dict['allLinks'].append({"source": current_node_number_for_activity_id, "target":  node_number})
                all_nodes_dict['allNodes'].append(record[1].properties)
                print record[0].properties.get('activity_id') # activity properties
                print record[1].properties # experience properties
                experience_nodes_dict['experienceNodes'].append(record[1].properties)
                node_number += 1


                current_experience_id_for_log_nodes = record[1].properties.get('experience_id')
            all_links_dict['allLinks'].append({"source": current_node_number_for_experience_id, "target":  node_number})
            all_nodes_dict['allNodes'].append(record[2].properties)
            print record[0].properties.get('experience_id') # experience properties
            print record[1].properties # log properties
            log_nodes_dict['logNodes'].append(record[2].properties)
            node_number += 1

            # if(current_activity_id_for_experience_nodes != record[0].properties.get('activity_id')):
            #     current_node_number_for_activity_id = node_number
            #     # node_number += 1
            #     print '======='+ str(node_number) +'==!!1====='
            #     print '======='+ current_activity_id_for_experience_nodes +'======='
            #     #########
            #     if(current_experience_id_for_log_nodes != record[1].properties.get('experience_id')):
            #         current_node_number_for_experience_id = node_number
            #         # node_number += 1
            #         print '======='+ str(node_number) +'======='
            #         all_nodes_dict['allNodes'].append(record[0].properties)
            #         activity_nodes_dict['activityNodes'].append(record[0].properties)
            #         current_experience_id_for_experience_nodes = record[1].properties.get('experience_id')
            #     #########
            #     all_links_dict['allLinks'].append({"source": current_node_number_for_activity_id, "target":  node_number})
            #     all_nodes_dict['allNodes'].append(record[1].properties)
            #     experience_nodes_dict['experienceNodes'].append(record[1].properties)
            # all_links_dict['allLinks'].append({"source": current_node_number_for_experience_id, "target":  node_number})
            # all_nodes_dict['allNodes'].append(record[2].properties)
            # log_nodes_dict['logNodes'].append(record[2].properties)
            # node_number += 1

        main_return_dict['all'].append(data_dict)
        main_return_dict['all'].append(agr_data_dict)
        main_return_dict['all'].append({'description_primary': 'This information is to show the clusters of logs and their relationship to the activities via experiences'})
        main_return_dict['all'].append({'description_secondary': 'If an activity has an experience with no log, it will not be displayed. Additionally, this implies that the activity must have have an experience to be displayed.'})
        main_return_dict['all'].append({'title': 'Experience Clusters'})
        main_return_dict['all'].append(all_links_dict)
        main_return_dict['all'].append(all_nodes_dict)
        main_return_dict['all'].append(activity_nodes_dict)
        main_return_dict['all'].append(experience_nodes_dict)
        main_return_dict['all'].append(log_nodes_dict)
        main_return_dict['all'].append({'totalLinks': len(all_links_dict['allLinks'])})
        main_return_dict['all'].append({'totalNodes': len(all_nodes_dict['allNodes'])})
        main_return_dict['all'].append({'totalActivities': len(activity_nodes_dict['activityNodes'])})
        main_return_dict['all'].append({'totalExperiences': len(experience_nodes_dict['experienceNodes'])})
        main_return_dict['all'].append({'totalLogs': len(log_nodes_dict['logNodes'])})

        return jsonify(**main_return_dict)
