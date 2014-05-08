"""
    Use the functions below for the web application
"""
from application import app
from flask import abort, flash, redirect, render_template, request, session, url_for
from google.appengine.ext.db import to_dict
from ..helpers import verify_password
from models import Game, Player


@app.route('/')  # calls root of the server, does the function below.  Take something and render something
def show_games():
    # Getting all the games
    gs = Game.all()

    # Build dictionary 
    games = []
    for g in gs:
        games.append(to_dict(g))

    print(games)

    return render_template('show_games.html', games=games)  # first games is key, games is value


@app.route('/add', methods=['POST'])
def add_game():
    if not session.get('logged_in'):  # session is a like a conference, the browser remembers data
        abort(401)

    # db = get_db()
    # # use ? to specify query parameters
    # db.execute('insert into game (title, num_player) values (?, ?)',
    # [request.form['title'], request.form['num_player']])
    # db.commit()

    title = request.form['title']  #takes what user put into show_games form
    num_player = request.form['num_player']
    g = Game(title=title, num_player=int(num_player))
    g.put()  # save in the database

    flash('New game was successfully posted')  #displays message
    return redirect(url_for('show_games'))  #takes you back to show games page, with the newly added game displayed


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        check_user = Player.gql("WHERE username = :username", username=request.form['username'])
        if check_user.count() == 0:
            error = 'Username does not exist'
        elif not verify_password(request.form['password'], check_user.get().password_hash):
            error = "Invalid password"
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_games'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # don't need to check it the key exist
    flash('You were logged out')
    return redirect(url_for('show_games'))


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''
