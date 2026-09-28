import json, time, argparse

KVStore = argparse.ArgumentParser()

subparsers = KVStore.add_subparsers()

data = {}

def load():
    try:
        with open('./logs.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue

                record = json.loads(line)

                if record['op'] == 'set':
                    data[record['key']] = {
                        'value': record['value'],
                        'expire_at': record['expire_at']
                    }

                if record['op'] == 'delete':
                    data.pop(record['key'], None)

    except FileNotFoundError:
        return

load()

set_parser = subparsers.add_parser('set')
set_parser.add_argument('key')
set_parser.add_argument('value')
set_parser.add_argument('--ttl', type=int)
set_parser.set_defaults(func='set')


get_parser = subparsers.add_parser('get')
get_parser.add_argument('key')
get_parser.set_defaults(func='get')


delete_parser = subparsers.add_parser('delete')
delete_parser.add_argument('key')
delete_parser.set_defaults(func='delete')


def _append_log(record):
    with open('./logs.jsonl', 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + '\n')


def set_value(key, value=None, ttl=None):
    expire_at = None

    if ttl is not None:
        expire_at = time.time() + ttl

    data[key] = {
        'value': value,
        'expire_at': expire_at
    }

    record = {
        'op': 'set',
        'key': key,
        'value': value,
        'expire_at': expire_at
    }

    _append_log(record)


def delete(key):
    data.pop(key, None)

    record = {'op': 'delete', 'key': key}
    _append_log(record)


def get(key):
    result = data.get(key, "NOT_FOUND")

    if result == "NOT_FOUND":
        return None

    if data[key]['expire_at'] is not None:
        if data[key]['expire_at'] < time.time():
            delete(key)
            return None

    return data[key]['value']


def main(args=None):
    args = KVStore.parse_args(args)

    if not hasattr(args, 'func'):
        KVStore.print_help()
        return

    if args.func == 'set':
        set_value(args.key, args.value, args.ttl)

    if args.func == 'get':
        print(get(args.key))

    if args.func == 'delete':
        delete(args.key)


if __name__ == '__main__':
    main()