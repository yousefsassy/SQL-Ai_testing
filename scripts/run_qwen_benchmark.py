import csv
import json
from pathlib import Path

import numpy as np

from src.models import call_qwen
from src.score import score_sql


DB_PATH = "data/database/shop.db"
ITEMS_PATH = "data/database/items.jsonl"

RESULTS_DIR = Path("results")
PER_ITEM_PATH = RESULTS_DIR / "qwen_per_item.csv"
SUMMARY_PATH = RESULTS_DIR / "qwen_summary.csv"


def build_prompt(question):
    return f"""
You are given the following SQLite database schema:

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

Convert the following natural-language question into SQLite SQL.

Return ONLY the SQL query.
Do not include markdown.
Do not include explanations.

Question:
{question}
""".strip()


# ---------------------------------------------
# Load benchmark items
# ---------------------------------------------

with open(ITEMS_PATH, "r", encoding="utf-8") as file:
    items = [
        json.loads(line)
        for line in file
        if line.strip()
    ]


RESULTS_DIR.mkdir(exist_ok=True)


results = []
correct_count = 0


# ---------------------------------------------
# Run Qwen on every item
# ---------------------------------------------

for item in items:

    prompt = build_prompt(item["question"])

    qwen_result = call_qwen(prompt)

    generated_sql = qwen_result["text"]

    score = score_sql(
        generated_sql,
        item["expected_sql"],
        DB_PATH,
        order_matters=item["order_matters"]
    )

    if score["correct"]:
        correct_count += 1

    row = {
        "model": "qwen3:8b",
        "item_id": item["id"],
        "split": item["split"],
        "difficulty": item["difficulty"],
        "question": item["question"],
        "generated_sql": generated_sql,
        "correct": score["correct"],
        "status": score["status"],
        "latency_ms": round(qwen_result["latency_ms"], 2),
        "input_tokens": qwen_result["input_tokens"],
        "output_tokens": qwen_result["output_tokens"],
        "tokens_per_second": round(
            qwen_result["tokens_per_second"],
            2
        )
    }

    results.append(row)

    print()
    print(
        f"Question {item['id']}: "
        f"{item['question']}"
    )
    print(f"Generated SQL: {generated_sql}")
    print(f"Status: {score['status']}")
    print(
        f"Latency: "
        f"{qwen_result['latency_ms']:.2f} ms"
    )
    print(
        f"Tokens/sec: "
        f"{qwen_result['tokens_per_second']:.2f}"
    )


# ---------------------------------------------
# Save per-item results
# ---------------------------------------------

with open(
    PER_ITEM_PATH,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = results[0].keys()

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


# ---------------------------------------------
# Calculate summary
# ---------------------------------------------

latencies = [
    row["latency_ms"]
    for row in results
]

token_speeds = [
    row["tokens_per_second"]
    for row in results
]

p50_latency = np.percentile(latencies, 50)
p95_latency = np.percentile(latencies, 95)

average_tokens_per_second = np.mean(token_speeds)

accuracy = correct_count / len(items)


summary = {
    "model": "qwen3:8b",
    "correct": correct_count,
    "total": len(items),
    "accuracy": round(accuracy, 4),
    "p50_latency_ms": round(p50_latency, 2),
    "p95_latency_ms": round(p95_latency, 2),
    "avg_tokens_per_second": round(
        average_tokens_per_second,
        2
    )
}


with open(
    SUMMARY_PATH,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=summary.keys()
    )

    writer.writeheader()
    writer.writerow(summary)


# ---------------------------------------------
# Print summary
# ---------------------------------------------

print()
print("=" * 50)
print("QWEN3 8B RESULTS")
print("=" * 50)

print(
    f"Accuracy: "
    f"{correct_count}/{len(items)} "
    f"({accuracy * 100:.2f}%)"
)

print(
    f"p50 latency: "
    f"{p50_latency:.2f} ms"
)

print(
    f"p95 latency: "
    f"{p95_latency:.2f} ms"
)

print(
    f"Average tokens/sec: "
    f"{average_tokens_per_second:.2f}"
)

print()
print(
    f"Per-item results saved to: "
    f"{PER_ITEM_PATH}"
)

print(
    f"Summary saved to: "
    f"{SUMMARY_PATH}"
)