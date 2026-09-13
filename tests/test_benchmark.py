import csv
from unittest.mock import patch

import pytest

from scripts.run_benchmark import save_model_results
from src.models import SUPPORTED_MODELS, call_model


@pytest.mark.parametrize('model', SUPPORTED_MODELS)
def test_model_request(model):
    response = {
        'message': {'content': 'SELECT 1;'},
        'prompt_eval_count': 10,
        'eval_count': 4,
        'eval_duration': 1_000_000_000,
    }
    with patch('src.models.client.chat', return_value=response) as chat:
        result = call_model('shared prompt', model)
    request = chat.call_args.kwargs
    assert request['model'] == model
    assert request['messages'] == [{'role': 'user', 'content': 'shared prompt'}]
    assert request['options'] == {'temperature': 0, 'num_predict': 256}
    if model == 'qwen3:8b':
        assert request['think'] is False
    else:
        assert 'think' not in request
    assert result['status'] == 'ok'
    assert result['text'] == 'SELECT 1;'
    assert result['tokens_per_second'] == 4


def test_results_preserve_other_models_and_splits(tmp_path):
    path = tmp_path / 'per_item.csv'
    runs = [
        ('qwen3:8b', 'dev', '1'),
        ('gemma3:1b', 'test', '2'),
        ('gemma3:1b', 'dev', '3'),
        ('gemma3:1b', 'dev', '4'),
    ]
    for model, split, item_id in runs:
        save_model_results(path, [dict(model=model, split=split, item_id=item_id)], model, split)
    with path.open(newline='') as file:
        rows = list(csv.DictReader(file))
    assert rows == [
        dict(model='qwen3:8b', split='dev', item_id='1'),
        dict(model='gemma3:1b', split='test', item_id='2'),
        dict(model='gemma3:1b', split='dev', item_id='4'),
    ]
