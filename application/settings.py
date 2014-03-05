"""
settings.py

Configuration for Flask app

Important: Place your keys in the secret_keys.py module, 
           which should be kept out of version control.

"""

#import os

from secret_keys import CSRF_SECRET_KEY, SESSION_KEY

class Config(object):
    # Set secret keys for CSRF protection
    SECRET_KEY = CSRF_SECRET_KEY
    CSRF_SESSION_KEY = SESSION_KEY
    # Flask-Cache settings
    CACHE_TYPE = 'gaememcached'
    USERNAME='ken' #fake admin username/password
    PASSWORD='default'

class Development(Config):
    DEBUG = True
    # Flask-DebugToolbar settings
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CSRF_ENABLED = True
    #_basedir = os.path.abspath(os.path.dirname(__file__))
    #DATABASE= os.path.join(_basedir, 'flaskr.db') # app.root_path get app root
    #USERNAME='admin' #fake admin username/password
    #PASSWORD='default'

class Testing(Config):
    TESTING = True
    DEBUG = True
    CSRF_ENABLED = True

class Production(Config):
    DEBUG = False
    CSRF_ENABLED = True
