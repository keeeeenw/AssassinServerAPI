# all the imports
import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify

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

def init_db():
    with app.app_context(): #app context is not created yet, so we create it by hand
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def api_verif(dev_key):
    if dev_key == 't6ra1M77Ei80b35LeV5I55EN7c':
        return True
    return False

@app.route('/')
def show_games():
    db = get_db()
    cur = db.execute('select title, num_player from game order by id desc')
    games = cur.fetchall()
    return render_template('show_games.html', games = games)

@app.route('/api/list_games', methods=['GET'])
def list_games():
    if 'dev_key' in request.args:
        key = request.args['dev_key']
        if not api_verif(key):
            abort(401)
    else:
        if not session.get('logged_in'):
            abort(401)
    db = get_db()
    cur = db.execute('select id, title, num_player from game order by id desc')
    dict_games = {}
    for row in cur:
        dict_games[str(row[0])] = list(row)[1:]
    return jsonify(**dict_games)

@app.route('/add', methods=['POST'])
def add_game():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    # use ? to specify query parameters
    db.execute('insert into game (title, num_player) values (?, ?)',
                [request.form['title'], request.form['num_player']])
    db.commit()
    flash('New game was successfully posted')
    return redirect(url_for('show_games'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_games'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None) #don't need to check it the key exist
    flash('You were logged out')
    return redirect(url_for('show_games'))

@app.teardown_appcontext
def close_db(error):
    """
    Closes the database again at the end of the request.
    """
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close();

if __name__ == '__main__':
    app.run(debug=True) # fireup the server

