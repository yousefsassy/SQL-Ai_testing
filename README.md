# SQL-Ai_testing

Evaluate four local Ollama models on natural-language questions about a SQLite ecommerce database. The current dataset contains 10 development items.

## Setup

With Python and Ollama installed, create a Python environment and install dependencies from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell. Ensure Ollama is running and download the models you want to evaluate:

```bash
ollama pull gemma3:1b
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull qwen3:8b
```

The repository includes `data/database/shop.db`. Running `python scripts/create_database.py` deletes and recreates that database with seeded sample data.

## Run

From the repository root, run any model with the same runner:

```bash
python scripts/run_benchmark.py --model gemma3:1b
python scripts/run_benchmark.py --model llama3.2:3b
python scripts/run_benchmark.py --model phi4-mini
python scripts/run_benchmark.py --model qwen3:8b
```

`python -m scripts.run_benchmark --model gemma3:1b` also works. The default is `--split dev`, using the current 10 questions. `--split test` requires at least 50 test items, which are not present yet.

All models share the prompt, parser, scorer, temperature 0, and 256-token output limit. Qwen's thinking is disabled; the other models receive no thinking option. Requests use the local Ollama server at `http://localhost:11434` with a 60-second client timeout.

## Results

- `results/per_item.csv`: one row per question, including model, split, SQL, correctness, latency, token counts, and errors.
- `results/summary.csv`: one summary row per model and split.

Each completed run replaces that model/split's previous rows and preserves other models and splits. Run benchmarks sequentially, not concurrently. These files contain the latest runs, not a historical archive; rerun all models after changing the dataset or prompt for a fair comparison. Hardware notes are stored in `results/hardware.txt`; the existing note describes a historical Qwen run on Windows, not the current machine.

Latency includes the full model request, including any model loading. Generation tokens/second uses Ollama's generation duration. Record hardware separately for each comparison. Cost remains blank unless `--hardware-cost-per-hour` is supplied; `--human-cost-per-1000` defaults to zero.

Use the shared runner above for all four models.

## Checks

```bash
python -m pytest -q tests/test_benchmark.py tests/test_parser.py
```

These tests check model routing, combined CSV preservation, and shared parser behavior without calling Ollama.

The shared parser accepts plain SQL or one complete Markdown code block with no language label, `sql`, or `sqlite` (case-insensitive). Explanations outside the block remain invalid. The same rules apply to every model.
