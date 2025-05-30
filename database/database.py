import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT ,
                location TEXT,
                latitude INTEGER,
                longitude INTEGER,
                bio TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')


    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS zones (
                zone_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                zone_label TEXT CHECK(zone_label IN ('A', 'B', 'C', 'D')),
                crop_type TEXT,
                irrigation_type TEXT,
                led_enabled BOOLEAN DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, zone_label)
            )
        ''')

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                data_id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL,
                humidity REAL,
                soil_moisture REAL,
                led_red_percent INTEGER CHECK(led_red_percent BETWEEN 0 AND 100),
                led_green_percent INTEGER CHECK(led_green_percent BETWEEN 0 AND 100),
                led_blue_percent INTEGER CHECK(led_blue_percent BETWEEN 0 AND 100),
                FOREIGN KEY(zone_id) REFERENCES zones(zone_id)
            )
        ''')

def add_user(name, phone, password, location, latitude, longitude ):
    try:
        hashed_pw = generate_password_hash(password)
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO users (name, phone, password, location, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)", (name, phone, hashed_pw, location, latitude, longitude))
            return True
    except sqlite3.IntegrityError:
        return False

def get_user_by_phone(phone):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE phone = ?", (phone,))
        return cur.fetchone()
    
def update_user_profile(user_id, name, phone, email, bio):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                UPDATE users
                SET name = ?, email = ?, phone = ?, bio = ?
                WHERE id = ?
            ''', (name, email, phone, bio, user_id))
            return True
    except sqlite3.IntegrityError:
        return False
    
def update_zone_data(zone_label, user_id, crop_type, irrigation_type, led_enabled):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                INSERT INTO zones (zone_label, user_id, crop_type, irrigation_type, led_enabled)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, zone_label)
                DO UPDATE SET
                    crop_type = excluded.crop_type,
                    irrigation_type = excluded.irrigation_type,
                    led_enabled = excluded.led_enabled
            ''', (zone_label, user_id, crop_type, irrigation_type, led_enabled))
            return True
    except sqlite3.Error as e:
        print("Database error:", e)
        return False


if __name__ == '__main__':
    init_db()