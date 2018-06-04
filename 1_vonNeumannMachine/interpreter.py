import struct

from utils import get_value, args_to_machine_word, is_hex

'''
Interpreter.asm_decoder() парсит этот ассемблер и записывает в бинарник в следующем виде:
-размер сегмента с данными
-данные
-размер сегмента с кодом
-код
-размер стека
-память под стек
'''


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

number_of_commands = dict(enumerate(commands.keys()))


class Interpreter:

    def __init__(self):
        self.stack_size = 0
        self.memory = [0]  # гарантируется что в 1 ячейке будет лежать ip
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
        if '.stack' in self.sections:
            self.__parse_stack_section()
            # print(self.stack_size, self.registers)
        if '.data' in self.sections:
            self.__parse_data()
        if '.program' in self.sections:
            self.__parse_program()

    def __parse_stack_section(self):
        # print(section)
        for line in self.sections['.stack']:
            if 'size' in line:
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
                addr += 1  # offset for IP written in memory[0]
                args.append(memory_code + addr)
                if addr >= len(self.memory):
                    raise MemoryError
            else:  # label or variable  #TODO variable
                if w in self.labels:
                    memory_code = 200
                    args.append(memory_code + self.labels[w])
                else:  # label not found yet
                    args.append(w)
        return args

    def __parse_program(self):
        section = self.sections['.program']
        # machine_program = []
        unpasted_labels = {}  # command_num: [{'ip', 'args'}]
        self.memory[0] = len(self.memory)

        ip = self.memory[0]
        for line in section:
            # print(line)
            self.memory.append(0)  # reserve a place for future instruction
            words = line.split()

            if words[0] in commands:
                if words[0] == 'halt':
                    self.memory[ip] = str(0)
                    ip += 1
                    continue

                command = (commands[words[0]]) * 1000000
                if len(words) > 1:  # если есть аргументы у команды
                    args = self.__parse_args(words[1:], ip)

                    is_args_ready = True
                    for arg in args:
                        if not str(arg).isnumeric():  # это может быть только не найденный label, т.к. остальное преобразовалось бы в машинный код
                            if command in unpasted_labels:
                                unpasted_labels[command].append({'ip': ip,'args': args})
                            else:
                                unpasted_labels[command] = [{'ip': ip, 'args': args}]
                            is_args_ready = False  # will form machine code later

                    if not is_args_ready:
                        ip += 1
                        continue

                    self.memory[ip] = command + args_to_machine_word(args)
                else:
                    self.memory[ip] = command

            else:  # label or procedure
                if len(words) > 1:  # procedure
                    # print(words)
                    assert len(words) == 2
                    assert words[1] == 'proc' or words[1] == 'endp'
                    if words[1] == 'proc':
                        self.labels[words[0]] = ip
                    self.memory.pop()  # those keywords aren't instructions actually, so we should free reserved memory
                    continue
                else:  # label
                    assert words[0][-1] == ':'
                    self.labels[words[0][:-1]] = ip
                    self.memory.pop()
                    continue
            ip += 1
        # print(labels)
        # final stage: place every label on its place in memory
        for command in unpasted_labels:
            values = unpasted_labels[command]
            for val in values:
                ip, args = val['ip'], val['args']
                replaced_args = []
                for arg in args:
                    if not str(arg).isnumeric():
                        label_addr = self.labels[arg]
                        memory_code = 200
                        replaced_args.append(memory_code + label_addr)
                    else:
                        replaced_args.append(arg)
                self.memory[ip] = command + args_to_machine_word(replaced_args)

        self.machine_src = [*self.memory[self.memory[0]:]]

    def __parse_data(self):
        section = self.sections['.data']
        last_free = 1  # first cell is for IP
        for line in section:
            tokens = line.split()
            assert len(tokens) > 1  # name value
            addr = last_free
            if addr >= len(self.memory):
                self.__grow_memory(addr + 1)
            self.memory[addr] = get_value(' '.join(tokens[1:]))

    def __grow_memory(self, new_size):
        assert new_size > len(self.memory)
        # print('grow to ', new_size)
        self.memory += [0] * (new_size - len(self.memory))

    def __write_to_binary(self, filename):
        binary_filename = filename[:filename.rfind('.')] + '.o'
        with open(binary_filename, "wb+") as binary:

            # write data in memory
            binary.write(bytearray(struct.pack('I', self.memory[0])))
            for val in self.memory[1:self.memory[0] + 1]:  # memory segment
                if str(val).isnumeric():
                    val = '0000'
                val_len = len(val)
                binary.write((struct.pack('I', val_len)))
                binary.write(struct.pack('{}s'.format(val_len), bytearray(val, encoding='utf8')))

            # write program
            binary.write(bytearray(struct.pack('I', len(self.machine_src))))
            for word in self.machine_src:
                # if not str(word).isnumeric():
                # print(word)
                binary.write(bytearray(struct.pack('I', int(word))))

            # allocate stack memory
            binary.write(struct.pack('I', int(self.stack_size)))
            for stack_word in range(int(self.stack_size)):
                binary.write(struct.pack('I', 0))

    def asm_decoder(self, filename):
        with open(filename, 'r') as asm_file:
            self.src = asm_file.readlines()
        self.__clear_comments()
        self.__divide_asm_into_sections()
        self.__parse_sections()
        self.__write_to_binary(filename)

        # print(len(self.memory))
        # print(self.memory[0])
        # print(self.stack_size)
        return self.machine_src


if __name__ == '__main__':
    interpreter = Interpreter()
    machine_code = interpreter.asm_decoder('./code/factorial.asm')
    with open('./code/factorial.machine', 'w') as f:
        for code in machine_code:
            f.write(str(code))
            f.write('\n')

    # print(number_of_commands)
