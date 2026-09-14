# SQL-Ai_testing

A CS496 AI Engineering benchmark comparing four local Ollama models on ecommerce text-to-SQL. Each generated query and its reference query are executed against the same SQLite database.

## Setup

Install Python and Ollama first. Run all commands below from the repository root.

Create and activate a Python environment (Linux/macOS):

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, use `.venv\Scripts\Activate.ps1` for activation instead.

Install the project's dependencies:

```bash
python -m pip install -r requirements.txt
```

Ensure Ollama is running locally at `http://localhost:11434`; if it is not already running as a service or desktop application, start `ollama serve` in another terminal. Download the model you want to test, or all four:

```bash
ollama pull gemma3:1b
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull qwen3:8b
```

Generate the local shop database:

```bash
python scripts/create_database.py
```

This recreates `data/database/shop.db`, replacing an existing database, with seed 42: 300 customers, 20 products, and 1,200 orders. A generated database is already included in the repository.

## Run a final benchmark

One run command for the selected model:

```bash
python scripts/run_benchmark.py --model phi4-mini
```

To evaluate each of the four models, run these commands sequentially:

```bash
python scripts/run_benchmark.py --model gemma3:1b
python scripts/run_benchmark.py --model llama3.2:3b
python scripts/run_benchmark.py --model phi4-mini
python scripts/run_benchmark.py --model qwen3:8b
```


The default split is `test` (50 items). Add `--split dev` to run the 10 development items for debugging.



## Final test results

These values come from `split=test` in [summary.csv](results/summary.csv). They are the recorded results on our machine, not guaranteed timings on other hardware.

| Model | Correct/50 (%) | p50 ms | p95 ms | Tokens/s | Requests/hour | Hardware €/1K |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `gemma3:1b` | 21/50 (42%) | 898.73 | 1,273.66 | 108.10 | 3,833.13 | 0.0522 |
| `llama3.2:3b` | 32/50 (64%) | 670.14 | 1,497.22 | 58.95 | 4,191.72 | 0.0477 |
| `phi4-mini` | 50/50 (100%) | 1,642.44 | 3,901.67 | 31.67 | 1,916.33 | 0.1044 |
| `qwen3:8b` | 47/50 (94%) | 5,141.19 | 12,683.48 | 7.97 | 600.79 | 0.3329 |


We choose **Phi4-mini** for this accuracy-focused task: 50/50 correct, with lower latency and hardware cost than Qwen. This result applies to the current synthetic test set, not all ecommerce questions.


## Contributions

- **Nour Guidara:** Initial project setup and Gemma testing.
- **Youssef Sassi:** Qwen 8B testing and item generation.
- **Asma Turki:** Llama testing and report.
- **Emna Smali:** Phi4-mini testing and postmortem.
