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
    def __init__(self, memory_size=100):
        self.program_counter = 0
        self.instruction = 0
        self.is_stack_arg = False
        self.is_memory_arg = False
        self.arg = 0
        self.acc = 0
        self.memory = Memory(memory_size)
        self.stack = []

    def add(self):
        if self.is_stack_arg:
            self.acc += self.stack[-self.arg]
        elif self.is_memory_arg:
            self.acc += self.memory[self.arg]
        else:
            self.acc += self.arg

    def call(self):
        self.jump()

    def halt(self):
        self.acc = 0
        self.instruction = 0
        self.arg = 0
        assert self.stack == []

    def inp(self):
        self.acc = int(input())

    def j0(self):
        # assert self.is_memory_arg
        if self.acc == 0:
            self.program_counter = self.arg - 1

    def j1(self):
        if self.acc > 0:
            self.program_counter = self.arg - 1

    def jump(self):
        self.program_counter = self.arg - 1

    def load(self):
        if self.is_stack_arg:
            self.acc = self.stack[-self.arg]
        elif self.is_memory_arg:
            self.acc = self.memory[-self.arg]
        else:
            self.acc = self.arg

    def mul(self):
        if self.is_stack_arg:
            self.acc *= self.stack[-self.arg]
        elif self.is_memory_arg:
            self.acc *= self.memory[self.arg]
        else:
            self.acc *= self.arg

    def out(self):
        print(self.acc)

    def pop(self):
        pass

    def push(self):
        if self.arg == 0:
            self.stack.append(self.acc)
        elif self.is_stack_arg:
            self.stack.append(self.stack[-self.arg])
        elif self.is_memory_arg:
            self.stack.append(self.arg)
        else:
            self.stack.append(self.arg)

    def ret(self):
        self.program_counter = self.stack[-1] - 1
        for i in range(self.arg):
            self.stack.pop()

    def store(self):
        self.memory[self.arg] = self.acc

    def sub(self):
        if self.is_stack_arg:
            self.acc -= self.stack[-self.arg]
        elif self.is_memory_arg:
            self.acc -= self.memory[self.arg]
        else:
            self.acc -= self.arg

    def start(self):
        while True:
            self.is_stack_arg = False
            self.is_memory_arg = False
            self.step()
            if self.instruction == 0:
                return

    def step(self):
        # print("Instruction counter " + str(self.program_counter))
        command = self.memory[self.program_counter]
        self.instruction = command // 1000
        arg = command % 1000
        storage = arg // 100
        if storage == 1:
            self.is_stack_arg = True
        elif storage == 2:
            self.is_memory_arg = True
        self.arg = arg % 100

        methods_list = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith('__')]
        # print(methods_list)
        # print("Calling " + methods_list[self.instruction-1] + " " + str(arg))
        getattr(self, methods_list[self.instruction-1])()

        self.program_counter += 1

