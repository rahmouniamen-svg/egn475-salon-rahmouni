import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import db  # noqa: E402
from app import app  # noqa: E402


@pytest.fixture
def client(tmp_path):
    """A test client with a fresh database from schema.sql."""
    app.config["DATABASE"] = str(tmp_path / "test.sqlite")
    app.config["TESTING"] = True
    with app.app_context():
        db.init_db()
    with app.test_client() as test_client:
        yield test_client


def test_home(client):
    assert client.get("/").status_code == 200


def test_services(client):
    assert client.get("/services").status_code == 200


def test_service_detail(client):
    assert client.get("/services/2").status_code == 200


def test_book(client):
    assert client.get("/book").status_code == 200


def test_calendar(client):
    assert client.get("/calendar").status_code == 200


def test_appointments(client):
    assert client.get("/appointments").status_code == 200


def test_missing_service_returns_404(client):
    assert client.get("/services/999").status_code == 404


def test_non_integer_service_id_returns_404(client):
    assert client.get("/services/abc").status_code == 404


def test_price_shows_two_decimals(client):
    html = client.get("/services").get_data(as_text=True)
    assert "$45.00" in html


def test_services_list_shows_every_service(client):
    html = client.get("/services").get_data(as_text=True)
    # Jinja escapes "&" to "&amp;" in the rendered HTML.
    for name in ["Signature Haircut", "Blowout &amp; Style", "Balayage",
                 "Full Color &amp; Gloss", "Classic Manicure", "Spa Pedicure",
                 "Bridal Updo"]:
        assert name in html


def test_new_service_form_shows(client):
    assert client.get("/admin/services/new").status_code == 200


def test_new_service_saves_and_redirects(client):
    response = client.post("/admin/services/new", data={
        "name": "Test Facial",
        "category": "Nails",
        "description": "A test service.",
        "duration_minutes": "30",
        "price_dollars": "25.50",
    })
    assert response.status_code == 302
    assert "/services" in response.headers["Location"]
    html = client.get("/services").get_data(as_text=True)
    assert "Test Facial" in html
    assert "$25.50" in html


def test_new_service_empty_name_is_refused(client):
    response = client.post("/admin/services/new", data={
        "name": "",
        "category": "Hair",
        "description": "",
        "duration_minutes": "30",
        "price_dollars": "10.00",
    })
    assert response.status_code == 400
    html = client.get("/services").get_data(as_text=True)
    assert "$10.00" not in html


def test_services_come_from_the_database(client):
    # The seeded list is in schema.sql, not in a Python list any more.
    with app.app_context():
        rows = db.get_db().execute("SELECT COUNT(*) FROM services").fetchone()
    assert rows[0] == 7
