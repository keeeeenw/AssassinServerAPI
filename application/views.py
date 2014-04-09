from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify
from google.appengine.ext.db import to_dict
from application import app
from models import Game, Player, GamePlayer, GameHistory, verify_password, hash_password
from decorators import crossdomain
from random import shuffle

"""
The functions below are the supported APIs
"""


@app.route('/api/list_users', methods=['GET'])  # client makes request to that url
@crossdomain(origin='*')
# @login_required
def list_users():
    us = Player.all()
    users = {}
    for u in us:
        users[u.username] = {'username': u.username, 'email': u.email, 'creation_date': u.creation_date,
                             'id': u.key().id()}
    return jsonify(**users)  # does not render a page, just returns a Json


@app.route('/api/new_user', methods=['POST'])
def new_user():
    username = request.json.get['username']
    password = request.json.get['password']
    if username is None or password is None:
        abort(400)  # missing arguments
    # if User.query.filter_by(username = username).first is not None:
    # abort(400)  # username already exists
    user = Player(username=username)  # constructing new user
    hash_password(password)
    user.put()  # put user in db
    return jsonify({'username': user.username}), 201, {
        'Location': url_for('get_user', id=user.username, _external=True)}
    # return jsonify({'username': user.username}), 201, {'Location': url_for('get_user', id=user.id, _external=True)}


@app.route('/api/rest_login', methods=['POST', 'OPTIONS'])  # login for the app
@crossdomain(origin='*', headers=['content-type'])
def rest_login():
    error = None
    # The first item is username, and the second is password
    user_data = [str(request.json['username']), str(request.json['password'])]  # get this from the url
    check_user = Player.gql("WHERE username = :username", username=user_data[
        0])  # making sure they entered in their username correctly, checking against db
    if check_user.count() == 0:
        error = 'Username does not exist'
        return jsonify({'status': error})
    elif not verify_password(user_data[1], check_user.get().password_hash):
        error = "Invalid password"
        return jsonify({'status': error})
    else:
        session['logged_in'] = True
        flash('You were logged in')
        return jsonify({'status': True})  # this tells the client side that the user is successfully logged in


@app.route('/api/create_new_game', methods=['POST'])  # client makes request to that url
@crossdomain(origin='*')
# @login_required
def create_new_game():
    if Game.all().filter('title =', request.json['title']).count() == 0:
        name_of_player_to_join = list(set(request.json['players']))  # Makes sure each player is registered only once
        shuffle(name_of_player_to_join)
        players_to_join = [Player.all().filter('username =', name).get() for name in name_of_player_to_join]
        new_game = Game(title=request.json['title'], num_player=len(players_to_join))
        new_game.put()
        for i in range(-1, len(players_to_join)-1):
            killer = players_to_join[i]
            GamePlayer(game=new_game, player=killer).put()
            target = players_to_join[i+1]
            GameHistory(killer=killer, target=target, game=new_game, is_complete=False).put()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


@app.route('/api/list_games', methods=['GET'])  # client makes request to that url
@crossdomain(origin='*')
# @login_required
def list_games():
    gs = Game.all()
    games = {}
    for g in gs:
        games[str(g.key().id())] = {"title": g.title, "num_players": g.num_player}
    return jsonify(**games)  # does not render a page, just returns a Json


@app.route('/api/game_info', methods=['GET'])  # client makes request to that url
@crossdomain(origin='*')
# @login_required
def get_game():
    game = None
    if len(request.args) == 1:
        if 'game_id' in request.args:
            game = Game.get_by_id(int(request.args['game_id']))
            print(game.title)
        if 'title' in request.args:
            game = Game.all().filter('title =', request.args['title']).get()
    if game is None:
        return jsonify({'success': False, 'info': None})
    info = to_dict(game)
    people = [game_player.player.username for game_player in game.players]
    info['success'] = True
    info['participants'] = str(people)
    return jsonify({'success': True, 'info': info})  # does not render a page, just returns a Json


@app.route('/api/games_for_player', methods=['GET'])  # client makes request to that url
@crossdomain(origin='*')
# @login_required
def games_for_player():
    username = request.args['username']
    # get all users, find where username matches game player
    users = Player.all().filter('username =', username)

    if users.count() == 0:
        return jsonify({'success': False})
    else:
        user = users.get()
        game_players = user.games
        games = {}
        for gp in game_players:
            game = gp.game
            game_id = game.key().id_or_name()
            games[game_id] = parse_game(game)
        info = {"success": True, "games": games, "username": username}
        return jsonify(**info)


@app.route('/api/kill', methods=['GET', 'POST'])
@crossdomain(origin='*')
# @login_required
def kill():
    try:
        killer = Player.all().filter('username =', request.args["killer_name"]).get()
        old_target = Player.all().filter('username =', request.args["target_name"]).get()
        game = Game.all().filter('title =', request.args["game_title"]).get()
        old_game_history_success = GameHistory.all()\
            .filter('game =', game)\
            .filter('killer =', killer)\
            .filter('target =', old_target).get()
        old_game_history_success.is_complete = True
        old_game_history_success.put()
        old_game_history_failure = GameHistory.all()\
            .filter('game =', game)\
            .filter('killer =', old_target)\
            .filter('is_complete =', False).get()
        old_game_history_failure.is_complete = True
        old_game_history_failure.put()
        new_target = old_game_history_failure.target
        GameHistory(killer=killer, target=new_target, game=game, is_complete=False).put()
        return jsonify({"success": True})
    except:  # TODO: please handle exceptions in a more proper way
        return jsonify({"success": False})


@app.route('/api/game_player_status', methods=['GET'])
@crossdomain(origin='*')
# @login_required
def get_game_status():
    killer = Player.all().filter('username =', request.args["username"]).get()
    game = Game.all().filter('title =', request.args["title"]).get()
    game_history = GameHistory.all().filter('killer =', killer).filter('game =', game).filter('is_complete', False).get()
    if game_history is None:
        return jsonify({"target": game_history.target.username})
    else:
        return jsonify({"target": None})


"""
Helper functions to parse object for JSON returns
"""


def parse_game(game):
    game_id = game.key().id_or_name()
    gameInfo = {
        'game_id': game_id,
        'title': game.title,
        'num_player': game.num_player,
        'creation_date': game.creation_date,
        'start_time': game.start_time,
        'end_time': game.end_time,
    }
    return gameInfo


"""
    Use the functions below for the web application
"""


@app.route('/')  # calls root of the server, does the function below.  Take something and render something
def show_games():
    # db = get_db()
    # cur = db.execute('select title, num_player from game order by id desc')
    # games = cur.fetchall()

    # Getting all the games
    gs = Game.all()

    # Build dictionary 
    games = []
    for g in gs:
        games.append({'title': str(g.title), 'num_player': int(g.num_player)})

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

