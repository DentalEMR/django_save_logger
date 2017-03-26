from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from .models import Parent, Child
from django_save_logger.archivers import Archiver, QueuedArchiver
from django_save_logger.jsonformatters import JsonStdOutWriter, JsonFormatter
from django_save_logger.pythonformatters import PythonStdOutWriter, PythonFormatter
from django_save_logger.writers.mongo import MongoWriter, URL, PORT, MONGO_DB
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from pymongo import MongoClient

from django_save_logger.monitors import LoginEventMonitor, SystemEventModel, LoginEventPersistMonitor
from django_save_logger.models import SystemEventModel

#from writers.s3 import BotoWriter
#from writers.mongo import MongoWriter
#import threading
import time
import datetime
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
        self.date = datetime.date.today()
        self.datetime = datetime.datetime.now()

    def tearDown(self):
       self.archiver.destroy()

    def test_archiver_write(self):
        with capture_output() as (out, err):
            self.parent = Parent.objects.create()
            time.sleep(5)
            self.child = Child.objects.create(parent = self.parent, date_field=self.date, datetime_field=self.datetime)
            outputOut = out.getvalue().strip()
            self.assertEqual(outputOut, 'Key: 1; Serialized objects: [{"fields": {"char_field": "Parent CharField contents."}, "model": "tests.parent", "op": "CREATE", "db_alias": "default", "pk": 1}]\nKey: 1; Serialized objects: [{"fields": {"parent": 1, "char_field": "Child CharField contents.", "datetime_field": "' + self.datetime.isoformat()[:23] + '", "decimal_field": 3.434, "date_field": "' + datetime.datetime.combine(self.date, datetime.datetime.min.time()).isoformat()[:23] + '", "text_field": "Child TextField contents."}, "model": "tests.child", "op": "CREATE", "db_alias": "default", "pk": 1}]')

class QueuedArchiverJsonFormatterUnitTests(TestCase):
    def setUp(self):
        self.archiver = QueuedArchiver(writer=JsonStdOutWriter(), formatter=JsonFormatter())
        self.archiver.connect_models()
        self.date = datetime.date.today()
        self.datetime = datetime.datetime.now()


    def tearDown(self):
        self.archiver.destroy()

    def test_archiver_write(self):
        self.parent = Parent.objects.create()
        time.sleep(5)
        self.child = Child.objects.create(parent = self.parent, date_field=self.date, datetime_field=self.datetime)
        self.archiver.destroy()


class ArchverPythonFormatterUnitTests(TestCase):
    def setUp(self):
        self.archiver = Archiver(writer=PythonStdOutWriter(), formatter=PythonFormatter())
        self.archiver.connect_models()
        self.date = datetime.date.today()
        self.datetime = datetime.datetime.now()

    def tearDown(self):
       self.archiver.destroy()

    def test_archiver_write(self):
        with capture_output() as (out, err):
            self.parent = Parent.objects.create()
            time.sleep(5)
            self.child = Child.objects.create(parent = self.parent, date_field=self.date, datetime_field=self.datetime)
            outputOut = out.getvalue().strip()
            self.assertEqual(outputOut, "Key: 2; Serialized objects: [{u'fields': {'char_field': u'Parent CharField contents.'}, u'model': u'tests.parent', 'op': 'CREATE', 'db_alias': 'default', u'pk': 2}]\nKey: 2; Serialized objects: [{u'fields': {'parent': 2, 'char_field': u'Child CharField contents.', 'datetime_field': " + repr(self.datetime) + ", 'decimal_field': 3.434, 'date_field': " + repr(datetime.datetime.combine(self.date, datetime.datetime.min.time())) + ", 'text_field': u'Child TextField contents.'}, u'model': u'tests.child', 'op': 'CREATE', 'db_alias': 'default', u'pk': 2}]")
            self.assertIs(type(self.child.date_field), datetime.date)   


class QueuedArchiverPythonFormatterUnitTests(TestCase):
    def setUp(self):
        self.archiver = QueuedArchiver(writer=PythonStdOutWriter(), formatter=PythonFormatter())
        self.archiver.connect_models()
        self.date = datetime.date.today()
        self.datetime = datetime.datetime.now()


    def tearDown(self):
        self.archiver.destroy()

    def test_archiver_write(self):
        parent = Parent.objects.create()
        time.sleep(5)
        self.child = Child.objects.create(parent = parent, date_field=self.date, datetime_field=self.datetime)
        self.archiver.destroy()


class MongoArchiverUnitTests(TestCase):
    def setUp(self):
        self.client = MongoClient(URL, PORT)
        self.db = self.client[MONGO_DB]

        self.archiver = QueuedArchiver(writer=MongoWriter(), formatter=PythonFormatter())
        self.archiver.connect_models()
        self.date = datetime.date.today()
        self.datetime = datetime.datetime.now()


    def tearDown(self):
        self.archiver.destroy()
        self.client.drop_database(MONGO_DB)

    def test_archiver_write(self):
        parent = Parent.objects.create()
        child = Child.objects.create(parent = parent, date_field=self.date, datetime_field=self.datetime)
        self.archiver.destroy()

        collection = self.db['tests.child']
        for record in collection.find():
            del record['_id']
            # Mongo appears to save datetime in resolution of milliseconds instead of microseconds.
            datetime_to_millis = self.datetime.replace(microsecond = self.datetime.microsecond - (self.datetime.microsecond % 1000))
            self.assertEqual(str(record), "{u'db_alias': u'default', u'fields': {u'parent': 3, u'char_field': u'Child CharField contents.', u'datetime_field': " + repr(datetime_to_millis) + ", u'decimal_field': 3.434, u'date_field': " + repr(datetime.datetime.combine(self.date, datetime.datetime.min.time())) + ", u'text_field': u'Child TextField contents.'}, u'pk': 3, u'model': u'tests.child', u'op': u'CREATE'}")

        collection = self.db['tests.parent']
        for record in collection.find():
            del record['_id']
            self.assertEqual(str(record), "{u'db_alias': u'default', u'fields': {u'char_field': u'Parent CharField contents.'}, u'pk': 3, u'model': u'tests.parent', u'op': u'CREATE'}")




class LoginEventMonitorTests(TestCase):
    def setUp(self):
      self.logger = logging.getLogger('django_save_logger.monitors')
      self.stream = StringIO()
      self.handler = logging.StreamHandler(self.stream)
      self.logger.addHandler(self.handler)
      self.logger.setLevel(logging.INFO)

      self.factory = RequestFactory()
      self.user = User.objects.create_user('billy', 'billy@dentalemr.com', 'password123')


    def tearDown(self):
      self.login_monitor.destroy()
      self.logger.removeHandler(self.handler)

    def create_session_store():
      engine = import_module(settings.SESSION_ENGINE)
      store = engine.SessionStore()
      store.save()
      return store

    def test_successful_login_logout(self):
      self.login_monitor = LoginEventMonitor().connect()
      request = self.factory.get('/login')
      request.session = SessionStore()
      user_ = authenticate(username='billy', password='password123')
      self.assertIsNotNone(user_)
      login(request, user_)
      request.user = user_
      logout(request)
      self.assertEqual(
        self.stream.getvalue(), 
        'logged_in: pk: 2, username: billy, request info: {"HTTP_USER_AGENT": "", "REMOTE_ADDR": "127.0.0.1", "HTTP_CLIENT_IP": "", "path": "/login", "HTTP_FORWARDED_FOR": "", "HTTP_X_FORWARDED": "", "method": "GET", "HTTP_FORWARDED": ""}\nlogged_out: pk: 2, username: billy, request info: {"HTTP_USER_AGENT": "", "REMOTE_ADDR": "127.0.0.1", "HTTP_CLIENT_IP": "", "path": "/login", "HTTP_FORWARDED_FOR": "", "HTTP_X_FORWARDED": "", "method": "GET", "HTTP_FORWARDED": ""}\n'
      )

    def test_successful_login_logout_with_extra_info(self):
      self.login_monitor = LoginEventMonitor(
        extra_user_attr_infos = [
          {
            'title': 'Email',
            'attr': 'email'
          }
        ]
      ).connect()

      request = self.factory.get('/login')
      request.session = SessionStore()
      user_ = authenticate(username='billy', password='password123')
      self.assertIsNotNone(user_)
      login(request, user_)
      request.user = user_
      logout(request)
      self.assertEqual(
        self.stream.getvalue(), 
        'logged_in: pk: 3, username: billy, request info: {"HTTP_USER_AGENT": "", "REMOTE_ADDR": "127.0.0.1", "HTTP_CLIENT_IP": "", "path": "/login", "HTTP_FORWARDED_FOR": "", "HTTP_X_FORWARDED": "", "method": "GET", "HTTP_FORWARDED": ""}, Email: billy@dentalemr.com\nlogged_out: pk: 3, username: billy, request info: {"HTTP_USER_AGENT": "", "REMOTE_ADDR": "127.0.0.1", "HTTP_CLIENT_IP": "", "path": "/login", "HTTP_FORWARDED_FOR": "", "HTTP_X_FORWARDED": "", "method": "GET", "HTTP_FORWARDED": ""}, Email: billy@dentalemr.com\n'
      )

    def test_failed_login(self):
      self.login_monitor = LoginEventMonitor().connect()
      request = self.factory.get('/login')
      request.session = SessionStore()
      user = authenticate(username='jimmy', password='password123')
      self.assertIsNone(user)
      self.assertEqual(
        self.stream.getvalue(), 
        'login_failed: pk: <no user>, username: <no user>, request info: None{"username": "jimmy", "password": "********************"}\n'
      )


class LoginEventPersistMonitorTests(TestCase):
    def setUp(self):
      self.logger = logging.getLogger('django_save_logger.monitors')
      self.stream = StringIO()
      self.handler = logging.StreamHandler(self.stream)
      self.logger.addHandler(self.handler)
      self.logger.setLevel(logging.INFO)

      self.factory = RequestFactory()
      self.user = User.objects.create_user('billy', 'billy@dentalemr.com', 'password123')


    def tearDown(self):
      self.login_monitor.destroy()

    def create_session_store():
      engine = import_module(settings.SESSION_ENGINE)
      store = engine.SessionStore()
      store.save()
      return store

    def test_successful_login_logout(self):
      self.login_monitor = LoginEventPersistMonitor().connect()
      request = self.factory.get('/login')
      request.session = SessionStore()
      user_ = authenticate(username='billy', password='password123')
      self.assertIsNotNone(user_)
      login(request, user_)
      request.user = user_
      logout(request)
      login_events = SystemEventModel.objects.all()
      self.assertIsInstance(login_events[0], SystemEventModel)
      self.assertEqual(login_events[0].type, 'logged_in')
      self.assertEqual(
        User.objects.get(pk = login_events[0].user_pk).username, 
        'billy'
      )
      self.assertIsInstance(login_events[1], SystemEventModel)
      self.assertEqual(login_events[1].type, 'logged_out')
      self.assertEqual(
        User.objects.get(pk = login_events[1].user_pk).username,
        'billy'
      )
      self.assertEqual(
        self.stream.getvalue(), 
        'logged_in: pk: 5, username: billy, request info: {"HTTP_USER_AGENT": "", "REMOTE_ADDR": "127.0.0.1", "HTTP_CLIENT_IP": "", "path": "/login", "HTTP_FORWARDED_FOR": "", "HTTP_X_FORWARDED": "", "method": "GET", "HTTP_FORWARDED": ""}\nlogged_out: pk: 5, username: billy, request info: {"HTTP_USER_AGENT": "", "REMOTE_ADDR": "127.0.0.1", "HTTP_CLIENT_IP": "", "path": "/login", "HTTP_FORWARDED_FOR": "", "HTTP_X_FORWARDED": "", "method": "GET", "HTTP_FORWARDED": ""}\n'
      )

    def test_successful_login_logout_with_extra_info(self):
      self.login_monitor = LoginEventPersistMonitor(
        extra_user_attr_infos = [
          {
            'title': 'Email',
            'attr': 'email'
          }
        ]
      ).connect()

      request = self.factory.get('/login')
      request.session = SessionStore()
      user_ = authenticate(username='billy', password='password123')
      self.assertIsNotNone(user_)
      login(request, user_)
      request.user = user_
      logout(request)
      login_events = SystemEventModel.objects.all()
      self.assertIsInstance(login_events[0], SystemEventModel)
      self.assertEqual(login_events[0].type, 'logged_in')
      self.assertEqual(
        User.objects.get(pk = login_events[0].user_pk).username, 
        'billy'
      )
      self.assertIsInstance(login_events[1], SystemEventModel)
      self.assertEqual(login_events[1].type, 'logged_out')
      self.assertEqual(
        User.objects.get(pk = login_events[1].user_pk).username,
        'billy'
      )
      self.assertEqual(
        self.stream.getvalue(), 
        'logged_in: pk: 6, username: billy, request info: {"HTTP_USER_AGENT": "", "REMOTE_ADDR": "127.0.0.1", "HTTP_CLIENT_IP": "", "path": "/login", "HTTP_FORWARDED_FOR": "", "HTTP_X_FORWARDED": "", "method": "GET", "HTTP_FORWARDED": ""}, Email: billy@dentalemr.com\nlogged_out: pk: 6, username: billy, request info: {"HTTP_USER_AGENT": "", "REMOTE_ADDR": "127.0.0.1", "HTTP_CLIENT_IP": "", "path": "/login", "HTTP_FORWARDED_FOR": "", "HTTP_X_FORWARDED": "", "method": "GET", "HTTP_FORWARDED": ""}, Email: billy@dentalemr.com\n'
      )

    def test_failed_login(self):
      self.login_monitor = LoginEventPersistMonitor().connect()
      request = self.factory.get('/login')
      request.session = SessionStore()
      user = authenticate(username='jimmy', password='password123')
      self.assertIsNone(user)
      login_events = SystemEventModel.objects.all()
      self.assertEqual(login_events.count(), 1)
      self.assertIsNone(login_events[0].user_pk)
      self.assertEqual(login_events[0].other_info,
        '{"username": "jimmy", "password": "********************"}'
      )
