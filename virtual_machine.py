from cpu import Cpu, memory
from interpreter import asm_decoder


def loadCodeInMemory(code):
    for i, word in enumerate(code.split()):
        memory[i] = int(word)


if __name__ == "__main__":
    vm = Cpu()
    summator ='./code/summator.asm'
    machine_code = asm_decoder(summator)
    loadCodeInMemory(machine_code)
    vm.start()


""" 
        INP         300
        STORE 99    1199
        INP         300
        ADD 99      199
        OUT         800
        HLT         200
// Output the sum of two numbers
['add', 'halt', 'inp', 'j0', 'j1', 'jump', 'load', 'out', 'start', 'step', 'store', 'sub']
"""