from flask import Blueprint

experiences = Blueprint('experiences', __name__)

@experiences.route('/')
def tester():
    return 'Experiences!'
