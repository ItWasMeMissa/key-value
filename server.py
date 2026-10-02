from key_value import KVStore
import socket
import threading

store = KVStore()

def _get_message_and_parse(conn, addr):
    buffer = b''

    while True:
        chunk = conn.recv(4)
        if not chunk:
            break
        buffer += chunk

        while b'\n' in buffer:
            line, _, buffer = buffer.partition(b'\n')

            client_input = line.decode()

            print(client_input)

            response = store.execute(client_input)
            conn.send((response + '\n').encode())

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