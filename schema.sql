-- Bella Vista Salon (Option B) — EGN 475 Week 4 Assignment 4.1
-- SQLite schema. Rebuild any time with: flask --app app init-db
-- Prices are whole cents (INTEGER), true/false is INTEGER 0/1,
-- dates are TEXT in YYYY-MM-DD format.

DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'client'
);

CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'Hair',
    description TEXT NOT NULL DEFAULT '',
    duration_minutes INTEGER NOT NULL,
    price_cents INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    service_id INTEGER NOT NULL REFERENCES services(id),
    client_name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Upcoming',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Seed data: 3 users, 7 services, 4 appointments.
-- password_hash values are placeholders; real hashing arrives in Week 6.
INSERT INTO users (username, password_hash, role) VALUES
    ('lucia', 'placeholder-hash-lucia', 'client'),
    ('sofia', 'placeholder-hash-sofia', 'staff'),
    ('admin', 'placeholder-hash-admin', 'admin');

INSERT INTO services (name, category, description, duration_minutes, price_cents, active) VALUES
    ('Signature Haircut', 'Hair', 'Consultation, wash, precision cut and finish styling.', 60, 4500, 1),
    ('Blowout & Style', 'Hair', 'Wash, blow-dry and styled finish for a polished look.', 45, 3500, 1),
    ('Balayage', 'Color', 'Hand-painted highlights for a soft, sun-kissed blend.', 150, 12500, 1),
    ('Full Color & Gloss', 'Color', 'Full color application with a shine gloss and treatment.', 120, 8500, 1),
    ('Classic Manicure', 'Nails', 'Shape, cuticle care, polish and a relaxing hand massage.', 45, 3000, 1),
    ('Spa Pedicure', 'Nails', 'Soak, exfoliation, nail care and polish in our spa chairs.', 60, 5500, 1),
    ('Bridal Updo', 'Hair', 'Elegant updo styling for weddings and special occasions.', 90, 7500, 1);

INSERT INTO appointments (user_id, service_id, client_name, date, time, status, notes) VALUES
    (1, 1, 'Lucia Fernandez', '2026-11-15', '9:00 AM', 'Completed', NULL),
    (1, 5, 'Lucia Fernandez', '2026-11-08', '10:00 AM', 'Cancelled', NULL),
    (1, 3, 'Lucia Fernandez', '2026-11-29', '10:00 AM', 'Upcoming', NULL),
    (1, 2, 'Lucia Fernandez', '2026-12-05', '11:00 AM', 'Upcoming', NULL);
