from .common import *
import os
import dj_database_url

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['krezer-donewithit.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config() #reads the DATABASE_URL environment variable, parses the connection and returns dictionary
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ['REDIS_URL'],],
        },
    },
}

DEFAULT_FILE_STORAGE = 'api.storages.CustomS3Boto3Storage'

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_BUCKET_NAME']
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False
# Finally done