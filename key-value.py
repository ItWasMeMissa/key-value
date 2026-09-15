import json

class KVStore:
    def __init__(self):
        self.data = {}

    def set(self, key, value=None):
        self.data[key] = value
        record = {'op':'set','key': key, 'value': value}
        with open('./logs.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        self.data.pop(key, None)
        record = {'op': 'delete', 'key': key}
        with open('./logs.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')

    def load(self):
        try:
            with open('./logs.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():  # "" == False
                        continue

                    record = json.loads(line)
                    if record['op'] == 'set':
                        self.data[record['key']] = record['value']

                    if record['op'] == 'delete':
                        self.data.pop(record['key'], None)
        except FileNotFoundError:
            return


#TEST
# store = KVStore()
# store.load()
# print(store.data)