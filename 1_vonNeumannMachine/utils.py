import string
import struct


def get_value(s):
    if s.isnumeric():
        return int(s)
    else:
        return s


def args_to_machine_word(args):
    if len(args) == 2:
        return args[0] * 1000 + args[1]
    else:
        return args[0]


def is_hex(s):
    if s.startswith('0x'):
        hex_digits = set(string.hexdigits)
        # if s is long, then it is faster to check against a set
        return all(c in hex_digits for c in s[2:])
    else:
        return False


def pack_str(s):
    s = bytes(s, 'utf-8')
    return struct.pack("I%ds" % (len(s),), len(s), s)


def unpack_str(data):
    # (i,), data = struct.unpack("I", data[:4]), data[4:]
    # s, data = data[:i], data[i:]
    return