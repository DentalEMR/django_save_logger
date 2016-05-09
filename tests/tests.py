from django.test import TestCase
from .models import Parent, Child
from django_save_logger.archivers import Archiver, QueuedArchiver
from django_save_logger.jsonformatters import JsonStdOutWriter, JsonFormatter
from django_save_logger.pythonformatters import PythonStdOutWriter, PythonFormatter
from django_save_logger.writers.mongo import MongoWriter, URL, PORT, MONGO_DB
from pymongo import MongoClient

#from writers.s3 import BotoWriter
#from writers.mongo import MongoWriter
#import threading
import time
import sys
from StringIO import StringIO
import subprocess
from contextlib import contextmanager
import logging
from django.conf import settings

@contextmanager
def capture_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

class ArchverJsonFormatterUnitTests(TestCase):
    """Run tests by calling ./manage.py test app.
    1. Test database created.
    2. A TestCase instance is created for each test in each test case:
    3. For each instance (one at a time):
       a) the database is flushed
       b) fixtures are installed
       c) setUp() is called
       d) the (single) test is called
       e) tearDown() is called
    4. The test database is destroyed
    """
    def setUp(self):
        self.archiver = Archiver(writer=JsonStdOutWriter(), formatter=JsonFormatter())
        self.archiver.connect_models()

    def tearDown(self):
       self.archiver.destroy()

    def test_archiver_write(self):
        with capture_output() as (out, err):
            self.parent = Parent.objects.create()
            time.sleep(5)
            self.child = Child.objects.create(parent = self.parent)
            outputOut = out.getvalue().strip()
            self.assertEqual(outputOut, 'Key: 1; Serialized objects: [{"fields": {"created_at": "' + self.parent.created_at.isoformat() + '", "char_field": "Parent CharField contents."}, "model": "tests.parent", "op": "CREATE", "db_alias": "default", "pk": 1}]\nKey: 1; Serialized objects: [{"fields": {"decimal_field": 3.434, "char_field": "Child CharField contents.", "parent": 1, "text_field": "Child TextField contents.", "date_field": "' + self.child.date_field.isoformat()[:23] + '"}, "model": "tests.child", "op": "CREATE", "db_alias": "default", "pk": 1}]')
        print("\nArchiver's Child's date_field is: {}. Should be different from output from QueuedArchiver output's child's date_field.\n".format(self.child.date_field.isoformat()[:23]))

class QueuedArchiverJsonFormatterUnitTests(TestCase):
    def setUp(self):
        self.archiver = QueuedArchiver(writer=JsonStdOutWriter(), formatter=JsonFormatter())
        self.archiver.connect_models()


    def tearDown(self):
        self.archiver.destroy()

    def test_archiver_write(self):
        self.parent = Parent.objects.create()
        time.sleep(5)
        self.child = Child.objects.create(parent = self.parent)
        self.archiver.destroy()


class ArchverPythonFormatterUnitTests(TestCase):
    def setUp(self):
        self.archiver = Archiver(writer=PythonStdOutWriter(), formatter=PythonFormatter())
        self.archiver.connect_models()

    def tearDown(self):
       self.archiver.destroy()

    def test_archiver_write(self):
        with capture_output() as (out, err):
            self.parent = Parent.objects.create()
            time.sleep(5)
            self.child = Child.objects.create(parent = self.parent)
            outputOut = out.getvalue().strip()
            self.assertEqual(outputOut, "Key: 2; Serialized objects: [{u'fields': {'created_at': " + repr(self.parent.created_at) + ", 'char_field': u'Parent CharField contents.'}, u'model': u'tests.parent', 'op': 'CREATE', 'db_alias': 'default', u'pk': 2}]\nKey: 2; Serialized objects: [{u'fields': {'decimal_field': 3.434, 'char_field': u'Child CharField contents.', 'parent': 2, 'text_field': u'Child TextField contents.', 'date_field': " + repr(self.child.date_field) + "}, u'model': u'tests.child', 'op': 'CREATE', 'db_alias': 'default', u'pk': 2}]")

        print("\nArchiver's Child's date_field is: {}. Should be different from output from QueuedArchiver output's child's date_field.\n".format(self.child.date_field.isoformat()[:23]))

class QueuedArchiverPythonFormatterUnitTests(TestCase):
    def setUp(self):
        self.archiver = QueuedArchiver(writer=PythonStdOutWriter(), formatter=PythonFormatter())
        self.archiver.connect_models()


    def tearDown(self):
        self.archiver.destroy()

    def test_archiver_write(self):
        parent = Parent.objects.create()
        time.sleep(5)
        child = Child.objects.create(parent = parent)
        self.archiver.destroy()


class MongoArchiverUnitTests(TestCase):
    def setUp(self):
        self.client = MongoClient(URL, PORT)
        db = self.client[MONGO_DB]
        self.collection = db['tests.parent']

        self.archiver = QueuedArchiver(writer=MongoWriter(), formatter=PythonFormatter())
        self.archiver.connect_models()


    def tearDown(self):
        self.archiver.destroy()
        self.client.drop_database(MONGO_DB)

    def test_archiver_write(self):
        parent = Parent.objects.create()
        self.archiver.destroy()

        for record in self.collection.find():
            del record['_id']
            self.assertEqual(str(record), "{u'db_alias': u'default', u'fields': {u'created_at': " + repr(parent.created_at) + ", u'char_field': u'Parent CharField contents.'}, u'pk': 3, u'model': u'tests.parent', u'op': u'CREATE'}")

