SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'tests", "django_save_logger'
]

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'dentalemr',
    'USER': 'ROLE',
    'PASSWORD': 'PASSWORD',
    'HOST': 'localhost',
    'PORT': '',
  }
}

MIDDLEWARE_CLASSES = (
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
)

