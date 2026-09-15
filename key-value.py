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

#TEST
store = KVStore()
store.set('name', 'slime')
store.set('name', 'skeleton')
print(store.get('name'))
store.delete('name')
print(store.get('name'))

