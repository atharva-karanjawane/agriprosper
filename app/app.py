from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import sys, os, random
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.database import init_db, add_user, get_user_by_phone, update_user_profile, update_zone_data

app = Flask(__name__)
app.secret_key = 'your_secret_key'

init_db()

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/dashboard')
def dashboard():
    username = session['name']
    return render_template('dashboard.html',username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        user = get_user_by_phone(phone)
        if user and check_password_hash(user[3], password):
            print(session)
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['phone'] = phone
            session['email'] = user[4]
            session['location'] = user[5]
            session['latitude'] = user[6]
            session['longitude'] = user[7]
            session['bio'] = user[8]

            return redirect(url_for('dashboard'))
        else:
            flash("Invalid phone number or password", "danger")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']
        location = request.form['location']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        if add_user(name, phone, password, location, latitude, longitude ):
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        else:
            flash("Phone number already registered!", "danger")

    return render_template('register.html')

@app.route('/analytics')
def analytics():
    username = session['name']
    return render_template('analytics.html',username=username)

@app.route('/alerts')
def alerts_page():
    username = session['name']
    return render_template('alerts.html',username=username)


@app.route('/controls')
def controls():
    username = session['name']
    default_zone = 'A'
    zone_data = get_zone_data(default_zone)
    return render_template('controls.html', username=username, zone=default_zone, zone_data=zone_data)

def get_zone_data(zone):
    dummy_data = {
        "A": {"red": 25.5, "green": 65, "blue": 85, "irrigation": 80},
        "B": {"red": 22.0, "green": 55, "blue": 45, "irrigation": 70},
        "C": {"red": 28.4, "green": 60, "blue": 90, "irrigation": 90},
        "D": {"red": 20.1, "green": 50, "blue": 65, "irrigation": 60},
    }
    return dummy_data.get(zone, {})

@app.route("/get_zone_data", methods=["POST"])
def get_zone_data_route():
    data = request.get_json()
    zone = data.get("zone")

    zone_data = get_zone_data(zone)
    return jsonify(zone_data)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = session.get('name', 'John Doe')
    phoneno = session.get('phone', '123-456-7890')
    location = session.get('location', 'New York')
    email = session.get('email', 'email@example.com')
    bio = session.get('bio', 'This is your bio.')

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        print("request hit")
        print(form_type)

        if form_type == 'profile':
            # Handle profile update
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            phone_number = request.form.get('phoneno')
            bio = request.form.get('bio')

            session['name'] = f"{first_name} {last_name}"
            session['phone'] = phone_number
            session['email'] = email
            session['bio'] = bio

            if update_user_profile(session['user_id'], f"{first_name} {last_name}", phone_number, email, bio):
                flash("Profile Updated", "success")
            else:
                flash("Profile not updated", "danger")

        elif form_type == 'zone':
            print("saving data for zone")
            # Parse zone config form
            irrigation_type = request.form.get('irrigation_type')
            led_enabled = request.form.get('led_enabled') == 'on'

            for zone_label in ['A', 'B', 'C', 'D']:
                crop = request.form.get(f'zone[{zone_label}][crop]')
                if crop:
                    update_zone_data(
                        zone_label=zone_label,
                        user_id=session['user_id'],
                        crop_type=crop,
                        irrigation_type=irrigation_type,
                        led_enabled=led_enabled
                    )

            flash("Zone configuration saved.", "success")
            return redirect(url_for('profile'))

    return render_template('profile.html', username=username, phoneno=phoneno, location=location, email=email, bio=bio)

@app.route('/marketplace-farmer')
def marketplace_farmer():
    username = session['name']
    return render_template("marketplace_farmer.html",username=username)

@app.route('/marketplace-user')
def marketplace_user():
    username = session['name']
    return render_template("marketplace_consumer.html",username=username)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
