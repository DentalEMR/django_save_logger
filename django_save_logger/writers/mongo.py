from __future__ import absolute_import

from pymongo import MongoClient
from django.conf import settings

from ..archivers import BaseWriter

MONGO_HOST = getattr(settings, "MONGO_HOST", "localhost")
MONGO_PORT = getattr(settings, "MONGO_PORT", 27017)
MONGO_DB = getattr(settings, "MONGO_DB", "archive")


class MongoWriter(BaseWriter):
  def __init__(self, mongo_host=MONGO_HOST, mongo_port=MONGO_PORT, mongo_db=MONGO_DB):
    self.client = MongoClient(mongo_host, mongo_port)
    self.db = self.client[mongo_db]

  def write(self, key, formatted_obj):
    self.collection = self.db[formatted_obj[0]['model']]
    self.collection.insert_many(formatted_obj)

  def destroy(self):
    pass
