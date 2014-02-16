# all the imports
import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__) #initialize uppercase variables in name

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'), # app.root_path get app root
    DEBUG=True,
    SECRET_KEY='eHX0FSvjC299QNx',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

if __name__ == '__main__':
    app.run() # fireup the server

