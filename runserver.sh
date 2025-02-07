python manage.py collectstatic --no-input
python manage.py migrate

gunicorn djcrm2.wsgi:application --bind 0.0.0.0:$PORT