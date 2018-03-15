
class Memory:
    def __init__(self, size):
        self.cells = [0] * size

    def fetch(self, address):
        return self.cells[address]

    def store(self, address, value):
        self.cells[address] = value