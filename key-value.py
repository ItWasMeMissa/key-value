
class KVStore:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        self.data.pop(key, None)

store = KVStore()
store.set('name', 'slime')
print(store.get('name'))
store.delete('name')
print(store.get('name'))

