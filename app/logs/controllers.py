from flask import Blueprint

logs = Blueprint('logs', __name__)

@logs.route('/')
def tester():
    return 'Logs!'
