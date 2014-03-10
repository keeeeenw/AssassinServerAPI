# all the imports
#import sqlite3
import os
from models import Game
from flask import Flask 
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.debug import DebuggedApplication
from flask_restful import Api, Resource

app = Flask('application')
api = Api(app)

if os.getenv('FLASK_CONF') == 'DEV':
	#development settings n
    app.config.from_object('application.settings.Development')
	# Flask-DebugToolbar (only enabled when DEBUG=True)
    toolbar = DebugToolbarExtension(app)
    
    # Google app engine mini profiler
    # https://github.com/kamens/gae_mini_profiler
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    from gae_mini_profiler import profiler, templatetags 
    @app.context_processor
    def inject_profiler():
        return dict(profiler_includes=templatetags.profiler_includes())
    app.wsgi_app = profiler.ProfilerWSGIMiddleware(app.wsgi_app)
    

elif os.getenv('FLASK_CONF') == 'TEST':
    app.config.from_object('application.settings.Testing')

else:
    app.config.from_object('application.settings.Production')

# Enable jinja2 loop controls extension
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# Pull in URL dispatch routes, urls module imports view
import urls

#app.config.from_object('config')

# Load default config and override config from 
# an environment variable
# app.config.update(dict(
# ))

#app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#def connect_db():
#    """Connects to the specific database."""
#    url = app.config['DATABASE']
#    rv = sqlite3.connect(url)
#    rv.row_factory = sqlite3.Row
#    return rv
#
#def get_db():
#    """
#    Opens a new database connection if there is none yet for the
#    current application context.
#    """
#    if not hasattr(g, 'sqlite_db'):
#        g.sqlite_db = connect_db()
#    return g.sqlite_db
#
#def init_db(): 
#    #app context is not created yet, so we create it by hand
#    with app.app_context():
#        db = get_db()
#        with app.open_resource('schema.sql', mode='r') as f:
#            db.cursor().executescript(f.read())
#        db.commit()
