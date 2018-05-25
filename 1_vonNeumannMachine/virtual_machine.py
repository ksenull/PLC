from cpu import Cpu
from interpreter import asm_decoder
import struct


def create_vm(src_name):
    commands = []
    with open(src_name, "rb") as src_f:
        while True:
            b = src_f.read(4)
            if not b:
                break;
            commands.append(struct.unpack(">I", b)[0])
    # print(commands)

    cpu = Cpu(memory_size=len(commands))
    for i, word in enumerate(commands):
        cpu.memory[i] = int(word)
    return cpu


if __name__ == "__main__":
    src = './code/factorial.asm'
    asm_decoder(src)
    vm = create_vm("./code/factorial.o")
    vm.start()

