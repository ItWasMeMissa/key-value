from key_value import KVStore
import socket
import threading
import resp
from resp import ParseError

store = KVStore()

def _choose_type_and_get_response_preset(args):
    match args[0]:
        case 'simple':
            return resp.encode_simple(args[1])

        case 'error':
            return resp.encode_error(args[1])

        case 'int':
            return resp.encode_int(args[1])

        case 'bulk':
            return resp.encode_bulk(args[1])

def _get_message_and_parse(conn, addr):
    buffer = b''

    try:
        while True:
            chunk = conn.recv(4)

            if len(buffer) >= 64000:
                _choose_type_and_get_response_preset(('error', 'too heavy'))
                return

            if not chunk:
                break
            buffer += chunk

            while True:
                try:
                    resalt = resp.parse_command(buffer)
                except ParseError:
                    conn.send(
                        _choose_type_and_get_response_preset(('error', 'ERR parse error'))
                    )
                    return
                if resalt == None:
                    break
                else:
                    cmd, rest = resalt
                    buffer = rest

                    response = store.execute_command(cmd)
                    conn.send(
                        _choose_type_and_get_response_preset(response)
                    )

    finally:
        print(f'Disconnected: {addr}')
        conn.close()

def main():
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind(('127.0.0.1', 5000))
    server.listen()

    while True:
        conn, addr = server.accept()

        print(f'Connected: {addr}')

        thread = threading.Thread(
            target=_get_message_and_parse,
            args=(conn, addr)
        )
        thread.start()


if __name__ == '__main__':
    main()