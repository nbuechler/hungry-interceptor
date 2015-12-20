from flask import Blueprint
from flask import render_template, redirect, url_for, jsonify

#databases
from config.database import mongo1, mongo2, mongo3, remoteDB1

# mongo dependecies
from flask.ext.pymongo import ObjectId

# bson
import json
from bson import json_util

experiences = Blueprint('experiences', __name__)

@experiences.route('/')
def tester():
    return 'Experiences!'

@experiences.route('/<database>/public')
def get_public_experiences(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_experiences = remoteDB1.experiences.find({'privacy': 1})
    else:
        database = 'default'
        all_experiences = mongo3.db.experiences.find({'privacy': 1})
    return render_template('experiences.html',
        all_experiences=all_experiences, database=database)


@experiences.route('/<database>/all')
def get_experiences(database=None):
    if database == 'remote':
        print('Receiving remote data')
        all_experiences = remoteDB1.experiences.find({})
    else:
        database = 'default'
        all_experiences = mongo3.db.experiences.find({})
    return render_template('experiences.html',
        all_experiences=all_experiences, database=database)

# This is the method that starts the processing of the experiences, and it will change
# over time as I get better and think more about the dependency structure.

@experiences.route('/overview/<user>')
def process_experiences_overview(user=None):
        cursor = mongo3.db.experiences.find({"user": ObjectId(user)}) #works! React User id

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a list to hold the time counts (in seconds)
        second_counts_dict = []
        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)

            # Append the second count to the second_counts_dict
            second_counts_dict.append(json_dict.get('seconds'))

            # Append the entire json_dict dictionary
            data_dict['data'].append(json_dict)

        main_return_dict['all'].append(data_dict) # last json dict, and needs refactoring
        main_return_dict['all'].append({'secondCounts': second_counts_dict})
        main_return_dict['all'].append({'description_primary': 'The experience information for every log you have written.'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Experience Summary'})

        return jsonify(**main_return_dict)

@experiences.route('/statistics/<user>')
def process_experiences_statistics(user=None):
        cursor = mongo3.db.experiences.find({"user": ObjectId(user)}) #works! React User id

        # Create a data dictionary to set up the building of data intended for different charts.
        data_dict = {'data': []}

        # Create a dictionary to hold the main object
        main_return_dict = {'all' : []}

        # Create a list to hold the time counts (in seconds)
        word_length_dict = []

        # Create a list to hold the time counts (in seconds)
        second_counts_dict = []

        # Create an empty array to hold the data I care about, in this case
        # the data is an array of privacy info
        privacy_dict = [0, 0]

        # Create an empty array to hold the data I care about, in this case
        # the data is an array of privacy info
        pronoun_dict = {
                    'singular1stPerson': 0,
                    'singular2ndPerson': 0,
                    'masculine3rdPerson': 0,
                    'femine3rdPerson': 0,
                    'neuter3rdPerson': 0,
                    'plural2ndPerson': 0,
                    'plural1stPerson': 0,
                    'plural3rdPerson': 0,
                    }

        # Create an empty array to hold the data I care about, in this case
        # the data is an array of experience time info
        experience_time_dict = {
                    'before': 0,
                    'while': 0,
                    'after': 0,
                    }

        # Totals
        totals_dict = {
                'totalSeconds' : 0,
                'totalWords' : 0,
                'totalExperiences' : 0,
                }

        # Averages
        averages_dict = {
                'avgSeconds' : 0,
                'avgWords' : 0,
                }

        for item in cursor:
            json_item = json.dumps(item, default=json_util.default)

            # Count total Experiences
            totals_dict['totalExperiences'] += 1

            # Create a new python dictionary from the json_item, we'll call it json_dict
            json_dict = json.loads(json_item)

            # Append the second count to the second_counts_dict
            second_counts_dict.append(json_dict.get('seconds'))

            # Count total seconds
            totals_dict['totalSeconds'] += json_dict.get('seconds')

            # Append the second count to the second_counts_dict
            word_length_dict.append(json_dict.get('descriptionArrayLength'))

            # Count total words
            totals_dict['totalWords'] += json_dict.get('descriptionArrayLength')

            # Append the entire json_dict dictionary
            data_dict['data'].append(json_dict)

            # Count the different privacies
            if json_dict.get('privacy') < 1:
                privacy_dict[0] += 1
            else:
                privacy_dict[1] += 1

            # Count the different pronouns
            if json_dict.get('pronoun') == 'I':
                pronoun_dict['singular1stPerson'] += 1
            elif json_dict.get('pronoun') == 'You':
                pronoun_dict['singular2ndPerson'] += 1
            elif json_dict.get('pronoun') == 'He':
                pronoun_dict['masculine3rdPerson'] += 1
            elif json_dict.get('pronoun') == 'She':
                pronoun_dict['femine3rdPerson'] += 1
            elif json_dict.get('pronoun') == 'It':
                pronoun_dict['neuter3rdPerson'] += 1
            elif json_dict.get('pronoun') == 'You all':
                pronoun_dict['plural2ndPerson'] += 1
            elif json_dict.get('pronoun') == 'We':
                pronoun_dict['plural1stPerson'] += 1
            elif json_dict.get('pronoun') == 'They':
                pronoun_dict['plural3rdPerson'] += 1
            else:
                print 'pronoun not found'

            # Count the different pronouns
            if json_dict.get('experienceTime') == 'Before':
                experience_time_dict['before'] += 1
            elif json_dict.get('experienceTime') == 'While':
                experience_time_dict['while'] += 1
            elif json_dict.get('experienceTime') == 'After':
                experience_time_dict['after'] += 1
            else:
                print 'pronoun not found'

        # Average total Importance
        averages_dict['avgSeconds'] = totals_dict['totalSeconds'] / len(second_counts_dict)
        averages_dict['avgWords'] = totals_dict['totalWords'] / len(word_length_dict)

        main_return_dict['all'].append(data_dict) # last json dict, and needs refactoring
        main_return_dict['all'].append(
            {'secondCounts': second_counts_dict,
             'wordLengths': word_length_dict,
             'privacyCounts': privacy_dict,
             'pronouns': pronoun_dict,
             'experienceTimes': experience_time_dict,
             'totals': totals_dict,
             'averages': averages_dict,
             })
        main_return_dict['all'].append({'description_primary': 'The experience statistics for every log you have written.'})
        main_return_dict['all'].append({'description_secondary': 'Use it wisely!'})
        main_return_dict['all'].append({'title': 'Experience Statistics'})

        return jsonify(**main_return_dict)
