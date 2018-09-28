# -*- coding: utf-8 -*-

class Parser(object):
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
        if com[0] == '@' :
            return 'A_COMMAND'
        elif com[0] == '(' and com[-1] == ')':
            return 'L_COMMAND'
        else:
            return 'C_COMMAND'

    def symbol(self, com, comtype):
        if comtype == 'A_COMMAND':
            return com[1:]
        elif comtype == 'L_COMMAND':
            return com[1:-1]

    def dest(self, com):
        if '=' in com:
            return com[:com.index('=')]
        else:
            return 'null'

    def comp(self, com):
        idx_eq = -1
        if '=' in com:
            idx_eq = com.index('=')
        idx_semi = len(com)
        if ';' in com:
            idx_semi = com.index(';')
        return com[idx_eq+1:idx_semi]

    def jump(self, com):
        if ";" in com:
            return com[com.index(';')+1:]
        else:
            return 'null'