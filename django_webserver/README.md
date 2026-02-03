# ABC Data Analytics Platform

Django-based multi-tenant data analytics application for organizations.

## Phase 1: Onboarding & Multi-Tenancy

Features:
- Organization signup with admin email
- User authentication & role-based access (admin/viewer)
- Multi-tenant architecture (OrganizationUser model)
- Data source management (PostgreSQL, MySQL, CSV)

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd django_webserver
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

## Architecture

```
Organization (1) ---- (many) OrganizationUser ---- (1) User
     |
     +---- (many) DataSource
```

- **Organization**: Company/client
- **OrganizationUser**: Links users to orgs with roles (admin/viewer)
- **DataSource**: Connected data sources (PostgreSQL, MySQL, CSV)

## Future Phases

- Phase 2: Data source connection & schema exploration
- Phase 3: Data modeling & transformations
- Phase 4: Dashboards & visualizations
- Phase 5: Scheduled data refreshes (Celery + RDS)

## Deployment

Simple options:
- **Elastic Beanstalk** (recommended): AWS-managed Python platform
- **EC2 + systemd**: Self-managed with Gunicorn
- **Heroku/Railway**: Quick cloud deployment
