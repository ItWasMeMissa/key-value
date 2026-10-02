import json
import pytest
from key_value import KVStore


@pytest.fixture
def store(tmp_path):
    return KVStore(tmp_path / 'logs.jsonl')


def test_no_command(store):
    with pytest.raises(SystemExit):
        store.execute('')


def test_set(store):
    store.main([
        'set', 'slime', '1'
    ])

    with open(store.log_path, 'r') as f:
        record = json.loads(f.readline())

    assert record['op'] == 'set'
    assert record['key'] == 'slime'
    assert record['value'] == '1'
    assert record['expire_at'] is None


def test_get(store, capsys):
    store.main([
        'set', 'slime', '1'
    ])

    store.main([
        'get', 'slime'
    ])

    assert capsys.readouterr().out == '1\n'


def test_delete(store):
    store.main([
        'set', 'slime', '1'
    ])

    store.main([
        'delete', 'slime'
    ])

    with open(store.log_path, 'r') as f:
        records = [json.loads(line) for line in f]

    assert records[0]['op'] == 'set'
    assert records[0]['key'] == 'slime'
    assert records[0]['value'] == '1'
    assert records[0]['expire_at'] is None

    assert records[1]['op'] == 'delete'
    assert records[1]['key'] == 'slime'


def test_set_ttl(store):
    store.main([
        'set', 'slime', '1',
        '--ttl', '10'
    ])

    with open(store.log_path, 'r') as f:
        record = json.loads(f.readline())

    assert record['expire_at'] is not None


def test_expired_ttl(store, capsys):
    store.main([
        'set', 'slime', '1',
        '--ttl', '-1'
    ])

    store.main([
        'get', 'slime'
    ])

    assert capsys.readouterr().out == 'None\n'

    with open(store.log_path, 'r') as f:
        records = [json.loads(line) for line in f]

    assert records[0]['op'] == 'set'
    assert records[1]['op'] == 'delete'
    assert records[1]['key'] == 'slime'


def test_get_missing_key(store, capsys):
    store.main([
        'get', 'slime'
    ])

    assert capsys.readouterr().out == 'None\n'


def test_persistence(store):
    store.set_value('slime', '1')

    store = KVStore(store.log_path)

    assert store.get('slime') == '1'