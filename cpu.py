from memory import Memory


class Cpu:
    def __init__(self, memory_size=100):
        self.program_counter = 0
        self.instruction = 0
        self.address = 0
        self.acc = 0
        self.memory = Memory(memory_size)
        self.stack = []

    def load(self):
        self.acc = self.memory[self.address]

    def store(self):
        self.memory[self.address] = self.acc

    def add(self):
        self.acc += self.memory[self.address]

    def sub(self):
        self.acc -= self.memory[self.address]

    def inp(self):
        self.acc = int(input())

    def out(self):
        print(self.acc)

    def halt(self):
        self.acc = 0
        self.instruction = 0
        self.address = 0

    def jump(self):
        self.program_counter = self.memory[self.address]

    def j0(self):
        if self.acc == 0:
            self.program_counter = self.memory[self.address]

    def j1(self):
        if self.acc > 0:
            self.program_counter = self.memory[self.address]

    def start(self):
        while True:
            self.step()
            if self.instruction == 0:
                return

    def step(self):
        command = self.memory[self.program_counter]
        self.instruction = command // 100
        self.address = command % 100

        method_list = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith('__')]
        getattr(self, method_list[self.instruction-1])()

        self.program_counter += 1

