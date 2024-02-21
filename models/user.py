#!/usr/bin/env python3

from bson.objectid import ObjectId
from utils.redis import redisClient
from utils.db_client import dbClient
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, **kwargs):
        self.id = str(kwargs.get('_id'))
        self.firstname = kwargs.get('firstname')
        self.lastname = kwargs.get('lastname')
        self.number = kwargs.get('number')
        self.password = kwargs.get('password')
    """
    @property
    def is_authenticated(self):
        usr = redisClient.get(f'auth_{self.id}')
        if not usr:
            return False
        return True

    @property
    def is_active(self):
        return self.is_authenticated

    @property
    def is_anonymous(self):
        return not self.is_authenticated
    """
    def get_id(self):
        return self.id

    @classmethod
    def get(cls, user_id):
        usr = dbClient.db.users.find_one({'_id': ObjectId(user_id)})
        print(usr)
        return cls(**usr)
