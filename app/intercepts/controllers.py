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

# date
import datetime

intercepts = Blueprint('intercepts', __name__)

'''
Helper functions - Get a new user node
Takes a user_id as a paramater
Returns a user_node (either a new one or a one that already exists)
'''
def get_user_node(user_id=None):

    cypher = secure_graph1.cypher

    user_cursor = mongo3.db.users.find({"_id": ObjectId(user_id)}) #find all activities
    json_user = json.dumps(user_cursor[0], default=json_util.default)

    # Create a new python dictionary from the json_user, we'll call it user_dict
    user_dict = json.loads(json_user)

    # Assumes either a record list of 1 or no records at all!
    user_node_list = cypher.execute("MATCH (user:User {user_id: '" + user_id + "'}) RETURN user")

    user_node=None
    if len(user_node_list) == 0:
        # Create a user node
        user_node = Node("User",
            email=user_dict.get('email'),
            user_id=user_dict.get('_id').get('$oid'),
            nodeType='user',
            )
    else:
        # Don't create a new user node it already exists
        user_node = user_node_list[0][0]

    return user_node

'''
Helper functions - Create new User/Activity Relationship
cnr --> create new relationship
Takes a user node and activity dict as paramaters
Returns a new_activity_node
'''
def cnr_user_did_activity(new_user_node=None, activity_dict=None):

    # Create a new activity node
    new_activity_node = Node("Activity",
        name=activity_dict.get('name'),
        activity_id=activity_dict.get('_id').get('$oid'),
        privacy=activity_dict.get('privacy'),
        word_length=activity_dict.get('descriptionArrayLength'),
        nodeType='activity',
        )

    for word in activity_dict.get('descriptionArray'):
        new_word_node = Node("Word", name=word, characters=len(word), nodeType='word',)
        activity_has_word = Relationship(new_activity_node, "HAS", new_word_node)
        secure_graph1.create(activity_has_word)
        user_spoke_word = Relationship(new_user_node, "SPOKE", new_word_node)
        secure_graph1.create(user_spoke_word)

    user_did_activity = Relationship(new_user_node, "DID", new_activity_node)
    secure_graph1.create(user_did_activity)

    return new_activity_node

'''
Helper functions - Create new User/Experience Relationship
cnr --> create new relationship
Takes a user node and experience dict as paramaters
Returns a new_activity_node
'''
def cnr_user_experienced_experience(new_user_node=None, experience_dict=None):

    # Create a new experience node
    new_experience_node = Node("Experience",
        name=experience_dict.get('name'),
        experience_id=experience_dict.get('_id').get('$oid'),
        privacy=experience_dict.get('privacy'),
        pronoun=experience_dict.get('pronoun'),
        word_length=experience_dict.get('descriptionArrayLength'),
        nodeType='experience',
        )

    for word in experience_dict.get('descriptionArray'):
        new_word_node = Node("Word", name=word, characters=len(word), nodeType='word',)
        experience_has_word = Relationship(new_experience_node, "HAS", new_word_node)
        secure_graph1.create(experience_has_word)
        user_spoke_word = Relationship(new_user_node, "SPOKE", new_word_node)
        secure_graph1.create(user_spoke_word)

    user_experienced_experience = Relationship(new_user_node, "EXPERIENCED", new_experience_node)
    secure_graph1.create(user_experienced_experience)

    return new_experience_node

'''
Helper functions - Create new User/Log Relationship
cnr --> create new relationship
Takes a user node and log dict as paramaters
Returns a new_log_node
'''
def cnr_user_logged_log(new_user_node=None, log_dict=None):

    milliDate = log_dict.get('created').get('$date')
    date = datetime.datetime.fromtimestamp(milliDate/1000.0)

    # Create a new log node
    new_log_node = Node("Log",
        name=log_dict.get('name'),
        log_id=log_dict.get('_id').get('$oid'),
        privacy=log_dict.get('privacy'),
        physicArrayLength=log_dict.get('physicArrayLength'),
        emotionArrayLength=log_dict.get('emotionArrayLength'),
        academicArrayLength=log_dict.get('academicArrayLength'),
        communeArrayLength=log_dict.get('communeArrayLength'),
        etherArrayLength=log_dict.get('etherArrayLength'),
        physicContent=log_dict.get('physicContent'),
        emotionContent=log_dict.get('emotionContent'),
        academicContent=log_dict.get('academicContent'),
        communeContent=log_dict.get('communeContent'),
        etherContent=log_dict.get('etherContent'),
        milliDate=milliDate,
        year=date.year,
        month=date.month,
        day=date.day,
        hour=date.hour,
        minute=date.minute,
        second=date.second,
        nodeType='log',
        )

    ## You might be wondering, where are the words for a log... see the 'cnr_user_described_sublog'

    user_logged_log = Relationship(new_user_node, "LOGGED", new_log_node)
    secure_graph1.create(user_logged_log)

    return new_log_node

'''
Helper functions - Create new User/SubLog Relationship
cnr --> create new relationship
Takes a user node, log node. log dict, sublog_array_name, and node_title as paramaters
Returns a new_log_node
'''
def cnr_user_described_sublog(new_user_node=None, new_log_node=None, log_dict=None, sublog_array_name=None, node_title=None):

    # Create a new sublog node
    new_sub_log_node = Node(node_title,
        parentLogName=log_dict.get('name'),
        parentLogId=log_dict.get('_id').get('$oid'),
        privacy=log_dict.get('privacy'),
        wordLength=log_dict.get('academicArrayLength'),
        content=log_dict.get('academicContent'),
        nodeType='sublog',
        )

    for word in log_dict.get(sublog_array_name):
        new_word_node = Node("Word", name=word, characters=len(word), nodeType='word',)
        log_has_word = Relationship(new_log_node, "HAS", new_word_node)
        secure_graph1.create(log_has_word)
        sublog_has_word = Relationship(new_sub_log_node, "HAS", new_word_node)
        secure_graph1.create(sublog_has_word)
        user_spoke_word = Relationship(new_user_node, "SPOKE", new_word_node)
        secure_graph1.create(user_spoke_word)

    user_described_sublog = Relationship(new_user_node, "DESCRIBED", new_sub_log_node)
    secure_graph1.create(user_described_sublog)

    return new_sub_log_node

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

# Move a user and some relationship to the neo4j database
## A word_length is the number of words in the descriptionArrayLength


'''
This method CREATES a single activity node from neo4j

To find a user node:
MATCH (u:User {user_id: "56db97954eca34d01404888a"}) RETURN u

'''
@intercepts.route('/mongo2neo/intercepts_create_single_activity/<activity>', methods=['POST'])
def intercepts_create_single_activity(activity=None):

    cypher = secure_graph1.cypher

    # Find all activities, but really just one in this case
    activity_cursor = mongo3.db.activities.find({"_id": ObjectId(activity)})
    json_activity = json.dumps(activity_cursor[0], default=json_util.default)

    # Create a new python dictionary from the json_activity, we'll call it activity_dict
    activity_dict = json.loads(json_activity)
    print activity_dict

    ###
    # Business logic for USER_NODE starts here, uses data from above.
    ###
    user_id = activity_dict.get('user').get('$oid')

    user_node = get_user_node(user_id=user_id)

    ###
    # Business logic for ACTIVITIY_NODE starts here, uses data from above.
    ###

    cnr_user_did_activity(new_user_node=user_node, activity_dict=activity_dict)

    return 'success'

'''
This method UPDATES a single activity node from neo4j
'''
@intercepts.route('/mongo2neo/intercepts_update_single_activity/<activity>', methods=['PUT'])
def intercepts_update_single_activity(activity=None):
    print '====update single activity node===='
    print activity

    activity_cursor = mongo3.db.activities.find({"_id": ObjectId(activity)}) #find all activities
    json_activity = json.dumps(activity_cursor[0], default=json_util.default)

    # Create a new python dictionary from the json_activity, we'll call it json_dict
    json_dict = json.loads(json_activity)
    print json_dict

    return 'success'

'''
This method DESTROYS a single activity node from neo4j
'''
@intercepts.route('/mongo2neo/intercepts_destroy_single_activity/<activity>', methods=['DELETE'])
def intercepts_destroy_single_activity(activity=None):
    print '====destroy single activity node===='
    print activity
    return 'success'

'''
This method CREATES a single experience node from neo4j
'''
@intercepts.route('/mongo2neo/intercepts_create_single_experience/<experience>', methods=['POST'])
def intercepts_create_single_experience(experience=None):
    print '====create single experience node===='
    print experience
    return 'success'

'''
This method UPDATES a single experience node from neo4j
'''
@intercepts.route('/mongo2neo/intercepts_update_single_experience/<experience>', methods=['PUT'])
def intercepts_update_single_experience(experience=None):
    print '====update single experience node===='
    print experience
    return 'success'

'''
This method DESTROYS a single experience node from neo4j
'''
@intercepts.route('/mongo2neo/intercepts_destroy_single_experience/<experience>', methods=['DELETE'])
def intercepts_destroy_single_experience(experience=None):
    print '====destroy single experience node===='
    print experience
    return 'success'

'''
This method CREATES a single log node from neo4j
'''
@intercepts.route('/mongo2neo/intercepts_create_single_log/<log>', methods=['POST'])
def intercepts_create_single_log(log=None):
    print '====create single log node===='
    print log
    return 'success'

'''
This method UPDATES a single log node from neo4j
'''
@intercepts.route('/mongo2neo/intercepts_update_single_log/<log>', methods=['PUT'])
def intercepts_update_single_log(log=None):
    print '====update single log node===='
    print log
    return 'success'

'''
This method DESTROYS a single log node from neo4j
'''
@intercepts.route('/mongo2neo/intercepts_destroy_single_log/<log>', methods=['DELETE'])
def intercepts_destroy_single_log(log=None):
    print '====destroy single log node===='
    print log
    return 'success'


'''
This method only deletes all the records.
It relies on there being a mongo database. **VERY IMPORTANT**
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

        user_dict = json.loads(json_user)

        # Create a bunch of user nodes
        new_user_node = Node("User",
            email=user_dict.get('email'),
            user_id=user_dict.get('_id').get('$oid'),
            nodeType='user',
            )

        ####
        user = user_dict.get('_id').get('$oid')
        activity_cursor = mongo3.db.activities.find({"user": ObjectId(user)}) #find all activities for a user
        ####
        # For every activity create a node
        ####
        for activity in activity_cursor:
            json_activity = json.dumps(activity, default=json_util.default)

            # Create a new python dictionary from the json_activity, we'll call it activity_dict
            activity_dict = json.loads(json_activity)

            # Output is a new_activity_node
            new_activity_node = cnr_user_did_activity(
                new_user_node=new_user_node,
                activity_dict=activity_dict
                )

            ####
            activity = activity_dict.get('_id').get('$oid')
            experience_cursor = mongo3.db.experiences.find({"firstActivity": ObjectId(activity)}) #find all experiences for an activity
            ####
            # For every experience create a node
            ####
            for experience in experience_cursor:
                json_experience = json.dumps(experience, default=json_util.default)

                # Create a new python dictionary from the json_experience, we'll call it experience_dict
                experience_dict = json.loads(json_experience)

                # Output is a new_experience_node
                new_experience_node = cnr_user_experienced_experience(
                    new_user_node=new_user_node,
                    experience_dict=experience_dict
                    )

                # Create a new relationship for the activity/experience
                activity_contains_experience = Relationship(new_activity_node, "CONTAINS", new_experience_node)
                secure_graph1.create(activity_contains_experience)

                ####
                experience = experience_dict.get('_id').get('$oid')
                log_cursor = mongo3.db.logs.find({"firstExperience": ObjectId(experience)}) #find all logs for an experience
                ####
                # For every log create a node
                ####
                for log in log_cursor:
                    json_log = json.dumps(log, default=json_util.default)

                    # Create a new python dictionary from the json_experience, we'll call it log_dict
                    log_dict = json.loads(json_log)

                    new_log_node = cnr_user_logged_log(
                        new_user_node=new_user_node,
                        log_dict=log_dict,
                        )

                    ## Only do the iteration step if there is a word to add

                    if log_dict.get('physicArrayLength') > 0:
                        new_sub_log_node = cnr_user_described_sublog(
                            new_user_node=new_user_node,
                            new_log_node=new_log_node,
                            log_dict=log_dict,
                            sublog_array_name='physicArray',
                            node_title='PhysicLog',
                            )
                        log_contains_sub = Relationship(new_log_node, "SUB_CONTAINS", new_sub_log_node)
                        secure_graph1.create(log_contains_sub)

                    ## Only do the iteration step if there is a word to add

                    if log_dict.get('emotionArrayLength') > 0:
                        new_sub_log_node = cnr_user_described_sublog(
                            new_user_node=new_user_node,
                            new_log_node=new_log_node,
                            log_dict=log_dict,
                            sublog_array_name='emotionArray',
                            node_title='EmotionLog',
                            )
                        log_contains_sub = Relationship(new_log_node, "SUB_CONTAINS", new_sub_log_node)
                        secure_graph1.create(log_contains_sub)

                    ## Only do the iteration step if there is a word to add

                    if log_dict.get('academicArrayLength') > 0:
                        new_sub_log_node = cnr_user_described_sublog(
                            new_user_node=new_user_node,
                            new_log_node=new_log_node,
                            log_dict=log_dict,
                            sublog_array_name='academicArray',
                            node_title='AcademicLog',
                            )
                        log_contains_sub = Relationship(new_log_node, "SUB_CONTAINS", new_sub_log_node)
                        secure_graph1.create(log_contains_sub)

                    ## Only do the iteration step if there is a word to add

                    if log_dict.get('communeArrayLength') > 0:
                        new_sub_log_node = cnr_user_described_sublog(
                            new_user_node=new_user_node,
                            new_log_node=new_log_node,
                            log_dict=log_dict,
                            sublog_array_name='communeArray',
                            node_title='CommuneLog',
                            )
                        log_contains_sub = Relationship(new_log_node, "SUB_CONTAINS", new_sub_log_node)
                        secure_graph1.create(log_contains_sub)

                    ## Only do the iteration step if there is a word to add

                    if log_dict.get('etherArrayLength') > 0:
                        new_sub_log_node = cnr_user_described_sublog(
                            new_user_node=new_user_node,
                            new_log_node=new_log_node,
                            log_dict=log_dict,
                            sublog_array_name='etherArray',
                            node_title='EtherLog',
                            )
                        log_contains_sub = Relationship(new_log_node, "SUB_CONTAINS", new_sub_log_node)
                        secure_graph1.create(log_contains_sub)

                    experience_contains_log = Relationship(new_experience_node, "CONTAINS", new_log_node)
                    secure_graph1.create(experience_contains_log)
                    user_logged_log = Relationship(new_user_node, "LOGGED", new_log_node)
                    secure_graph1.create(user_logged_log)


    return 'success'

@intercepts.route('/mongo2neo/intercepts_delete_records')
def intercepts_delete_records():

    # Clear the database
    secure_graph1.delete_all()

    return 'success'

'''
This method deletes all the records then adds all relationships and nodes.
It relies on there being a mongo database. **VERY IMPORTANT**

Here are useful queries to find all the records for a user for a given node attr:

--Find all the nodes that are words with a name of name 'spoken' by a user with an email address of email--
MATCH (n:User {email: "<email>"})-[r:SPOKE]-(a:Word {name: "<name>"}) return a

--Find all the distinct nodes that are 'spoken' by a user--
MATCH (n:User)-[r:SPOKE]-(a) return DISTINCT a

'''

# Move an event - as a year, month, or day - and some relationship to the neo4j database
'''
The whole point of running this step is to store this information as a data warehouse

To find all the distinct dates (event):
    MATCH (n:Log)  RETURN DISTINCT n.year, n.month, n.day, n.user

To find all the sums we care about for a given date (event):
    MATCH (n:Log) where n.year = 2016 and n.month = 1 and n.day = 6
    RETURN sum(n.physicArrayLength), sum(n.academicArrayLength), sum(n.emotionArrayLength), sum(n.communeArrayLength), sum(n.etherArrayLength)

To find all the nodes we care about for a given date (event):
    MATCH (n:Log) where n.year = 2015 and n.month = 11 and n.day = 29
    RETURN n

To find all nodes in a year (event):
  MATCH (n:Log) where n.year = 2016 RETURN (n)

To find all nodes in a month (event):
  MATCH (n:Log) where n.year = 2016 and n.month = 1 RETURN (n)

To find all nodes in a day (event):
  MATCH (n:Log) where n.year = 2016 and n.month = 1 and n.day = 6 RETURN (n)
'''
@intercepts.route('/mongo2neo/intercepts_create_event_supplement')
def intercepts_create_event_supplement():
    # Create events with the following attributes...
    # logCount, highestValue, totals for each category, winningCategoryName
    cypher = secure_graph1.cypher

    # All distinct events for each give user
    for event_record in cypher.execute("MATCH (n:Log)  RETURN DISTINCT n.year, n.month, n.day, n.user"):
        sums = cypher.execute("MATCH (n:Log) where n.year = " + str(event_record[0]) + " and n.month = " + str(event_record[1]) + " and n.day = " + str(event_record[2]) + " and n.user = '" + event_record[3] + "' " +
                              "RETURN sum(n.physicArrayLength), sum(n.emotionArrayLength), sum(n.academicArrayLength), sum(n.communeArrayLength), sum(n.etherArrayLength), n.user, count(n)")[0]


        # Find the position of the max values in the list
        winningIndexes = []

        sum_list = [sums[0], sums[1], sums[2], sums[3], sums[4]]
        max_value = max(sum_list)

        for idx,s in enumerate(sum_list):
            if s >= max_value:
                winningIndexes.append(idx)

        new_event_node = Node("Event",
            user = sums[5],
            ymd=str(event_record[0]) + '-' + str(event_record[1]) + '-' + str(event_record[2]),
            year=event_record[0],
            month=event_record[1],
            day=event_record[2],
            physicArrayLengthSum = sums[0],
            emotionArrayLengthSum = sums[1],
            academicArrayLengthSum = sums[2],
            communeArrayLengthSum = sums[3],
            etherArrayLengthSum = sums[4],
            winningIndexes = winningIndexes,
            logCount = sums[6],
            )

        for log_record in cypher.execute("MATCH (n:Log) where n.year = " + str(event_record[0]) + " and n.month = " + str(event_record[1]) + " and n.day = " + str(event_record[2]) + " and n.user = '" + event_record[3] + "' " + " " +
                                         "RETURN n"):
            for log_node in log_record:
                event_includes_log = Relationship(new_event_node, "INCLUDES", log_node)
                secure_graph1.create(event_includes_log)

    return 'success'
