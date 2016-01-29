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

@users.route('/spoke/unique_word/<user>')
def query_users_contains_unique_word(user=None):
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

        for record in cypher.execute("MATCH (u:User {user_id: '" + user + "'})-[r:EXPERIENCED]->(experience)-[h:HAS]->(word) RETURN experience,word"):
            print record

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


# Logro perspective? time filtered
# TODO : MATCH ()-[r:DID]->(a)-[b:CONTAINS]->(e)-[c:CONTAINS]->(l) RETURN a, e, l
