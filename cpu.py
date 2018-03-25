from memory import Memory

memory = Memory()  # one for (multiple) cpu


class Cpu:
    def __init__(self,):
        self.program_counter = 0
        self.instruction = 0
        self.address = 0
        self.acc = 0

    def load(self):
        self.acc = memory[self.address]

    def store(self):
        memory[self.address] = self.acc

    def add(self):
        self.acc += memory[self.address]

    def sub(self):
        self.acc -= memory[self.address]

    def inp(self):
        self.acc = int(input())

    def out(self):
        print(self.acc)

    def halt(self):
        self.acc = 0
        self.instruction = 0
        self.address = 0

    def jump(self):
        self.program_counter = memory[self.address]

    def j0(self):
        if self.acc == 0:
            self.program_counter = memory[self.address]

    def j1(self):
        if self.acc > 0:
            self.program_counter = memory[self.address]

    def start(self):
        while True:
            self.step()
            if self.instruction == 0:
                return

    def step(self):
        self.program_counter += 1
        command = memory[self.program_counter]
        self.instruction = command // 100
        self.address = command % 100
        if self.instruction == 1:
            self.load()
        elif self.instruction == 2:
            self.store()
        elif self.instruction == 3:
            self.add()
        elif self.instruction == 4:
            self.sub()

        # TODO