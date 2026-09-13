import pytest

from src.parser import parse_sql


@pytest.mark.parametrize('output', [
    'SELECT 1;',
    '```\nSELECT 1;\n```',
    '```sql\nSELECT 1;\n```',
    '```sqlite\nSELECT 1;\n```',
    '  ```SQLite\r\nSELECT 1\r\n```  ',
])
def test_shared_sql_formats(output):
    assert parse_sql(output) == {'status': 'ok', 'sql': 'SELECT 1;', 'error': None}


@pytest.mark.parametrize('output', [
    '',
    'Here is the query:\n```sqlite\nSELECT 1;\n```',
    '```sqlite\nSELECT 1;\n```\nExplanation.',
    '```sqlite\nSELECT 1; SELECT 2;\n```',
    '```sqlite\nDELETE FROM customers;\n```',
    '```sqlite\nSELECT 1;',
])
def test_invalid_outputs_remain_rejected(output):
    assert parse_sql(output)['status'] == 'parse_error'


def test_refusal_remains_rejected():
    assert parse_sql('I cannot assist with this request.')['status'] == 'refusal'
