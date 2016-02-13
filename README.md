# hungry-interceptor
Intercepts data, does something with it, stores it
Storing happens in a neo4j database.
This app is going to be a gate keeper for the rest of the engines, vroom, vroom, go??

Well yes.

Its primary function is getting data from its counterpart in the front end side of the app. Or sending data it to its counterpart via its mechanisms and apis.

#Steps
.. first, install virtualenv if not done so already -- https://virtualenv.pypa.io/en/latest/installation.html

.. then, run this command:  $ virtualenv venv

.. next, activate virtualenv with this command (make sure you get the'.'):  $ . venv/bin/activate

.. we are using 'Flask-PyMongo' - so next, run this command: $ pip install Flask-PyMongo

.. read about it here:

https://flask-pymongo.readthedocs.org/en/latest/

"Flask-PyMongo depends, and will install for you, recent versions of Flask (0.8 or later) and PyMongo (2.4 or later). Flask-PyMongo is compatible with and tested on Python 2.6, 2.7, and 3.3."

..

#Start databases
Start mongo:: mongod
Start Neo4j:: sudo /etc/init.d/neo4j-service start


#Run the application
python app/runserver.py


#Future plans

After learning about basic neural network models and frameworks, it would be neat to see how this project might interact with frameworks like these: Blocks, Lasagne, Keras, and/or Theano... but there is a lot of room for growth and developing what we all might do with the data. We probably need A LOT more.

Tensorflow just came out a few weeks ago from early December 2015.

#Scripts folder
The scripts folder is for automation

#TODO: More details about this here


Ongoing Dependency List:  
pip install flask-wtf
pip install -U flask-cors

-->https://flask-cors.readthedocs.org/en/latest/

#CORS
from flask.ext.cors import CORS

cors = CORS(app, resources={r"/*": {"origins": "*"}}) #CORS :WARNING everything!
