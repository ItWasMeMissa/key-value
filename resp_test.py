import resp
import pytest

def test_cut_of_command_1():
    resalt = resp.parse_command(b'*3')

    assert resalt is None


def test_cut_of_command_2():
    resalt = resp.parse_command(b'*3\r\n$3\r\n')

    assert resalt is None


def test_cut_of_command_3():
    resalt = resp.parse_command(b'*3\r\n$3\r\nSET\r\n')

    assert resalt is None


def test_cut_of_command_4():
    resalt = resp.parse_command(b'*3\r\n$3\r\nSET\r')

    assert resalt is None


def test_two_commands():
    resalt = resp.parse_command(b'*3\r\n'
        b'$3\r\nSET\r\n'
        b'$1\r\na\r\n'
        b'$1\r\n1\r\n'
        b'*3\r\n'
        b'$3\r\nSET\r\n'
        b'$1\r\nb\r\n'
        b'$1\r\n1\r\n'
        )

    assert resalt == ([b'SET', b'a', b'1'],
                      b'*3\r\n$3\r\nSET\r\n$1\r\nb\r\n$1\r\n1\r\n'
                      )


def test_cut_of_command_5():
    data = b'*3\r\n$3\r\nSET\r\n$1\r\na\r\n$1\r\n1\r\n'

    for i in range(len(data)):
        assert resp.parse_command(data[:i]) is None


def test_garbage_input():
    with pytest.raises(resp.ParseError):
        resp.parse_command(b'hello\r\n')

    with pytest.raises(resp.ParseError):
        resp.parse_command(b'*x\r\n')

    with pytest.raises(resp.ParseError):
        resp.parse_command(b'*1\r\n$x\r\n')

    with pytest.raises(resp.ParseError):
        resp.parse_command(b'*1\r\n$3\r\nSETX\r\n')

    with pytest.raises(resp.ParseError):
        resp.parse_command(b'*\xff\r\n')

    with pytest.raises(resp.ParseError):
        resp.parse_command(b'*\xc2\xb2\r\n')

    with pytest.raises(resp.ParseError):
        resp.parse_command(b'*-1\r\n')

    with pytest.raises(resp.ParseError):
        resp.parse_command(b'*1\r\n$-1\r\n')

    with pytest.raises(resp.ParseError):
        resp.parse_command(b'*\r\n')

    with pytest.raises(resp.ParseError):
        resp.parse_command(b'*1\r\n$99999999999\r\nx')

    with pytest.raises(resp.ParseError):
        resp.parse_command(b'*0\r\n')


def test_value_with_space():
    result = resp.parse_command(b'*3\r\n$3\r\nSET\r\n$1\r\na\r\n$3\r\na b\r\n')

    assert result == ([b'SET', b'a', b'a b'], b'')


def test_value_with_crlf_inside():
    result = resp.parse_command(b'*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$4\r\na\r\nb\r\n')

    assert result == ([b'SET', b'k', b'a\r\nb'], b'')


def test_empty_value_and_value_starting_with_dollar():
    result = resp.parse_command(b'*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$0\r\n\r\n')
    assert result == ([b'SET', b'k', b''], b'')

    result = resp.parse_command(b'*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$2\r\n$x\r\n')
    assert result == ([b'SET', b'k', b'$x'], b'')