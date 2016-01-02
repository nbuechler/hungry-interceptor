from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.databases import mongo1, mongo2, mongo3, remoteDB1, secure_graph1

# mongo dependecies
from flask.ext.pymongo import ObjectId

# neo4j dependecies
from py2neo import Node, Relationship, Path

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

# Create constraints
'''
This method creates constrains
'''
@intercepts.route('/mongo2neo/intercepts_create_constraint')
def intercepts_create_constraint():
    # secure_graph1.schema.create_uniqueness_constraint("Word", "name")
    return 'success'

# Drop constraints
'''
This method drops constrains
'''
@intercepts.route('/mongo2neo/intercepts_drop_constraint')
def intercepts_drop_constraint():
    # secure_graph1.schema.drop_uniqueness_constraint("Word", "name")
    return 'success'

# Move a user and some relationship to the neo4j databse
## A word_length is the number of words in the descriptionArrayLength
'''
This method deletes all the records then adds all relationships and nodes.
It relies on there being a mongo database. **VERY IMPORTANT**

Here are useful queries to find all the records for a user for a given node attr:

--Find all the nodes that are words with a name of name 'spoken' by a user with an email address of email--
MATCH (n:User {email: "<email>"})-[r:SPOKE]-(a:Word {name: "<name>"}) return a

--Find all the distinct nodes that are 'spoken' by a user--
MATCH (n:User)-[r:SPOKE]-(a) return DISTINCT a

'''
@intercepts.route('/mongo2neo/intercepts_create_records')
def intercepts_create_records():

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
        new_user_node = Node("User",
            email=json_dict.get('email'),
            user_id=json_dict.get('_id').get('$oid'),
            nodeType='user',
            )

        ####
        user = json_dict.get('_id').get('$oid')
        activity_cursor = mongo3.db.activities.find({"user": ObjectId(user)}) #find all activities for a user
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
                nodeType='activity',
                )

            for word in json_dict.get('descriptionArray'):
                new_word_node = Node("Word", name=word, characters=len(word), nodeType='word',)
                activity_has_word = Relationship(new_activity_node, "HAS", new_word_node)
                secure_graph1.create(activity_has_word)
                user_spoke_word = Relationship(new_user_node, "SPOKE", new_word_node)
                secure_graph1.create(user_spoke_word)

            user_did_activity = Relationship(new_user_node, "DID", new_activity_node)
            secure_graph1.create(user_did_activity)

            ####
            activity = json_dict.get('_id').get('$oid')
            experience_cursor = mongo3.db.experiences.find({"firstActivity": ObjectId(activity)}) #find all experiences for an activity
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
                    pronoun=json_dict.get('pronoun'),
                    word_length=json_dict.get('descriptionArrayLength'),
                    nodeType='experience',
                    )

                for word in json_dict.get('descriptionArray'):
                    new_word_node = Node("Word", name=word, characters=len(word), nodeType='word',)
                    experience_has_word = Relationship(new_experience_node, "HAS", new_word_node)
                    secure_graph1.create(experience_has_word)
                    user_spoke_word = Relationship(new_user_node, "SPOKE", new_word_node)
                    secure_graph1.create(user_spoke_word)

                activity_contains_experience = Relationship(new_activity_node, "CONTAINS", new_experience_node)
                secure_graph1.create(activity_contains_experience)
                user_experienced_experience = Relationship(new_user_node, "EXPERIENCED", new_experience_node)
                secure_graph1.create(user_experienced_experience)

                ####
                experience = json_dict.get('_id').get('$oid')
                log_cursor = mongo3.db.logs.find({"firstExperience": ObjectId(experience)}) #find all logs for an experience
                ####
                # For every activity create a node
                ####
                for log in log_cursor:
                    json_log = json.dumps(log, default=json_util.default)

                    # Create a new python dictionary from the json_experience, we'll call it json_dict
                    json_dict = json.loads(json_log)

                    # Create a bunch of experience nodes
                    new_log_node = Node("Log",
                        name=json_dict.get('name'),
                        log_id=json_dict.get('_id').get('$oid'),
                        privacy=json_dict.get('privacy'),
                        physicArrayLength=json_dict.get('physicArrayLength'),
                        emotionArrayLength=json_dict.get('emotionArrayLength'),
                        academicArrayLength=json_dict.get('academicArrayLength'),
                        communeArrayLength=json_dict.get('communeArrayLength'),
                        etherArrayLength=json_dict.get('etherArrayLength'),
                        physicContent=json_dict.get('physicContent'),
                        emotionContent=json_dict.get('emotionContent'),
                        academicContent=json_dict.get('academicContent'),
                        communeContent=json_dict.get('communeContent'),
                        etherContent=json_dict.get('etherContent'),
                        nodeType='log',
                        )

                    ## Only do the iteration step if there is a word to add
                    if json_dict.get('physicArrayLength') > 0:
                        new_sub_log_node = Node("PhysicLog",
                            parentLogName=json_dict.get('name'),
                            parentLogId=json_dict.get('_id').get('$oid'),
                            privacy=json_dict.get('privacy'),
                            wordLength=json_dict.get('physicArrayLength'),
                            content=json_dict.get('physicContent'),
                            nodeType='sublog',
                            )
                        log_contains_sub = Relationship(new_log_node, "CONTAINS", new_sub_log_node)
                        secure_graph1.create(log_contains_sub)
                        user_described_sublog = Relationship(new_user_node, "DESCRIBED", new_sub_log_node)
                        secure_graph1.create(user_described_sublog)

                        for word in json_dict.get('physicArray'):
                            new_word_node = Node("Word", name=word, characters=len(word), nodeType='word',)
                            log_has_word = Relationship(new_log_node, "HAS", new_word_node)
                            secure_graph1.create(log_has_word)
                            sublog_has_word = Relationship(new_sub_log_node, "HAS", new_word_node)
                            secure_graph1.create(sublog_has_word)
                            user_spoke_word = Relationship(new_user_node, "SPOKE", new_word_node)
                            secure_graph1.create(user_spoke_word)


                    ## Only do the iteration step if there is a word to add
                    if json_dict.get('emotionArrayLength') > 0:
                        new_sub_log_node = Node("EmotionLog",
                            parentLogName=json_dict.get('name'),
                            parentLogId=json_dict.get('_id').get('$oid'),
                            privacy=json_dict.get('privacy'),
                            wordLength=json_dict.get('emotionArrayLength'),
                            content=json_dict.get('emotionContent'),
                            nodeType='sublog',
                            )
                        log_contains_sub = Relationship(new_log_node, "CONTAINS", new_sub_log_node)
                        secure_graph1.create(log_contains_sub)
                        user_described_sublog = Relationship(new_user_node, "DESCRIBED", new_sub_log_node)
                        secure_graph1.create(user_described_sublog)

                        for word in json_dict.get('emotionArray'):
                            new_word_node = Node("Word", name=word, characters=len(word), nodeType='word',)
                            log_has_word = Relationship(new_log_node, "HAS", new_word_node)
                            secure_graph1.create(log_has_word)
                            sublog_has_word = Relationship(new_sub_log_node, "HAS", new_word_node)
                            secure_graph1.create(sublog_has_word)
                            user_spoke_word = Relationship(new_user_node, "SPOKE", new_word_node)
                            secure_graph1.create(user_spoke_word)

                    ## Only do the iteration step if there is a word to add
                    if json_dict.get('academicArrayLength') > 0:
                        new_sub_log_node = Node("AcademicLog",
                            parentLogName=json_dict.get('name'),
                            parentLogId=json_dict.get('_id').get('$oid'),
                            privacy=json_dict.get('privacy'),
                            wordLength=json_dict.get('academicArrayLength'),
                            content=json_dict.get('academicContent'),
                            nodeType='sublog',
                            )
                        log_contains_sub = Relationship(new_log_node, "CONTAINS", new_sub_log_node)
                        secure_graph1.create(log_contains_sub)
                        user_described_sublog = Relationship(new_user_node, "DESCRIBED", new_sub_log_node)
                        secure_graph1.create(user_described_sublog)

                        for word in json_dict.get('academicArray'):
                            new_word_node = Node("Word", name=word, characters=len(word), nodeType='word',)
                            log_has_word = Relationship(new_log_node, "HAS", new_word_node)
                            secure_graph1.create(log_has_word)
                            sublog_has_word = Relationship(new_sub_log_node, "HAS", new_word_node)
                            secure_graph1.create(sublog_has_word)
                            user_spoke_word = Relationship(new_user_node, "SPOKE", new_word_node)
                            secure_graph1.create(user_spoke_word)

                    ## Only do the iteration step if there is a word to add
                    if json_dict.get('communeArrayLength') > 0:
                        new_sub_log_node = Node("CommuneLog",
                            parentLogName=json_dict.get('name'),
                            parentLogId=json_dict.get('_id').get('$oid'),
                            privacy=json_dict.get('privacy'),
                            wordLength=json_dict.get('communeArrayLength'),
                            content=json_dict.get('communeContent'),
                            nodeType='sublog',
                            )
                        log_contains_sub = Relationship(new_log_node, "CONTAINS", new_sub_log_node)
                        secure_graph1.create(log_contains_sub)
                        user_described_sublog = Relationship(new_user_node, "DESCRIBED", new_sub_log_node)
                        secure_graph1.create(user_described_sublog)

                        for word in json_dict.get('communeArray'):
                            new_word_node = Node("Word", name=word, characters=len(word), nodeType='word',)
                            log_has_word = Relationship(new_log_node, "HAS", new_word_node)
                            secure_graph1.create(log_has_word)
                            sublog_has_word = Relationship(new_sub_log_node, "HAS", new_word_node)
                            secure_graph1.create(sublog_has_word)
                            user_spoke_word = Relationship(new_user_node, "SPOKE", new_word_node)
                            secure_graph1.create(user_spoke_word)

                    ## Only do the iteration step if there is a word to add
                    if json_dict.get('etherArrayLength') > 0:
                        new_sub_log_node = Node("EtherLog",
                            parentLogName=json_dict.get('name'),
                            parentLogId=json_dict.get('_id').get('$oid'),
                            privacy=json_dict.get('privacy'),
                            wordLength=json_dict.get('etherArrayLength'),
                            content=json_dict.get('etherContent'),
                            nodeType='sublog',
                            )
                        log_contains_sub = Relationship(new_log_node, "CONTAINS", new_sub_log_node)
                        secure_graph1.create(log_contains_sub)
                        user_described_sublog = Relationship(new_user_node, "DESCRIBED", new_sub_log_node)
                        secure_graph1.create(user_described_sublog)

                        for word in json_dict.get('etherArray'):
                            new_word_node = Node("Word", name=word, characters=len(word), nodeType='word',)
                            log_has_word = Relationship(new_log_node, "HAS", new_word_node)
                            secure_graph1.create(log_has_word)
                            sublog_has_word = Relationship(new_sub_log_node, "HAS", new_word_node)
                            secure_graph1.create(sublog_has_word)
                            user_spoke_word = Relationship(new_user_node, "SPOKE", new_word_node)
                            secure_graph1.create(user_spoke_word)

                    experience_contains_log = Relationship(new_experience_node, "CONTAINS", new_log_node)
                    secure_graph1.create(experience_contains_log)
                    user_logged_log = Relationship(new_user_node, "LOGGED", new_log_node)
                    secure_graph1.create(user_logged_log)


    return 'success'
