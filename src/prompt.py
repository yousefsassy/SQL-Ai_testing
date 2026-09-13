def build_prompt(question):
    return f"""
You are given the following SQLite database schema:

customers(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL
)

products(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
)

orders(
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    order_date TEXT NOT NULL
)

Relationships:
- orders.customer_id references customers.id
- orders.product_id references products.id

Task:
Convert the natural-language question below into one valid read-only SQLite query.

Rules:
- Use only the tables and columns defined above.
- Return exactly one SQLite query.
- The query must be read-only: SELECT or WITH ... SELECT only.
- Return only the SQL query.
- Do not include explanations.
- Do not include markdown or code fences.
- Do not include SQL comments.
- Return only the columns requested by the question.
- Do not add helper columns such as IDs, counts, or totals unless the question explicitly asks for them.
- Use ORDER BY only when the question requires ordering, ranking, top, most, least, earliest, or latest results.
- The query must be executable directly in SQLite.

Question:
{question}
""".strip()