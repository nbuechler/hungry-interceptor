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
## A word_length is the number of words in the descriptionArrayLength
'''
This method deletes all the nodes then adds all the users with the email attr
This method also adds all the activites with the name attr because of course let's experiment
'''
@intercepts.route('/mongo2neo/intercepts_create_users')
def intercepts_create_users():

    # Clear the database
    secure_graph1.delete_all()

    user_cursor = mongo3.db.users.find({}) #find all users
    ####
    # For every user create a node
    ####
    for user in user_cursor:
        json_user = json.dumps(user, default=json_util.default)

        # Create a new python dictionary from the json_user, we'll call it json_dict
        json_dict = json.loads(json_user)

        # Create a bunch of user nodes
        new_user_node = Node("User", email=json_dict.get('email'), user_id=json_dict.get('_id').get('$oid'))
        secure_graph1.create(new_user_node)

        ####
        user = json_dict.get('_id').get('$oid')
        activity_cursor = mongo3.db.activities.find({"user": ObjectId(user)}) #find all activitiyes for a user
        ####
        # For every activity create a node
        ####
        for activity in activity_cursor:
            json_activity = json.dumps(activity, default=json_util.default)

            # Create a new python dictionary from the json_activity, we'll call it json_dict
            json_dict = json.loads(json_activity)

            # Create a bunch of activity nodes
            new_activity_node = Node("Activity",
                name=json_dict.get('name'),
                activity_id=json_dict.get('_id').get('$oid'),
                privacy=json_dict.get('privacy'),
                word_length=json_dict.get('descriptionArrayLength'),
                )
            for word in json_dict.get('descriptionArray'):
                new_word_node = Node("Word", name=word, characters=len(word))
                activity_has_word = Relationship(new_activity_node, "HAS", new_word_node)
                secure_graph1.create(activity_has_word)
            user_did_activity = Relationship(new_user_node, "DID", new_activity_node)
            secure_graph1.create(user_did_activity)

            ####
            activity = json_dict.get('_id').get('$oid')
            experience_cursor = mongo3.db.experiences.find({"firstActivity": ObjectId(activity)}) #find all activitiyes for a user
            ####
            # For every activity create a node
            ####
            for experience in experience_cursor:
                json_experience = json.dumps(experience, default=json_util.default)

                # Create a new python dictionary from the json_experience, we'll call it json_dict
                json_dict = json.loads(json_experience)

                # Create a bunch of experience nodes
                new_experience_node = Node("Experience",
                    name=json_dict.get('name'),
                    experience_id=json_dict.get('_id').get('$oid'),
                    privacy=json_dict.get('privacy'),
                    word_length=json_dict.get('descriptionArrayLength'),
                    )
                for word in json_dict.get('descriptionArray'):
                    new_word_node = Node("Word", name=word, characters=len(word))
                    experience_has_word = Relationship(new_experience_node, "HAS", new_word_node)
                    secure_graph1.create(experience_has_word)

                activity_contains_experience = Relationship(new_activity_node, "CONTAINS", new_experience_node)
                secure_graph1.create(activity_contains_experience)
                user_experienced_experience = Relationship(new_user_node, "EXPERIENCED", new_experience_node)
                secure_graph1.create(user_experienced_experience)



    return 'success'
