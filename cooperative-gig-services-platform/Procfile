release: python manage.py migrate --noinput
web: gunicorn coopgig.wsgi:application --bind 0.0.0.0:$PORT
