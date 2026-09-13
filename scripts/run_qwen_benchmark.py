import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np

from src.cost import calculate_local_cost_per_1000
from src.models import call_qwen
from src.parser import parse_sql
from src.prompt import build_prompt
from src.score import score_sql


DB_PATH = "data/database/shop.db"
ITEMS_PATH = "data/database/items.jsonl"

RESULTS_DIR = Path("results")


def load_items(split):
    with open(
        ITEMS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        all_items = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    items = [
        item
        for item in all_items
        if item["split"] == split
    ]

    if not items:
        raise ValueError(
            f"No items found for split '{split}'"
        )

    if split == "test" and len(items) < 50:
        raise ValueError(
            "Final test split must contain at least 50 items. "
            f"Currently found {len(items)}."
        )

    return items


def main():

    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument(
        "--split",
        choices=["dev", "test"],
        default="dev"
    )

    argument_parser.add_argument(
        "--hardware-cost-per-hour",
        type=float,
        default=None
    )

    argument_parser.add_argument(
        "--human-cost-per-1000",
        type=float,
        default=0.0
    )

    args = argument_parser.parse_args()

    items = load_items(args.split)

    RESULTS_DIR.mkdir(exist_ok=True)

    per_item_path = (
        RESULTS_DIR /
        f"qwen_{args.split}_per_item.csv"
    )

    summary_path = (
        RESULTS_DIR /
        f"qwen_{args.split}_summary.csv"
    )

    results = []
    correct_count = 0

    benchmark_start = time.perf_counter()

    # Normal for-loop means calls happen sequentially.
    for item in items:

        prompt = build_prompt(
            item["question"]
        )

        qwen_result = call_qwen(prompt)

        raw_output = qwen_result["text"]

        generated_sql = ""
        error = qwen_result["error"]

        # -------------------------------------
        # Model-level failure
        # -------------------------------------

        if qwen_result["status"] != "ok":

            result = {
                "correct": False,
                "status": qwen_result["status"]
            }

        else:

            # ---------------------------------
            # Shared parser
            # ---------------------------------

            parsed = parse_sql(raw_output)

            if parsed["status"] != "ok":

                result = {
                    "correct": False,
                    "status": parsed["status"]
                }

                error = parsed["error"]

            else:

                generated_sql = parsed["sql"]

                # -----------------------------
                # SQL scoring
                # -----------------------------

                result = score_sql(
                    generated_sql,
                    item["expected_sql"],
                    DB_PATH,
                    order_matters=item[
                        "order_matters"
                    ]
                )

                error = result["error"]

        if result["correct"]:
            correct_count += 1

        row = {
            "model": "qwen3:8b",
            "item_id": item["id"],
            "split": item["split"],
            "difficulty": item["difficulty"],
            "question": item["question"],
            "raw_output": raw_output,
            "generated_sql": generated_sql,
            "correct": result["correct"],
            "status": result["status"],
            "latency_ms": round(
                qwen_result["latency_ms"],
                2
            ),
            "input_tokens":
                qwen_result["input_tokens"],
            "output_tokens":
                qwen_result["output_tokens"],
            "tokens_per_second": round(
                qwen_result[
                    "tokens_per_second"
                ],
                2
            ),
            "error": error
        }

        results.append(row)

        print()
        print(
            f"Question {item['id']}: "
            f"{item['question']}"
        )

        print(
            f"Status: {result['status']}"
        )

        print(
            f"Latency: "
            f"{qwen_result['latency_ms']:.2f} ms"
        )

        print(
            f"Tokens/sec: "
            f"{qwen_result['tokens_per_second']:.2f}"
        )

    benchmark_seconds = (
        time.perf_counter()
        - benchmark_start
    )

    # -----------------------------------------
    # Save per-item results
    # -----------------------------------------

    with open(
        per_item_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )

        writer.writeheader()
        writer.writerows(results)

    # -----------------------------------------
    # Statistics
    # -----------------------------------------

    latencies = [
        row["latency_ms"]
        for row in results
    ]

    token_speeds = [
        row["tokens_per_second"]
        for row in results
        if row["tokens_per_second"] > 0
    ]

    p50_latency = np.percentile(
        latencies,
        50
    )

    p95_latency = np.percentile(
        latencies,
        95
    )

    average_tokens_per_second = (
        np.mean(token_speeds)
        if token_speeds
        else 0
    )

    accuracy = (
        correct_count /
        len(items)
    )

    requests_per_hour = (
        len(items) /
        benchmark_seconds
    ) * 3600

    # -----------------------------------------
    # Local cost
    # -----------------------------------------

    local_cost_per_1000 = None

    if args.hardware_cost_per_hour is not None:

        cost_result = (
            calculate_local_cost_per_1000(
                hardware_cost_per_hour=
                    args.hardware_cost_per_hour,

                requests_per_hour=
                    requests_per_hour,

                human_cost_per_1000=
                    args.human_cost_per_1000
            )
        )

        local_cost_per_1000 = (
            cost_result[
                "total_cost_per_1000"
            ]
        )

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    summary = {
        "model": "qwen3:8b",
        "split": args.split,
        "correct": correct_count,
        "total": len(items),
        "accuracy":
            round(accuracy, 4),
        "p50_latency_ms":
            round(p50_latency, 2),
        "p95_latency_ms":
            round(p95_latency, 2),
        "avg_tokens_per_second":
            round(
                average_tokens_per_second,
                2
            ),
        "benchmark_seconds":
            round(benchmark_seconds, 2),
        "requests_per_hour":
            round(requests_per_hour, 2),
        "hardware_cost_per_hour":
            args.hardware_cost_per_hour,
        "local_cost_per_1000":
            (
                round(
                    local_cost_per_1000,
                    4
                )
                if local_cost_per_1000
                is not None
                else None
            )
    }

    with open(
        summary_path,
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

    # -----------------------------------------
    # Console output
    # -----------------------------------------

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

    print(
        f"Requests/hour: "
        f"{requests_per_hour:.2f}"
    )

    if local_cost_per_1000 is not None:
        print(
            f"Local cost / 1000 requests: "
            f"{local_cost_per_1000:.4f}"
        )

    print()
    print(
        f"Per-item results: "
        f"{per_item_path}"
    )

    print(
        f"Summary: "
        f"{summary_path}"
    )


if __name__ == "__main__":
    main()