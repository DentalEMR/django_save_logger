import os
from setuptools import setup


def read(fname):
  with open(os.path.join(os.path.dirname(__file__), fname), "r") as fp:
    return fp.read()


setup(
  name="django_save_logger",
  version="0.0.1",
  author="Russell Morley",
  author_email="russ@compass-point.net",
  description="A simple archiver that intercepts all Django writes to "
              "its DB and saves to archive storage on a separate thread.",
  license="MIT",
  keywords="django signals archive",
  url="https://github.com/russellmorley/django_save_logger",
  packages=["django_save_logger"],
  install_requires=[
    "pymongo",
    "boto",
    "django-model-utils==3.2.0",
  ],
  long_description=read("README.rst"),
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Framework :: Django",
    "License :: OSI Approved :: MIT License",
  ],
)
