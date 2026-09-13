import time
import ollama


QWEN_MODEL = "qwen3:8b"
MAX_OUTPUT_TOKENS = 256


def call_qwen(prompt):
    start_time = time.perf_counter()

    response = ollama.chat(
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

    end_time = time.perf_counter()

    latency_ms = (end_time - start_time) * 1000

    generated_text = response["message"]["content"]

    input_tokens = response.prompt_eval_count or 0
    output_tokens = response.eval_count or 0

    eval_duration_ns = response.eval_duration or 0

    if eval_duration_ns > 0:
        tokens_per_second = output_tokens / (eval_duration_ns / 1_000_000_000)
    else:
        tokens_per_second = 0

    return {
        "text": generated_text,
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tokens_per_second": tokens_per_second
    }