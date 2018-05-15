from cpu import Cpu
from interpreter import asm_decoder


def create_vm(src_name):
    commands = []
    with open(src_name, "r") as src_f:
        for line in src_f:
            commands += line.split()

    cpu = Cpu(memory_size=len(commands))
    for i, word in enumerate(commands):
        cpu.memory[i] = int(word)
    return cpu


if __name__ == "__main__":
    src = './code/factorial.asm'
    asm_decoder(src)
    vm = create_vm("./code/factorial.o")
    vm.start()

