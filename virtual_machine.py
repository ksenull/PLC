from cpu import Cpu
from interpreter import Interpreter
import struct

if __name__ == "__main__":
    src = './code/factorial.asm'
    i = Interpreter()
    i.asm_decoder(src)

    vm = Cpu("./code/factorial.o")
    # print(vm.__get_data_from_memory(0))
    # memory = 4 + 2 * 4
    # pos = 0
    vm.start()
    # vm.mm[0:4] = bytearray(struct.pack('I', 42))
    # print(struct.unpack('I', vm.mm[pos:pos + 4]))
    vm.close()

