commands = ['add', 'halt', 'inp', 'j0', 'j1', 'jump', 'load', 'out', 'start', 'step', 'store', 'sub']


def asm_decoder(filename):
    machine_program = ''
    for line in open(filename):
        words = line.split()
        command = (commands.index(words[0]) + 1) * 100
        if len(words) > 1:
            command += int(words[1])

        machine_program += str(command) + ' '
    return machine_program
