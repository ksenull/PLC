commands = {
    'add': 'adds arg to acc',
    'call': 'alias for [jump]',
    'halt': 'stops machine',
    'inp': 'reads from cin to acc',
    'j0': 'compares with 0 and if yes, jumps to address-arg',
    'j1': 'compares if acc > 0 and if yes jumps to address-arg',
    'jump': 'jumps to address-arg',
    'load': 'loads data from memory, stack or register to acc',
    'mul': 'multiplies number on given arg',
    'out': 'prints acc to standard input',
    'pop': 'removes last item from stack',
    'push': 'pushes arg to stack',
    'ret': 'returns from procedure to the ret addr and unwinds the stack',
    'start': 'runs machine',
    'step': 'steps one machine tact',
    'store': 'saves acc to memory of registry',
    'sub': 'subtracts arg from acc'
}

commands_numbers = {com: num for num, com in enumerate(commands.keys())}


def asm_decoder(filename):
    machine_program = []
    labels = {}  # label, addr
    unpasted_labels = {}  # command_num: {ip, label}
    ip = 0
    for line in open(filename):
        # print(line)

        machine_program.append('_')

        words = line.split()
        if words[0] in commands.keys():
            if words[0] == 'halt':
                machine_program[ip] = str(0)
                ip += 1
                continue
            command = (commands_numbers[words[0]] + 1) * 1000
            if len(words) > 1:
                assert len(words) == 2
                arg = words[1]

                if 'IP' in arg:
                    memory_code = 200

                    sign = arg[2]
                    assert sign == '+' or sign == '-'
                    offset = int(arg[3:])

                    if sign == '+':
                        arg = memory_code + ip + offset
                    else:
                        arg = memory_code + ip - offset
                elif 'SP' in arg:
                    stack_code = 100

                    sign = arg[2]
                    assert sign == '-'
                    offset = int(arg[3:])

                    arg = stack_code + offset

                elif arg.isnumeric():
                    arg = int(arg)
                else:  # label
                    if arg in labels:
                        arg = labels[arg]
                    else:  # label not found yet
                        if command in unpasted_labels:
                            unpasted_labels[command].append((ip, arg))
                        else:
                            unpasted_labels[command] = [(ip, arg)]
                        ip += 1
                        continue

                machine_program[ip] = str(command + arg)
            else:
                machine_program[ip] = str(command)

        else:  # label or procedure
            if len(words) > 1:
                assert len(words) == 2
                assert words[1] == 'proc' or words[1] == 'endp'
                if words[1] == 'proc':
                    labels[words[0]] = ip
                machine_program.pop()
                continue
            else:
                assert words[0][-1] == ':'
                labels[words[0][:-1]] = ip
                machine_program.pop()
                continue
        ip += 1

    # print(labels)
    for com in unpasted_labels:
        vals = unpasted_labels[com]
        for val in vals:
            ip, label = val
            # print(ip, label)
            label_addr = labels[label]
            machine_program[ip] = str(com + label_addr)

    with open("./code/factorial.o", "w+") as bin:
        for word in machine_program:
            bin.write(word)
            bin.write(" ")
    # return ' '.join(machine_program)


if __name__ == '__main__':
    asm_decoder('./code/factorial.asm')
    with open("./code/factorial.o") as bin:
        for line in bin:
            print(line)
