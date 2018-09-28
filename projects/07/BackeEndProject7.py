# -*- coding: utf-8 -*- 
import os, sys

from Parser import Parser
from CodeWriter import CodeWriter

class BackEndProject7(object):
    def __init__(self, vmfile):
        # project7 不考虑分支命令 和 函数调用命令
        # 只考虑单个vm文件
        if os.path.isdir(vmfile):
            return
        else:
            f = open(vmfile, 'r')
            lines = f.readlines()
            f.close()

            vm_commands = []
            for i in range(len(lines)):
                line = lines[i].strip()

                slash_idx = len(line)
                if '//' in line:
                    slash_idx = line.index('//')
                line = line[:slash_idx]

                line= line.rstrip()

                line = line.split(' ')
                line = filter(lambda x:x, line)
                line = ' '.join(line)

                if line == '':
                    continue

                if not self.valid(line):
                    raise Exception("invalid vm statement in line {0}".format(i+1))

                print "line: ", line
                vm_commands.append(line)

            self.parser = Parser()
            self.parser.coms = vm_commands
            self.parser.len_coms = len(vm_commands)

            dirt = os.path.dirname(vmfile)
            filename = os.path.basename(vmfile)
            asm_name = filename.split('.')[0] + '.asm'
            self.asm_name = os.path.join(dirt, asm_name)

            print ''
            print "direct: ", dirt
            print "vmname: ", filename
            print "asmname: ", asm_name
            print "fullpath_asm: ", self.asm_name
            print ''
            self.codewriter = CodeWriter(self.asm_name)


    def valid(self, line):
        return True

    def complile(self):
        while self.parser.hasMoreCommands():
            vm_com = self.parser.advance()
            comtype = self.parser.commandType(vm_com)
            if comtype in ["C_PUSH", "C_POP"]:
                seg   = self.parser.arg1(vm_com, comtype)
                index = self.parser.arg2(vm_com, comtype)
                self.codewriter.writePushPop(comtype, seg, index)

            elif comtype == "C_ARITHMETIC":
                self.codewriter.writeArithmetic(vm_com)

        self.codewriter.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("please transfer one argument to program!!!")
    backend = BackEndProject7(sys.argv[1])
    backend.complile()

