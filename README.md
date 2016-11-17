# hungry-interceptor
This project intercepts/manipulates/requests/handles data. Then, it does one of many things:
* Formats the data
* Stores the data in a neo4j database.
* Stores the data in a mongo database.
* Stores the data in a different datastore entirely.
* Kicks off an ETL process (planned Mid Oct 2016)
* Etc.

This app is planned to be a gate keeper or router-like microservice for the rest of the engines, such as a machine learning engine (Non-existent in 2016), NLP engine ('speedy-affect-scorer' in 2016), ETL engine ('energetic-etl') or another engine.

# Overview
Its primary function is getting data from its counterpart in the front end side of the _Logro_ application (currently callled 'fixed-gateway' in 2016). Its other important function is sending data to its counterpart engines listed above via its mechanisms and API.

# History
The project originally was designed to also do ETL functions which are now part of 'energetic-etl' (GPLv3) where the intercepts directory contained some of the logic this project used as boilerplate. See the other project called: energetic-etl

Find the project here: https://github.com/nbuechler/hungry-interceptor

# Getting Started
* First, install virtualenv if not done so already -- https://virtualenv.pypa.io/en/latest/installation.html(https://virtualenv.pypa.io/en/latest/installation.html)
* Then, run this command:
<pre>
  <code>
    $ virtualenv venv
  </code>
</pre>
* Next, activate the virtual environment (make sure you get the'.'):
<pre>
  <code>
    $ . venv/bin/activate
  </code>
</pre>
* Last, install the requirements with pip:
<pre>
  <code>
    $ pip install -r requirements.txt
  </code>
</pre>

# Most exciting future plans
If I begin working with a friend of mine (likely 2016), it would be useful to intercept the data and send it to a machine learning model to notice trends in affect. This machine learning model would be in a separate project.

# Start databases - if they are not already running
_From a terminal, start mongo:_
<pre>
  <code>
    mongod
  </code>
</pre>

_From a terminal start Neo4j:_
<pre>
  <code>
    sudo /etc/init.d/neo4j-service start
  </code>
</pre>

# Run the application
<pre>
  <code>
    python app/runserver.py 5000
  </code>
</pre>

This contains a port - 5000 - for running local, otherwise it will try to run on the default port - 80 - and that's taken. If you run it on a server instance, such as one on AWS without the port specified, it should running open to the world. That is the usual configuration for deploying code and making it 'live' to the world. But, make sure you are prudent in running the code in the way you want it to run.

# Scripts folder
The scripts folder is for automation. If using AWS, here's a problem I encountered in the middle of Feb, 2016:
_DO NOT UPGRADE PIP_ from 6.1.1 on a standard AWS EC2 instance, or it will bite you. I don't really know why so this might have changed when you are reading this.

# Requirements

* Flask==0.10.1
* Flask-Cors==2.1.0
* Flask-PyMongo==0.3.1
* Flask-WTF==0.11
* itsdangerous==0.24
* Jinja2==2.8
* MarkupSafe==0.23
* py2neo==2.0.8
* pymongo==2.8.1
* six==1.10.0
* Werkzeug==0.11.3
* wheel==0.24.0
* WTForms==2.0.2

# Things to do
* Refactor: Remove old code from 'hungry-interceptor' when this is complete!

# CORS and dealing with it
Make sure to pay attention to how CORS right now accepts everything.

See more here: https://flask-cors.readthedocs.org/en/latest/

<pre>
  <code>
    from flask.ext.cors import CORS
    cors = CORS(app, resources={r"/\*": {"origins": "\*"}}) #CORS :WARNING everything!
  </code>
</pre>

# LICENSE
GPLv3
