from flask import Blueprint

activities = Blueprint('activities', __name__)

@activities.route('/')
def tester():
    return 'Activities!'
