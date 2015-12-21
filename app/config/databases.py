from app import app

from flask.ext.pymongo import PyMongo, MongoClient
from py2neo import Graph

# connect to MongoDB with the defaults
mongo1 = PyMongo(app)

## connect to another MongoDB database on the same host
app.config['MONGO2_DBNAME'] = 'evgroio-dev'
mongo2 = PyMongo(app, config_prefix='MONGO2')
app.config['MONGO3_DBNAME'] = 'test'
mongo3 = PyMongo(app, config_prefix='MONGO3')

#remoteDB1
mongolab_uri = 'mongodb://evgroio01:admin@ds041238.mongolab.com:41238/heroku_app36697506'
client = MongoClient(mongolab_uri,
                     connectTimeoutMS=30000,
                     socketTimeoutMS=None,
                     socketKeepAlive=True)

remoteDB1 = client.get_default_database()

## connect to default instance of neo4j
secure_graph1 = Graph("https://neo4j:admin@0.0.0.0:7474/db/data/")  
