#!/usr/bin/env python3
"""Database client
"""
import pymongo

class DBClient():
    """Database client
    """
    
    def __init__(self):
        self.__client = pymongo.MongoClient('localhost', 27017)
        self.db = self.__client['xchange']

    def isAlive(self):
        return True if self.db else False

dbClient = DBClient()
