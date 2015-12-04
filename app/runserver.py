from app import app
from logs.controllers import logs
from experiences.controllers import experiences
from activities.controllers import activities

app.register_blueprint(logs, url_prefix='/logs')
app.register_blueprint(experiences, url_prefix='/experiences')
app.register_blueprint(activities, url_prefix='/activities')

app.run(debug=True)
