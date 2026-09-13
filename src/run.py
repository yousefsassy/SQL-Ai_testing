import json

from src.models import generate_sql
from src.score import score_sql


DB_PATH = "data/database/shop.db"
MODEL = "gemma3:1b"


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
evaluated_count = 0
correct_count = 0



   

def load_items(file_path):
    items = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                items.append(json.loads(line))

    return items


def main():
    items = load_items("data/database/items.jsonl")
    evaluated_count = 0
    correct_count = 0

    for item in items:


        evaluated_count += 1

        # For now, only run development questions
        if item["split"] != "dev":
            continue

        print("\n" + "=" * 60)

        print(f"Question {item['id']}:")
        print(item["question"])

        generated_sql = generate_sql(
            question=item["question"],
            schema=SCHEMA,
            model=MODEL
        )

        print("\nGenerated SQL:")
        print(generated_sql)

        result = score_sql(
            generated_sql=generated_sql,
            expected_sql=item["expected_sql"],
            db_path=DB_PATH,
            order_matters=item["order_matters"]
        )

        print("\nResult:")
        print(result["status"])

        if result["correct"]:
            correct_count += 1

    print("\n" + "=" * 60)

    print("Final result:")
    print(f"Correct: {correct_count}/{evaluated_count}")
    print(f"Accuracy: {correct_count / evaluated_count * 100:.2f}%")


if __name__ == "__main__":
    main()