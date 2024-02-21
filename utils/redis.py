#!/usr/bin/env python3

import redis

class RedisClient():
    """Redis client
    """

    def __init__(self):
       self.client = redis.Redis(decode_responses=True)

    def isAlive(self):
        return self.client.ping()

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value, expiry):
        return self.client.set(key, value, ex=expiry)

    def delete(self, key):
        return self.client.delete(key)


redisClient = RedisClient()
