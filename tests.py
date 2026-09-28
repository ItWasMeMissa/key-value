import json

from key_value import main
import os, pytest

@pytest.fixture(autouse=True)
def clean_log():
    if os.path.exists('./logs.jsonl'):
        os.remove('./logs.jsonl')

#TEST
def test():
    with pytest.raises(SystemExit):
        main()

# python cli.py set slime 1
def test_set():
    main([
        'set', 'slime', '1'
    ])

    with open('./logs.jsonl', 'r') as f:
        record = json.loads(f.readline())

    assert record['op'] == 'set'
    assert record['key'] == 'slime'
    assert record['value'] == '1'
    assert record['expire_at'] is None

# python cli.py get slime
def test_get(capsys):
    main([
        'set', 'slime', '1'
    ])

    main([
        'get', 'slime'
    ])

    assert capsys.readouterr().out == '1\n'

# python cli.py delete slime
def test_delete():
    main([
        'set', 'slime', '1'
    ])

    main([
        'delete', 'slime'
    ])

    with open('./logs.jsonl', 'r') as f:
        records = [json.loads(line) for line in f]

    assert records[0]['op'] == 'set'
    assert records[0]['key'] == 'slime'
    assert records[0]['value'] == '1'
    assert records[0]['expire_at'] is None

    assert records[1]['op'] == 'delete'
    assert records[1]['key'] == 'slime'


def test_set_ttl():
    main([
        'set', 'slime', '1',
        '--ttl', '10'
    ])

    with open('./logs.jsonl', 'r') as f:
        record = json.loads(f.readline())

    assert record['expire_at'] is not None

def test_expired_ttl(capsys):
    main([
        'set', 'slime', '1',
        '--ttl', '-1'
    ])

    main([
        'get', 'slime'
    ])

    assert capsys.readouterr().out == 'None\n'

    with open('./logs.jsonl', 'r') as f:
        records = [json.loads(line) for line in f]

    assert records[0]['op'] == 'set'
    assert records[1]['op'] == 'delete'
    assert records[1]['key'] == 'slime'