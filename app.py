from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
from datetime import datetime
import json
import re
from core.database import Database
from core.menu_manager import MenuManager
from core.order_manager import OrderManager
from core.user_manager import UserManager
from config import Config
from admin import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)

db = Database()
menu_manager = MenuManager(db)
order_manager = OrderManager(db)
user_manager = UserManager(db)

app.register_blueprint(admin_bp)

USER_STATES = {
    'MENU_BROWSING': 'menu_browsing',
    'ADDING_TO_CART': 'adding_to_cart',
    'QUANTITY_INPUT': 'quantity_input',
    'LOCATION_INPUT': 'location_input',
    'ORDER_CONFIRMATION': 'order_confirmation'
}

class WhatsAppBot:
    def __init__(self):
        self.user_sessions = {}
    def get_user_state(self, phone_number):
        return self.user_sessions.get(phone_number, {
            'state': USER_STATES['MENU_BROWSING'],
            'cart': {},
            'current_item': None,
            'location': None
        })
    def update_user_state(self, phone_number, state_data):
        self.user_sessions[phone_number] = state_data
    def process_message(self, phone_number, message_body):
        user = user_manager.get_or_create_user(phone_number)
        user_state = self.get_user_state(phone_number)
        message_body = message_body.strip().lower()
        if user_state['state'] == USER_STATES['MENU_BROWSING']:
            return self.handle_menu_browsing(phone_number, message_body, user_state)
        elif user_state['state'] == USER_STATES['QUANTITY_INPUT']:
            return self.handle_quantity_input(phone_number, message_body, user_state)
        elif user_state['state'] == USER_STATES['LOCATION_INPUT']:
            return self.handle_location_input(phone_number, message_body, user_state)
        elif user_state['state'] == USER_STATES['ORDER_CONFIRMATION']:
            return self.handle_order_confirmation(phone_number, message_body, user_state)
        else:
            return self.handle_menu_browsing(phone_number, message_body, user_state)
    def handle_menu_browsing(self, phone_number, message_body, user_state):
        if message_body in ['hi', 'hello', 'hey', 'start', 'menu']:
            return self.show_welcome_menu()
        elif message_body == 'cart':
            return self.show_cart(user_state)
        elif message_body == 'checkout':
            if not user_state['cart']:
                return "🛒 Your cart is empty! Browse our menu first."
            user_state['state'] = USER_STATES['LOCATION_INPUT']
            self.update_user_state(phone_number, user_state)
            return "📍 Please share your delivery location (address):"
        elif message_body == 'clear':
            user_state['cart'] = {}
            self.update_user_state(phone_number, user_state)
            return "🗑️ Cart cleared! What would you like to order?"
        else:
            item = menu_manager.get_item_by_name_or_id(message_body)
            if item:
                user_state['current_item'] = item
                user_state['state'] = USER_STATES['QUANTITY_INPUT']
                self.update_user_state(phone_number, user_state)
                return f"🍽️ *{item['name']}* - ₹{item['price']}\n\n{item['description']}\n\nHow many would you like to order?"
            else:
                return self.show_help_message()
    def handle_quantity_input(self, phone_number, message_body, user_state):
        try:
            quantity = int(message_body)
            if quantity <= 0:
                return "❌ Please enter a valid quantity (greater than 0)."
            item = user_state['current_item']
            item_id = item['id']
            if item_id in user_state['cart']:
                user_state['cart'][item_id]['quantity'] += quantity
            else:
                user_state['cart'][item_id] = {
                    'name': item['name'],
                    'price': item['price'],
                    'quantity': quantity
                }
            user_state['state'] = USER_STATES['MENU_BROWSING']
            user_state['current_item'] = None
            self.update_user_state(phone_number, user_state)
            return f"✅ Added {quantity} x {item['name']} to cart!\n\nType 'cart' to view cart or 'menu' to continue ordering."
        except ValueError:
            return "❌ Please enter a valid number for quantity."
    def handle_location_input(self, phone_number, message_body, user_state):
        if len(message_body) < 10:
            return "❌ Please provide a detailed address with area/landmark."
        user_state['location'] = message_body
        user_state['state'] = USER_STATES['ORDER_CONFIRMATION']
        self.update_user_state(phone_number, user_state)
        return self.show_order_summary(user_state)
    def handle_order_confirmation(self, phone_number, message_body, user_state):
        if message_body in ['yes', 'y', 'confirm', 'order']:
            order_id = order_manager.create_order(
                phone_number, 
                user_state['cart'], 
                user_state['location']
            )
            user_state['cart'] = {}
            user_state['state'] = USER_STATES['MENU_BROWSING']
            user_state['location'] = None
            self.update_user_state(phone_number, user_state)
            return f"🎉 Order confirmed! Order ID: #{order_id}\n\n💰 Payment: Cash on Delivery\n⏰ Estimated delivery: 30-45 minutes\n\nThank you for ordering with us!"
        elif message_body in ['no', 'n', 'cancel']:
            user_state['state'] = USER_STATES['MENU_BROWSING']
            self.update_user_state(phone_number, user_state)
            return "❌ Order cancelled. Type 'menu' to start over."
        else:
            return "Please reply with 'yes' to confirm or 'no' to cancel the order."
    def show_welcome_menu(self):
        menu_text = "🍽️ *Welcome to Tasty Bites Restaurant!*\n\n"
        menu_text += "📋 *Our Menu:*\n\n"
        categories = menu_manager.get_menu_by_category()
        for category, items in categories.items():
            menu_text += f"*{category}:*\n"
            for item in items:
                menu_text += f"• {item['name']} - ₹{item['price']}\n"
            menu_text += "\n"
        menu_text += "💡 *How to order:*\n"
        menu_text += "• Type item name to add to cart\n"
        menu_text += "• Type 'cart' to view your cart\n"
        menu_text += "• Type 'checkout' to place order\n"
        menu_text += "• Type 'clear' to empty cart\n"
        return menu_text
    def show_cart(self, user_state):
        if not user_state['cart']:
            return "🛒 Your cart is empty! Browse our menu to add items."
        cart_text = "🛒 *Your Cart:*\n\n"
        total = 0
        for item_id, item in user_state['cart'].items():
            subtotal = item['price'] * item['quantity']
            total += subtotal
            cart_text += f"• {item['name']} x{item['quantity']} - ₹{subtotal}\n"
        cart_text += f"\n💰 *Total: ₹{total}*\n\n"
        cart_text += "Type 'checkout' to proceed with order or continue browsing!"
        return cart_text
    def show_order_summary(self, user_state):
        summary = "📋 *Order Summary:*\n\n"
        total = 0
        for item_id, item in user_state['cart'].items():
            subtotal = item['price'] * item['quantity']
            total += subtotal
            summary += f"• {item['name']} x{item['quantity']} - ₹{subtotal}\n"
        summary += f"\n💰 *Total: ₹{total}*\n"
        summary += f"📍 *Delivery Address:* {user_state['location']}\n"
        summary += f"💳 *Payment:* Cash on Delivery\n\n"
        summary += "Reply 'yes' to confirm or 'no' to cancel."
        return summary
    def show_help_message(self):
        return ("❓ I didn't understand that. Try:\n\n"
                "• Type 'menu' to see our menu\n"
                "• Type an item name to order\n"
                "• Type 'cart' to view your cart\n"
                "• Type 'checkout' to place order")
bot = WhatsAppBot()
@app.route('/')
def home():
    return '''
    <h1>Welcome to the WhatsApp Order Bot!</h1>
    <p>This is a demo portfolio project for WhatsApp-based restaurant ordering using Flask and Twilio.</p>
    <ul>
        <li>To test the WhatsApp bot, message the Twilio sandbox number after joining the sandbox.</li>
        <li>Admin dashboard: <a href="/admin/login">/admin/login</a></li>
    </ul>
    <p>See the README for setup and testing instructions.</p>
    '''
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        phone_number = request.form.get('From', '').replace('whatsapp:', '')
        message_body = request.form.get('Body', '')
        response_text = bot.process_message(phone_number, message_body)
        response = MessagingResponse()
        response.message(response_text)
        return str(response)
    except Exception as e:
        print(f"Error processing webhook: {e}")
        response = MessagingResponse()
        response.message("Sorry, something went wrong. Please try again.")
        return str(response)
@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'total_users': user_manager.get_total_users(),
        'total_orders': order_manager.get_total_orders()
    })
@app.route('/orders', methods=['GET'])
def get_orders():
    orders = order_manager.get_all_orders()
    return jsonify(orders)
@app.route('/menu', methods=['GET'])
def get_menu():
    menu = menu_manager.get_all_items()
    return jsonify(menu)
if __name__ == '__main__':
    db.init_db()
    menu_manager.load_sample_menu()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
