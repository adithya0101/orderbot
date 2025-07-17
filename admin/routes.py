from flask import Blueprint, render_template, jsonify, request, send_file, session, redirect, url_for, flash
from core.database import Database
from core.order_manager import OrderManager
from core.user_manager import UserManager
from core.menu_manager import MenuManager
import io
import csv
from datetime import datetime
import os
from functools import wraps
import json

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

db = Database()
order_manager = OrderManager(db)
user_manager = UserManager(db)
menu_manager = MenuManager(db)

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# --- Auth Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin/login.html')

@admin_bp.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/admin/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/api/orders')
@login_required
def api_orders():
    orders = order_manager.get_all_orders()
    for o in orders:
        o['customer_name'] = o.get('user_phone', 'Customer')
        o['payment_method'] = o.get('payment_method', 'pay_cash')
    return jsonify({'status': 'success', 'orders': orders})

@admin_bp.route('/api/orders/<int:order_id>')
@login_required
def api_order_detail(order_id):
    orders = order_manager.get_all_orders()
    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return jsonify({'status': 'error', 'message': 'Order not found'}), 404
    # Parse items JSON and fetch menu details
    try:
        items = []
        cart = order.get('items')
        if isinstance(cart, str):
            cart = json.loads(cart)
        total = 0
        for item_id, item in cart.items():
            menu_item = menu_manager.get_item_by_name_or_id(item_id)
            subtotal = item['price'] * item['quantity']
            total += subtotal
            items.append({
                'name': menu_item['name'] if menu_item else item.get('name', str(item_id)),
                'quantity': item['quantity'],
                'price': item['price'],
                'subtotal': subtotal
            })
    except Exception as e:
        items = []
    order['items'] = items
    order['customer_name'] = order.get('user_phone', 'Customer')
    order['customer_phone'] = order.get('user_phone', '')
    order['customer_address'] = order.get('delivery_address', '')
    order['payment_method'] = order.get('payment_method', 'pay_cash')
    order['estimated_delivery'] = order.get('created_at', '')
    return jsonify({'status': 'success', 'order': order})

@admin_bp.route('/api/analytics')
@login_required
def api_analytics():
    orders = order_manager.get_all_orders()
    total_orders = len(orders)
    total_revenue = sum(float(o.get('total_amount', 0)) for o in orders)
    # Popular items
    item_counts = {}
    for o in orders:
        cart = o.get('items')
        if isinstance(cart, str):
            cart = json.loads(cart)
        for item_id, item in cart.items():
            name = item.get('name', str(item_id))
            item_counts[name] = item_counts.get(name, 0) + item['quantity']
    popular_items = [{'name': k, 'quantity': v} for k, v in sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    # Payment methods (currently only cash)
    payment_methods = [{'method': 'pay_cash', 'count': total_orders}]
    return jsonify({
        'status': 'success',
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'popular_items': popular_items,
        'payment_methods': payment_methods
    })

@admin_bp.route('/api/orders/export')
@login_required
def api_orders_export():
    orders = order_manager.get_all_orders()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Order ID', 'Customer', 'Amount', 'Status', 'Date'])
    for o in orders:
        writer.writerow([o['id'], o.get('user_phone', ''), o.get('total_amount', ''), o.get('status', ''), o.get('created_at', '')])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name=f'orders_{datetime.now().date()}.csv')
