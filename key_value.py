import json, time

class KVStore:
    def load(self):     #load logs
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
        self.load()     #load file logs if exist

    def _append_log(self, record): #test name?
        with open('./logs.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')

    def set(self, key, value=None, ttl=None):   #add log
        expire_at = None

        if ttl is not None:                     #timer for log
            expire_at = time.time() + ttl

        self.data[key] = {                      #loc log
            'value': value,
            'expire_at': expire_at
        }

        record = {                              #file log
            'op': 'set',
            'key': key,
            'value': value,
            'expire_at': expire_at
        }
        self._append_log(record)

    def get(self, key):             #find log
        result = self.data.get(key, "NOT_FOUND")
        if result == "NOT_FOUND":           #no resalt
            return None

        if self.data[key]['expire_at'] != None:     #chek expire at before give log
            if self.data[key]['expire_at'] < time.time():
                self.data.pop(key, None)
                return None

        return self.data[key]['value']

    def delete(self, key):          #delete log
        self.data.pop(key, None)
        record = {'op': 'delete', 'key': key}
        self._append_log(record)            #delete file log