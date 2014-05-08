"""
Helper functions
"""
import hashlib
from random import choice, shuffle
import string


def hash_password(password):
    return hashlib.md5(password).hexdigest()


def verify_password(password, hashed_password):
    return hashlib.md5(password).hexdigest() == hashed_password


def msg_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(choice(chars) for _ in range(size))

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
