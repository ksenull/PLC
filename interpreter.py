import argparse


class Interpreter:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Process assembly input')
        self.parser.add_argument('mov', nargs=2)
        self.parser.add_argument("add", nargs=2)
        self.parser.add_argument("mul", nargs=2)
        self.parser.add_argument("sub", nargs=2)
        self.parser.add_argument("je", nargs=1)
        self.parser.add_argument("jg", nargs=1)
        self.parser.add_argument("ret", nargs=1)

    def decode(self, program):
        for line in program:
            self.parser.parse_args(line.split())

