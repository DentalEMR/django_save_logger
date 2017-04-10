from __future__ import absolute_import

import logging

from multiprocessing import Process, JoinableQueue

from django.db.models.signals import post_save
from django.db.models.signals import post_delete

CREATE_OP = "CREATE"
UPDATE_OP = "UPDATE"
DELETE_OP = "DELETE"


class Archiver(object):

  def __init__(self, writer, formatter, models=None):
    self.formatter = formatter
    self.writer = writer
    self.models = models

  def connect_models(self, models=None):
    if models is not None:
      for model in models:
        self.models.append(model)
    if self.models is not None:
      for model in self.models:
        post_save.connect(self.handle_post_save, sender=model)
        post_delete.connect(self.handle_post_delete, sender=model)
    else:
      post_save.connect(self.handle_post_save)
      post_delete.connect(self.handle_post_delete)

  def disconnect__models(self):
    if self.models is not None:
      for model in self.models:
        post_save.disconnect(self.handle_post_save, sender=model)
        post_delete.disconnect(self.handle_post_delete, sender=model)
    else:
      post_save.disconnect(self.handle_post_save)
      post_delete.disconnect(self.handle_post_delete)

  def handle_post_save(self, sender, **kwargs):
    # Params:
    # - sender=model class
    # - instance=instance saved
    # - created=true if created,
    # - update_fields=set of fields to update explicitly in save()
    # - using=db alias
    op = UPDATE_OP
    if kwargs["created"] is True:
      op = CREATE_OP
    self.writer.write(kwargs["instance"].pk, self.formatter.format_obj(kwargs["instance"], op, kwargs["using"]))

  def handle_post_delete(self, sender, **kwargs):
    # Params:
    # - sender=model class
    # - instance=instance deleted
    # - using = db alias
    self.writer.write(kwargs["instance"].pk, self.formatter.format_obj(kwargs["instance"], DELETE_OP, kwargs["using"]))

  def destroy(self):
    # django doesn't have shutdown mechanism anyway to don't focus on this yet.
    self.disconnect__models()
    self.writer.destroy()


class QueuedArchiver(Archiver):

  def __init__(self, writer, formatter, number_of_workers=1, models=None):
    super(QueuedArchiver, self).__init__(writer, formatter, models)
    self.q = JoinableQueue()
    for i in range(number_of_workers):
      self.p = Process(target=self.worker)
      self.p.daemon = True  # process will be terminated when parent process terminates.
      self.p.start()

  def handle_post_save(self, sender, **kwargs):
    op = UPDATE_OP
    if kwargs["created"] is True:
      op = CREATE_OP
    self.q.put((kwargs["instance"].pk, self.formatter.format_obj(kwargs["instance"], op, kwargs["using"])))

  def handle_post_delete(self, sender, **kwargs):
    self.q.put((kwargs["instance"].pk, self.formatter.format_obj(kwargs["instance"], DELETE_OP, kwargs["using"])))

  def worker(self):
    while True:
      try:
        pk, formattedDict = self.q.get()
        if pk is None and formattedDict is None:
          break
        else:
          self.writer.write(pk, formattedDict)
          self.q.task_done()
      except Exception as ex:
        # log the exception, but continue on. Don't want this process to die...
        logging.error(ex)

  def destroy(self):
    # if destroy not called, a daemon process will terminate when parent process dies.
    super(QueuedArchiver, self).destroy()
    # tells worker to terminate gracefully
    self.q.put((None, None))
    # waits for process to end
    self.p.join()
    self.writer.destroy()


class BaseFormatter(object):
  def format_obj(self, instance, op, db_alias):
    return ""


class BaseWriter(object):
  """ Writers must implement this interface """
  def write(self, key, formatted_dict):
    pass

  def destroy(self):
    pass
