class MenuManager:
    def __init__(self, database):
        self.db = database
    def load_sample_menu(self):
        sample_items = [
            {'name': 'Chicken Wings', 'description': 'Crispy chicken wings with BBQ sauce', 'price': 250, 'category': 'Appetizers'},
            {'name': 'Veg Spring Rolls', 'description': 'Crispy vegetable spring rolls', 'price': 180, 'category': 'Appetizers'},
            {'name': 'Paneer Tikka', 'description': 'Grilled paneer with spices', 'price': 220, 'category': 'Appetizers'},
            {'name': 'Chicken Biryani', 'description': 'Fragrant basmati rice with chicken', 'price': 350, 'category': 'Main Course'},
            {'name': 'Veg Biryani', 'description': 'Fragrant basmati rice with vegetables', 'price': 280, 'category': 'Main Course'},
            {'name': 'Butter Chicken', 'description': 'Creamy tomato-based chicken curry', 'price': 320, 'category': 'Main Course'},
            {'name': 'Dal Makhani', 'description': 'Rich and creamy black lentils', 'price': 200, 'category': 'Main Course'},
            {'name': 'Mango Lassi', 'description': 'Creamy mango yogurt drink', 'price': 80, 'category': 'Beverages'},
            {'name': 'Masala Chai', 'description': 'Spiced Indian tea', 'price': 40, 'category': 'Beverages'},
            {'name': 'Fresh Lime Soda', 'description': 'Refreshing lime soda', 'price': 50, 'category': 'Beverages'},
            {'name': 'Gulab Jamun', 'description': 'Sweet milk dumplings in syrup', 'price': 100, 'category': 'Desserts'},
            {'name': 'Ice Cream', 'description': 'Vanilla, chocolate, or strawberry', 'price': 80, 'category': 'Desserts'},
        ]
        with self.db.get_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) FROM menu_items')
            count = cursor.fetchone()[0]
            if count == 0:
                for item in sample_items:
                    conn.execute('''
                        INSERT INTO menu_items (name, description, price, category)
                        VALUES (?, ?, ?, ?)
                    ''', (item['name'], item['description'], item['price'], item['category']))
                conn.commit()
    def get_all_items(self):
        with self.db.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM menu_items WHERE available = TRUE')
            return [dict(row) for row in cursor.fetchall()]
    def get_menu_by_category(self):
        items = self.get_all_items()
        categories = {}
        for item in items:
            category = item['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        return categories
    def get_item_by_name_or_id(self, identifier):
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM menu_items 
                WHERE LOWER(name) LIKE ? AND available = TRUE
            ''', (f'%{identifier}%',))
            result = cursor.fetchone()
            if result:
                return dict(result)
            try:
                item_id = int(identifier)
                cursor = conn.execute('''
                    SELECT * FROM menu_items 
                    WHERE id = ? AND available = TRUE
                ''', (item_id,))
                result = cursor.fetchone()
                if result:
                    return dict(result)
            except ValueError:
                pass
            return None
