class ParseError(Exception):
    pass

def _to_int(raw):
    if not raw.isdigit():
        raise ParseError()
    return int(raw)

def parse_command(args):
    cmd = []

    if not args: return None

    if args[0:1] != b'*' :
        raise ParseError()

    end_pos_of_elements = args.find(b'\r\n')
    if end_pos_of_elements == -1:
        return None

    target_num_of_elements = _to_int(args[1:end_pos_of_elements])

    if target_num_of_elements == 0:
        raise ParseError()

    pos = end_pos_of_elements+2

    for _ in range(target_num_of_elements):
        #get head and its pos
        end = args.find(b'\r\n', pos)

        if end < 0: return None

        head = args[pos:end]

        if head[:1] != b'$':
            raise ParseError()

        L = _to_int(head[1:])

        if L > 999999999:
            raise ParseError()

        pos = end+2

        if not len(args) >= pos + L + 2:
            return None

        #part that get data of head + move pos to next head
        data = args[pos:pos+L]

        if args[pos + L:pos + L + 2] != b'\r\n':
            raise ParseError()

        cmd.append(data)

        pos += L + 2

    return (cmd, args[pos:])

def encode_simple(value):
    data = value.encode('utf-8')
    return b'+' + data + b'\r\n'

def encode_error(value):
    data = value.encode('utf-8')
    return b'-' + data + b'\r\n'

def encode_int(value):
    return b':' + str(value).encode('utf-8') + b'\r\n'


def encode_bulk(value):
    if value is None:
        return b'$-1\r\n'
    data = value.encode('utf-8')
    return b'$' + str(len(data)).encode() + b'\r\n' + data + b'\r\n'
