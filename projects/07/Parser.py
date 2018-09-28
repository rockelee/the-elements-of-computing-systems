# -*- coding: utf-8 -*-

class Parser(object):
    ARITHMETIC_COM = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
    def __init__(self):
        self.coms = []
        self.n = 0
        self.len_coms = 0

    def hasMoreCommands(self):
        if self.n < self.len_coms:
            return True
        self.n = 0
        return False

    def advance(self):
        com = self.coms[self.n]
        self.n += 1
        return com

    def commandType(self, com):
        self.ss = com.split(' ')
        if self.ss[0] == 'push':
            return "C_PUSH"
        elif self.ss[0] == 'pop':
            return "C_POP"
        elif self.ss[0] in self.ARITHMETIC_COM:
            return "C_ARITHMETIC"

    def arg1(self, com, comtype):
        if comtype in ["C_PUSH", "C_POP"]:
            return com.split(' ')[1]

    def arg2(self, com, comtype):
        if comtype in ["C_PUSH", "C_POP"]:
            return int(com.split(' ')[2])
