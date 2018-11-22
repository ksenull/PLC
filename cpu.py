import mmap
import struct

from interpreter import number_of_commands
from typeinfo import uint_s, byte_s

from memory import Memory
'''
    'add': 'adds arg to acc',
    'call': 'alias for [jump]',
    'halt': 'stops machine',
    'inp': 'reads from cin to acc',
    'j0': 'compares with 0 and if yes, jumps to address-arg',
    'j1': 'compares if less and if yes jumps to address-arg',
    'jump': 'jumps to address-arg',
    'load': 'loads data from memory, stack or register to acc',
    'mul': 'multiplies number on given arg',
    'out': 'prints acc to standard input',
    'pop': 'removes last item from stack',
    'push': 'pushes arg to stack',
    'ret': 'returns from procedure to the ret addr and unwinds the stack',
    'start': 'runs machine',
    'step': 'steps one machine tact',
    'store': 'saves acc to memory of registry',
    'sub': 'subtracts arg from acc'
'''


class Cpu:
    def __init__(self, binary):
        self.binary = open(binary, 'a+b')
        self.mm = mmap.mmap(self.binary.fileno(), 0)

        self.n_data_elements = 0
        self.n_commands = 0
        self.data_segment_size = 0
        self.stack_size = 0
        self.mm_stack_start = 0

        self.sp = 0
        self.ip = 0

        self.instruction = 0
        self.arg0 = {'type': 'N', 'val': 0}  # type on stack (S) on memory (M) number (N)
        self.arg1 = {'type': 'N', 'val': 0}

    def __get_data_from_memory(self, cell):
        if cell > self.n_data_elements + self.n_commands:
            raise MemoryError
        mm_pos = uint_s
        for i in range(self.n_data_elements):
            data_size = struct.unpack('I', self.mm[mm_pos: mm_pos + uint_s])[0]
            mm_pos += uint_s
            if i == cell:
                value = struct.unpack('{}s'.format(data_size), self.mm[mm_pos:mm_pos + data_size])[0].decode("utf8")
                return value
            mm_pos += data_size

        return cell
        # mm_pos += uint_s  # n_commands offset
        # for i in range(self.n_commands):
        #     if cell == i + self.n_data_elements:
        #         return struct.unpack('I', self.mm[mm_pos: mm_pos + uint_s])[0]
        #     mm_pos += uint_s

    def __set_data_to_memory(self, cell, value):
        assert cell < self.n_data_elements
        assert isinstance(value, str)
        assert str(value).isnumeric()  # vm can input only numbers as for now
        mm_pos = uint_s
        for i in range(self.n_data_elements):
            data_size = struct.unpack('I', self.mm[mm_pos: mm_pos + uint_s])[0]
            mm_pos += uint_s
            if i == cell:
                val = '0' * (uint_s - len(value)) + value
                self.mm[mm_pos:mm_pos + data_size] = struct.pack('{}s'.format(uint_s), bytearray(val, encoding='utf8'))
                return
            mm_pos += data_size

    def __get_stack_top(self):
        mm_pos = self.mm_stack_start + self.sp * uint_s
        return struct.unpack('I', self.mm[mm_pos: mm_pos + uint_s])[0]

    def __get_from_stack(self, offset):
        assert self.sp >= offset
        mm_pos = self.mm_stack_start + (self.sp - offset) * uint_s
        value = struct.unpack('I', self.mm[mm_pos: mm_pos + uint_s])[0]
        return value

    def __set_stack_top(self, value):
        mm_pos = self.mm_stack_start + self.sp * uint_s
        self.mm[mm_pos:mm_pos + uint_s] = bytearray(struct.pack('I', int(value)))

    def __set_to_stack(self, offset, value):
        assert self.sp >= offset
        mm_pos = self.mm_stack_start + (self.sp - offset) * uint_s
        self.mm[mm_pos:mm_pos + uint_s] = bytearray(struct.pack('I', int(value)))

    def __get_value(self, arg):
        storage = arg['type']
        if storage == 'S':
            return self.__get_from_stack(arg['val'])
        elif storage == 'M':
            value = self.__get_data_from_memory(arg['val'])
            if str(value).isnumeric():
                return int(value)
            return value
        else:
            return arg['val']

    def halt(self):
        self.ip = 0
        self.arg0 = 0
        self.arg1 = 0

    def add(self):
        assert self.arg0['type'] == 'M' or self.arg0['type'] == 'S'
        if self.arg0['type'] == 'S':
            val = self.__get_from_stack(self.arg0['val']) + self.__get_value(self.arg1)
            self.__set_to_stack(self.arg0['val'], val)
        else:
            val = self.__get_data_from_memory(self.arg0['val']) + self.__get_value(self.arg1)
            self.__set_data_to_memory(self.arg0['val'], val)

    def sub(self):
        assert self.arg0['type'] == 'M' or self.arg0['type'] == 'S'
        if self.arg0['type'] == 'S':
            left = self.__get_from_stack(self.arg0['val'])
            right = self.__get_value(self.arg1)
            val = left - right
            self.__set_to_stack(self.arg0['val'], val)
        else:
            val = self.__get_data_from_memory(self.arg0['val']) - self.__get_value(self.arg1)
            self.__set_data_to_memory(self.arg0['val'], val)

    def mul(self):
        assert self.arg0['type'] == 'M' or self.arg0['type'] == 'S'
        if self.arg0['type'] == 'S':
            left = self.__get_from_stack(self.arg0['val'])
            right = self.__get_value(self.arg1)
            val = left * right
            # print(left, '*',  right)
            self.__set_to_stack(self.arg0['val'], val)
            # print("mul", self.__get_stack_top())
        else:
            val = self.__get_data_from_memory(self.arg0['val']) * self.__get_value(self.arg1)
            self.__set_data_to_memory(self.arg0['val'], val)

    def push(self):
        if self.arg1['type'] is not None:
            # if self.arg1['type'] == 'S' or self.arg1['type'] == 'N':
            value = self.__get_value(self.arg1)
            # else:
            #     value = self.arg1['val']
            self.sp += 1
            self.__set_stack_top(value)
            print("[push]", self.__get_stack_top())
        else:
            self.sp += 1

    def pop(self):
        if self.arg1['type'] == 'N' and self.arg1['val'] is not None:
            self.sp -= self.arg1['val']
            print('[pop]', self.arg1['val'])
        else:
            self.sp -= 1
            print('[pop]')

    def inp(self):
        assert self.arg1['type'] == 'M'
        val = int(input())  # TODO
        self.__set_data_to_memory(self.arg1['val'], str(val))

    def out(self):
        value = self.__get_value(self.arg1)
        print(value)

    def jump(self):
        if self.arg1['type'] == 'M':
            self.ip = self.arg1['val'] - 2  # TODO
        else:
            self.ip = self.__get_value(self.arg1) - 2

    def j0(self):
        assert self.arg1['type'] == 'M'
        what = self.__get_value(self.arg0)
        if what == 0:
            where = self.arg1['val'] - 1
            assert self.n_data_elements < where < self.n_commands + self.n_data_elements
            self.ip = where - 1

    def jeq(self):
        pass

    def jlt(self):
        pass

    def call(self):
        self.jump()

    def mov(self):
        assert self.arg0['type'] == 'M' or self.arg0['type'] == 'S'
        val = self.__get_value(self.arg1)
        assert str(val).isnumeric()
        if self.arg0['type'] == 'S':
            self.__set_to_stack(self.arg0['val'], val)
            # print('mov', self.__get_from_stack(self.arg0['val']))
        else:
            self.__set_data_to_memory(self.arg0['val'], val)

    def step(self):
        assert self.ip >= self.n_data_elements
        command_pos = uint_s + self.data_segment_size + uint_s + (self.ip - self.n_data_elements) * uint_s
        command = struct.unpack('I', self.mm[command_pos:command_pos + uint_s])[0]
        # print(command)
        self.instruction = command // 1000000

        args = []
        for val in command % 1000000 // 1000, command % 1000:
            arg = {'type': None, 'val': None}
            storage = val // 100
            if storage == 1:
                arg['type'] = 'S'
            elif storage == 2:
                arg['type'] = 'M'
            else:
                arg['type'] = 'N'
            arg['val'] = val % 100
            args.append(arg)
        self.arg0, self.arg1 = args

        method_name = number_of_commands[self.instruction]
        # print('Calling ' + method_name + ' with args ' + str(self.arg0) + ' and ' + str(self.arg1))

        self.__getattribute__(method_name)()

        self.ip += 1

    def start(self):
        mm_pos = 0
        self.n_data_elements = struct.unpack('I', self.mm[mm_pos:mm_pos + uint_s])[0]
        # print("Data elements count", self.n_data_elements)
        self.ip = self.n_data_elements

        mm_pos += uint_s

        for i in range(self.n_data_elements):
            data_size = struct.unpack('I', self.mm[mm_pos:mm_pos + uint_s])[0]
            # print("Fragment size:", data_size)
            mm_pos += uint_s + data_size  # сдвигаем на размер данных
            self.data_segment_size += uint_s + data_size

        self.n_commands = struct.unpack('I', self.mm[mm_pos:mm_pos + uint_s])[0]
        # print("Commands count", self.n_commands)

        mm_pos += uint_s + uint_s * self.n_commands
        self.stack_size = struct.unpack('I', self.mm[mm_pos:mm_pos + uint_s])[0]
        self.mm_stack_start += mm_pos + uint_s
        # print("Stack size", self.stack_size)
        while True:
            self.step()
            if self.instruction == 0 or self.ip >= self.n_commands + self.n_data_elements:
                return

    def close(self):
        if self.mm:
            self.mm.close()
            self.mm = None
        if self.binary:
            self.binary.close()
            self.binary = None
