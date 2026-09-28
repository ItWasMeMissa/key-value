# Key-Value Store

A small key-value storage project written in Python.

## Features

- Store values by key
- Get values by key
- Delete values
- Persistent operation log
- TTL / key expiration

### Completed

- [x] Basic `set`, `get`, `delete`
- [x] Save operations to `logs.jsonl`
- [x] Load data from logs
- [x] TTL
- [x] `_append_log()` refactor
- [x] Add tests with pytest
- [x] CLI

### Next steps

- [ ] Improve error handling
- [ ] TCP/WebSocket server
- [ ] Support multiple clients