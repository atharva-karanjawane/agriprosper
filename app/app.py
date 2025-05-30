from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import sys, os, random
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.database import (
    init_db, add_user, get_user_by_phone, update_user_profile, update_zone_data,
    get_all_products, get_product_by_id, create_order, add_order_item,
    get_customer_orders,get_farmer_products,add_product,get_pending_orders
)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

init_db()

# Initialize cart in session if not present
@app.before_request
def initialize_cart():
    if 'cart' not in session:
        session['cart'] = {'items': [], 'count': 0, 'total': 0}

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
    username = session['name']
    role = session['role']
    return render_template('dashboard.html', username=username,role=role)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        user = get_user_by_phone(phone)
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['phone'] = phone
            session['email'] = user[4]
            session['location'] = user[5]
            session['latitude'] = user[6]
            session['longitude'] = user[7]
            session['bio'] = user[8]
            session['role'] = user[9]

            if session['role'] != 'farmer': 
                return redirect(url_for('marketplace_user'))
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
        role = request.form['role']

        if add_user(name, phone, password, location, latitude, longitude, role):
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        else:
            flash("Phone number already registered!", "danger")

    return render_template('register.html')

@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
    username = session['name']
    role = session['role']
    return render_template('analytics.html', username=username, role=role)

@app.route('/alerts')
def alerts_page():
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
    username = session['name']
    role = session['role']
    return render_template('alerts.html', username=username, role=role)

@app.route('/controls')
def controls():
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
    username = session['name']
    role = session['role']
    default_zone = 'A'
    zone_data = get_zone_data(default_zone)
    return render_template('controls.html', username=username, zone=default_zone, zone_data=zone_data, role=role)

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
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
    
    username = session.get('name', 'John Doe')
    phoneno = session.get('phone', '123-456-7890')
    location = session.get('location', 'New York')
    email = session.get('email', 'email@example.com')
    bio = session.get('bio', 'This is your bio.')
    role = session.get('role')

    if request.method == 'POST':
        form_type = request.form.get('form_type')

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

    return render_template('profile.html', username=username, phoneno=phoneno, location=location, email=email, bio=bio, role=role)

@app.route('/schemes')
def schemes():
    with open(os.path.join('static', 'data', 'schemes.json')) as f:
        schemes = json.load(f)
    username=session['name']
    role = session['role']
    return render_template('schemes.html', schemes=schemes,username=username,role=role)

@app.route('/marketplace-farmer')
def marketplace_farmer():
    if 'user_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('login'))
    
    
    products = get_farmer_products(session["user_id"])
    
    # Calculate tomorrow's date for delivery date input
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime('%Y-%m-%d')
    
    # return render_template('marketplace_consumer.html',)

    username = session['name']
    role = session['role']

    pending_orders = get_pending_orders()
    # for order in pending_orders:
    #     print(order['order_id'], order['delivery_address'], order['delivery_date'])

    return render_template("marketplace_farmer.html",
                            username=username,
                          products=products, 
                          tomorrow_date=tomorrow_date,
                          role=role,orders=pending_orders)

@app.route('/add-product-farmer', methods=['POST'])
def add_product_farmer():
    farmer_id = session.get('user_id')
    if not farmer_id:
        return redirect(url_for('login'))

    # Get form data
    zone_id = request.form.get('zone_id')
    name = request.form.get('name')
    category = request.form.get('category')
    description = request.form.get('description')
    price = request.form.get('price')
    unit = request.form.get('unit')
    quantity = request.form.get('quantity')
    quality_score = request.form.get('quality_score')
    harvest_date = request.form.get('harvest_date')

    # Handle image upload
    image = request.files.get('image')
    image_path = None

    if image and image.filename != '':
        filename = secure_filename(image.filename)
        upload_folder = 'static/uploads'
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, filename)
        image.save(image_path)

    add_product(
        farmer_id=farmer_id,
        zone_id=zone_id,
        name=name,
        category=category,
        description=description,
        price=price,
        unit=unit,
        quantity=quantity,
        quality_score=quality_score,
        harvest_date=harvest_date,
        image_path=image_path
    )

    # Redirect to the dashboard or same page
    return redirect(url_for('marketplace_farmer'))
 
# Updated marketplace route with product loading
@app.route('/marketplace')
@app.route('/marketplace-user')
def marketplace_user():
    username = session.get('name', '')
    role = session['role']
    # Get filter parameters
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', '')
    
    # Get products from database
    products = get_all_products(category, sort_by)
    
    # Calculate tomorrow's date for delivery date input
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime('%Y-%m-%d')
    
    return render_template('marketplace_consumer.html', 
                          username=username,
                          products=products, 
                          tomorrow_date=tomorrow_date,
                          category=category,
                          sort_by=sort_by,
                          role=role)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# New routes for checkout functionality

# Get cart route (AJAX)
@app.route('/update_cart', methods=['GET'])
def get_cart():
    cart = session.get('cart', {'items': [], 'count': 0, 'total': 0})
    return jsonify({'success': True, 'cart': cart})

# Update cart route (AJAX)
@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart_data = request.json
    session['cart'] = cart_data
    print(session['cart'])
    session.modified = True
    return jsonify({'success': True})

# Add to cart route (AJAX)
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    # Get product from database
    product = get_product_by_id(product_id)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    
    # Check if product is available in sufficient quantity
    if product['quantity_available'] < quantity:
        return jsonify({
            'success': False, 
            'message': f'Only {product["quantity_available"]} units available'
        })
    
    # Calculate subtotal
    subtotal = product['price'] * quantity
    
    # Get cart from session
    cart = session.get('cart', {'items': [], 'count': 0, 'total': 0})
    
    # Check if product already in cart
    existing_item = None
    for item in cart['items']:
        if item['product_id'] == product_id:
            existing_item = item
            break
    
    if existing_item:
        # Update existing item
        existing_item['quantity'] += quantity
        existing_item['subtotal'] += subtotal
    else:
        # Add new item
        cart['items'].append({
            'product_id': product_id,
            'name': product['name'],
            'farmer_name': product['farmer_name'],
            'price_per_unit': product['price'],
            'unit': product['unit'],
            'quantity': quantity,
            'subtotal': subtotal,
            'image_path': "sample.jpg"
        })
    
    # Update cart totals
    cart['count'] += quantity
    cart['total'] += subtotal
    
    # Save cart to session
    session['cart'] = cart
    session.modified = True

    return jsonify({
        'success': True, 
        'cart_count': cart['count'],
        'cart_total': cart['total']
    })

# Remove from cart route (AJAX)
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.json
    product_id = data.get('product_id')
    
    # Get cart from session
    cart = session.get('cart', {'items': [], 'count': 0, 'total': 0})
    
    # Find item in cart
    item_index = None
    for i, item in enumerate(cart['items']):
        if str(item['product_id']) == str(product_id):
            item_index = i
            break
    
    if item_index is not None:
        # Get item details before removing
        item = cart['items'][item_index]
        
        # Update cart totals
        cart['count'] -= item['quantity']
        cart['total'] -= item['subtotal']
        
        # Remove item from cart
        cart['items'].pop(item_index)
        
        # Save cart to session
        session['cart'] = cart
        session.modified = True
        
        # Calculate delivery fee
        delivery_fee = 5.00 if cart['total'] < 50 else 0.00
        
        return jsonify({
            'success': True,
            'cart_count': cart['count'],
            'subtotal': cart['total'],
            'delivery_fee': delivery_fee,
            'total': cart['total'] + delivery_fee
        })
    
    return jsonify({'success': False, 'message': 'Item not found in cart'})

# Checkout page route
# Checkout page route
@app.route('/checkout')
def checkout():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to checkout', 'error')
        return redirect(url_for('login'))
        
    # Get cart from session
    cart = session.get('cart', {'items': [], 'count': 0, 'total': 0})
    
    # Ensure cart structure is consistent
    if not cart.get('items'):
        cart['items'] = []
    if not cart.get('count'):
        cart['count'] = 0
    if not cart.get('total'):
        cart['total'] = 0
    
    # Calculate delivery fee
    delivery_fee = 5.00 if cart['total'] < 50 else 0.00
    
    # Calculate total
    total = cart['total'] + delivery_fee
    
    # Calculate tomorrow's date for delivery date input
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.strftime('%Y-%m-%d')
    
    username = session.get('name', '')
    
    # Make sure cart items have all required fields for the template
    for item in cart['items']:
        # Ensure these fields exist in each item
        if 'image_path' not in item:
            item['image_path'] = "images/product_placeholder.jpg"
        if 'unit' not in item:
            item['unit'] = "kg"
        if 'subtotal' not in item and 'price_per_unit' in item and 'quantity' in item:
            item['subtotal'] = item['price_per_unit'] * item['quantity']
    
    return render_template('checkout.html',
                          username=username,
                          cart_items=cart['items'],
                          subtotal=cart['total'],
                          delivery_fee=delivery_fee,
                          total=total,
                          tomorrow_date=tomorrow_date)

# Process checkout route
@app.route('/process_checkout', methods=['POST'])
def process_checkout():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to checkout', 'error')
        return redirect(url_for('login'))
        
    # Get cart from session
    cart = session.get('cart', {'items': [], 'count': 0, 'total': 0})
    
    # Check if cart is empty
    if not cart['items']:
        flash('Your cart is empty', 'error')
        return redirect(url_for('marketplace_user'))
    
    try:
        # Get form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        delivery_date = request.form.get('delivery_date')
        special_instructions = request.form.get('special_instructions')
        
        # Validate required fields
        if not all([name, phone, address, delivery_date]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('checkout'))
        
        # Calculate delivery fee
        delivery_fee = 5.00 if cart['total'] < 50 else 0.00
        
        # Calculate total
        total = cart['total'] + delivery_fee
        
        # Create order
        order_id = create_order(
            customer_id=session['user_id'],
            total_amount=total,
            delivery_address=address,
            contact_number=phone,
            delivery_date=delivery_date,
            special_instructions=special_instructions
        )
        
        if not order_id:
            flash('Error creating order', 'error')
            return redirect(url_for('checkout'))
        
        # Add order items
        for item in cart['items']:
            success = add_order_item(
                order_id=order_id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price_per_unit=item['price_per_unit']
            )
            
            if not success:
                flash('Error adding order item', 'error')
                return redirect(url_for('checkout'))
        
        # Clear cart
        session['cart'] = {'items': [], 'count': 0, 'total': 0}
        session.modified = True
        
        # Show success message
        flash('Order placed successfully!', 'success')
        
        # Redirect to order confirmation page
        return redirect(url_for('order_confirmation', order_id=order_id))
    
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('checkout'))

# Order confirmation page
@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to view order confirmation', 'error')
        return redirect(url_for('login'))
        
    username = session.get('name', '')
    
    # Calculate delivery date (for demo purposes)
    delivery_date = (datetime.now() + timedelta(days=3)).strftime('%B %d, %Y')
    
    return render_template('order_confirmation.html', 
                          username=username,
                          order_id=order_id,
                          delivery_date=delivery_date)

# Order history page
@app.route('/order_history')
def order_history():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login to view your order history', 'error')
        return redirect(url_for('login'))
    
    username = session.get('name', '')
    
    # Get customer orders
    orders = get_customer_orders(session['user_id'])
    
    return render_template('order_history.html', 
                          username=username,
                          orders=orders)

@app.route('/order-placed')
def order_placed():
    username = session.get('name', '')
    customer_id = session['user_id']
    contact_number = session['phone']
    delivery_address = session['location']

    cart = session.get('cart',{'items': [], 'count': 0, 'total': 0})
    total_amount = cart['total']

    print('order placed')

    create_order(customer_id, total_amount, delivery_address, contact_number, delivery_date = None, special_instructions=None)
    session['cart']['count'] = 0
    session['cart']['total'] = 0
    session["cart"] = {'items': [], 'count': 0, 'total': 0}
    return render_template("order_placed.html",username=username, amount=total_amount)

@app.route('/ai-predictions')
def ai_predictions():
    username = session.get('name','')
    return render_template('predictions.html',username=username)

if __name__ == '__main__':
    app.run(debug=True)
