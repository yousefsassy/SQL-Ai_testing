import sqlite3
import random
from pathlib import Path
from datetime import date, timedelta

# Same data every time the script is executed
random.seed(42)

DB_PATH = Path("data/database/shop.db")

NUM_CUSTOMERS = 300
NUM_PRODUCTS = 20
NUM_ORDERS = 1200


def random_date(start, end):
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


# --------------------------------------------------
# Create database
# --------------------------------------------------

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")


# --------------------------------------------------
# Create tables
# --------------------------------------------------

cursor.executescript("""
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    order_date TEXT NOT NULL,

    FOREIGN KEY (customer_id)
        REFERENCES customers(id),

    FOREIGN KEY (product_id)
        REFERENCES products(id)
);
""")


# --------------------------------------------------
# Generate 300 customers
# --------------------------------------------------

first_names = [
    "Alice", "John", "Nour", "Youssef", "Emma",
    "Lucas", "Sara", "Adam", "Lena", "Marco",
    "Sofia", "Omar", "Anna", "Daniel", "Julie",
    "Karim", "Maya", "Thomas", "Ines", "Leo"
]

last_names = [
    "Martin", "Smith", "Ben Ali", "Sassi", "Muller",
    "Rossi", "Brown", "Dubois", "Garcia", "Schmidt",
    "Wilson", "Haddad", "Bernard", "Moreau", "Costa"
]

countries = [
    "France",
    "Germany",
    "Tunisia",
    "Italy",
    "Spain",
    "United Kingdom"
]

customers = []

for customer_id in range(1, NUM_CUSTOMERS + 1):

    name = (
        f"{random.choice(first_names)} "
        f"{random.choice(last_names)}"
    )

    country = random.choice(countries)

    customers.append(
        (customer_id, name, country)
    )


cursor.executemany(
    """
    INSERT INTO customers
    (id, name, country)
    VALUES (?, ?, ?)
    """,
    customers
)


# --------------------------------------------------
# Create 20 products
# --------------------------------------------------

products = [
    (1, "Laptop", "Electronics", 999.99),
    (2, "Smartphone", "Electronics", 699.99),
    (3, "Monitor", "Electronics", 249.99),
    (4, "Keyboard", "Electronics", 79.99),
    (5, "Mouse", "Electronics", 29.99),

    (6, "Desk", "Furniture", 299.99),
    (7, "Office Chair", "Furniture", 199.99),
    (8, "Bookshelf", "Furniture", 129.99),
    (9, "Desk Lamp", "Furniture", 49.99),
    (10, "Side Table", "Furniture", 89.99),

    (11, "T-Shirt", "Clothing", 24.99),
    (12, "Hoodie", "Clothing", 59.99),
    (13, "Jeans", "Clothing", 69.99),
    (14, "Jacket", "Clothing", 119.99),
    (15, "Sneakers", "Clothing", 89.99),

    (16, "Yoga Mat", "Sports", 34.99),
    (17, "Dumbbells", "Sports", 59.99),
    (18, "Football", "Sports", 29.99),
    (19, "Tennis Racket", "Sports", 109.99),
    (20, "Gym Bag", "Sports", 44.99)
]


cursor.executemany(
    """
    INSERT INTO products
    (id, name, category, price)
    VALUES (?, ?, ?, ?)
    """,
    products
)


# --------------------------------------------------
# Generate 1200 orders
# --------------------------------------------------

orders = []

start_date = date(2024, 1, 1)
end_date = date(2026, 8, 31)

for order_id in range(1, NUM_ORDERS + 1):

    customer_id = random.randint(
        1,
        NUM_CUSTOMERS
    )

    product_id = random.randint(
        1,
        NUM_PRODUCTS
    )

    quantity = random.randint(1, 5)

    order_date = random_date(
        start_date,
        end_date
    ).isoformat()

    orders.append(
        (
            order_id,
            customer_id,
            product_id,
            quantity,
            order_date
        )
    )


cursor.executemany(
    """
    INSERT INTO orders
    (id, customer_id, product_id, quantity, order_date)
    VALUES (?, ?, ?, ?, ?)
    """,
    orders
)


# --------------------------------------------------
# Save database
# --------------------------------------------------

conn.commit()


# --------------------------------------------------
# Verify database
# --------------------------------------------------

cursor.execute("SELECT COUNT(*) FROM customers")
customer_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM products")
product_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM orders")
order_count = cursor.fetchone()[0]


print("Database created successfully!")
print(f"Database: {DB_PATH}")
print(f"Customers: {customer_count}")
print(f"Products: {product_count}")
print(f"Orders: {order_count}")


conn.close()