from flask import Flask
from flask import render_template, redirect, url_for

#from .forms import DefaultForm

from flask.ext.pymongo import PyMongo
from flask.ext.pymongo import MongoClient

app = Flask(__name__)
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

if __name__ == '__main__':
    app.run()
