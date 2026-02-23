FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PORT=8000
EXPOSE 8000

# Create entrypoint script for migrations and superuser
RUN echo '#!/bin/bash\n\
python manage.py migrate --noinput\n\
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then\n\
  python manage.py shell << END\n\
from django.contrib.auth import get_user_model\n\
User = get_user_model()\n\
if not User.objects.filter(username="admin").exists():\n\
  User.objects.create_superuser("admin", "admin@shopsonboard.com", "$DJANGO_SUPERUSER_PASSWORD")\n\
END\n\
fi\n\
exec gunicorn webserver_project.wsgi:application --bind 0.0.0.0:8000 --workers 3\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
