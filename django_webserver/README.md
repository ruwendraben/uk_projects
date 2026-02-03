# Django conversion of webserver.yaml

This minimal Django project reproduces the simple web page that the original
CloudFormation template wrote to NGINX's `index.html`.

Quick start (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd django_webserver
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Open http://127.0.0.1:8000/ to see the page.
