SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    "tests", "django_save_logger"
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
)


