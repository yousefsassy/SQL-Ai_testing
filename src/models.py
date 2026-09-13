import ollama


DEFAULT_MODEL = "gemma3:1b"

OPTIONS = {
    "temperature": 0,
    "top_p": 1.0,
    "top_k": 40,
    "num_predict": 256,
    "num_ctx": 4096,
    "seed": 42,
    "repeat_penalty": 1.0
}


def build_prompt(schema, question):
    return f"""
You are a SQL generation system.

Given the database schema and a question, generate the SQLite query
that answers the question.

Rules:
- Use SQLite syntax.
- Return only the SQL query.
- Do not include explanations.
- Do not use Markdown.
- Generate exactly one query.
- Only use tables and columns present in the schema.

Schema:
{schema}

Question:
{question}

SQL:
""".strip()


def generate_sql(question, schema, model=DEFAULT_MODEL):
    prompt = build_prompt(schema, question)

    response = ollama.generate(
        model=model,
        prompt=prompt,
        options=OPTIONS
    )

    return response["response"].strip()