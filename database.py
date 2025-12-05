import sqlite3


# создание таблиц


def create_users_tables():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.executescript('''
    DROP TABLE IF EXISTS users;
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        full_name TEXT, 
        telegram_id BIGINT NOT NULL UNIQUE,
        phone TEXT
    ); 
    ''')
def create_cards_table():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.executescript('''
    DROP TABLE IF EXISTS cards;
    CREATE TABLE IF NOT EXISTS cards(
        card_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER REFERENCES users(user_id), 
        total_price DECIMAL(12, 2) DEFAULT 0, 
        total_products INTEGER DEFAULT 0
    );
    ''')



def create_card_products_table():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.executescript('''
    DROP TABLE IF EXISTS card_products;
    CREATE TABLE IF NOT EXISTS card_products(
        card_product_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        product_name VARCHAR(50) NOT NULL, 
        quantity INTEGER NOT NULL, 
        final_price DECIMAL(12, 2) NOT NULL,
        card_id INTEGER REFERENCES cards(card_id),
        
        UNIQUE(product_name, card_id) 
    );
    ''')



def create_categories_table():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories(
        category_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        category_name VARCHAR(30) NOT NULL UNIQUE
    );
    ''')


def create_products_table():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    product_name VARCHAR(30) NOT NULL UNIQUE, 
    price DECIMAL(12, 2)  NOT NULL, 
    description VARCHAR(200), 
    image TEXT, 
    category_id INTEGER NOT NULL, 
    
    FOREIGN KEY(category_id) REFERENCES categories(category_id)
    );
    ''')


def order_total_price():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.executescript('''
    DROP TABLE IF EXISTS orders_total_price;
    CREATE TABLE IF NOT EXISTS orders_total_price(
    orders_total_price_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    card_id INTEGER REFERENCES cards(card_id), 
    total_price DECIMAL(12, 2) DEFAULT 0, 
    total_products INTEGER DEFAULT 0, 
    time_now TEXT, 
    new_date TEXT
    );
    ''')


def order():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.executescript('''
    DROP TABLE IF EXISTS orders;
    CREATE TABLE IF NOT EXISTS orders(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    orders_total_price_id INTEGER REFERENCES orders_total_price(orders_total_price_id), 
    product_name VARCHAR(100) NOT NULL, 
    quantity INTEGER NOT NULL, 
    final_price DECIMAL(12, 2) NOT NULL
    );
    ''')



def create_table_feedbacks():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.executescript('''
    DROP TABLE IF EXISTS feedbacks;
    CREATE TABLE IF NOT EXISTS feedbacks(
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        feedback_text TEXT, 
        full_name TEXT REFERENCES users(full_name), 
        user_id INTEGER REFERENCES users(user_id)
    );
    ''')


# -----------------------------------


# добавление в таблицу

def insert_into_categories():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO categories(category_name) VALUES
    ('Лаваш'),
    ('Донары'),
    ('Бургеры'),
    ('Хот-доги'),
    ('Напитки'),
    ('Соусы')
    ''')
    database.commit()
    database.close()


# insert_into_categories()


def insert_products_table():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO products(category_id, product_name, price, description, image) VALUES
    (1, 'Лаваш говяжий', 28000, 'Мясо, огурчики, чипсы, помидоры', 'media/Lavash/lavash_meet.jpg'),
    (1, 'Лаваш куриный', 26000, 'Мясо куриное, огурчики, чипсы, помидоры', 'media/Lavash/lavash_chicken.jpg'),
    (1, 'Лаваш говяжий с сыром', 30000, 'Мясо, огурчики, чипсы, помидоры, сыр', 'media/Lavash/lavash_meet_cheese.png')
    ''')
    database.commit()
    database.close()


# insert_products_table()


def first_register_user(chat_id, full_name):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO users(telegram_id, full_name) VALUES (?, ?)
    ''', (chat_id, full_name))
    database.commit()
    database.close()


def update_user_to_finish_register(chat_id, phone):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
        UPDATE users
        SET phone = ?
        WHERE telegram_id = ?
    ''', (phone, chat_id))
    database.commit()
    database.close()


def insert_into_card(chat_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO cards(user_id) VALUES
    (
    (SELECT user_id FROM users WHERE telegram_id = ?)
    )
    ''', (chat_id,))
    database.commit()
    database.close()


def insert_or_update_card_product(card_id, product_name, quantity, final_price):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    try:
        cursor.execute('''
        INSERT INTO card_products(card_id, product_name, quantity, final_price)
        VALUES(?, ?, ?, ?)
        ''', (card_id, product_name, quantity, final_price))
        database.commit()
        return True

    except:
        cursor.execute('''
        UPDATE card_products
        SET quantity = ?, 
        final_price = ?
        WHERE product_name = ? AND card_id = ?
        ''', (quantity, final_price, product_name, card_id))
        database.commit()
        return False
    finally:
        database.close()


def update_total_product_price(card_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    UPDATE cards
    SET total_products = (
    SELECT SUM(quantity) FROM card_products
    WHERE card_id = :card_id
    ), 
    total_price = (
    SELECT SUM(final_price) FROM card_products
    WHERE card_id = :card_id
    )
    WHERE card_id = :card_id
    ''', {'card_id': card_id})
    database.commit()
    database.close()


def delete_card_prodcut_from(card_product_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    DELETE FROM card_products WHERE card_product_id = ?
    ''', (card_product_id,))
    database.commit()
    database.close()


def save_order_table(card_id, total_products, total_price, time_now, new_date):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO orders_total_price(card_id, total_products, total_price, time_now, new_date)
    VALUES (?, ?, ?, ?, ?)
    ''', (card_id, total_products, total_price, time_now, new_date))
    database.commit()
    database.close()


def save_order(orders_total_id, product_name, quantity, final_price):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO orders(orders_total_price_id, product_name, quantity, final_price)
    VALUES (?, ?, ?, ?)
    ''', (orders_total_id, product_name, quantity, final_price))
    database.commit()
    database.close()

def update_users_name(chat_id, new_name):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    UPDATE users
    SET full_name = ?
    WHERE telegram_id = ?
    ''', (new_name, chat_id))
    database.commit()
    database.close()



def insert_into_feedbacks(text, chat_id, full_name):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO feedbacks(feedback_text, full_name, user_id)
    VALUES(?, ?, (SELECT user_id FROM users WHERE telegram_id = ?))
    ''', (text, full_name, chat_id))
    database.commit()
    database.close()

def update_users_phone(chat_id, new_phone):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
        UPDATE users
        SET phone = ?
        WHERE telegram_id = ?
        ''', (new_phone, chat_id))
    database.commit()
    database.close()

# --------------------------------------------------------------------------

# получение информации из базы

def first_select_user(chat_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM users WHERE telegram_id = ?
    ''', (chat_id,))
    user = cursor.fetchone()
    database.close()

    return user


def get_all_categories():
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM categories;
    ''')
    categories = cursor.fetchall()
    database.close()
    return categories


def get_products_by_category_id(category_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_id, product_name FROM products
    WHERE category_id = ?
    ''', (category_id,))
    products = cursor.fetchall()
    return products


def get_product_detail(product_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM products
    WHERE product_id = ?
    ''', (product_id,))
    product = cursor.fetchone()
    database.close()
    return product


def get_user_card_id(chat_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT card_id FROM cards
    WHERE user_id = (
        SELECT user_id FROM users
        WHERE telegram_id = ?
    )
    ''', (chat_id,))

    card_id = cursor.fetchone()[0]
    database.close()
    return card_id


def get_quantity(card_id, product):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT quantity FROM card_products
    WHERE card_id = ? AND product_name = ?
    ''', (card_id, product))
    quantity = cursor.fetchone()[0]
    database.close()
    return quantity


def get_card_products(card_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_name, quantity, final_price FROM card_products
    WHERE card_id = ?
    ''', (card_id,))
    card_products = cursor.fetchall()
    database.close()
    return card_products


def get_total_products_price(card_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT total_products, total_price FROM cards WHERE card_id = ?
    ''', (card_id,))
    total_products, total_price = cursor.fetchone()
    database.close()
    return total_products, total_price


def get_card_product_for_delete(card_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT card_product_id, product_name FROM card_products
    WHERE card_id = ?
    ''', (card_id,))
    card_products = cursor.fetchall()
    database.close()
    return card_products




def orders_total_price(card_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT orders_total_price_id FROM orders_total_price
    WHERE card_id = ?
    ''', (card_id,))
    order_total_id = cursor.fetchall()[-1][0]
    database.close()
    return order_total_id

def get_orders_total_price(card_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM orders_total_price
    WHERE card_id = ?
    ''', (card_id,))
    orders_total_price = cursor.fetchall()
    database.close()
    return orders_total_price

def get_detail_product(id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_name, quantity, final_price FROM orders
    WHERE orders_total_price_id = ?
    ''', (id,))
    detail_product = cursor.fetchall()
    database.close()
    return detail_product

def get_user_name(chat_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    SELECT full_name FROM users
    WHERE telegram_id = ?
    ''', (chat_id,))
    name = cursor.fetchone()[0]
    database.close()
    return name

# удаление

def drop_card_products_default(card_id):
    database = sqlite3.connect('vkusnyaha.bd')
    cursor = database.cursor()
    cursor.execute('''
    DELETE FROM card_products WHERE card_id = ?
    ''', (card_id,))
    database.commit()
    database.close()

