import json, time


class KVStore:

    def load(self):
        # Rebuild the current state of the store from the log file.
        # The log contains all operations that happened before the program started.
        try:
            with open('./logs.jsonl', 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        # Skip empty lines because they are not valid JSON records.
                        continue

                    record = json.loads(line)

                    if record['op'] == 'set':
                        # Restore the key with both its value and expiration time.
                        self.data[record['key']] = {
                            'value': record['value'],
                            'expire_at': record['expire_at']
                        }

                    if record['op'] == 'delete':
                        # Reproduce the deletion from the log.
                        self.data.pop(record['key'], None)

        except FileNotFoundError:
            # There is no log file on the first run, so there is nothing to load.
            return

    def __init__(self):
        # data contains the current state of the key-value store.
        # The log file is only the history used to rebuild this state.
        self.data = {}

        # Restore previously saved data when creating the store.
        self.load()

    def _append_log(self, record):
        # Save one operation to the log.
        # The log keeps the history so the store can be restored after restarting.
        with open('./logs.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')

    def set(self, key, value=None, ttl=None):
        # Store a value under a key.
        # ttl is an optional lifetime of the key in seconds.
        expire_at = None

        if ttl is not None:
            # Convert the lifetime into an exact expiration timestamp.
            # Example: current time + 10 seconds = the time when the key expires.
            expire_at = time.time() + ttl

        # Update the current state of the store.
        self.data[key] = {
            'value': value,
            'expire_at': expire_at
        }

        # Save the operation to the log so it can be restored after restarting.
        record = {
            'op': 'set',
            'key': key,
            'value': value,
            'expire_at': expire_at
        }

        self._append_log(record)

    def get(self, key):
        # Return the value stored under the key.
        # Before returning it, check whether the key has expired.
        result = self.data.get(key, "NOT_FOUND")

        if result == "NOT_FOUND":
            # The key does not exist in the current store.
            return None

        if self.data[key]['expire_at'] != None:
            # The key has an expiration time, so check whether it has expired.
            if self.data[key]['expire_at'] < time.time():
                self.data.pop(key, None)
                return None

        # The key exists and has not expired.
        return self.data[key]['value']

    def delete(self, key):
        # Remove the key from the current state of the store.
        self.data.pop(key, None)

        # Save the deletion to the log so it will stay deleted after restarting.
        record = {'op': 'delete', 'key': key}
        self._append_log(record)