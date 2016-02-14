from app import app
import sys
from logs.controllers import logs
from experiences.controllers import experiences
from activities.controllers import activities
from users.controllers import users
from intercepts.controllers import intercepts

app.register_blueprint(logs, url_prefix='/logs')
app.register_blueprint(experiences, url_prefix='/experiences')
app.register_blueprint(activities, url_prefix='/activities')
app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(intercepts, url_prefix='/intercepts')

# Sets the port, or defaults to 80
if (len(sys.argv) > 1):
    port = int(sys.argv[1])
else:
    port=80

app.run(debug=True, host='0.0.0.0', port=port)
