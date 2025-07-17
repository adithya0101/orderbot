import json
class OrderManager:
    def __init__(self, database):
        self.db = database
    def create_order(self, user_phone, cart_items, delivery_address):
        total_amount = sum(item['price'] * item['quantity'] for item in cart_items.values())
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO orders (user_phone, items, total_amount, delivery_address)
                VALUES (?, ?, ?, ?)
            ''', (user_phone, json.dumps(cart_items), total_amount, delivery_address))
            order_id = cursor.lastrowid
            conn.execute('''
                UPDATE users 
                SET order_count = order_count + 1, 
                    total_spent = total_spent + ?,
                    last_interaction = CURRENT_TIMESTAMP
                WHERE phone_number = ?
            ''', (total_amount, user_phone))
            for item_id, item_data in cart_items.items():
                conn.execute('''
                    INSERT INTO order_frequency (user_phone, menu_item_id, frequency, last_ordered)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_phone, menu_item_id) DO UPDATE SET
                        frequency = frequency + ?,
                        last_ordered = CURRENT_TIMESTAMP
                ''', (user_phone, item_id, item_data['quantity'], item_data['quantity']))
            conn.commit()
            return order_id
    def get_all_orders(self):
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT o.*, u.order_count, u.total_spent
                FROM orders o
                JOIN users u ON o.user_phone = u.phone_number
                ORDER BY o.created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    def get_user_orders(self, user_phone):
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM orders 
                WHERE user_phone = ? 
                ORDER BY created_at DESC
            ''', (user_phone,))
            return [dict(row) for row in cursor.fetchall()]
    def get_total_orders(self):
        with self.db.get_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM orders')
            return cursor.fetchone()[0]
    def get_popular_items(self, limit=10):
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT m.name, m.price, SUM(f.frequency) as total_orders
                FROM order_frequency f
                JOIN menu_items m ON f.menu_item_id = m.id
                GROUP BY m.id
                ORDER BY total_orders DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
