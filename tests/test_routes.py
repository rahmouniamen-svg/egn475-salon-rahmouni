import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app  # noqa: E402


def test_home():
    assert app.test_client().get("/").status_code == 200


def test_services():
    assert app.test_client().get("/services").status_code == 200


def test_service_detail():
    assert app.test_client().get("/services/2").status_code == 200


def test_book():
    assert app.test_client().get("/book").status_code == 200


def test_calendar():
    assert app.test_client().get("/calendar").status_code == 200


def test_appointments():
    assert app.test_client().get("/appointments").status_code == 200


def test_missing_service_returns_404():
    assert app.test_client().get("/services/999").status_code == 404


def test_non_integer_service_id_returns_404():
    assert app.test_client().get("/services/abc").status_code == 404


def test_price_shows_two_decimals():
    html = app.test_client().get("/services").get_data(as_text=True)
    assert "$45.00" in html


def test_services_list_shows_every_service():
    html = app.test_client().get("/services").get_data(as_text=True)
    # Jinja escapes "&" to "&amp;" in the rendered HTML.
    for name in ["Signature Haircut", "Blowout &amp; Style", "Balayage",
                 "Full Color &amp; Gloss", "Classic Manicure", "Spa Pedicure",
                 "Bridal Updo"]:
        assert name in html
