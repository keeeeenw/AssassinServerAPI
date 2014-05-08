from datetime import datetime, timedelta
from random import shuffle

from flask import request, session, url_for, abort, flash, jsonify, render_template
from google.appengine.ext.db import to_dict
from application import app
from models import Game, Player, GamePlayer, GameHistory
from decorators import crossdomain
from application.helpers import hash_password, verify_password, msg_generator, parse_game
from application import app
from flask import abort, flash, redirect, render_template, request, session, url_for
from google.appengine.ext.db import to_dict


"""
The functions below are the supported APIs
See documentation for details
"""


@app.route('/api/users', methods=['GET'])  # client makes request to that url
@crossdomain(origin='*')
# @login_required
def users():
    us = Player.all()
    users = {}
    for u in us:
        users[u.username] = {'username': u.username, 'email': u.email, 'creation_date': u.creation_date,
                             'player_id': u.key().id()}
    return jsonify(**users)


@app.route('/api/games/players/<int:player_id>', methods=['GET'])  # client makes request to that url
@crossdomain(origin='*')
# @login_required
def get_player(player_id):
    player = Player.get_by_id(player_id)
    game_players = GamePlayer.all().filter('player =', player)
    games = [game_player.game for game_player in game_players]
    info = {}
    for game in games:
        info[str(game.key().id())] = to_dict(game)
    return jsonify(**info)


@app.route('/api/players/new', methods=['POST'])
@crossdomain(origin='*')
def new_user():
    username = request.json.get['username']
    password = request.json.get['password']
    email = request.json.get['email']
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
    player = Player.all().filter('username =', user_data[0]).get()  # making sure they entered in their username correctly, checking against db
    if player is None:
        error = 'Username does not exist'
        return jsonify({'status': error, "user_id": None})
    elif not verify_password(user_data[1], player.password_hash):
        error = "Invalid password"
        return jsonify({'status': error, "user_id": None})
    else:
        session['logged_in'] = True
        flash('You were logged in')
        return jsonify({'status': True, "user_id": player.key().id()})  # this tells the client side that the user is successfully logged in


@app.route('/api/games', methods=['GET'])  # client makes request to that url
@crossdomain(origin='*')
# @login_required
def games():
    gs = Game.all()
    games = {}
    for g in gs:
        game_id = str(g.key().id_or_name())
        games[game_id] = parse_game(g)
    return jsonify(**games)  # does not render a page, just returns a Json


@app.route('/api/games', methods=['POST', 'OPTIONS'])  # client makes request to that url
@crossdomain(origin='*', headers=['content-type'])
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
            GameHistory(killer=killer, target=target, game=new_game, is_complete=False, confirm_msg=msg_generator()).put()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


@app.route('/api/games/<int:game_id>', methods=['GET'])  # client makes request to that url
@crossdomain(origin='*')
# @login_required
def get_game(game_id):
    game = Game.get_by_id(int(game_id))
    if game is None:
        return jsonify({'success': False, 'info': None})
    info = to_dict(game)
    people = [game_player.player.username for game_player in game.players]
    info['success'] = True
    info['participants'] = str(people)
    game_history = GameHistory.all().filter('game =', game).filter('is_complete =', False)
    info['survivors'] = [record.killer.username for record in game_history]
    return jsonify({'success': True, 'info': info})  # does not render a page, just returns a Json


@app.route('/api/user_info', methods=['GET'])  # client makes request to that url
@crossdomain(origin='*')
# @login_required
def get_user():
    user = None
    if 'username' in request.args:
        user = Player.all().filter('username =',request.args['username']).get()
    if user is None:
        return jsonify({'success': False, 'info': None})
    info = to_dict(user)
    info.pop("password_hash", None) #We don't want to show the hash
    info['success'] = True
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


@app.route('/api/kill', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['content-type'])
# @login_required
def kill():
    try:
        msg = request.json["msg"].upper()
        killer = Player.all().filter('username =', request.json["username"]).get()
        game = Game.get_by_id(int(request.json["game_id"]))
        old_game_history_success = GameHistory.all()\
            .filter('game =', game)\
            .filter('killer =', killer)\
            .filter('is_complete =', False).get()
        if msg == old_game_history_success.confirm_msg:
            will_be_last_kill = None
            if GameHistory.all().filter("game =", game).filter("is_complete =", False).count() == 2:
                will_be_last_kill = True
            old_target = old_game_history_success.target
            old_game_history_success.is_complete = True
            old_game_history_success.put()
            old_game_history_failure = GameHistory.all()\
                .filter('game =', game)\
                .filter('killer =', old_target)\
                .filter('is_complete =', False).get()
            old_game_history_failure.is_complete = True
            old_game_history_failure.put()
            if will_be_last_kill:
                game_player = GamePlayer.all().filter('game =', game).filter('player =', killer).get()
                game_player.is_winner = True
                game_player.put()
                return jsonify({"success": True, "info": "Your enemy has been slain! "})
            new_target = old_game_history_failure.target
            GameHistory(killer=killer, target=new_target, game=game, is_complete=False, confirm_msg=msg_generator()).put()
            return jsonify({"success": True, "info": "Your enemy has been slain! "})
        else:
            return jsonify({"success": False, "info": "The message is incorrect. Are you trying to game the system?!"})
    except:  # TODO: please handle exceptions in a more proper way
        return jsonify({"success": False, "info": "Something is fundamentally wrong. ", "Data received by server": str(request.data)})


@app.route('/api/game_player_status', methods=['GET'])
@crossdomain(origin='*')
# @login_required
def get_game_status():
    info = {"target": None, "in_game": False, "game_exists": False, "msg": None, "player_exists": False, "game_completed": False, "time_left": None}
    try:
        game = Game.get_by_id(int(request.args["game_id"]))
        if game is None:
            info["msg"] = "Game does not exists. "
            return jsonify(info)
        info["game_exists"] = True
        killer = Player.all().filter('username =', request.args["username"]).get()
        if killer is None:
            info["msg"] = "Player trying to kill does not exist. "
            return jsonify(info)
        info["player_exists"] = True
        player_in = GamePlayer.all().filter('game =', game).filter('player =', killer).get()
        if player_in is None:
            info["msg"] = "Player trying to kill is not in this game. "
            return jsonify(info)
        info["in_game"] = True
        if GameHistory.all().filter("game =", game).filter("is_complete =", False).count() == 0:
            info["game_completed"] = True
            game_player = GamePlayer.all().filter('game =', game).filter('is_winner =', True).get()
            info["winner_name"] = str(game_player.player.username)
            return jsonify(info)
        to_kill_game_history = GameHistory.all().filter('killer =', killer).filter('game =', game).filter('is_complete', False).get()
        be_killed_game_history = GameHistory.all().filter('target =', killer).filter('game =', game).filter('is_complete', False).get()
        if to_kill_game_history is None:
            return jsonify(info)
        else:
            info["time_left"] = to_kill_game_history.assign_date + timedelta(hours=1)
            info["target"] = to_kill_game_history.target.username
            info["msg"] = be_killed_game_history.confirm_msg
            return jsonify(info)
    except:
        # info["time_left"] = str(datetime.datetime.now())
        info["msg"] = "Something is fundamentally wrong. "
        return jsonify(info)

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
