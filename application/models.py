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


class Game(db.Model): #each class is a table, each field is a column
    title = db.StringProperty(required=True) #required=True means not nullable
    num_player = db.IntegerProperty(required=True)  # maximum number of player
    start_up = db.StringListProperty(required=True)
    current_state = db.StringListProperty(required=True)
    creation_date = db.DateTimeProperty(auto_now_add=True)
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()


class User(db.Model):
    __table_name__ = 'user'
    username = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)
    creation_date = db.DateTimeProperty(auto_now_add=True)
    email = db.StringProperty()


class GamePlayer(db.Model):
    join_date = db.DateTimeProperty(auto_now_add=True)
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()
    player = db.ReferenceProperty(User, collection_name="game_players")
    game = db.ReferenceProperty(Game, collection_name="game_players") #a 1-many relationship
    isFinished = db.BooleanProperty()


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
    game1 = Game(title="BattleRoyale", num_player=5, start_up=["admin", "u1", "u2"], current_state=["admin", "u1", "u2"])
    game1.put()
    game2 = Game(title="SQLAssassin", num_player=20, start_up=["admin", "u1", "u2"], current_state=["admin", "u1", "u2"])
    game2.put()
    game3 = Game(title="g_test", num_player=3, start_up=["admin", "u1", "u2"], current_state=["admin", "u1", "u2"])
    game3.put()


    user1 = User(username="admin", password_hash=hash_password("default"))
    user1.put()

    for i in range(0, 10):
        user = User(username="u" + str(i), password_hash=hash_password("p" + str(i)))
        user.put()

    # gameplayer1 = GamePlayer()
    # gameplayer1.game = game1
    # gameplayer1.player = user2
    # gameplayer1.isFinished = False
    # gameplayer1.put()
    #
    # gameplayer2 = GamePlayer()
    # gameplayer2.game = game1
    # gameplayer2.player = user3
    # gameplayer2.isFinished = False
    # gameplayer2.put()
    #
    # gameplayer3 = GamePlayer()
    # gameplayer3.game = game2
    # gameplayer3.player = user2
    # gameplayer3.isFinished = False
    # gameplayer3.put()

def cleanup():
    for user in User.all():
        if isinstance(user, User):
            user.delete()
    for game in Game.all():
        if isinstance(game, Game):
            game.delete()
    for gp in GamePlayer.all():
        if isinstance(gp, GamePlayer):
            gp.delete()

# Using this because before_fist_request only registers one function
def set_up_wrapped():
    cleanup()
    bootstrap()