from __future__ import print_function
from __future__ import unicode_literals

import logging
from copy import deepcopy
from datetime import date, datetime

from django.conf import settings
from django.core import serializers
from django.core.serializers.python import Serializer as PythonSerializer

from .archivers import BaseFormatter, BaseWriter

PYTHON_SERIALIZER_NAME = "pythonextra"


class AddFormatFieldsMixin(object):
  """ Overrides the method that sets pk and model on serialized object to add op and db_alias properties """
  def get_dump_object(self, obj):
    data = super(AddFormatFieldsMixin, self).get_dump_object(obj)
    data["op"] = obj._op
    data["db_alias"] = obj._db_alias
    return data


class PythonFormatter(BaseFormatter):

  def get_serializer_name(self):
    return PYTHON_SERIALIZER_NAME

  def finalize_format_obj(self, serializedinstance):
    return serializedinstance

  def format_obj(self, instance, op, db_alias):
    """
    Formatter that serializes an instance into a dictionary using an extension to Django's python serializer that
    adds in additional fields and returns the dictionary.
    """
    try:
      inst_copy = deepcopy(instance)
      # add two extra properties, serialize using enhanced serializer, then delete the properties.
      inst_copy._op = op
      inst_copy._db_alias = db_alias
      # PyMongo only supports datetime, not date
      # (http://api.mongodb.com/python/current/faq.html#how-can-i-save-a-datetime-date-instance)
      for attr, val in vars(inst_copy).iteritems():
        if type(val) is date:
          inst_copy.__setattr__(attr, datetime.combine(val, datetime.min.time()))

      # will use the natural_key() method to serialize any foreign key reference to objects of the type that
      # defines the method
      # https://docs.djangoproject.com/en/1.7/topics/serialization/#serialization-of-natural-keys
      serializedinstance = serializers.serialize(
        self.get_serializer_name(),
        [inst_copy],
        use_natural_foreign_keys=True
      )
      del inst_copy._op
      del inst_copy._db_alias
      return self.finalize_format_obj(serializedinstance)
    except Exception as ex:
      logging.error(ex)


class Serializer(AddFormatFieldsMixin, PythonSerializer):
  pass


# Adds the new serializer to django's python serializer when imported in settings.
if hasattr(settings, 'SERIALIZATION_MODULES') and settings.SERIALIZATION_MODULES:
  settings.SERIALIZATION_MODULES[PYTHON_SERIALIZER_NAME] = "django_save_logger.pythonformatters"
else:
  settings.SERIALIZATION_MODULES = {
    PYTHON_SERIALIZER_NAME: "django_save_logger.pythonformatters"
  }


class PythonStdOutWriter(BaseWriter):
  """ Default Python writer that outputs formatted object to logger """
  def write(self, key, formatted_obj):
    if key is not None and formatted_obj is not None:
      print("Key: {}; Serialized objects: {}".format(key, str(formatted_obj)))
    else:
      raise Exception("Either key and/or formatted_dict parameters is None")
