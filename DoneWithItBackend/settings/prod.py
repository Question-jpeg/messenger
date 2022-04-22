from .common import *
import os
import dj_database_url

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['krezer-donewithit.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config() #reads the DATABASE_URL environment variable, parses the connection and returns dictionary
}

DEFAULT_FILE_STORAGE = 'api.storages.CustomS3Boto3Storage'

AWS_ACCESS_KEY_ID = os.environ['BUCKETEER_AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['BUCKETEER_AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['BUCKETEER_BUCKET_NAME']
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False