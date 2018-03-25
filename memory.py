
class Memory:
    def __init__(self, memory_size=100):
        self.memory = [0] * memory_size

    def __getitem__(self, item):
        return self.memory[item]

    def __setitem__(self, key, value):
        self.memory[key] = value