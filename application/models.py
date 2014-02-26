"""
models.py

App Engine datastore models

"""
from google.appengine.ext import db

class Game(db.Model):
    title = db.StringProperty(required=True)
    num_player = db.IntegerProperty(required=True)

def bootstrap():
    """
        Adding bootstrap model objects to the database
    """
    game1 = Game(title="MacAssassin", num_player=5)
    game1.put()
    game2 = Game(title="SQLAssassin", num_player=20)
    game2.put()

if Game.all().count()==0: #run bootstrap if there is no data
    bootstrap()


