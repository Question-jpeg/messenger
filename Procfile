release: python manage.py migrate
web: daphne -b 0.0.0.0 -p $PORT DoneWithItBackend.asgi:application --timeout 300