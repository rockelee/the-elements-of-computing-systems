# -*- coding: utf-8 -*-

import sys, string

from Parser import Parser
from Code import Code
from SymbolTable import SymbolTable

class Assembler(object):
    def __init__(self, asm):
        f = open(asm, 'r')
        lines = f.readlines()
        f.close()

        self.parser = Parser()
        self.symtaber = SymbolTable()
        self.coder = Code()

        self.asm_name = asm
        self.hack_name = asm.split('.')[0] + '.my.hack'

        for i in range(len(lines)):
            # 删除行首空白符
            line = lines[i].strip()
            print "line: ", line

            # 删除注释
            slash_idx = len(line)
            if '//' in line:
                slash_idx = line.index('//')
            line = line[:slash_idx]
            
            # 删除末尾空白符
            line = line.rstrip()
            if line == '':
                continue

            # 命令是否合法
            if not self.valid(line, self.parser, self.symtaber, self.coder):
                raise Exception("invalid instruction in line {0}".format(i+1))
            
            self.parser.coms.append(line)
        self.parser.len_coms = len(self.parser.coms)

    def valid_symbol(self, s):
        valid_char = string.letters + string.digits + "_.$:"
        if s[0].isdigit():
            return False
        for i in s:
            if i not in valid_char:
                return False
        return True

    def valid_a_command(self, com):
        if com[1:].isdigit():
            return True
        elif com[1:] in self.symtaber.PREDIFINED:
            return True
        elif self.valid_symbol(com[1:]):
            return True
        return False

    def valid_l_command(self, com):
        if self.valid_symbol(com[1:-1]):
            return True
        return False

    def valid_c_command(self, com):
        # 对于 dest，comp，jump的提取，可以用正则
        idx_eq = -1
        dest = None
        if '=' in com:
            idx_eq = com.index('=')
            dest = com[:idx_eq]
        else:
            dest = 'null'
        if dest not in self.coder.DEST:
            return False

        idx_semi = len(com)
        jump = None
        if ';' in com:
            idx_semi = com.index(';')
            jump = com[idx_semi+1:]
        else:
            jump = 'null'
        if jump not in self.coder.JUMP:
            return False

        comp = com[idx_eq+1:idx_semi]
        if comp not in self.coder.COMP:
            return False
        return True

    def valid(self, com, parser, symtaber, coder):
        assert ' ' not in com  # 命令不允许包含空格
        comtype = parser.commandType(com)
        if comtype == 'A_COMMAND'   and self.valid_a_command(com):
            return True
        elif comtype == 'L_COMMAND' and self.valid_l_command(com):
            return True
        elif comtype == 'C_COMMAND' and self.valid_c_command(com):
            return True
        return False

    def asse(self):
        self.process1()
        self.macins = self.process2()

        with open(self.hack_name, 'w') as f:
            for ins in self.macins:
                f.write(ins + '\n')

    def process1(self):
        id_com = 0
        while self.parser.hasMoreCommands():
            com = self.parser.advance()
            comtype = self.parser.commandType(com)

            if comtype == 'L_COMMAND':
                sym = self.parser.symbol(com, 'L_COMMAND')
                self.symtaber.symtab[sym] = id_com

            if comtype in ['A_COMMAND', 'C_COMMAND']:
                id_com += 1

        var_address = 16
        while self.parser.hasMoreCommands():
            com = self.parser.advance()
            comtype = self.parser.commandType(com)
            if comtype == 'A_COMMAND':
                sym = self.parser.symbol(com, 'A_COMMAND')
                if sym in self.symtaber.PREDIFINED:
                    self.symtaber.symtab[sym] = self.symtaber.PREDIFINED[sym]
                
                elif not sym.isdigit():
                    if sym not in self.symtaber.symtab:
                        self.symtaber.symtab[sym] = var_address
                        var_address += 1
        
        # 符号只可能出现在 A指令和L指令中
        # A指令中的符号要么是数字，要么是预定义的，要么是自定义的
        # 数字不用管
        # 预定义的，那么可以加入到符号表中
        # 自定义的符号要分两种情况讨论：指向变量的地址，指向指令的地址
        # 该怎么区分这两种情况呢？
        # 如果这个符号出现在了L指令中，那么就是指向指令的地址。否则，就是指向变量的地址。
        # 那么是不是应该先遍历一遍所有指令，然后找出所有的L指令中的符号？
        #
        # L指令中的符号就是它的下一条非 L 指令的地址，这个好解析

    def process2(self):
        macins = []
        while self.parser.hasMoreCommands():
            com = self.parser.advance()
            comtype = self.parser.commandType(com) 

            if comtype == 'A_COMMAND':
                sym = self.parser.symbol(com, 'A_COMMAND')
                if sym.isdigit():
                    address = bin(int(sym))[2:]
                else:
                    address = bin(self.symtaber.symtab[sym])[2:]
                Ains = (16 - len(address)) * '0' + address
                print Ains
                macins.append(Ains)

            if comtype == 'C_COMMAND':
                dest = self.parser.dest(com)
                comp = self.parser.comp(com)
                jump = self.parser.jump(com)

                Cins = '111' + self.coder.comp(comp) + self.coder.dest(dest) + self.coder.jump(jump)
                print Cins
                macins.append(Cins)
        return macins

    def compare(self):
        tocompare = self.asm_name.split('.')[0] + '.hack'
        tocompare_incs = []
        print "asm: ", self.asm_name
        print "myhack: ", self.hack_name
        print "tocompare: ", tocompare
        try :
            with open(tocompare, 'r') as f:
                for line in f:
                    tocompare_incs.append(line.strip())
        except:
            print "there is no correct hack file to compare!!!"
            return

        if len(tocompare_incs) != len(self.macins):
            raise Exception("the number of instruction of correct hack file isn't equal to my hack file")
        
        i = 0
        for a, b in zip(self.macins, tocompare_incs):
            i += 1
            if a != b:
                raise Exception("the {0}th instruction is not equal".format(i))







if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("there is no asm file")

    assembler = Assembler(sys.argv[1])
    assembler.asse()
    assembler.compare()