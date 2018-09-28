# -*- coding: utf-8 -*-

class Parser(object):
    ARITHMETIC_COM = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
    FLOW = ["label", "goto", "if-goto"]
    FUNC = ["function", "call", "return"]
    
    def __init__(self):
        self.coms = []
        self.n = 0
        self.len_coms = 0
        self.vmf = ''

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
        ss = com.split(' ')
        if ss[0] in self.ARITHMETIC_COM: return "C_ARITHMETIC"
        elif ss[0] == 'push':            return "C_PUSH"
        elif ss[0] == 'pop':             return "C_POP"
        elif ss[0] == 'label':           return "C_LABEL"
        elif ss[0] == 'goto':            return "C_GOTO"
        elif ss[0] == 'if-goto':         return "C_IF"
        elif ss[0] == 'function':        return "C_FUNCTION"
        elif ss[0] == 'return':          return "C_RETURN"
        elif ss[0] == 'call':            return "C_CALL"

    def arg1(self, com, comtype):
        if comtype in ["C_PUSH", "C_POP", "C_GOTO", "C_IF", "C_LABEL", "C_FUNCTION", "C_CALL"]:
            return com.split(' ')[1]

    def arg2(self, com, comtype):
        ss = com.split(' ')
        ans = None
        if comtype in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
            ans = ss[2]
        if ss[1] == "static":
            ans = self.vmf + "." + ans
        return ans
