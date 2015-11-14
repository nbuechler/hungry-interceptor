from flask import Flask
from flask import render_template, redirect, url_for, jsonify


# bson
import json
from bson import json_util

#from .forms import DefaultForm

from flask.ext.pymongo import PyMongo, MongoClient

from flask.ext.cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}}) #CORS :WARNING everything!
# connect to MongoDB with the defaults
mongo1 = PyMongo(app)

## connect to another MongoDB database on the same host
app.config['MONGO2_DBNAME'] = 'evgroio-dev'
mongo2 = PyMongo(app, config_prefix='MONGO2')

#remoteDB1
mongolab_uri = 'mongodb://evgroio01:admin@ds041238.mongolab.com:41238/heroku_app36697506'
client = MongoClient(mongolab_uri,
                     connectTimeoutMS=30000,
                     socketTimeoutMS=None,
                     socketKeepAlive=True)

remoteDB1 = client.get_default_database()

#TODO: List out more apis for specific calls I need
@app.route('/')
def home_page():
    foo = mongo2.db.users
    print(foo)
    print(__name__)
    print(2+2)
    return 'hello world'

@app.route('/secret')
def secret_page():
    foo = mongo2.db.users
    return 'shhh..this is a secret'

@app.route('/<database>/users')
def get_users(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_users = remoteDB1.users.find({})
    else:
        database = 'default'
        all_users = mongo2.db.users.find({})
    return render_template('users.html',
        all_users=all_users, database=database)

#Go to new user create page
@app.route('/<database>/users/new')
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

#Makes a form insert a user record into mongo instance
@app.route('/<database>/users/create', methods=["GET", "POST"])
def create_user(database=None):
    print('called create_user')
    return render_template('createdUser.html')

#Find a user by first name for fun!
@app.route('/<database>/users/<first_name>')
def get_user(database=None, first_name=None):
    print('User is ' + first_name)
    if database == 'remote':
        print('Receiving remote data')
        user = remoteDB1.users.find_one({'firstName': first_name})
        print('==User==')
        print(user)
    else:
        database = 'default'
        user = mongo2.db.users.find_one({'firstName': first_name})
        print('==User==')
        print(user)
    return render_template('userPage.html',
        user=user, database=database)

@app.route('/<database>/activities/public')
def get_public_activities(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_activities = remoteDB1.activities.find({'privacy': 1})
    else:
        database = 'default'
        all_activities = mongo2.db.activities.find({'privacy': 1})
    return render_template('activities.html',
        all_activities=all_activities, database=database)

@app.route('/<database>/experiences/public')
def get_public_experiences(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_experiences = remoteDB1.experiences.find({'privacy': 1})
    else:
        database = 'default'
        all_experiences = mongo2.db.experiences.find({'privacy': 1})
    return render_template('experiences.html',
        all_experiences=all_experiences, database=database)

@app.route('/<database>/activities')
def get_activities(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_activities = remoteDB1.activities.find({})
    else:
        database = 'default'
        all_activities = mongo2.db.activities.find({})
    return render_template('activities.html',
        all_activities=all_activities, database=database)

@app.route('/<database>/experiences')
def get_experiences(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_experiences = remoteDB1.experiences.find({})
    else:
        database = 'default'
        all_experiences = mongo2.db.experiences.find({})
    return render_template('experiences.html',
        all_experiences=all_experiences, database=database)

@app.route('/<database>/logs')
def get_logs(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_logs = remoteDB1.logs.find({})
    else:
        database = 'default'
        all_logs = mongo2.db.logs.find({})
    return render_template('logs.html',
        all_logs=all_logs, database=database)

# This is the method that starts the processing of the logs, and it will change
# over time as I get better and think more about the dependecy structure.

# The general gist od this is that the logs should be processed like the dummy
# example below so that another service can use this method as a sevice.

# The cursor object gets turned into a json which then in turn gets made into a
# a python dictionary. Then processing can happen on it and be returned ultimately
# --> like so:    return jsonify(**allOfIt)


@app.route('/process-logs/<user>')
def process_logs(user=None):
    print user
    if user == 'all':
        # http://stackoverflow.com/questions/11280382/python-mongodb-pymongo-json-encoding-and-decoding

        print '!!!got all, here are all logs!!!'
        # [all_logs for all_logs in remoteDB1.logs.find({})]

        cursor = remoteDB1.logs.find({})


        json_items = []
        # Create a pie dictionary to set up the building of data intended for pie charts.
        pie_dict = {'pies': []}

        # Create counters for the total lengths of word_arrays
        physicArrayTotal = 0
        emotionArrayTotal = 0
        academicArrayTotal = 0
        communeArrayTotal = 0
        etherArrayTotal = 0

        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)
            json_items.append(json_item)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)
            # Define the json key for the array to hold the
            json_key = json_dict.get('_id').get('$oid')
            # Create an empty array to hold the data I care about, in this case
            # the data is an array of five numbers for each json_dict, the word_array lengths (words)
            word_array_lengths = []
            word_array_lengths.append(json_dict.get('physicArrayLength'))
            word_array_lengths.append(json_dict.get('emotionArrayLength'))
            word_array_lengths.append(json_dict.get('academicArrayLength'))
            word_array_lengths.append(json_dict.get('communeArrayLength'))
            word_array_lengths.append(json_dict.get('etherArrayLength'))

            # Get the content for each of the word array values, and order it correctly in the array
            word_array_contents = []
            word_array_contents.append(json_dict.get('physicContent'))
            word_array_contents.append(json_dict.get('emotionContent'))
            word_array_contents.append(json_dict.get('academicContent'))
            word_array_contents.append(json_dict.get('communeContent'))
            word_array_contents.append(json_dict.get('etherContent'))

            pie_instance_dict = {
                                'key': json_key,
                                'data': word_array_lengths,
                                'values': word_array_contents,
                                'name': json_dict.get('name')
                                }
            print pie_instance_dict

            # By the way, we are also counting the total lengths
            if json_dict.get('physicArrayLength') > 0:
                physicArrayTotal += json_dict.get('physicArrayLength')
            if json_dict.get('emotionArrayLength') > 0:
                emotionArrayTotal += json_dict.get('emotionArrayLength')
            if json_dict.get('academicArrayLength') > 0:
                academicArrayTotal += json_dict.get('academicArrayLength')
            if json_dict.get('communeArrayLength') > 0:
                communeArrayTotal += json_dict.get('communeArrayLength')
            if json_dict.get('etherArrayLength') > 0:
                etherArrayTotal += json_dict.get('etherArrayLength')

            print '========json_item========'
            print '========start here========'
            print json_dict
            print '=================='

        # Append the totals to an array now that the 'for in' loop is done
        counts = []
        counts.append(physicArrayTotal)
        counts.append(emotionArrayTotal)
        counts.append(academicArrayTotal)
        counts.append(communeArrayTotal)
        counts.append(etherArrayTotal)

        # Create an dictionart for all the totals
        word_array_dict = {'logCounts': counts}
        print word_array_dict

        the_dict = json.loads(json_items[20])
        # print the_dict
        return jsonify(**the_dict)
        # return jsonify(**raw_dict)
    else:
        print '!!!user detected, do something!!!'
        # TODO: do something to get specific user
    return 'Success!'

@app.route('/dummy')
def get_all_dummy():
    allOfIt = dict(
    {'all' : [
        {'pies': [
                  {'key': 'P1', 'data': [2, 4, 5, 4, 7]},
                  {'key': 'P2', 'data': [3, 2, 9, 1, 8]},
                  {'key': 'P3', 'data': [3, 4, 0, 7, 8]},
                  {'key': 'P4', 'data': [3, 5, 5, 0, 4]},
                  {'key': 'P5', 'data': [3, 8, 3, 2, 3]}
                ]},
        {'logCounts': [14, 23, 22, 14, 30]},
        {'description_primary': 'The main desciption is going to detail that this is one view of the data'},
        {'description_secondary': 'The secondary description is going to detail that this is really a lot more information'}
    ]})

    return jsonify(**allOfIt)

@app.route('/altdummy')
def get_all_altdummy():
    allOfIt = dict(
    {'all' : [
        {'pies': [
                  {'key': 'P1', 'data': [6, 5, 8, 8, 7]},
                  {'key': 'P2', 'data': [3, 6, 9, 1, 8]},
                  {'key': 'P3', 'data': [3, 0, 8, 6, 3]},
                  {'key': 'P4', 'data': [3, 5, 5, 0, 4]},
                  {'key': 'P5', 'data': [8, 0, 3, 5, 6]}
                ]},
        {'logCounts': [14, 23, 22, 14, 30]},
        {'description_primary': 'The main desciption --- look it is different!'},
        {'description_secondary': 'The secondary description --- look at the data below, it should be, too!'}
    ]})

    return jsonify(**allOfIt)

if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
