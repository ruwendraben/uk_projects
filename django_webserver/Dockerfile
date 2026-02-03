FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./django_webserver/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./django_webserver /app

ENV PORT=8000
EXPOSE 8000

CMD ["gunicorn", "webserver_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
