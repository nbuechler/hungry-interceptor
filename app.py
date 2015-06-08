from flask import Flask
from flask import render_template
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
# connect to MongoDB with the defaults
mongo1 = PyMongo(app)

## connect to another MongoDB database on the same host
app.config['MONGO2_DBNAME'] = 'evgroio-dev'
mongo2 = PyMongo(app, config_prefix='MONGO2')

#'mongodb://evgroio01:admin@ds041238.mongolab.com:41238/heroku_app36697506'

## connect to another MongoDB server altogether
#app.config['MONGO3_HOST'] = 'another.host.example.com'
#app.config['MONGO3_PORT'] = 27017
#app.config['MONGO3_DBNAME'] = 'dbname_three'
#mongo3 = PyMongo(app, config_prefix='MONGO3')

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

@app.route('/users')
@app.route('/users/<database>')
def users(database=None):
    all_users = mongo2.db.users.find({})
    return render_template('users.html',
        all_users=all_users, database=database)

@app.route('/logs')
@app.route('/logs/<database>')
def logs(database=None):
    all_logs = mongo2.db.logs.find({})
    return render_template('logs.html',
        all_logs=all_logs, database=database)

if __name__ == '__main__':
    app.run()