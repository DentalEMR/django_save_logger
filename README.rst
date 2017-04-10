django_save_logger
================

**django_save_logger** is an extension to the Django web framework that intercepts all Django writes and deletes
to its DB and saves to archive storage in a separate process(es).

Features
--------

- QueuedArchiver archives in separate process(es) instead of threats to avoid unexpected interations with web server threads.


**django_save_logger** can be easily added to your existing Django project with an
absolute minimum of code changes.


Installing
------------

You can install django_save_logger at the command line with the following command:

    $ pip install -e git+https://github.com/russellmorley/django_save_logger#egg=django_save_logger

or by adding the following line to your requirement.txt:

    --e git+https://github.com/russellmorley/django_save_logger#egg=django_save_logger

Testing and using MongoWriter requires a `MongoDB server <https://www.mongodb.com>`_.

Check the `CHANGES <https://github.com/russellmorley/django_save_logger/blob/master/CHANGES>`_
before installing.

Getting Started
-----------

Set the following in your Django project's settings to archive all db saves in a separate process by
printing them to stdout as JSON.

    from django_save_logger.archivers import QueuedArchiver

    from django_save_logger.jsonformatters import JsonStdOutWriter, JsonFormatter

    QueuedArchiver(writer=JsonStdOutWriter(), formatter=JsonFormatter())

How it works
-----------

Django_save_logger uses Django's `signal mechanism <https://docs.djangoproject.com/en/1.9/topics/signals/>`_ by hooking
its `post_save <https://docs.djangoproject.com/en/1.9/ref/signals/#django.db.models.signals.post_save>`_ and post_delete
signals for `some or all models in a project <https://github.com/russellmorley/django_save_logger/blob/master/django_save_logger/archivers.py#L21>`_.

The writer that writes to a `MongoDB <https://github.com/russellmorley/django_save_logger/blob/master/django_save_logger/writers/mongo.py>`_ will
put different models into different MongoDB collections.

The derived `QueuedArchiver <https://github.com/russellmorley/django_save_logger/blob/master/django_save_logger/archivers.py#L61>`_ writes
to a destination from a separate process so as to not reduce the performance of the process hosting Django or unexpectedly impact Django's constituent
threads of execution.

Testing
------------

Run tests by first setting the database ROLE and PASSWORD in tests/test_settings.py then executing the following command:

    $./runtests.py

Contributing
------------

Bug reports, bug fixes, and new features are always welcome. Please raise issues on the
`django_save_log source site <https://github.com/russellmorley/django_save_logger>`_, and submit
pull requests for any new code.


More information
----------------

The django_save_logger project was developed by Russell Morley. You can get the code
from the `django_save_logger project site <https://github.com/russellmorley/django_save_logger>`_.

-  `Website <http://www.compass-point.net/>`_
