from flask import Flask
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app)

@app.route('/')
def home_page():
    foo = mongo.db
    print(foo)
    return 'hello world'

if __name__ == '__main__':
    app.run()