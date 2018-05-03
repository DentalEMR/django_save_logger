from __future__ import absolute_import
from __future__ import unicode_literals

import atexit
import logging
import multiprocessing
import signal
from django.core.serializers import serialize
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from pymongo import MongoClient


logger = logging.getLogger(__name__)


def cleanup_worker(pool, djsignals):
  for djsignal, receiver in djsignals:
    djsignal.disconnect(receiver)
  pool.terminate()
  pool.join()


def init_worker(worker_fn, host, port, dbname):
  signal.signal(signal.SIGINT, signal.SIG_IGN)
  worker_fn.db = MongoClient(host, port, serverSelectionTimeoutMS=5000)[dbname]


def run_worker(obj):
  return getattr(run_worker, "db")[obj["model"]].insert(obj)


def initialize(host, port, db_name, processes=1):
  pool = multiprocessing.Pool(processes=processes, initializer=init_worker, initargs=(run_worker, host, port, db_name))

  def post_delete_receiver(sender, **kwargs):
    obj = serialize("python", (kwargs["instance"],), use_natural_foreign_keys=True)[0]
    obj["op"] = "DELETE"
    obj["db_alias"] = kwargs["using"]
    result = pool.apply_async(run_worker, (obj,))
    try:
      result.get()
    except Exception as e:
      logger.error("Exception: %s Receiving signal 'post_delete' for %s with id '%s'", str(e), obj["model"], obj["pk"])

  def post_save_receiver(sender, **kwargs):
    obj = serialize("python", (kwargs["instance"],), use_natural_foreign_keys=True)[0]
    obj["op"] = "CREATE" if kwargs["created"] else "UPDATE"
    obj["db_alias"] = kwargs["using"]
    result = pool.apply_async(run_worker, (obj,))
    try:
      result.get()
    except Exception as e:
      logger.error("Exception: %s Receiving signal 'post_save' for %s with id '%s'", str(e), obj["model"], obj["pk"])

  djsignals = [(post_delete, post_delete_receiver), (post_save, post_save_receiver)]

  for djsignal, receiver in djsignals:
    djsignal.connect(receiver, weak=False)

  atexit.register(cleanup_worker, pool, djsignals)
