import json
import time
import threading

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

    def execute_command(self, args):
        if not args:
            return ('error', 'ERR empty command')

        try:
            name = args[0].decode('utf-8').upper()
            params = [a.decode('utf-8') for a in args[1:]]
        except UnicodeDecodeError:
            return ('error', 'ERR unsupported encoding')

        wrong_args = ('error', 'ERR wrong number of arguments')

        with self._lock:
            match name:
                case 'PING':
                    if params:
                        return wrong_args
                    return ('simple', 'PONG')

                case 'SET':
                    if len(params) not in (2, 4):
                        return wrong_args

                    ttl = None
                    if len(params) == 4:
                        if params[2].upper() != 'EX':
                            return ('error', 'ERR syntax error')
                        try:
                            ttl = int(params[3])
                        except ValueError:
                            return ('error', 'ERR value is not an integer')
                        if ttl <= 0:
                            return ('error', 'ERR invalid expire time')

                    self.set_value(params[0], params[1], ttl)
                    return ('simple', 'OK')

                case 'GET':
                    if len(params) != 1:
                        return wrong_args
                    return ('bulk', self.get(params[0]))

                case 'DEL':
                    if len(params) != 1:
                        return wrong_args
                    existed = self.get(params[0]) is not None
                    if existed:
                        self.delete(params[0])
                    return ('int', 1 if existed else 0)

                case _:
                    return ('error', 'ERR unknown command')