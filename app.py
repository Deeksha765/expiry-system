# app.py
# ─────────────────────────────────────────────────────────────
# Main Flask Application: Routes, Auth, APIs
# ─────────────────────────────────────────────────────────────

from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, flash)
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime, date
import pandas as pd
from functools import wraps
from config import Config
from analysis.expiry_analysis import analyze_products

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# ─────────────────────────────────────────────────────────────
# DATABASE CONNECTION HELPER
# ─────────────────────────────────────────────────────────────
def get_db():
    """Returns a fresh MySQL connection."""
    conn = mysql.connector.connect(
        host     = Config.DB_HOST,
        user     = Config.DB_USER,
        password = Config.DB_PASSWORD,
        database = Config.DB_NAME
    )
    return conn

# ─────────────────────────────────────────────────────────────
# DECORATORS — protect routes that need login
# ─────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        # For demo: allow plain-text match OR hashed match
        if user and (password == user['password'] or
                     check_password_hash(user['password'], password)):
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['role']     = user['role']
            flash(f"Welcome, {user['username']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# ─────────────────────────────────────────────────────────────
# DASHBOARD ROUTE
# ─────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        conn.close()

        analysis = analyze_products(products)

        return render_template('dashboard.html',
                               analysis  = analysis,
                               username  = session['username'],
                               role      = session['role'])
    except Exception as e:
        # This will show the REAL error in browser
        return f"<h2>Error: {str(e)}</h2><p>Check terminal for details.</p>", 500

# ─────────────────────────────────────────────────────────────
# SCANNER ROUTE
# ─────────────────────────────────────────────────────────────

@app.route('/scan')
@login_required
def scan():
    return render_template('scan.html')

# ─────────────────────────────────────────────────────────────
# API: FETCH PRODUCT BY BARCODE (called by JS after scanning)
# ─────────────────────────────────────────────────────────────

@app.route('/api/product/<path:barcode>')
@login_required
def get_product_by_barcode(barcode):
    # Clean the barcode — remove spaces, dashes
    barcode = barcode.strip().replace(' ', '').replace('-', '')
    
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE barcode = %s", (barcode,))
    product = cursor.fetchone()

    if product:
        product['mfg_date']    = str(product['mfg_date'])
        product['exp_date']    = str(product['exp_date'])
        product['created_at']  = str(product['created_at'])

        exp_date       = date.fromisoformat(product['exp_date'])
        today          = date.today()
        days_remaining = (exp_date - today).days

        if days_remaining < 0:
            status = 'Expired'
        elif days_remaining <= 30:
            status = 'Near-Expiry'
        else:
            status = 'Safe'

        product['days_remaining'] = days_remaining
        product['status']         = status

        cursor.execute(
            "INSERT INTO scan_logs (user_id, product_id, status) VALUES (%s,%s,%s)",
            (session['user_id'], product['id'], status)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'product': product})
    else:
        conn.close()
        return jsonify({'success': False,
                        'message': 'Product not found.',
                        'barcode': barcode})

# ─────────────────────────────────────────────────────────────
# PRODUCT MANAGEMENT ROUTES (Admin only)
# ─────────────────────────────────────────────────────────────

@app.route('/products')
@login_required
@admin_required
def products():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products ORDER BY exp_date ASC")
    all_products = cursor.fetchall()
    conn.close()

    today = date.today()
    enriched = []
    for p in all_products:
        days = (p['exp_date'] - today).days
        p['days_remaining'] = days
        p['status'] = 'Expired' if days < 0 else ('Near-Expiry' if days <= 30 else 'Safe')
        enriched.append(p)

    return render_template('products.html', products=enriched)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        data = request.form
        conn   = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO products
                  (barcode, name, category, manufacturer, mfg_date, exp_date, quantity, unit, added_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['barcode'], data['name'], data['category'],
                data['manufacturer'], data['mfg_date'], data['exp_date'],
                data['quantity'], data['unit'], session['user_id']
            ))
            conn.commit()
            flash('Product added successfully!', 'success')
        except mysql.connector.IntegrityError:
            flash('Barcode already exists!', 'danger')
        finally:
            conn.close()
        return redirect(url_for('products'))

    return render_template('add_product.html')

@app.route('/products/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(pid):
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        data = request.form
        cursor.execute("""
            UPDATE products
            SET name=%s, category=%s, manufacturer=%s,
                mfg_date=%s, exp_date=%s, quantity=%s, unit=%s
            WHERE id=%s
        """, (
            data['name'], data['category'], data['manufacturer'],
            data['mfg_date'], data['exp_date'], data['quantity'],
            data['unit'], pid
        ))
        conn.commit()
        conn.close()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))

    cursor.execute("SELECT * FROM products WHERE id = %s", (pid,))
    product = cursor.fetchone()
    conn.close()
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<int:pid>')
@login_required
@admin_required
def delete_product(pid):
    conn   = get_db()
    cursor = conn.cursor()
    # Delete related scan logs first (foreign key constraint)
    cursor.execute("DELETE FROM scan_logs WHERE product_id = %s", (pid,))
    cursor.execute("DELETE FROM products WHERE id = %s", (pid,))
    conn.commit()
    conn.close()
    flash('Product deleted.', 'warning')
    return redirect(url_for('products'))

# ─────────────────────────────────────────────────────────────
# API: Dashboard Chart Data
# ─────────────────────────────────────────────────────────────

@app.route('/api/chart-data')
@login_required
def chart_data():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    analysis = analyze_products(products)
    return jsonify(analysis['chart_data'])

# app.py — add this block near the bottom

from datetime import datetime

@app.context_processor
def inject_now():
    """Makes 'now' available in all templates automatically."""
    return {'now': datetime.now()}

# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)