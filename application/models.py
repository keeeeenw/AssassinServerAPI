"""
models.py

App Engine datastore models

"""
from random import shuffle
from google.appengine.ext import db
import hashlib

"""
Here are the models
"""


class Game(db.Model):  # each class is a table, each field is a column
    title = db.StringProperty(required=True)  # required=True means not nullable
    num_player = db.IntegerProperty(required=True)  # maximum number of player
    creation_date = db.DateTimeProperty(auto_now_add=True)
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()


class Player(db.Model):
    username = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)
    creation_date = db.DateTimeProperty(auto_now_add=True)
    email = db.StringProperty()


class GamePlayer(db.Model):
    join_date = db.DateTimeProperty(auto_now_add=True)
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()
    player = db.ReferenceProperty(Player, required=True, collection_name="games")  # collection_name='game_players111')
    game = db.ReferenceProperty(Game, required=True, collection_name="players")  # a 1-many relationship


class GameHistory(db.Model):
    killer = db.ReferenceProperty(Player, required=True, collection_name="killer_history")  # killer can be many players
    target = db.ReferenceProperty(Player, required=True, collection_name="target_history")  # target can be many players
    game = db.ReferenceProperty(Game, required=True,
                                collection_name="game_history")  # target can be many players    filter('killer =', killer).
    assign_date = db.DateTimeProperty()
    is_complete = db.BooleanProperty(required=True)
    complete_time = db.DateTimeProperty()


"""
Helper functions
"""


def hash_password(password):
    return hashlib.md5(password).hexdigest()


def verify_password(password, hashed_password):
    if hashlib.md5(password) == hashed_password:
        return password == hashed_password
    else:
        return False


"""
Let's create some fake data
"""


def bootstrap():
    """
        Adding bootstrap model objects to the database
    """

    # Seed an admin user, which equivalent to a normal user as for now
    user = Player(username="admin", password_hash=hash_password("default"))
    user.put()

    # Seed 10 users and a game

    player_ids = []
    for i in range(0, 10):
        player = Player(username="u" + str(i), password_hash=hash_password("p" + str(i)))
        player_ids.append(player.put().id())

    player_names = player_ids[0:5]
    game_title = "Java"
    shuffle(player_names)
    players_to_join = [Player.get_by_id(player_id) for player_id in player_names]
    new_game = Game(title=game_title, num_player=len(players_to_join))
    new_game.put()
    for i in range(-1, len(players_to_join) - 1):
        killer = players_to_join[i]
        target = players_to_join[i + 1]
        if killer is not None and target is not None:
            GamePlayer(game=new_game, player=killer).put()
            GameHistory(killer=killer, target=target, game=new_game, is_complete=False).put()
        else:
            cleanup()
            print("Error in seeding!")


def cleanup():
    for user in Player.all():
        if isinstance(user, Player):
            user.delete()
    for game in Game.all():
        if isinstance(game, Game):
            game.delete()
    for gp in GamePlayer.all():
        if isinstance(gp, GamePlayer):
            gp.delete()
    for gh in GameHistory.all():
        if isinstance(gh, GameHistory):
            gh.delete()


# Using this because before_fist_request only registers one function
if Player.all().get() is None:
    cleanup()
    bootstrap()
