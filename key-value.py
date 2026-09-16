import json, time

class KVStore:
    def load(self):
        try:
            with open('./logs.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():  # "" == False
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

    def __init__(self):
        self.data = {}
        self.load()

    def _append_log(self, record): #test name?
        with open('./logs.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')

    def set(self, key, value=None, ttl=None):
        if ttl is not None:
            ttl += time.time()
            self.data[key] = {'value': value, 'expire_at': ttl}
        else:
            self.data[key] = {'value': value, 'expire_at': ttl}
        # how note record time? Days Hours Sec "%H:%M:%S in cli?"
        record = {'op':'set','key': key, 'value': value, 'expire_at': ttl}
        self._append_log(record)

    def get(self, key):
        if not self.data.get(key): #None == False
            return 'not found'
        else:
            if self.data[key]['expire_at'] < time.time():
                return self.data[key]
            else:
                self.delete(key)

    def delete(self, key):
        self.data.pop(key, None)
        record = {'op': 'delete', 'key': key}
        self._append_log(record)

#TEST
# store = KVStore()
#
# print(store.get('test'))
#
# print(store.data)