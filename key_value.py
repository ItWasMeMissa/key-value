import json
import time
import argparse
import threading

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(required=True)

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

class KVStore:
    def __init__(self, log_path='./logs.jsonl'):
        self.data = {}
        self._lock = threading.Lock()
        self.log_path = log_path
        self.load()

    def load(self):
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue

                    record = json.loads(line)

                    if record['op'] == 'set':
                        self.data[record['key']] = {
                            'value': record['value'],
                            'expire_at': record['expire_at']
                        }

                    if record['op'] == 'delete':
                        self.data.pop(record['key'], None)

        except FileNotFoundError:
            return

    def _append_log(self, record):
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')

    def set_value(self, key, value=None, ttl=None):
        expire_at = None

        if ttl is not None:
            expire_at = time.time() + ttl

        self.data[key] = {
            'value': value,
            'expire_at': expire_at
        }

        record = {
            'op': 'set',
            'key': key,
            'value': value,
            'expire_at': expire_at
        }

        self._append_log(record)

    def delete(self, key):
        self.data.pop(key, None)

        record = {'op': 'delete', 'key': key}
        self._append_log(record)


    def get(self, key):
        result = self.data.get(key, "NOT_FOUND")

        if result == "NOT_FOUND":
            return None

        if result['expire_at'] is not None and result['expire_at'] < time.time():
            self.delete(key)
            return None

        return result['value']

    def execute(self, line):
        try:
            args = parser.parse_args(line.split())
        except SystemExit:
            return '-ERR'

        with self._lock:
            if args.func == 'set':
                self.set_value(args.key, args.value, args.ttl)
                return '+OK'

            if args.func == 'get':
                value = self.get(args.key)
                return 'None' if value is None else value

            if args.func == 'delete':
                self.delete(args.key)
                return '+OK'