from src.score import score_sql


DB_PATH = "data/database/shop.db"


expected_sql = """
SELECT COUNT(*)
FROM customers
WHERE country = 'France';
"""


# 1. Equivalent query
generated_sql = """
SELECT COUNT(id)
FROM customers
WHERE country = 'France';
"""

result = score_sql(
    generated_sql,
    expected_sql,
    DB_PATH
)

print("Equivalent query:")
print(result)


# 2. Wrong result
wrong_sql = """
SELECT COUNT(*)
FROM customers
WHERE country = 'Germany';
"""

result = score_sql(
    wrong_sql,
    expected_sql,
    DB_PATH
)

print("\nWrong query:")
print(result)


# 3. Syntax error
syntax_error_sql = """
SELEC COUNT(*)
FROM customers;
"""

result = score_sql(
    syntax_error_sql,
    expected_sql,
    DB_PATH
)

print("\nSyntax error:")
print(result)


# 4. Execution error
execution_error_sql = """
SELECT something_wrong
FROM customers;
"""

result = score_sql(
    execution_error_sql,
    expected_sql,
    DB_PATH
)

print("\nExecution error:")
print(result)