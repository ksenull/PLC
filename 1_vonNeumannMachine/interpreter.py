import struct

from utils import get_value, args_to_machine_word, is_hex

commands = {
    'halt': 0,
    'add': 1,
    'sub': 2,
    'mul': 3,
    'push': 4,
    'pop': 5,
    'inp': 6,
    'out': 7,
    'jump': 8,
    'j0': 9,
    'jeq': 10,
    'jlt': 11,
    'call': 12,
    'mov': 13
}


class Interpreter:

    def __init__(self):
        self.stack_size = 0
        self.memory = []
        self.src = []
        self.sections = {}
        self.labels = {}  # label, addr
        self.machine_src = []
        self.source_file = None
        self.obj_file = None

    def __clear_comments(self):
        new_src = []
        for line in self.src:
            comment_start = line.find(';')
            if comment_start == -1:
                new_src.append(line)
            else:
                new_src.append(line[:comment_start])
        self.src = new_src

    def __divide_asm_into_sections(self):
        section = []
        section_name = None
        for line in self.src:
            if line.startswith('.'):
                if len(section) > 0:
                    self.sections[section_name] = [*section]
                    section = []
                section_name = line.strip()
                assert section_name not in self.sections
            else:
                section.append(line.strip())
        self.sections[section_name] = [*section]

    def __parse_sections(self):
        if '.init' in self.sections:
            self.__parse_init_section()
            # print(self.stack_size, self.registers)
        if '.program' in self.sections:
            self.__parse_program()
        if '.data' in self.sections:
            self.__parse_data()

    def __parse_init_section(self):
        # print(section)
        for line in self.sections['.init']:
            if 'stack_size' in line:
                self.stack_size = line.split()[2]

    def __parse_args(self, words, ip):
        assert len(words) <= 2
        args = []
        for w in words:
            if w.startswith('IP'):
                memory_code = 200
                sign = w[2]
                assert sign == '+' or sign == '-'
                offset = int(w[3:])

                if sign == '+':
                    args.append(memory_code + ip + offset)
                else:
                    args.append(memory_code + ip - offset)
            elif w.startswith('SP'):
                stack_code = 100
                offset = 0
                if len(w) > 2:
                    sign = w[2]
                    assert sign == '-'
                    offset = int(w[3:])
                args.append(stack_code + offset)

            elif w.isnumeric():
                args.append(int(w))
            elif is_hex(w):
                memory_code = 200
                addr = int(w, 16)
                args.append(memory_code + addr)
                if addr >= len(self.memory):
                    self.__grow_memory(addr + 1)
            else:  # label
                if w in self.labels:
                    memory_code = 200
                    args.append(memory_code + self.labels[w])
                else:  # label not found yet
                    args.append(w)
        return args

    def __parse_program(self):
        section = self.sections['.program']
        machine_program = []
        unpasted_labels = {}  # command_num: [{'ip', 'args'}]
        ip = 0
        for line in section:
            # print(line)
            machine_program.append(None)
            words = line.split()

            if words[0] in commands:
                if words[0] == 'halt':
                    machine_program[ip] = str(0)
                    ip += 1
                    continue

                command = (commands[words[0]]) * 1000000
                if len(words) > 1:
                    args = self.__parse_args(words[1:], ip)

                    is_args_ready = True
                    for arg in args:
                        if not str(arg).isnumeric():
                            if command in unpasted_labels:
                                unpasted_labels[command].append({'ip': ip,'args': args})
                            else:
                                unpasted_labels[command] = [{'ip': ip, 'args': args}]
                            is_args_ready = False  # will form machine code later
                    if not is_args_ready:
                        ip += 1
                        continue

                    machine_program[ip] = command + args_to_machine_word(args)
                else:
                    machine_program[ip] = command

            else:  # label or procedure
                if len(words) > 1:  # procedure
                    # print(words)
                    assert len(words) == 2
                    assert words[1] == 'proc' or words[1] == 'endp'
                    if words[1] == 'proc':
                        self.labels[words[0]] = ip
                    machine_program.pop()
                    continue
                else:  # label
                    assert words[0][-1] == ':'
                    self.labels[words[0][:-1]] = ip
                    machine_program.pop()
                    continue
            ip += 1
        # print(labels)
        for command in unpasted_labels:
            vals = unpasted_labels[command]
            for val in vals:
                ip, args = val['ip'], val['args']
                replaced_args = []
                for arg in args:
                    if not str(arg).isnumeric():
                        label_addr = self.labels[arg]
                        memory_code = 200
                        replaced_args.append(memory_code + label_addr)
                    else:
                        replaced_args.append(arg)
                machine_program[ip] = command + args_to_machine_word(replaced_args)

        self.machine_src = [*machine_program]

    def __parse_data(self):
        section = self.sections['.data']
        for line in section:
            tokens = line.split()
            assert len(tokens) > 3  # name value address
            addr = int(tokens[-1], 16)
            if addr >= len(self.memory):
                self.__grow_memory(addr + 1)
            self.memory[addr] = get_value(''.join(tokens[1:-1]))

    def __grow_memory(self, new_size):
        assert new_size > len(self.memory)
        # print('grow to ', new_size)
        new_memory = [0] * new_size
        for i in range(len(self.memory)):
            new_memory[i] = self.memory[i]
        self.memory = new_memory

    def asm_decoder(self, filename):
        with open(filename, 'r') as asm_file:
            self.src = asm_file.readlines()
        self.__clear_comments()
        self.__divide_asm_into_sections()
        self.__parse_sections()

        # print(len(self.memory))
        # print(self.memory[0])
        # print(self.stack_size)
        # return

        with open("./code/factorial.o", "wb+") as binf:
            for word in self.machine_src:
                # if not str(word).isnumeric():
                # print(word)
                binf.write(bytearray(struct.pack('I', int(word))))
                # bin.write(" ")
            for mem_word in self.memory:
                if str(mem_word).isnumeric():
                    binf.write(bytearray(struct.pack('I', mem_word)))
                else:
                    binf.write(bytearray(struct.pack('s', str(mem_word))))
        return self.machine_src


if __name__ == '__main__':
    interpreter = Interpreter()
    machine_code = interpreter.asm_decoder('./code/factorial.asm')
    print(machine_code)
    # with open("./code/factorial.o") as bin:
    #     for line in bin:
    #         print(line)
