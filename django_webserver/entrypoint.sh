#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if needed..."
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@shopsonboard.com", "$DJANGO_SUPERUSER_PASSWORD")
    print("✅ Superuser 'admin' created")
else:
    print("✅ Superuser 'admin' already exists")
END
fi

echo "Starting Gunicorn..."
exec gunicorn webserver_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
