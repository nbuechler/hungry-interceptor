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

    print '====create single activity node===='
    print activity
    print '========'

    activity_cursor = mongo3.db.activities.find({"_id": ObjectId(activity)}) #find all activities
    json_activity = json.dumps(activity_cursor[0], default=json_util.default)

    # Create a new python dictionary from the json_activity, we'll call it activity_dict
    activity_dict = json.loads(json_activity)
    print activity_dict

    print '---===--=-=-=-'
    user_id = activity_dict.get('user').get('$oid')

    user_cursor = mongo3.db.users.find({"_id": ObjectId(user_id)}) #find all activities
    json_user = json.dumps(user_cursor[0], default=json_util.default)

    # Create a new python dictionary from the json_user, we'll call it user_dict
    user_dict = json.loads(json_user)
    print user_dict

    print 'here'

    ###
    # TODO: Create an external method called create activity node.
    # Business logic for ACTIVITIY_NODE starts here, uses data from above.
    ###

    # Create a new python dictionary from the json_user, we'll call it json_dict
    json_dict = user_dict

    usernode = cypher.execute("MATCH (user:User {user_id: '" + user_id + "'}) RETURN user")
    print usernode

    # Create a bunch of user nodes
    new_user_node = Node("User",
        email=json_dict.get('email'),
        user_id=json_dict.get('_id').get('$oid'),
        nodeType='user',
        )

    ###
    # TODO: Create an external method called create activity node.
    # Business logic for ACTIVITIY_NODE starts here, uses data from above.
    ###

    json_dict = activity_dict

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

                    milliDate = json_dict.get('created').get('$date')
                    date = datetime.datetime.fromtimestamp(milliDate/1000.0)


                    # Create a bunch of experience nodes
                    new_log_node = Node("Log",
                        user=user,
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
                        milliDate=milliDate,
                        year=date.year,
                        month=date.month,
                        day=date.day,
                        hour=date.hour,
                        minute=date.minute,
                        second=date.second,
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
                        log_contains_sub = Relationship(new_log_node, "SUB_CONTAINS", new_sub_log_node)
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
                        log_contains_sub = Relationship(new_log_node, "SUB_CONTAINS", new_sub_log_node)
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
                        log_contains_sub = Relationship(new_log_node, "SUB_CONTAINS", new_sub_log_node)
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
                        log_contains_sub = Relationship(new_log_node, "SUB_CONTAINS", new_sub_log_node)
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
                        log_contains_sub = Relationship(new_log_node, "SUB_CONTAINS", new_sub_log_node)
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
