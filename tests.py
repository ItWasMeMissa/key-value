from key_value import KVStore

#TEST
def test_get_exist_store():
    store = KVStore()

    store.set("name", "slime")
    store.set("hp", 100)
    store.set("gold", 50)

    assert store.get('hp') == 100

def test_get_not_exist_store():
    store = KVStore()

    assert store.get('miew') == None

def test_delete_removes_key():
    store = KVStore()
    store.set('temp', 'x')
    store.delete('temp')

    assert store.get('temp') is None

def test_ttl_expired_returns_none():
    store = KVStore()
    store.set('temp', 'x', ttl=-5)  # Spoiled

    assert store.get('temp') is None