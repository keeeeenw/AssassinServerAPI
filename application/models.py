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
    join_date = db.DateTimeProperty(required=True)
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()
    player = db.ReferenceProperty(User, collection_name="players")
    game = db.ReferenceProperty(Game, collection_name="games") #a 1-many relationship
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
    game1 = Game(title="BattleRoyal", num_player=5)
    game1.put()
    game2 = Game(title="SQLAssassin", num_player=20)
    game2.put()

    user1 = User(username="admin", password_hash=hash_password("default"))
    user1.put()
    user2 = User(username="u1", password_hash=hash_password("p1"))
    user2.put()
    user3 = User(username="u2", password_hash=hash_password("p2"))
    user3.put()


def cleanup():
    for user in User.all():
        if isinstance(user, User):
            user.delete()
    for game in Game.all():
        if isinstance(game, Game):
            game.delete()


# if Game.all().count() == 0 or User.all().count() == 0:  # run bootstrap if there is no data
# As for now, always bootstrap for development purposes
cleanup()
bootstrap()
