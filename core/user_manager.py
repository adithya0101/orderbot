class UserManager:
    def __init__(self, database):
        self.db = database
    def get_or_create_user(self, phone_number):
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM users WHERE phone_number = ?
            ''', (phone_number,))
            user = cursor.fetchone()
            if user:
                conn.execute('''
                    UPDATE users 
                    SET last_interaction = CURRENT_TIMESTAMP 
                    WHERE phone_number = ?
                ''', (phone_number,))
                conn.commit()
                return dict(user)
            else:
                conn.execute('''
                    INSERT INTO users (phone_number) VALUES (?)
                ''', (phone_number,))
                conn.commit()
                return self.get_or_create_user(phone_number)
    def get_user_stats(self, phone_number):
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM users WHERE phone_number = ?
            ''', (phone_number,))
            user = cursor.fetchone()
            return dict(user) if user else None
    def get_total_users(self):
        with self.db.get_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]
    def get_user_preferences(self, phone_number):
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT m.name, m.price, f.frequency
                FROM order_frequency f
                JOIN menu_items m ON f.menu_item_id = m.id
                WHERE f.user_phone = ?
                ORDER BY f.frequency DESC
                LIMIT 5
            ''', (phone_number,))
            return [dict(row) for row in cursor.fetchall()]
