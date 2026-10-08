# Key-Value Store

A small Redis-compatible key-value server written in Python.
It speaks the RESP protocol, so the standard `redis-cli` can connect to it.

## Status

Completed as a learning project. The core works: commands, persistence, key expiration and multiple clients.
See [Known limitations](#known-limitations) for what is missing.

## Features

- Commands: `PING`, `SET`, `GET`, `DEL`
- Key expiration: `SET key value EX seconds`
- Persistence: every change is appended to a log file and replayed on start
- Multiple clients at the same time (one thread per connection)
- Values can contain spaces, line breaks and any other characters
- The parser handles partial and malformed input
- Covered by tests (`pytest`)

## Requirements

- Python 3.10 or newer (the code uses `match`)
- No third-party libraries are needed to run the server
- `pytest` to run the tests
- `redis-cli` (optional) to talk to the server

## Quick start

Start the server:

```bash
python server.py
```

It listens on `127.0.0.1:5000`. In another terminal:

```bash
redis-cli -p 5000
```

Example session:

```
127.0.0.1:5000> PING
PONG
127.0.0.1:5000> SET name "Ivan Petrov"
OK
127.0.0.1:5000> GET name
"Ivan Petrov"
127.0.0.1:5000> GET nope
(nil)
127.0.0.1:5000> SET token abc EX 3
OK
127.0.0.1:5000> GET token
"abc"
# wait 4 seconds
127.0.0.1:5000> GET token
(nil)
127.0.0.1:5000> DEL name
(integer) 1
127.0.0.1:5000> DEL name
(integer) 0
```

Data is stored in `logs.jsonl` in the directory where the server was started.

## Commands

| Command | What it does | Reply |
|---|---|---|
| `PING` | Checks that the server is alive | `PONG` |
| `SET key value [EX seconds]` | Stores a value. With `EX` the key expires after the given number of seconds | `OK` |
| `GET key` | Reads a value | The value, or `(nil)` if the key is missing or expired |
| `DEL key` | Deletes one key | `1` if the key existed, otherwise `0` |

Command names are case-insensitive. Errors are returned in the standard RESP form (`-ERR ...`).

## How it works

A request travels through three modules, and each one knows only its own job:

- `server.py` accepts connections, starts one thread per client and collects incoming bytes in a buffer.
  It knows nothing about the protocol format or about storage.
- `resp.py` parses RESP requests into lists of arguments and encodes replies into bytes.
  It knows nothing about sockets or storage.
- `key_value.py` stores data, handles expiration, writes the log and executes commands.
  It knows nothing about the network.

Data flow: bytes arrive, go to the buffer, `parse_command` turns them into arguments,
`execute_command` runs the command, an encoder turns the result into bytes, and the server sends them back.

### Design decisions

- **Append-only log (JSON lines).** Every `SET` and `DEL` is appended to a file, and on start the file is replayed to rebuild memory.
  It is simple, and every record is independent. Cost: the file only grows.
- **One lock around every command.** Memory and the log are updated together, so their order always matches.
  Cost: commands run one at a time.
- **RESP with length prefixes instead of splitting by newline.** The length is known before the data is read,
  so values can contain spaces, line breaks or any bytes. An incomplete request is not an error:
  the parser returns `None` and the server waits for more data. Cost: a more complex parser.
- **Parser separated from sockets.** It is a pure function, so it can be tested without a network.

## Known limitations

- One global lock: there is no parallel execution of commands.
- The log is never compacted and is not forced to disk (`fsync`), so the latest writes can be lost on a power failure.
- Expired keys are removed only when they are read.
- One thread per client; the server listens on localhost only and has no authentication.
- Only a subset of Redis commands is supported. `SET` understands only `EX`, `DEL` takes one key,
  and `PING` does not accept a message (real Redis does).
- A request larger than 64000 bytes is rejected.
- The network layer (`server.py`) has no automated tests; it was checked manually with `redis-cli`.

## Tests

```bash
pip install pytest
pytest
```

Covered: the parser (cut, malformed and binary-safe input), reply encoders, storage with the log,
and command execution. Expiration is tested with a fake clock, so the tests do not sleep.

