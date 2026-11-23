# Bella Vista Salon — EGN 475 Week 3 Assignment 3.1

Flask prototype for Bella Vista Salon (Option B). Every screen is a route
with its own Jinja template, all sharing `templates/base.html`. Data comes
from Python lists in `app.py` — no database yet (Week 4).

## Routes

| Route | Screen |
|---|---|
| `/` | Home |
| `/services` | Services list |
| `/services/<int:service_id>` | Service detail (404 if missing) |
| `/book` | Book an appointment (display-only form) |
| `/calendar` | Staff calendar |
| `/appointments` | My appointments |

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
```

Then visit http://127.0.0.1:5000/ and click through every screen.
Visit `/services/999` to see the custom 404 page.

## Tests

```bash
python -m pytest -q
```

10 tests: all six screens return 200, `/services/999` and `/services/abc`
return 404, prices show two decimals (`$45.00`), and the list shows every service.
