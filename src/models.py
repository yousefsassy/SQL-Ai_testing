import time

import httpx
from ollama import Client


QWEN_MODEL = "qwen3:8b"
MAX_OUTPUT_TOKENS = 256
TIMEOUT_SECONDS = 60


client = Client(
    host="http://localhost:11434",
    timeout=TIMEOUT_SECONDS
)


def call_qwen(prompt):
    start_time = time.perf_counter()

    try:
        response = client.chat(
            model=QWEN_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0,
                "num_predict": MAX_OUTPUT_TOKENS
            },
            think=False
        )

    except httpx.TimeoutException as e:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "status": "timeout",
            "text": "",
            "latency_ms": latency_ms,
            "input_tokens": 0,
            "output_tokens": 0,
            "tokens_per_second": 0,
            "error": str(e)
        }

    except Exception as e:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "status": "model_error",
            "text": "",
            "latency_ms": latency_ms,
            "input_tokens": 0,
            "output_tokens": 0,
            "tokens_per_second": 0,
            "error": str(e)
        }

    latency_ms = (
        time.perf_counter() - start_time
    ) * 1000

    generated_text = response["message"]["content"]

    input_tokens = response.get(
        "prompt_eval_count",
        0
    )

    output_tokens = response.get(
        "eval_count",
        0
    )

    eval_duration_ns = response.get(
        "eval_duration",
        0
    )

    if eval_duration_ns > 0:
        tokens_per_second = (
            output_tokens /
            (eval_duration_ns / 1_000_000_000)
        )
    else:
        tokens_per_second = 0

    return {
        "status": "ok",
        "text": generated_text,
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tokens_per_second": tokens_per_second,
        "error": None
    }