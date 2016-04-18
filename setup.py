import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django_save_logger",
    version = "0.0.1",
    author = "Russell Morley",
    author_email = "russ@compass-point.net",
    description = ("A simple archiver that intercepts all Django writes to "
                                   "its DB and saves to archive storage on a separate thread."),
    license = "MIT",
    keywords = "django signals archive",
    url = "https://github.com/russellmorley/django_save_logger",
    packages=['django_save_logger',],
    install_requires=['pymongo==3.1', 'boto==2.38'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
    ],
)



