import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

DB_NAME = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                location TEXT,
                latitude INTEGER,
                longitude INTEGER,
                bio TEXT,
                user_type TEXT DEFAULT 'farmer' CHECK(user_type IN ('farmer', 'consumer')),
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

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS plant_lifecycle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop VARCHAR(50) NOT NULL,
                stage TINYINT NOT NULL CHECK (stage BETWEEN 1 AND 4),
                red TINYINT NOT NULL CHECK (red BETWEEN 0 AND 100),
                green TINYINT NOT NULL CHECK (green BETWEEN 0 AND 100),
                blue TINYINT NOT NULL CHECK (blue BETWEEN 0 AND 100),
                ppfd SMALLINT NOT NULL,
                day_start SMALLINT NOT NULL,
                day_end SMALLINT NOT NULL,
                CONSTRAINT chk_days CHECK (day_end > day_start)
            )
        ''')

    # New tables for marketplace functionality
    with sqlite3.connect(DB_NAME) as conn:
        # Products table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id INTEGER NOT NULL,
                zone_id INTEGER,
                name TEXT NOT NULL,
                category TEXT NOT NULL CHECK(category IN ('vegetables', 'fruits', 'grains', 'herbs')),
                description TEXT,
                price REAL NOT NULL,
                unit TEXT NOT NULL,
                quantity_available INTEGER NOT NULL,
                quality_score REAL CHECK(quality_score BETWEEN 0 AND 10),
                harvest_date DATE NOT NULL,
                image_path TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(farmer_id) REFERENCES users(id),
                FOREIGN KEY(zone_id) REFERENCES zones(zone_id)
            )
        ''')

        # Orders table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
                delivery_address TEXT NOT NULL,
                contact_number TEXT NOT NULL,
                delivery_date DATE NOT NULL,
                special_instructions TEXT,
                FOREIGN KEY(customer_id) REFERENCES users(id)
            )
        ''')

        # Order items table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_unit REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(order_id),
                FOREIGN KEY(product_id) REFERENCES products(product_id)
            )
        ''')

        # Crop analysis table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS crop_analysis (
                analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                zone_id INTEGER NOT NULL,
                analysis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                crop_health_score REAL CHECK(crop_health_score BETWEEN 0 AND 10),
                estimated_yield REAL,
                pest_detection TEXT,
                disease_detection TEXT,
                nutrient_deficiency TEXT,
                recommendations TEXT,
                FOREIGN KEY(zone_id) REFERENCES zones(zone_id)
            )
        ''')

def add_user(name, phone, password, location, latitude, longitude, user_type='farmer'):
    try:
        hashed_pw = generate_password_hash(password)
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO users (name, phone, password, location, latitude, longitude, user_type) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                        (name, phone, hashed_pw, location, latitude, longitude, user_type))
            return True
    except sqlite3.IntegrityError:
        return False

def get_user_by_phone(phone):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
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

def plant_lifecyle_static():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
            INSERT INTO plant_lifecycle (crop, stage, red, green, blue, ppfd, day_start, day_end) VALUES
                -- Tomato
                ('Tomato', 1, 50, 0, 50, 120, 1, 14),
                ('Tomato', 2, 75, 0, 25, 180, 15, 42),
                ('Tomato', 3, 80, 0, 20, 220, 43, 63),
                ('Tomato', 4, 70, 0, 30, 280, 64, 105),

                -- Chili
                ('Chili', 1, 0, 0, 100, 110, 1, 15),
                ('Chili', 2, 65, 0, 35, 170, 16, 45),
                ('Chili', 3, 85, 0, 15, 230, 46, 65),
                ('Chili', 4, 75, 0, 25, 270, 66, 110),

                -- Spinach
                ('Spinach', 1, 0, 0, 100, 100, 1, 10),
                ('Spinach', 2, 50, 0, 50, 160, 11, 35),
                ('Spinach', 3, 80, 0, 20, 210, 36, 50),
                ('Spinach', 4, 20, 0, 80, 130, 51, 57),

                -- Lettuce
                ('Lettuce', 1, 50, 0, 50, 130, 1, 10),
                ('Lettuce', 2, 65, 0, 35, 190, 11, 30),
                ('Lettuce', 3, 60, 20, 20, 220, 31, 45),
                ('Lettuce', 4, 0, 0, 100, 80, 46, 52),

                -- Okra
                ('Okra', 1, 0, 0, 100, 110, 1, 14),
                ('Okra', 2, 70, 0, 30, 175, 15, 44),
                ('Okra', 3, 85, 0, 15, 225, 45, 65),
                ('Okra', 4, 75, 0, 25, 260, 66, 110);
                        ''')
            return True
    except sqlite3.IntegrityError:
        return False

def insert_mock_products():
    products = [
        ("Tomato", "vegetables", "Fresh red tomatoes", 20.0, "kg", 100, 8.5, "2025-05-01"),
        ("Spinach", "vegetables", "Green leafy spinach", 15.0, "bunch", 80, 9.0, "2025-05-02"),
        ("Okra", "vegetables", "Tender okra pods", 18.0, "kg", 60, 8.0, "2025-05-03"),
        ("Potato", "vegetables", "Organic potatoes", 12.0, "kg", 150, 7.5, "2025-04-28"),
        ("Strawberry", "fruits", "Sweet strawberries", 50.0, "box", 30, 9.2, "2025-05-04"),
        ("Apple", "fruits", "Juicy apples", 60.0, "kg", 40, 8.8, "2025-04-30"),
        ("Carrot", "vegetables", "Crunchy carrots", 22.0, "kg", 90, 8.3, "2025-05-01"),
        ("Corn", "grains", "Fresh corn cobs", 25.0, "dozen", 70, 8.7, "2025-05-03"),
        ("Cucumber", "vegetables", "Cool cucumbers", 17.0, "kg", 85, 8.1, "2025-05-02"),
        ("Mint", "herbs", "Fresh mint leaves", 10.0, "bunch", 50, 9.5, "2025-05-05")
    ]

    with sqlite3.connect(DB_NAME) as conn:
        for name, category, desc, price, unit, qty, score, date in products:
            conn.execute('''
                INSERT INTO products (
                    farmer_id, zone_id, name, category, description, price,
                    unit, quantity_available, quality_score, harvest_date,
                    is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            ''', (
                1, 1, name, category, desc, price, unit,
                qty, score, date, datetime.now()
            ))
        conn.commit()
    print("Mock products inserted successfully.")

def get_farmer_products(farmer_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT p.*, z.zone_label, z.crop_type 
            FROM products p
            LEFT JOIN zones z ON p.zone_id = z.zone_id
            WHERE p.farmer_id = ?
            ORDER BY p.created_at DESC
        ''', (farmer_id,))
        return cur.fetchall()

def get_farmer_zones(farmer_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM zones
            WHERE user_id = ?
        ''', (farmer_id,))
        return cur.fetchall()

def get_zone_data(zone_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM sensor_data
            WHERE zone_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (zone_id,))
        return cur.fetchone()

def add_product(farmer_id, zone_id, name, category, description, price, unit, quantity, quality_score, harvest_date, image_path=None):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                INSERT INTO products 
                (farmer_id, zone_id, name, category, description, price, unit, quantity_available, quality_score, harvest_date, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (farmer_id, zone_id, name, category, description, price, unit, quantity, quality_score, harvest_date, image_path))
            return True
    except sqlite3.IntegrityError:
        return False

def analyze_crop(zone_id):
    # This would typically involve complex analysis based on sensor data
    # For demonstration, we'll create a simple analysis
    try:
        with sqlite3.connect(DB_NAME) as conn:
            # Get latest sensor data
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('''
                SELECT * FROM sensor_data
                WHERE zone_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (zone_id,))
            sensor_data = cur.fetchone()
            
            if not sensor_data:
                return None
            
            # Simple analysis based on sensor data
            temp = sensor_data['temperature']
            humidity = sensor_data['humidity']
            moisture = sensor_data['soil_moisture']
            
            # Calculate health score (simplified)
            health_score = 0
            if 20 <= temp <= 30:
                health_score += 3
            elif 15 <= temp <= 35:
                health_score += 2
            else:
                health_score += 1
                
            if 50 <= humidity <= 70:
                health_score += 3
            elif 40 <= humidity <= 80:
                health_score += 2
            else:
                health_score += 1
                
            if 40 <= moisture <= 60:
                health_score += 4
            elif 30 <= moisture <= 70:
                health_score += 2
            else:
                health_score += 1
            
            # Generate recommendations
            recommendations = []
            if temp < 20:
                recommendations.append("Increase temperature")
            elif temp > 30:
                recommendations.append("Decrease temperature")
                
            if humidity < 50:
                recommendations.append("Increase humidity")
            elif humidity > 70:
                recommendations.append("Decrease humidity")
                
            if moisture < 40:
                recommendations.append("Increase irrigation")
            elif moisture > 60:
                recommendations.append("Decrease irrigation")
            
            # Insert analysis into database
            conn.execute('''
                INSERT INTO crop_analysis
                (zone_id, crop_health_score, recommendations)
                VALUES (?, ?, ?)
            ''', (zone_id, health_score, ", ".join(recommendations)))
            
            # Return the analysis
            return {
                'health_score': health_score,
                'recommendations': recommendations,
                'estimated_yield': round(health_score * 1.5, 1),  # Simplified yield estimation
                'pest_detection': 'None detected',
                'disease_detection': 'None detected',
                'nutrient_deficiency': 'None detected'
            }
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def get_farmer_orders(farmer_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT o.*, u.name as customer_name, u.phone as customer_phone
            FROM orders o
            JOIN users u ON o.customer_id = u.id
            WHERE o.order_id IN (
                SELECT oi.order_id
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE p.farmer_id = ?
            )
            ORDER BY o.order_date DESC
        ''', (farmer_id,))
        orders = cur.fetchall()
        
        # Get order items for each order
        result = []
        for order in orders:
            cur.execute('''
                SELECT oi.*, p.name as product_name, p.unit
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = ? AND p.farmer_id = ?
            ''', (order['order_id'], farmer_id))
            items = cur.fetchall()
            
            order_dict = dict(order)
            order_dict['items'] = [dict(item) for item in items]
            result.append(order_dict)
            
        return result

def update_order_status(order_id, status):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                UPDATE orders
                SET status = ?
                WHERE order_id = ?
            ''', (status, order_id))
            return True
    except sqlite3.Error:
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

def get_all_products(category=None, sort_by=None):
    """Get all available products with optional filtering and sorting"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        query = """
            SELECT p.*, u.name as farmer_name, u.location as farm_location 
            FROM products p
            JOIN users u ON p.farmer_id = u.id
            WHERE p.is_active = 1 AND p.quantity_available > 0
        """
        params = []
        
        if category and category != '':
            query += " AND p.category = ?"
            params.append(category)
        
        if sort_by:
            if sort_by == 'price-low':
                query += " ORDER BY p.price ASC"
            elif sort_by == 'price-high':
                query += " ORDER BY p.price DESC"
            elif sort_by == 'quality':
                query += " ORDER BY p.quality_score DESC"
            elif sort_by == 'recent':
                query += " ORDER BY p.harvest_date DESC"
        else:
            query += " ORDER BY p.created_at DESC"
        
        cur.execute(query, params)
        return cur.fetchall()

def get_product_by_id(product_id):
    """Get a product by its ID"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT p.*, u.name as farmer_name, u.location as farm_location 
            FROM products p
            JOIN users u ON p.farmer_id = u.id
            WHERE p.product_id = ?
        """, (product_id,))
        return cur.fetchone()

def create_order(customer_id, total_amount, delivery_address, contact_number, delivery_date, special_instructions=None):
    """Create a new order and return the order ID"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            # Set delivery date to today + 3 days
            delivery_date = (datetime.today() + timedelta(days=3)).strftime('%Y-%m-%d')

            # Now insert the data into the orders table
            cur.execute("""
                INSERT INTO orders 
                (customer_id, total_amount, delivery_address, contact_number, delivery_date, special_instructions)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (customer_id, total_amount, delivery_address, contact_number, delivery_date, special_instructions))
            print("order success")
            return cur.lastrowid
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def add_order_item(order_id, product_id, quantity, price_per_unit):
    """Add an item to an order"""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            # Calculate subtotal
            subtotal = quantity * price_per_unit
            
            # Add the order item
            conn.execute("""
                INSERT INTO order_items 
                (order_id, product_id, quantity, price_per_unit, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, product_id, quantity, price_per_unit, subtotal))
            
            # Update product quantity
            conn.execute("""
                UPDATE products
                SET quantity_available = quantity_available - ?
                WHERE product_id = ?
            """, (quantity, product_id))
            
            return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def get_customer_orders(customer_id):
    """Get all orders for a customer"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM orders
            WHERE customer_id = ?
            ORDER BY order_date DESC
        """, (customer_id,))
        orders = cur.fetchall()
        
        # Get order items for each order
        result = []
        for order in orders:
            cur.execute("""
                SELECT oi.*, p.name as product_name, p.unit, u.name as farmer_name
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                JOIN users u ON p.farmer_id = u.id
                WHERE oi.order_id = ?
            """, (order['order_id'],))
            items = cur.fetchall()
            
            order_dict = dict(order)
            order_dict['items'] = [dict(item) for item in items]
            result.append(order_dict)
            
        return result

def get_pending_orders():
    """Fetch all orders with 'pending' status"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM orders
            WHERE status = 'pending'
            ORDER BY order_date DESC
        """)
        return cur.fetchall()

if __name__ == '__main__':
    init_db()
    plant_lifecyle_static()
    insert_mock_products()
