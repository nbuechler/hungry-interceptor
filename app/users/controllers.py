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


        all_unique_words_dict = {'allUniqueWords': []}

        # Create a dictionary to hold all the nodes
        experience_nodes_dict = {'experienceNodes': []}

        # Create a dictionary to hold all the nodes
        word_nodes_dict = {'wordNodes': []}

        # Create a dictionary to hold all the nodes
        totals_dict = {'totalUniqueWords': 0}

        for record in cypher.execute("MATCH (u:User {user_id: '" + user + "'})-[r:SPOKE]->(word) RETURN DISTINCT word.name, count(word.name)"):
            print record
            all_unique_words_dict['allUniqueWords'].append(
                {
                'word': record[0],
                'count': record[1]
                }
            )
        totals_dict['totalUniqueWords'] = len(all_unique_words_dict['allUniqueWords'])

        main_return_dict['all'].append(data_dict)
        main_return_dict['all'].append(agr_data_dict)
        main_return_dict['all'].append({'description_primary': 'The list of unique words and the number of times the words are used (frequency)'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Unique words'})
        main_return_dict['all'].append(all_unique_words_dict)
        main_return_dict['all'].append(totals_dict)

        return jsonify(**main_return_dict)


# Logro perspective? time filtered
# TODO : MATCH ()-[r:DID]->(a)-[b:CONTAINS]->(e)-[c:CONTAINS]->(l) RETURN a, e, l
