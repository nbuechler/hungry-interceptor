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

intercepts = Blueprint('intercepts', __name__)

@intercepts.route('/')
def tester():
    print(2+2)
    foo = mongo3.db.users
    print(foo)
    return 'Intercepts!'

# Move a user and some relationship to the neo4j databse
'''
This method deletes all the nodes then adds all the users with the email attr
This method also adds all the experiences with the name attr because of course let's experiment
'''
@intercepts.route('/mongo2neo/intercepts_create_users')
def intercepts_create_users():
    user_cursor = mongo3.db.users.find({}) #find all users

    secure_graph1.delete_all()

    for item in user_cursor:
        json_item = json.dumps(item, default=json_util.default)

        # Create a new python dictionary from the json_item, we'll call it json_dict
        json_dict = json.loads(json_item)

        # Create a bunch of user nodes
        new_user_node = Node("User", email=json_dict.get('email'), user_id=json_dict.get('_id').get('$oid'))
        secure_graph1.create(new_user_node)


        print '=====New====='
        print json_dict.get('email')
        print '============='
        user = json_dict.get('_id').get('$oid')

        experience_cursor = mongo3.db.experiences.find({"user": ObjectId(user)}) #find all users

        for item in experience_cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)

            print json_dict.get('name')

            # Create a bunch of user nodes
            new_experience_node = Node("Experience", name=json_dict.get('name'))
            user_experienced_experience = Relationship(new_user_node, "EXPERIENCED", new_experience_node)
            secure_graph1.create(user_experienced_experience)

    return 'success'
