# NGO Reporting Tool (Flask)

A lightweight NGO/M&E reporting tool with:
- Projects
- Strategic Objectives (SO1, SO2...)
- Indicators
- Activities (optional link to indicator)
- Attendance/Reach (Male/Female)
- Period reach report (by SO + by Indicator)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Initialize DB (Flask-Migrate)

```bash
export FLASK_APP=app.py
flask db init
flask db migrate -m "init"
flask db upgrade
```

## Run

```bash
python app.py
```

Open:
- http://127.0.0.1:5000/

## CSRF (Flask-WTF)

CSRF protection is enabled globally using `CSRFProtect`.
All POST forms include a hidden `csrf_token`.

## Dashboard charts

Dashboard charts use Chart.js via CDN in `templates/dashboard/index.html`.


## ✉️ Contact Support (Email)

The app includes a Contact page at `/contact` that sends messages to an admin/support inbox via SMTP.

### Configure SMTP
Create a `.env` file (or export env vars) using `.env.example` as a guide:

- `MAIL_HOST`
- `MAIL_PORT` (default 587)
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_TO` (receiver inbox)
- `MAIL_USE_TLS` (true/false)

> Gmail users: enable 2‑step verification and use an **App Password**.

### Test
1. Start the app
2. Open `/contact`
3. Send a test message
4. Confirm it arrives in `MAIL_TO`


## Multi-tenant (Organisations + Users)

This app supports multiple organisations. Each user belongs to an organisation, and all projects/activities/reports are scoped to that organisation.

### Bootstrap first organisation and super admin

Run the app once to create the database tables, then run this in a Python shell:

```python
from app import create_app
from extensions import db
from models import Organisation, User

app = create_app()
with app.app_context():
    org = Organisation(name="Example NGO", slug="example-ngo")
    db.session.add(org)
    db.session.commit()

    admin = User(full_name="Super Admin", email="admin@example.com", role="super_admin", organisation_id=org.id, is_active=True)
    admin.set_password("ChangeMe123!")
    db.session.add(admin)
    db.session.commit()
```

Then login at `/auth/login`.

### Roles
- `staff`: normal user (data access in their organisation)
- `org_admin`: can manage users in their organisation
- `super_admin`: can manage organisations and all users
