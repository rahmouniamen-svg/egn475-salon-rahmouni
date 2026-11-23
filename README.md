# Bella Vista Salon — EGN 475 Week 4 Assignment 4.1

Flask + SQLite app for Bella Vista Salon (Option B). Every screen is a route
with its own Jinja template, all sharing `templates/base.html`. Services are
stored in a SQLite database (`schema.sql`, `db.py`); the database file itself
lives in `instance/` and is never committed.

## Routes

| Route | Screen |
|---|---|
| `/` | Home |
| `/services` | Services list (from the database) |
| `/services/<int:service_id>` | Service detail (404 if missing) |
| `/admin/services/new` | Staff form to add a service (GET shows, POST saves) |
| `/book` | Book an appointment (display-only form) |
| `/calendar` | Staff calendar |
| `/appointments` | My appointments |

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app init-db
flask --app app run --debug
```

Then visit http://127.0.0.1:5000/ and click through every screen.
Visit `/services/999` to see the custom 404 page.
Add a service at `/admin/services/new` — it stays listed after a restart,
because it is saved in `instance/salon.sqlite`.

## Tests

```bash
python -m pytest -q
```

14 tests: all six screens return 200, `/services/999` and `/services/abc`
return 404, prices show two decimals (`$45.00`), the list shows every service,
the new-service form shows, a valid POST saves and redirects, an empty name
is refused (400), and the seeded database has 7 services.
