from flask import Flask, request, render_template_string, redirect
import sqlite3

app = Flask(__name__)

DB_NAME = "foodbridge.db"

# Demo number only. Replace with a real number if you want actual calls.
FOODBRIDGE_PHONE = "9876543210"


def create_database():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor TEXT,
            food TEXT,
            quantity TEXT,
            location TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS shelters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            contact TEXT NOT NULL,
            shelter_type TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS delivery_partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            vehicle TEXT NOT NULL
        )
    """)

    # Add new columns safely to an existing donations table.
    existing_columns = [
        row[1] for row in conn.execute(
            "PRAGMA table_info(donations)"
        ).fetchall()
    ]

    if "shelter_id" not in existing_columns:
        conn.execute(
            "ALTER TABLE donations ADD COLUMN shelter_id INTEGER"
        )

    if "status" not in existing_columns:
        conn.execute(
            "ALTER TABLE donations ADD COLUMN status TEXT DEFAULT 'Pending'"
        )

    if "partner_id" not in existing_columns:
        conn.execute(
            "ALTER TABLE donations ADD COLUMN partner_id INTEGER"
        )

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FoodBridge</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { box-sizing: border-box; }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f0f7f1;
                color: #243b2b;
            }

            header {
                background: #176b45;
                color: white;
                padding: 24px 16px;
                text-align: center;
            }

            header h1 { margin: 0; font-size: 34px; }

            .container {
                max-width: 600px;
                margin: 30px auto;
                padding: 24px;
            }

            .card {
                background: white;
                padding: 25px;
                border-radius: 16px;
                box-shadow: 0 4px 15px #00000012;
            }

            label {
                display: block;
                margin: 14px 0 7px;
                font-weight: bold;
            }

            input, select {
                width: 100%;
                padding: 12px;
                border: 1px solid #cbd8ce;
                border-radius: 8px;
                font-size: 16px;
                background: white;
                color: #243b2b;
            }

            button, .link {
                display: block;
                width: 100%;
                margin-top: 18px;
                padding: 13px;
                background: #176b45;
                color: white;
                border: none;
                border-radius: 8px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                cursor: pointer;
            }

            button:hover, .link:hover { background: #105436; }

            footer {
                text-align: center;
                padding: 20px;
                color: #526b59;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>🌿 FoodBridge</h1>
            <p>Share Food • Spread Hope • Reduce Waste</p>
        </header>

        <div class="container">
            <div class="card">
                <h2>🍲 Donate Surplus Food</h2>
                <p>Share your extra food with people who need it.</p>

                <form action="/donate" method="POST">
                    <label>Donor Name</label>
                    <input name="donor" required>

                    <label>Food Details</label>
                    <input name="food" required>

                    <label>Quantity</label>
                    <input name="quantity" required>

                    <label>Pickup Location</label>
                    <input name="location" required>

                    <button type="submit">Submit Donation 💚</button>
                </form>

                <a class="link" href="/donations">View All Donations</a>
                <a class="link" href="/shelters">View Shelter Details</a>
                <a class="link" href="/partners">Delivery Partner Details</a>
                <a class="link" href="tel:{{ phone }}">📞 Call FoodBridge</a>
            </div>
        </div>

        <footer>FoodBridge — Every Meal Matters 💚</footer>
    </body>
    </html>
    """, phone=FOODBRIDGE_PHONE)


@app.route("/donate", methods=["POST"])
def donate():
    donor = request.form["donor"].strip()
    food = request.form["food"].strip()
    quantity = request.form["quantity"].strip()
    location = request.form["location"].strip()

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        INSERT INTO donations (donor, food, quantity, location)
        VALUES (?, ?, ?, ?)
    """, (donor, food, quantity, location))

    conn.commit()
    conn.close()

    return """
        <h2>Donation Saved Successfully! 💚</h2>
        <p>Your donation details have been stored.</p>
        <a href="/donations">View Donations</a>
        <br><br>
        <a href="/">Back to Home</a>
    """


@app.route("/donations")
def view_donations():
    search = request.args.get("search", "").strip()

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    donations = conn.execute("""
        SELECT
            donations.*,
            shelters.name AS shelter_name,
            delivery_partners.name AS partner_name,
            delivery_partners.phone AS partner_phone,
            delivery_partners.vehicle AS partner_vehicle
        FROM donations
        LEFT JOIN shelters
            ON donations.shelter_id = shelters.id
        LEFT JOIN delivery_partners
            ON donations.partner_id = delivery_partners.id
        WHERE donations.food LIKE ?
        ORDER BY donations.id DESC
    """, (f"%{search}%",)).fetchall()

    shelters_list = conn.execute(
        "SELECT * FROM shelters ORDER BY id DESC"
    ).fetchall()

    partners_list = conn.execute(
        "SELECT * FROM delivery_partners ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FoodBridge Donations</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f0f7f1;
                color: #243b2b;
                padding: 20px;
            }

            .card {
                background: white;
                padding: 18px;
                margin: 15px auto;
                max-width: 650px;
                border-radius: 12px;
                border: 1px solid #cbd8ce;
            }

            input, select {
                width: 100%;
                padding: 12px;
                border-radius: 8px;
                margin-top: 8px;
                box-sizing: border-box;
                border: 1px solid #cbd8ce;
            }

            button {
                width: 100%;
                padding: 12px;
                margin-top: 12px;
                background: #176b45;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }

            a { color: #176b45; }
        </style>
    </head>
    <body>
        <h1>FoodBridge - All Donations 💚</h1>

        <form action="/donations" method="GET">
            <input
                type="text"
                name="search"
                placeholder="Search food name..."
                value="{{ search }}"
            >
            <button type="submit">Search</button>
        </form>

        {% if donations %}
            {% for d in donations %}
                <div class="card">
                    <h3>Donation #{{ d['id'] }}</h3>

                    <p><b>Donor:</b> {{ d['donor'] }}</p>
                    <p><b>Food:</b> {{ d['food'] }}</p>
                    <p><b>Quantity:</b> {{ d['quantity'] }}</p>
                    <p><b>Location:</b> {{ d['location'] }}</p>
                    <p><b>Status:</b> {{ d['status'] or 'Pending' }}</p>

                    <form action="/update_status/{{ d['id'] }}" method="POST">
                        <label><b>Update Status:</b></label>
                        <select name="status">
                            <option value="Pending"
                                {% if d['status'] == 'Pending' %}selected{% endif %}>
                                Pending
                            </option>
                            <option value="Assigned"
                                {% if d['status'] == 'Assigned' %}selected{% endif %}>
                                Assigned
                            </option>
                            <option value="Delivered"
                                {% if d['status'] == 'Delivered' %}selected{% endif %}>
                                Delivered
                            </option>
                        </select>
                        <button type="submit">Update Status</button>
                    </form>

                    <hr>

                    <h3>Shelter Assignment</h3>
                    <p>
                        <b>Assigned Shelter:</b>
                        {{ d['shelter_name'] or 'Not assigned yet' }}
                    </p>

                    {% if shelters_list %}
                        <form action="/assign/{{ d['id'] }}" method="POST">
                            <label><b>Select Shelter:</b></label>
                            <select name="shelter_id" required>
                                <option value="">Choose a shelter</option>
                                {% for s in shelters_list %}
                                    <option value="{{ s['id'] }}"
                                        {% if d['shelter_id'] == s['id'] %}selected{% endif %}>
                                        {{ s['name'] }}
                                    </option>
                                {% endfor %}
                            </select>
                            <button type="submit">Assign to Shelter</button>
                        </form>
                    {% else %}
                        <p>No shelters registered yet.</p>
                        <a href="/shelters">Add a Shelter</a>
                    {% endif %}

                    <hr>

                    <h3>Delivery Partner Assignment</h3>

                    <p>
                        <b>Assigned Partner:</b>
                        {{ d['partner_name'] or 'Not assigned yet' }}
                    </p>

                    {% if d['partner_name'] %}
                        <p><b>Partner Phone:</b> {{ d['partner_phone'] }}</p>
                        <p><b>Vehicle:</b> {{ d['partner_vehicle'] }}</p>
                    {% endif %}

                    {% if partners_list %}
                        <form action="/assign_partner/{{ d['id'] }}" method="POST">
                            <label><b>Select Delivery Partner:</b></label>
                            <select name="partner_id" required>
                                <option value="">Choose a partner</option>
                                {% for p in partners_list %}
                                    <option value="{{ p['id'] }}"
                                        {% if d['partner_id'] == p['id'] %}selected{% endif %}>
                                        {{ p['name'] }} - {{ p['vehicle'] }}
                                    </option>
                                {% endfor %}
                            </select>
                            <button type="submit">Assign Delivery Partner</button>
                        </form>
                    {% else %}
                        <p>No delivery partners registered yet.</p>
                        <a href="/partners">Register a Delivery Partner</a>
                    {% endif %}
                </div>
            {% endfor %}
        {% else %}
            <p>No donations found.</p>
        {% endif %}

        <a href="/">Back to Home</a>
        <br><br>
        <a href="/partners">Delivery Partner Details</a>
    </body>
    </html>
    """,
    donations=donations,
    shelters_list=shelters_list,
    partners_list=partners_list,
    search=search)


@app.route("/update_status/<int:donation_id>", methods=["POST"])
def update_status(donation_id):
    status = request.form.get("status")

    if status not in ["Pending", "Assigned", "Delivered"]:
        return "Invalid status", 400

    conn = sqlite3.connect(DB_NAME)

    conn.execute(
        "UPDATE donations SET status = ? WHERE id = ?",
        (status, donation_id)
    )

    conn.commit()
    conn.close()

    return redirect("/donations")


@app.route("/assign/<int:donation_id>", methods=["POST"])
def assign_shelter(donation_id):
    shelter_id = request.form.get("shelter_id", type=int)

    if shelter_id is None:
        return "Please select a shelter.", 400

    conn = sqlite3.connect(DB_NAME)

    shelter = conn.execute(
        "SELECT id FROM shelters WHERE id = ?",
        (shelter_id,)
    ).fetchone()

    donation = conn.execute(
        "SELECT id FROM donations WHERE id = ?",
        (donation_id,)
    ).fetchone()

    if shelter is None or donation is None:
        conn.close()
        return "Shelter or donation not found.", 404

    conn.execute(
        "UPDATE donations SET shelter_id = ? WHERE id = ?",
        (shelter_id, donation_id)
    )

    conn.commit()
    conn.close()

    return redirect("/donations")


@app.route("/partners", methods=["GET", "POST"])
def partners():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        vehicle = request.form.get("vehicle", "").strip()

        if not name or not phone or not vehicle:
            return "Please fill all delivery partner details.", 400

        conn = sqlite3.connect(DB_NAME)

        conn.execute("""
            INSERT INTO delivery_partners (name, phone, vehicle)
            VALUES (?, ?, ?)
        """, (name, phone, vehicle))

        conn.commit()
        conn.close()

        return redirect("/partners")

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    records = conn.execute("""
        SELECT * FROM delivery_partners
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FoodBridge Delivery Partners</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f0f7f1;
                color: #243b2b;
                padding: 20px;
            }

            .card {
                background: white;
                max-width: 600px;
                margin: 15px auto;
                padding: 20px;
                border-radius: 12px;
            }

            input, select {
                width: 100%;
                padding: 12px;
                margin: 7px 0 15px;
                box-sizing: border-box;
                border: 1px solid #cbd8ce;
                border-radius: 8px;
            }

            button {
                width: 100%;
                padding: 12px;
                background: #176b45;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }

            a { color: #176b45; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚚 Delivery Partner Registration</h1>

            <form method="POST">
                <label>Partner Name</label>
                <input name="name" required>

                <label>Phone Number</label>
                <input name="phone" type="tel" required>

                <label>Vehicle Type</label>
                <select name="vehicle" required>
                    <option value="">Select Vehicle</option>
                    <option value="Bike">Bike</option>
                    <option value="Scooter">Scooter</option>
                    <option value="Auto">Auto</option>
                    <option value="Van">Van</option>
                    <option value="Other">Other</option>
                </select>

                <button type="submit">Register Delivery Partner</button>
            </form>
        </div>

        <div class="card">
            <h2>Registered Delivery Partners</h2>

            {% for p in records %}
                <div>
                    <h3>{{ p['name'] }}</h3>
                    <p>Phone: {{ p['phone'] }}</p>
                    <p>Vehicle: {{ p['vehicle'] }}</p>
                </div>
                <hr>
            {% else %}
                <p>No delivery partners registered yet.</p>
            {% endfor %}

            <a href="/">Back to Home</a>
            <br><br>
            <a href="/donations">Assign Partner to Donations</a>
        </div>
    </body>
    </html>
    """, records=records)


@app.route("/assign_partner/<int:donation_id>", methods=["POST"])
def assign_partner(donation_id):
    partner_id = request.form.get("partner_id", type=int)

    if partner_id is None:
        return "Please select a delivery partner.", 400

    conn = sqlite3.connect(DB_NAME)

    partner = conn.execute(
        "SELECT id FROM delivery_partners WHERE id = ?",
        (partner_id,)
    ).fetchone()

    donation = conn.execute(
        "SELECT id FROM donations WHERE id = ?",
        (donation_id,)
    ).fetchone()

    if partner is None or donation is None:
        conn.close()
        return "Delivery partner or donation not found.", 404

    conn.execute(
        "UPDATE donations SET partner_id = ? WHERE id = ?",
        (partner_id, donation_id)
    )

    conn.commit()
    conn.close()

    return redirect("/donations")


@app.route("/shelters", methods=["GET", "POST"])
def shelters():
    if request.method == "POST":
        name = request.form["name"].strip()
        address = request.form["address"].strip()
        contact = request.form["contact"].strip()
        shelter_type = request.form["shelter_type"]

        conn = sqlite3.connect(DB_NAME)
        conn.execute("""
            INSERT INTO shelters (name, address, contact, shelter_type)
            VALUES (?, ?, ?, ?)
        """, (name, address, contact, shelter_type))
        conn.commit()
        conn.close()

        return redirect("/shelters")

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    records = conn.execute(
        "SELECT * FROM shelters ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FoodBridge Shelters</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>FoodBridge - Register Shelter</h1>

        <form method="POST">
            <input name="name" placeholder="Shelter Name" required>
            <input name="address" placeholder="Address" required>
            <input name="contact" placeholder="Contact Number" required>

            <select name="shelter_type" required>
                <option value="">Select Shelter Type</option>
                <option value="Orphanage">Orphanage</option>
                <option value="Ashram">Ashram</option>
                <option value="Old Age Home">Old Age Home</option>
                <option value="Other">Other</option>
            </select>

            <button type="submit">Register Shelter</button>
        </form>

        <h2>Registered Shelters</h2>
        {% for item in records %}
            <p>
                <b>{{ item['name'] }}</b><br>
                {{ item['address'] }}<br>
                {{ item['contact'] }}<br>
                {{ item['shelter_type'] }}
            </p>
            <hr>
        {% else %}
            <p>No shelters registered yet.</p>
        {% endfor %}

        <a href="/">Home</a> |
        <a href="/donations">View Donations</a>
    </body>
    </html>
    """, records=records)
if __name__ == "__main__":
    create_database()
    app.run(host="0.0.0.0", port=5000, debug=True)