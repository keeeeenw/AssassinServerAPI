"""
models.py

App Engine datastore models

"""
from google.appengine.ext import db
import hashlib
import uuid

"""
Here are the models
"""


class Game(db.Model):  # each class is a table, each field is a column
    title = db.StringProperty(required=True) #required=True means not nullable
    num_player = db.IntegerProperty(required=True)  # maximum number of player
    creation_date = db.DateTimeProperty(auto_now_add=True)
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()


class Player(db.Model):
    # __table_name__ = 'user'
    username = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)
    creation_date = db.DateTimeProperty(auto_now_add=True)
    email = db.StringProperty()


class GamePlayer(db.Model):
    join_date = db.DateTimeProperty(auto_now_add=True)
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()
    player = db.ReferenceProperty(Player, required=True, collection_name="games") #, collection_name='game_players111')
    game = db.ReferenceProperty(Game, required=True, collection_name="players")  # a 1-many relationship
    # is_finished = db.BooleanProperty()


class TargetHistory(db.Model):
    killer = db.ReferenceProperty(GamePlayer, collection_name="killerplayers") #killer can be many players
    target = db.ReferenceProperty(GamePlayer, collection_name="targetedplayers")#target can be many players
    assign_date = db.DateTimeProperty()
    isComplete = db.BooleanProperty()


"""
Helper functions
"""


def hash_password(password):
    # salt = uuid.uuid4().hex
    # return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ":" + salt
    return password


def verify_password(password, hashed_password):
    # password, salt = hashed_password.split(':')
    # return password == hashlib.sha256(salt.encode() + password.encode()).hexdigest()
    return password == hashed_password


"""
Let's create some fake data
"""


def bootstrap():
    """
        Adding bootstrap model objects to the database
    """
    game1 = Game(title="BattleRoyale", num_player=5)
    game1.put()
    game2 = Game(title="SQLAssassin", num_player=20)
    game2.put()
    game3 = Game(title="g_test", num_player=3)
    game3.put()

    # Seed an admin user, which equivalent to a normal user as for now
    user = Player(username="admin", password_hash=hash_password("default"))
    user.put()

    # Seed 10 users
    for i in range(0, 10):
        player = Player(username="u" + str(i), password_hash=hash_password("p" + str(i)))
        player.put()


    p10 = Player(username="u10", password_hash=hash_password("p10"))
    p10.put()
    p11 = Player(username="u11", password_hash=hash_password("p11"))
    p11.put()
    p12 = Player(username="u12", password_hash=hash_password("p12"))
    p12.put()

    # Seed a game

    # names = ["u1", "u2", "u3", "u10"]
    # for n in names:
    #     p = Player.gql("username=" + n).get()
    #     GamePlayer(game=game1, player=p).put()
        #     print("*************************** seeded gp: " + str(p.username))
        # else:
        #     print("*************************** temp not a player: " + str(type(p)))



    gameplayer1 = GamePlayer(game=game1, player=p10)
    # gameplayer1.isFinished = False
    gameplayer1.put()

    gameplayer2 = GamePlayer(game=game1, player=p11)
    # gameplayer2.isFinished = False
    gameplayer2.put()

    gameplayer3 = GamePlayer(game=game1, player=p12)
    # gameplayer3.isFinished = False
    gameplayer3.put()

    temp_player = Player.get_by_id(5821089435353088)

    print("**********************************" + temp_player.username)



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


# Using this because before_fist_request only registers one function
if Player.all() is None:
    cleanup()
    bootstrap()