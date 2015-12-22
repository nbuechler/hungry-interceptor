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

# Move a user to the neo4j databse
'''
This method deletes all the nodes then adds all the users with the email attr
This method also adds all the experiences with the name attr because of course let's experiment
'''
@users.route('/mongo2neo/add_all_users')
def add_all_users():
    cursor = mongo3.db.users.find({}) #find all users

    secure_graph1.delete_all()

    for item in cursor:
        json_item = json.dumps(item, default=json_util.default)

        # Create a new python dictionary from the json_item, we'll call it json_dict
        json_dict = json.loads(json_item)

        # Create a bunch of user nodes
        new_node = Node("User", email=json_dict.get('email'))
        secure_graph1.create(new_node)

        print json_dict.get('email')

    cursor = mongo3.db.experiences.find({}) #find all users

    for item in cursor:
        json_item = json.dumps(item, default=json_util.default)

        # Create a new python dictionary from the json_item, we'll call it json_dict
        json_dict = json.loads(json_item)

        # Create a bunch of user nodes
        new_node = Node("Experience", name=json_dict.get('name'))
        secure_graph1.create(new_node)

    return 'success'
