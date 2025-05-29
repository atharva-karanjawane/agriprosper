from flask import Flask, render_template, request, redirect, url_for, session, flash
import sys, os, random
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.database import init_db, add_user, get_user_by_phone

app = Flask(__name__)
app.secret_key = 'your_secret_key'

init_db()

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        user = get_user_by_phone(phone)
        if user and check_password_hash(user[3], password):
            session['name'] = user[1]
            session['phone'] = phone
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

        if add_user(name, phone, password):
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        else:
            flash("Phone number already registered!", "danger")

    return render_template('register.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/alerts')
def alerts_page():
    return render_template('alerts.html')


@app.route('/controls')
def controls():
    return render_template('controls.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
