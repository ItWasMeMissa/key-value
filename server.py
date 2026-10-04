from key_value import KVStore
import socket
import threading

store = KVStore()

def _get_message_and_parse(conn, addr):
    buffer = b''

    try:
        while True:
            chunk = conn.recv(4)

            if len(buffer) >= 64000:
                conn.send('-ERR\n'.encode())
                return

            if not chunk:
                break
            buffer += chunk

            while b'\n' in buffer:
                line, _, buffer = buffer.partition(b'\n')

                try:
                    client_input = line.decode()
                except UnicodeDecodeError:
                    conn.send('-ERR\n'.encode())
                    continue

                print(client_input)

                response = store.execute(client_input)
                conn.send((response + '\n').encode())
    finally:
        print(f'Disconnected: {addr}')
        conn.close()

def main():
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

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