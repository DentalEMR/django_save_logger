from __future__ import print_function

import json
from django.core import serializers
from django.core.serializers.json import Serializer as JsonSerializer
from django.conf import settings

import logging
from .pythonformatters import AddFormatFieldsMixin, PythonFormatter, PythonStdOutWriter

JSON_SERIALIZER_NAME = "jsonextra"

class JsonFormatter(PythonFormatter):
    def get_serializer_name(self):
        return JSON_SERIALIZER_NAME

    def finalize_format_obj(self, serializedinstance):
        return  {'instance': serializedinstance}


class Serializer(AddFormatFieldsMixin, JsonSerializer):
    pass

# Adds the new serializer to django's json serializer when imported in settings.
if hasattr(settings, 'SERIALIZATION_MODULES') and settings.SERIALIZATION_MODULES:
    settings.SERIALIZATION_MODULES[JSON_SERIALIZER_NAME] = "django_save_logger.jsonformatters"
else:
    settings.SERIALIZATION_MODULES = {
        JSON_SERIALIZER_NAME: "django_save_logger.jsonformatters"
    }


class JsonStdOutWriter(PythonStdOutWriter):
    """ Default JSON writer that outputs formatted object to logger
    """
        
    def write(self, key, formatted_obj):
        instance = formatted_obj.get('instance')
        if instance is not None:
            print("Key: {}; Serialized objects: {}".format(key, instance))
        else:
            raise Exception("No instance provided to write")


class JsonLoggerWriter(PythonStdOutWriter):
    """ Default JSON writer that outputs formatted object to logger
    """
    def __init__(self):
        logging.basicConfig(level = logging.INFO)
        
    def write(self, key, formatted_obj):
        instance = formatted_obj.get('instance')
        if instance is not None:
            logging.info("Key: {}; Serialized objects: {}".format(key, instance))
        else:
            raise Exception("No instance provided to write")



