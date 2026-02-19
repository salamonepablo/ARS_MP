web: /opt/venv/bin/python manage.py migrate && /opt/venv/bin/python manage.py collectstatic --noinput && /opt/venv/bin/gunicorn config.wsgi --bind 0.0.0.0:$PORT
