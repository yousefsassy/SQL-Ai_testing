import re


REFUSAL_PHRASES = [
    "i can't",
    "i cannot",
    "i'm unable",
    "i am unable",
    "cannot assist",
    "can't assist"
]


def parse_sql(raw_output):

    # Empty response
    if raw_output is None or not raw_output.strip():
        return {
            "status": "parse_error",
            "sql": None,
            "error": "Empty model response"
        }

    text = raw_output.strip()

    # Detect obvious refusal
    lowered = text.lower()

    if any(
        phrase in lowered
        for phrase in REFUSAL_PHRASES
    ):
        return {
            "status": "refusal",
            "sql": None,
            "error": "Model refused the request"
        }

    # Remove Markdown code fences if model ignored prompt
    fence_match = re.fullmatch(
        r"```(?:sql)?\s*(.*?)\s*```",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    if fence_match:
        text = fence_match.group(1).strip()

    # Query must begin with SELECT or WITH
    if not re.match(
        r"^(SELECT|WITH)\b",
        text,
        flags=re.IGNORECASE
    ):
        return {
            "status": "parse_error",
            "sql": None,
            "error": "Response does not start with SELECT or WITH"
        }

    # Remove one final semicolon
    clean_sql = text.rstrip()

    if clean_sql.endswith(";"):
        clean_sql = clean_sql[:-1].rstrip()

    # Reject multiple SQL statements
    if ";" in clean_sql:
        return {
            "status": "parse_error",
            "sql": None,
            "error": "Multiple SQL statements detected"
        }

    return {
        "status": "ok",
        "sql": clean_sql + ";",
        "error": None
    }