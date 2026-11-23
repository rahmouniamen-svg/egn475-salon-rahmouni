"""Bella Vista Salon (Option B) — EGN 475 Week 3 Assignment 3.1.

Every screen is a Flask route with its own Jinja template.
Data comes from Python lists of dicts (sample data only — no database yet).
Prices are stored as whole cents and shown with two decimals via the
``money`` filter.
"""

from flask import Flask, abort, render_template

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Sample data (shaped like future database rows)
# ---------------------------------------------------------------------------

SAMPLE_SERVICES = [
    {
        "id": 1,
        "name": "Signature Haircut",
        "category": "Hair",
        "price_cents": 4500,
        "duration_minutes": 60,
        "description": "Consultation, wash, precision cut and finish styling.",
    },
    {
        "id": 2,
        "name": "Blowout & Style",
        "category": "Hair",
        "price_cents": 3500,
        "duration_minutes": 45,
        "description": "Wash, blow-dry and styled finish for a polished look.",
    },
    {
        "id": 3,
        "name": "Balayage",
        "category": "Color",
        "price_cents": 12500,
        "duration_minutes": 150,
        "description": "Hand-painted highlights for a soft, sun-kissed blend.",
    },
    {
        "id": 4,
        "name": "Full Color & Gloss",
        "category": "Color",
        "price_cents": 8500,
        "duration_minutes": 120,
        "description": "Full color application with a shine gloss and treatment.",
    },
    {
        "id": 5,
        "name": "Classic Manicure",
        "category": "Nails",
        "price_cents": 3000,
        "duration_minutes": 45,
        "description": "Shape, cuticle care, polish and a relaxing hand massage.",
    },
    {
        "id": 6,
        "name": "Spa Pedicure",
        "category": "Nails",
        "price_cents": 5500,
        "duration_minutes": 60,
        "description": "Soak, exfoliation, nail care and polish in our spa chairs.",
    },
    {
        "id": 7,
        "name": "Bridal Updo",
        "category": "Hair",
        "price_cents": 7500,
        "duration_minutes": 90,
        "description": "Elegant updo styling for weddings and special occasions.",
    },
]

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
        return find_by_id(SAMPLE_SERVICES, service_id)

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
    featured = SAMPLE_SERVICES[:3]
    return render_template("index.html", featured=featured)


@app.route("/services")
def services():
    # Group services by category, keeping the order they first appear in.
    grouped = {}
    for service in SAMPLE_SERVICES:
        grouped.setdefault(service["category"], []).append(service)
    return render_template(
        "services.html", services=SAMPLE_SERVICES, grouped_services=grouped
    )


@app.route("/services/<int:service_id>")
def service_detail(service_id):
    service = find_by_id(SAMPLE_SERVICES, service_id)
    if service is None:
        abort(404)
    related = [
        s
        for s in SAMPLE_SERVICES
        if s["category"] == service["category"] and s["id"] != service["id"]
    ][:3]
    return render_template("service.html", service=service, related=related)


@app.route("/book")
def book():
    # Display-only form in Week 3; saving arrives in Week 4.
    return render_template(
        "book.html", services=SAMPLE_SERVICES, stylists=SAMPLE_STYLISTS
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
