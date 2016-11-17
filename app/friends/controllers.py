from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.databases import mongo1, mongo2, mongo3, remoteDB1, secure_graph1

# mongo dependecies
from flask.ext.pymongo import ObjectId

# bson
import json
from bson import json_util

friends = Blueprint('friends', __name__)

@friends.route('/')
def tester():
    print(2+2)
    foo = mongo3.db.users
    print(foo)
    return 'Friends!'


@friends.route('/overview/<user>')
def process_activities_overview(user=None):

        cursor = mongo3.db.activities.find({"user": ObjectId(user)}) #works! React User id

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}


        return jsonify(**main_return_dict)
