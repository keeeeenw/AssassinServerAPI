from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify
from application import app
from models import Game, User, verify_password, hash_password
from decorators import jsonp, support_jsonp, crossdomain, login_required

"""
The functions below are the supported APIs
"""

@app.route('/api/list_users', methods=['GET']) #client makes request to that url
@login_required
def list_users():
    # Getting all the users
    us = User.all()

    # Build dictionary 
    users = {}
    for u in us:
        users[u.username] = {'username':u.username, 'email':u.email, 'creation_date':u.creation_date} 

    return jsonify(**users) #does not render a page, just returns a Json

@app.route('/api/new_user', methods=['POST'])
def new_user():
    username = request.json.get['username']
    password = request.json.get['password']
    if username is None or password is None:
        abort(400)  # missing arguments
    # if User.query.filter_by(username = username).first is not None:
    # abort(400)  # username already exists
    user = User(username=username) #constructing new user
    hash_password(password)
    user.put() #put user in db
    return jsonify({'username': user.username}), 201, {
        'Location': url_for('get_user', id=user.username, _external=True)}
    # return jsonify({'username': user.username}), 201, {'Location': url_for('get_user', id=user.id, _external=True)}

@app.route('/api/rest_login', methods=['POST', 'OPTIONS']) #login for the app. most of time return json when working with app as opposed to rendering a page
@crossdomain(origin='*', headers=['content-type'])
def rest_login():
    error = None
    # The first item is username, and the second is password
    user_data = [item.split("=")[1] for item in str(request.data).split("&")] #get this from the url
    check_user = User.gql("WHERE username = :username", username=user_data[0]) #making sure they entered in their username correctly, checking against db
    if check_user.count() == 0:
        error = 'Username does not exist'
        return jsonify({'status': error})
    elif not verify_password(user_data[1], check_user.get().password_hash):
        error = "Invalid password"
        return jsonify({'status': error})
    else:
        session['logged_in'] = True
        flash('You were logged in')
        return jsonify({'status': True}) #this tells the client side that the user is successfully logged in

@app.route('/api/list_games', methods=['GET']) #client makes request to that url
@login_required
def list_games():
    # Getting all the games
    gs = Game.all()

    # Build dictionary 
    games = {}
    for g in gs:
        games[g.title] = g.num_player

    return jsonify(**games) #does not render a page, just returns a Json

@app.route('/api/games_for_player', methods=['GET']) #client makes request to that url
@login_required
def games_for_player():
    username = request.args['username']
    #get all users, find where username matches game player
    users = User.all().filter('username =', username)
    
    if users.count()==0:
        return jsonify({'success':False})
    else:
        user = users.get()
        game_players = user.game_players
        games = {}
        for gp in game_players:
            game = gp.game
            game_id = game.key().id_or_name()
            games[game_id] = parse_game(game)
        info = {"success":True, "games":games, "username": username}
        return jsonify(**info)

"""
Helper functions to parse object for JSON returns
"""
def parse_game(game):
    game_id = game.key().id_or_name()
    gameInfo = {
        'game_id':game_id,
        'title':game.title,
        'num_player':game.num_player,
        'creation_date':game.creation_date,
        'start_time':game.start_time,
        'end_time':game.end_time,
    }
    return gameInfo

"""
    Use the functions below for the web application
"""
@app.route('/') #calls root of the server, does the function below.  Take something and render something
def show_games():
    # db = get_db()
    #cur = db.execute('select title, num_player from game order by id desc')
    #games = cur.fetchall()

    # Getting all the games
    gs = Game.all()

    # Build dictionary 
    games = []
    for g in gs:
        games.append({'title': str(g.title), 'num_player': int(g.num_player)})

    print(games)

    return render_template('show_games.html', games=games) #first games is key, games is value

@app.route('/add', methods=['POST'])
def add_game():
    if not session.get('logged_in'): #session is a like a conference, the browser remembers data
        abort(401)

    # db = get_db()
    ## use ? to specify query parameters
    #db.execute('insert into game (title, num_player) values (?, ?)',
    #            [request.form['title'], request.form['num_player']])
    #db.commit()

    title = request.form['title'] #takes what user put into show_games form
    num_player = request.form['num_player']
    g = Game(title=title, num_player=int(num_player))
    g.put()  # save in the database

    flash('New game was successfully posted') #displays message
    return redirect(url_for('show_games')) #takes you back to show games page, with the newly added game displayed


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        check_user = User.gql("WHERE username = :username", username=request.form['username'])
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

