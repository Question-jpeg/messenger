from .common import *


DEBUG = True

SECRET_KEY = 'c_-0n*cl_fk066!yj#mmph68fc4il%p!=c58qp6j()u870$a=1'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'DoneWithIt',
        'USER': 'Test',
        'PASSWORD': '1234',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}