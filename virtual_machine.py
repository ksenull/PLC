import Memory from memory
import Processor from processing_unit

class VirtualMachine:

    def __init__(self, memory_size=16):
        memory = Memory(memory_size)
        cpu = Processor()

    def run(self):
        pass

    def check_if_stops(self):
        pass


if __name__ == "main":
    vm = VirtualMachine()
    vm.run()