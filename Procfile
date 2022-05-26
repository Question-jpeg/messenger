release: python manage.py migrate
web: daphne -b 0.0.0.0 -p $PORT DoneWithItBackend.asgi:application -t 300 --websocket_timeout 300