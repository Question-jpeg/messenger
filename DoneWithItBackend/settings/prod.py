from .common import *
import os
import dj_database_url

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['krezer-donewithit.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config() #reads the DATABASE_URL environment variable, parses the connection and returns dictionary
}