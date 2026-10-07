import json
import pytest
import key_value
from key_value import KVStore


@pytest.fixture
def store(tmp_path):
    return KVStore(tmp_path / 'logs.jsonl')


def read_log(store):
    with open(store.log_path, 'r') as f:
        return [json.loads(line) for line in f]


def test_set_writes_log_record(store):
    store.execute_command([b'SET', b'slime', b'1'])

    records = read_log(store)

    assert len(records) == 1
    assert records[0]['op'] == 'set'
    assert records[0]['key'] == 'slime'
    assert records[0]['value'] == '1'
    assert records[0]['expire_at'] is None


def test_delete_writes_log_record(store):
    store.execute_command([b'SET', b'slime', b'1'])
    store.execute_command([b'DEL', b'slime'])

    records = read_log(store)

    assert records[0]['op'] == 'set'
    assert records[0]['key'] == 'slime'
    assert records[0]['value'] == '1'
    assert records[0]['expire_at'] is None

    assert records[1]['op'] == 'delete'
    assert records[1]['key'] == 'slime'


def test_del_missing_key_writes_nothing(store):
    assert store.execute_command([b'DEL', b'slime']) == ('int', 0)

    assert not store.log_path.exists()


def test_expired_key_is_deleted_and_logged(store, monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(key_value.time, 'time', lambda: clock[0])

    store.execute_command([b'SET', b'slime', b'1', b'EX', b'10'])

    clock[0] = 1011.0
    assert store.execute_command([b'GET', b'slime']) == ('bulk', None)

    records = read_log(store)

    assert records[0]['op'] == 'set'
    assert records[0]['expire_at'] == 1010.0

    assert records[1]['op'] == 'delete'
    assert records[1]['key'] == 'slime'


def test_persistence(store):
    store.set_value('slime', '1')

    store = KVStore(store.log_path)

    assert store.get('slime') == '1'