DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "my_db",
        "USER": "my_user",
        "PASSWORD": "my_password",
        "HOST": "my_host",
        "PORT": "5432",
    }
}

default_config = {
    "ES_HOST"           :   "my_es_host",
    "ES_PORT"           :   9200,
    "MONGO_HOST"        :   "my_mongo_host",
    "MONGO_PORT"        :   27017,
    }
