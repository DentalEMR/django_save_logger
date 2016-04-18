from django_save_logger.archivers import BaseWriter
from pymongo import MongoClient
from django.conf import settings

if hasattr(settings, 'MONGO_SERVER_URL'):
    URL = settings.MONGO_SERVER_URL
else:
    URL = 'localhost'

if hasattr(settings, 'MONGO_SERVER_PORT'):
    PORT = settings.MONGO_SERVER_PORT
else:
    PORT = 27017

if hasattr(settings, 'MONGO_DB'):
    MONGO_DB = settings.MONGO_DB
else:
    MONGO_DB = 'archive'



class MongoWriter(BaseWriter):
    def __init__(self):
        self.client = MongoClient(URL, PORT)
        self.db = self.client[MONGO_DB]

    def write(self, key, formatted_obj):
        self.collection = self.db[formatted_obj[0]['model']]
        self.collection.insert_many(formatted_obj)

    def destroy(self):
        pass

