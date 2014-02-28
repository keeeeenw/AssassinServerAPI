from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from application import app
from models import Game
from google.appengine.api import users
from decorators import login_required, admin_required


def api_verif(dev_key):
    if dev_key == 't6ra1M77Ei80b35LeV5I55EN7c':
        return True
    return False

@app.route('/')
def show_games():

    #db = get_db()
    #cur = db.execute('select title, num_player from game order by id desc')
    #games = cur.fetchall()

    # Getting all the games
    gs = Game.all()

    # Build dictionary 
    games = []
    for g in gs:
        games.append({'title':str(g.title), 'num_player': int(g.num_player)})

    # print(games)

    return render_template('show_games.html', games = games)

@app.route('/api/list_games', methods=['GET'])
def list_games():
    if 'dev_key' in request.args:
        key = request.args['dev_key']
        if not api_verif(key):
            abort(401)
    else:
        user = users.get_current_user()
        if not user:
            abort(401)
    # Getting all the games
    gs = Game.all()

    # Build dictionary 
    games = {}
    for g in gs:
        games[g.title] = g.num_player

    return jsonify(**games)

@app.route('/add', methods=['POST'])
@login_required
def add_game():
    user = users.get_current_user()
    if not user:
        abort(401)

    #db = get_db()
    ## use ? to specify query parameters
    #db.execute('insert into game (title, num_player) values (?, ?)',
    #            [request.form['title'], request.form['num_player']])
    #db.commit()

    title = request.form['title']
    num_player = request.form['num_player']
    g = Game(title=title, num_player=int(num_player))
    g.put() # save in the database

    flash('New game was successfully posted')
    return redirect(url_for('show_games'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    providers = {
        'Google'   : 'https://www.google.com/accounts/o8/id',
        'Yahoo'    : 'yahoo.com',
        'MySpace'  : 'myspace.com',
        'AOL'      : 'aol.com',
        'MyOpenID' : 'myopenid.com'
        # add more here
    }
    loginInfo = {} 
    loginInfo['greeting'] = "Not Signed In"
    user = users.get_current_user()
    if user:  # signed in already
        loginInfo['greeting'] = ('Hello %s!') % (
            user.nickname())
    else:     # let user choose authenticator
        for name, uri in providers.items():
            provider = {'url':users.create_login_url(federated_identity=uri),
                        'name': name}
            print(provider)
            if 'providers' not in loginInfo:
                loginInfo['providers'] = [provider]
            else:
                loginInfo['providers'].append(provider)

    #if request.method == 'POST':
    #    user = users.get_current_user()
    #    if user:
    #        greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
    #                    (user.nickname(), users.create_logout_url('/')))
    #    else:
    #        error = "Not Signed In"
    #        greeting = ('<a href="%s">Sign in or register</a>.' %
    #                    users.create_login_url('/'))

    #error = None
    #if request.method == 'POST':
    #    if request.form['username'] != app.config['USERNAME']:
    #        error = 'Invalid username'
    #    elif request.form['password'] != app.config['PASSWORD']:
    #        error = 'Invalid password'
    #    else:
    #        session['logged_in'] = True
    #        flash('You were logged in')
    #        return redirect(url_for('show_games'))
    # return render_template('login.html', error=greeting)

    return render_template('login.html', loginInfo=loginInfo)

@app.route('/logout')
def logout():
    session.pop('logged_in', None) #don't need to check it the key exist
    flash('You were logged out')
    return redirect(url_for('show_games'))

#@app.teardown_appcontext
#def close_db(error):
#    """
#    Closes the database again at the end of the request.
#    """
#    if hasattr(g, 'sqlite_db'):
#        g.sqlite_db.close();


