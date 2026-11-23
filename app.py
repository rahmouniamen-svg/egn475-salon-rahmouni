"""Bella Vista Salon (Option B) — EGN 475 Week 4 Assignment 4.1.

Flask + SQLite. Services are read from the database (schema.sql, via db.py);
the staff calendar and My Appointments pages still use sample lists in Week 4
(their tables are seeded, and they move to the database in a later week).
Prices are stored as whole cents and shown with two decimals via the
``money`` filter.
"""

import os

from flask import Flask, abort, redirect, render_template, request, url_for

import db

app = Flask(__name__)
app.config["DATABASE"] = os.path.join(app.instance_path, "salon.sqlite")
os.makedirs(app.instance_path, exist_ok=True)
db.init_app(app)

# ---------------------------------------------------------------------------
# Sample data still used in Week 4 for the calendar / appointments pages
# (no stylists table yet in the Week 4 schema)
# ---------------------------------------------------------------------------

SAMPLE_STYLISTS = [
    {"id": 1, "name": "Sofia Marino", "role": "Senior Stylist"},
    {"id": 2, "name": "Elena Ruiz", "role": "Color Specialist"},
    {"id": 3, "name": "Maya Chen", "role": "Nail Artist"},
]

# Staff calendar: one fixed day, one flat list grouped by stylist in the view.
SAMPLE_BOOKINGS = [
    {"id": 1, "client": "Lucia Fernandez", "service_id": 1, "stylist_id": 1, "time": "9:00 AM", "status": "Confirmed"},
    {"id": 2, "client": "Ana Gomez", "service_id": 2, "stylist_id": 1, "time": "10:30 AM", "status": "Checked in"},
    {"id": 3, "client": "Camila Torres", "service_id": 3, "stylist_id": 2, "time": "9:30 AM", "status": "Confirmed"},
    {"id": 4, "client": "Valentina Ruiz", "service_id": 4, "stylist_id": 2, "time": "12:00 PM", "status": "Pending"},
    {"id": 5, "client": "Sofia Delgado", "service_id": 5, "stylist_id": 3, "time": "10:00 AM", "status": "Confirmed"},
    {"id": 6, "client": "Isabella Morales", "service_id": 6, "stylist_id": 3, "time": "11:30 AM", "status": "Pending"},
]

# My appointments: history for one sample client.
SAMPLE_APPOINTMENTS = [
    {"id": 1, "client": "Lucia Fernandez", "service_id": 1, "stylist_id": 1, "date": "2026-11-15", "time": "9:00 AM", "status": "Completed"},
    {"id": 2, "client": "Lucia Fernandez", "service_id": 5, "stylist_id": 3, "date": "2026-11-08", "time": "10:00 AM", "status": "Cancelled"},
    {"id": 3, "client": "Lucia Fernandez", "service_id": 3, "stylist_id": 2, "date": "2026-11-29", "time": "10:00 AM", "status": "Upcoming"},
    {"id": 4, "client": "Lucia Fernandez", "service_id": 2, "stylist_id": 1, "date": "2026-12-05", "time": "11:00 AM", "status": "Upcoming"},
]


def find_by_id(records, record_id):
    """Return the dict with the given id, or None if there is no match."""
    for record in records:
        if record["id"] == record_id:
            return record
    return None


def get_services():
    """All active services from the database, ordered by category then name."""
    return db.get_db().execute(
        "SELECT id, name, category, description, duration_minutes, price_cents"
        " FROM services WHERE active = 1 ORDER BY category, name"
    ).fetchall()


# ---------------------------------------------------------------------------
# Jinja helpers
# ---------------------------------------------------------------------------

@app.template_filter("money")
def money_filter(price_cents):
    """Show a price stored in whole cents with two decimals, e.g. $45.00."""
    # Integer arithmetic, not float division: 4500 cents -> $45.00 exactly.
    dollars, cents = divmod(int(price_cents), 100)
    return f"${dollars}.{cents:02d}"


@app.context_processor
def lookup_helpers():
    """Helpers so templates can look up a service/stylist by id."""

    def service_for(service_id):
        return db.get_db().execute(
            "SELECT * FROM services WHERE id = ?", (service_id,)
        ).fetchone()

    def stylist_for(stylist_id):
        return find_by_id(SAMPLE_STYLISTS, stylist_id)

    def status_label(status):
        return status

    return {
        "service_for": service_for,
        "stylist_for": stylist_for,
        "status_label": status_label,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    featured = db.get_db().execute(
        "SELECT id, name, category, description, duration_minutes, price_cents"
        " FROM services WHERE active = 1 ORDER BY id LIMIT 3"
    ).fetchall()
    return render_template("index.html", featured=featured)


@app.route("/services")
def services():
    all_services = get_services()
    # Group services by category, keeping the order they first appear in.
    grouped = {}
    for service in all_services:
        grouped.setdefault(service["category"], []).append(service)
    return render_template(
        "services.html", services=all_services, grouped_services=grouped
    )


@app.route("/services/<int:service_id>")
def service_detail(service_id):
    service = db.get_db().execute(
        "SELECT * FROM services WHERE id = ?", (service_id,)
    ).fetchone()
    if service is None:
        abort(404)
    related = db.get_db().execute(
        "SELECT id, name, category, description, duration_minutes, price_cents"
        " FROM services WHERE category = ? AND id != ? AND active = 1"
        " ORDER BY name LIMIT 3",
        (service["category"], service["id"]),
    ).fetchall()
    return render_template("service.html", service=service, related=related)


@app.route("/admin/services/new", methods=["GET", "POST"])
def service_new():
    """Staff form to add a service. GET shows the form, POST saves it."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "Hair").strip() or "Hair"
        description = request.form.get("description", "").strip()
        error = None
        try:
            duration_minutes = int(request.form.get("duration_minutes", ""))
            price_cents = int(round(float(request.form.get("price_dollars", "")) * 100))
            if duration_minutes <= 0 or price_cents < 0:
                raise ValueError
        except (TypeError, ValueError):
            duration_minutes = price_cents = None
            error = "Enter a duration in minutes and a price in dollars."
        if not name:
            error = "A service name is required."
        if error:
            return render_template(
                "service_new.html", error=error,
                name=name, category=category, description=description,
            ), 400
        database = db.get_db()
        database.execute(
            "INSERT INTO services (name, category, description,"
            " duration_minutes, price_cents, active)"
            " VALUES (?, ?, ?, ?, ?, 1)",
            (name, category, description, duration_minutes, price_cents),
        )
        database.commit()
        return redirect(url_for("services"))
    return render_template("service_new.html", error=None)


@app.route("/book")
def book():
    return render_template(
        "book.html", services=get_services(), stylists=SAMPLE_STYLISTS
    )


@app.route("/calendar")
def calendar():
    by_stylist = {stylist["id"]: [] for stylist in SAMPLE_STYLISTS}
    for booking in SAMPLE_BOOKINGS:
        by_stylist.setdefault(booking["stylist_id"], []).append(booking)
    return render_template(
        "calendar.html",
        stylists=SAMPLE_STYLISTS,
        by_stylist=by_stylist,
        bookings=SAMPLE_BOOKINGS,
    )


@app.route("/appointments")
def appointments():
    return render_template(
        "appointments.html", appointments=SAMPLE_APPOINTMENTS
    )


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
