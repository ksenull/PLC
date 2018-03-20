MAX_BYTE_VALUE = 2 ** 8


class Register:
    def __init__(self, init_value=0):
        self.bytes = [init_value] * 4

    def set(self, value, ind):
        assert 0 <= ind < 4
        assert 0 <= value < MAX_BYTE_VALUE

        self.bytes[ind] = value

    def get(self, ind):
        assert 0 <= ind < 4

        return self.bytes[ind]


class ALU:
    def __init__(self):
        pass

    def add(self, a, b):
        return a + b


class CPU:
    def __init__(self):
        self.EIP = Register()
        self.ESP = Register()
        self.FLAGS = Register()

        self.ALU = ALU()



