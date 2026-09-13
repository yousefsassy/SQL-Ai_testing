from src.models import generate_sql
from src.score import score_sql


DB_PATH = "data/database/shop.db"

SCHEMA = """
customers(
    id INTEGER,
    name TEXT,
    country TEXT
)

products(
    id INTEGER,
    name TEXT,
    category TEXT,
    price REAL
)

orders(
    id INTEGER,
    customer_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    order_date TEXT
)
"""


question = "How many customers are from France?"

expected_sql = """
SELECT COUNT(*)
FROM customers
WHERE country = 'France';
"""


# Generate SQL with the model
generated_sql = generate_sql(
    question=question,
    schema=SCHEMA,
    model="gemma3:1b"
)


print("Question:")
print(question)

print("\nGenerated SQL:")
print(generated_sql)


# Score the generated SQL
result = score_sql(
    generated_sql=generated_sql,
    expected_sql=expected_sql,
    db_path=DB_PATH,
    order_matters=False
)


print("\nEvaluation:")
print(result)