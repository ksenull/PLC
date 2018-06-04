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

        mm_pos += uint_s  # n_commands offset
        for i in range(self.n_commands):
            if cell == i + self.n_data_elements:
                return struct.unpack('I', self.mm[mm_pos: mm_pos + uint_s])[0]
            mm_pos += uint_s

    def __set_data_to_memory(self, cell, value):
        assert cell < self.n_data_elements
        mm_pos = uint_s
        for i in range(self.n_data_elements):
            data_size = struct.unpack('I', self.mm[mm_pos: mm_pos + uint_s])[0]
            mm_pos += uint_s
            if i == cell:
                assert str(value).isnumeric()  # vm can input only numbers as for now
                self.mm[mm_pos:mm_pos + data_size] = bytearray(struct.pack('I', value))
                return
            mm_pos += data_size

    def __get_stack_top(self):
        mm_pos = self.mm_stack_start + self.sp * uint_s
        return struct.unpack('I', self.mm[mm_pos: mm_pos + uint_s])[0]

    def __get_from_stack(self, offset):
        assert self.sp >= offset
        mm_pos = self.mm_stack_start + (self.sp - offset) * uint_s
        return struct.unpack('I', self.mm[mm_pos: mm_pos + uint_s])[0]

    def __set_stack_top(self, value):
        mm_pos = self.mm_stack_start + self.sp * uint_s
        self.mm[mm_pos:mm_pos + uint_s] = bytearray(struct.pack('I', value))

    def __get_value(self, arg):
        storage = arg['type']
        if storage == 'S':
            return self.__get_from_stack(arg['val'])
        elif storage == 'M':
            return self.__get_data_from_memory(arg['val'])
        else:
            return arg['val']

    def halt(self):
        self.ip = 0
        self.arg0 = 0
        self.arg1 = 0

    # def add(self):
    #     if self.arg0['type'] == 'S':
    #         pos = self.stack_start + (self.sp + self.arg0['val']) * uint_s
    #         val = self.mm[pos: pos + uint_s]
    #         val += self.mm[[-self.arg]
    #     elif self.is_memory_arg:
    #         self.acc += self.memory[self.arg]
    #     else:
    #         self.acc += self.arg
    #
    # def call(self):
    #     self.jump()
    #
    def push(self):
        if self.arg1['type'] is not None:
            self.__set_stack_top(self.arg1['val'])
        self.sp += uint_s

    #
    # def pop(self):
    #     pass
    #

    def inp(self):
        assert self.arg1['type'] == 'M'
        val = int(input())
        self.__set_data_to_memory(self.arg1['val'], val)

    def out(self):
        value = self.__get_value(self.arg1)
        print(value)

    def j0(self):
        _, val = self.__get_pos_and_value(self.arg0)
        if val == 0:
            where_pos, where_value= self.__get_pos_and_value(self.arg1)
            assert where_value < self.n_commands
            self.ip = where_value
            # self.ip = self.ip - val
    #
    # def j1(self):
    #     if self.acc > 0:
    #         self.program_counter = self.arg - 1
    #
    # def jump(self):
    #     self.program_counter = self.arg - 1
    #
    # def load(self):
    #     if self.is_stack_arg:
    #         self.acc = self.stack[-self.arg]
    #     elif self.is_memory_arg:
    #         self.acc = self.memory[-self.arg]
    #     else:
    #         self.acc = self.arg
    #
    # def mul(self):
    #     if self.is_stack_arg:
    #         self.acc *= self.stack[-self.arg]
    #     elif self.is_memory_arg:
    #         self.acc *= self.memory[self.arg]
    #     else:
    #         self.acc *= self.arg
    #





    #
    # def ret(self):
    #     self.program_counter = self.stack[-1] - 1
    #     for i in range(self.arg):
    #         self.stack.pop()
    #
    # def store(self):
    #     self.memory[self.arg] = self.acc
    #
    # def sub(self):
    #     if self.is_stack_arg:
    #         self.acc -= self.stack[-self.arg]
    #     elif self.is_memory_arg:
    #         self.acc -= self.memory[self.arg]
    #     else:
    #         self.acc -= self.arg
    #
    #

    def step(self):
        # print("Instruction counter " + str(self.program_counter))
        command_pos = uint_s + self.data_segment_size + uint_s + self.ip * uint_s
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
        print('Calling ' + method_name + ' with args ' + str(self.arg0) + ' and ' + str(self.arg1))

        self.__getattribute__(method_name)()

        self.ip += 1

    def start(self):
        mm_pos = 0
        self.n_data_elements = struct.unpack('I', self.mm[mm_pos:mm_pos + uint_s])[0]
        print("Data elements count", self.n_data_elements)

        mm_pos += uint_s

        for i in range(self.n_data_elements):
            data_size = struct.unpack('I', self.mm[mm_pos:mm_pos + uint_s])[0]
            print("Fragment size:", data_size)
            mm_pos += uint_s + data_size  # сдвигаем на размер данных
            self.data_segment_size += uint_s + data_size

        self.n_commands = struct.unpack('I', self.mm[mm_pos:mm_pos + uint_s])[0]
        print("Commands count", self.n_commands)

        mm_pos += uint_s + uint_s * self.n_commands
        self.stack_size = struct.unpack('I', self.mm[mm_pos:mm_pos + uint_s])[0]
        self.mm_stack_start += mm_pos + uint_s
        print("Stack size", self.stack_size)
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
