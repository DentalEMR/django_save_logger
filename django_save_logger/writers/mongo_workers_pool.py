from __future__ import absolute_import
from __future__ import unicode_literals

from django.core.serializers import serialize
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from multiprocessing import Pool
from pymongo import MongoClient


def set_worker_db(worker_fn, host, port, dbname):
  worker_fn.db = MongoClient(host, port)[dbname]


def worker(obj):
  getattr(worker, "db")[obj["model"]].insert(obj)


def initialize(host, port, db_name, processes=1):
  pool = Pool(processes=processes, initializer=set_worker_db, initargs=(worker, host, port, db_name))

  def post_delete_receiver(sender, **kwargs):
    obj = serialize("python", (kwargs["instance"],), use_natural_foreign_keys=True)[0]
    obj["op"] = "DELETE"
    obj["db_alias"] = kwargs["using"]
    pool.apply_async(worker, (obj,)).get()

  def post_save_receiver(sender, **kwargs):
    obj = serialize("python", (kwargs["instance"],), use_natural_foreign_keys=True)[0]
    obj["op"] = "CREATE" if kwargs["created"] else "UPDATE"
    obj["db_alias"] = kwargs["using"]
    pool.apply_async(worker, (obj,)).get()

  for signal, receiver in [(post_delete, post_delete_receiver), (post_save, post_save_receiver)]:
    signal.connect(receiver, weak=False)
