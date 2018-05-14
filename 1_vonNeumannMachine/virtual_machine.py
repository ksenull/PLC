from cpu import Cpu
from interpreter import asm_decoder


def create_vm(src):
    commands = src.split()
    cpu = Cpu(memory_size=len(commands))
    for i, word in enumerate(commands):
        cpu.memory[i] = int(word)
    return cpu


if __name__ == "__main__":
    src = './code/factorial.asm'
    machine_code = asm_decoder(src)
    vm = create_vm(machine_code)
    vm.start()

