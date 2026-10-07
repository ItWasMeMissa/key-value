import json
import pytest
import key_value
from key_value import KVStore


@pytest.fixture
def store(tmp_path):
    return KVStore(tmp_path / 'logs.jsonl')


def test_ping(store):
    assert store.execute_command([b'PING']) == ('simple', 'PONG')


def test_set_and_get(store):
    assert store.execute_command([b'SET', b'a', b'1']) == ('simple', 'OK')
    assert store.execute_command([b'GET', b'a']) == ('bulk', '1')


def test_get_missing_key(store):
    assert store.execute_command([b'GET', b'nope']) == ('bulk', None)


def test_command_name_is_case_insensitive(store):
    assert store.execute_command([b'set', b'a', b'1']) == ('simple', 'OK')
    assert store.execute_command([b'GeT', b'a']) == ('bulk', '1')


def test_value_with_spaces(store):
    store.execute_command([b'SET', b'name', b'Ivan Petrov'])

    assert store.execute_command([b'GET', b'name']) == ('bulk', 'Ivan Petrov')


def test_del_existing_and_missing(store):
    store.execute_command([b'SET', b'a', b'1'])

    assert store.execute_command([b'DEL', b'a']) == ('int', 1)
    assert store.execute_command([b'GET', b'a']) == ('bulk', None)
    assert store.execute_command([b'DEL', b'a']) == ('int', 0)


def test_unknown_command(store):
    assert store.execute_command([b'LOL']) == ('error', 'ERR unknown command')


def test_empty_args(store):
    assert store.execute_command([])[0] == 'error'


def test_non_utf8_input(store):
    assert store.execute_command([b'GET', b'\xff'])[0] == 'error'
    assert store.execute_command([b'SET', b'a', b'\xff'])[0] == 'error'


@pytest.mark.parametrize('args', [
    [b'PING', b'x'],
    [b'GET'],
    [b'GET', b'a', b'b'],
    [b'SET', b'a'],
    [b'SET', b'a', b'1', b'EX'],
    [b'SET', b'a', b'1', b'EX', b'10', b'extra'],
    [b'DEL'],
    [b'DEL', b'a', b'b'],
])
def test_wrong_number_of_arguments(store, args):
    assert store.execute_command(args) == ('error', 'ERR wrong number of arguments')


def test_set_with_ex_expires(store, monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(key_value.time, 'time', lambda: clock[0])

    assert store.execute_command([b'SET', b'a', b'1', b'EX', b'10']) == ('simple', 'OK')

    with open(store.log_path) as f:
        assert json.loads(f.readline())['expire_at'] == 1010.0

    clock[0] = 1005.0
    assert store.execute_command([b'GET', b'a']) == ('bulk', '1')

    clock[0] = 1011.0
    assert store.execute_command([b'GET', b'a']) == ('bulk', None)


@pytest.mark.parametrize('args', [
    [b'SET', b'a', b'1', b'EX', b'abc'],
    [b'SET', b'a', b'1', b'EX', b'0'],
    [b'SET', b'a', b'1', b'EX', b'-1'],
    [b'SET', b'a', b'1', b'PX', b'10'],
])
def test_set_with_bad_ex(store, args):
    assert store.execute_command(args)[0] == 'error'
    assert store.execute_command([b'GET', b'a']) == ('bulk', None)


def test_persistence_via_execute_command(store):
    store.execute_command([b'SET', b'a', b'1'])

    reloaded = KVStore(store.log_path)

    assert reloaded.execute_command([b'GET', b'a']) == ('bulk', '1')