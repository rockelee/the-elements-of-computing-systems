# -*- coding: utf-8 -*-

import sys
import os
import argparse

from Parser import Parser
from CodeWriter import CodeWriter


class BackEndProject8(object):
    def __init__(self, prodir, WriteInit=True):
        vmfiles = []
        for vf in os.listdir(prodir):
            if vf[-3:] == ".vm":
                vmfiles.append(os.path.join(prodir, vf))
        assert vmfiles

        self.parser = [Parser() for vmf in vmfiles]
        for vmf, parser in zip(vmfiles, self.parser):
            parser.coms = self.read_vm(vmf)
            parser.len_coms = len(parser.coms)
            parser.vmf = os.path.basename(vmf)

        directory = os.path.dirname(vmfiles[0])
        asm_name = os.path.basename(directory) + '.asm'
        self.asmf = os.path.join(directory, asm_name)

        print ''
        print "direct: ", directory
        print "vmfiles:"
        for vmf in vmfiles:
            print "\t", vmf
        print "asmname: ", asm_name
        print "asmf:    ", self.asmf
        print ''

        self.codewriter = CodeWriter(self.asmf)
        self.WI = WriteInit

    def read_vm(self, vmf):
        print "vmf: ", vmf
        
        f = open(vmf, 'r')
        lines = f.readlines()
        f.close()
        
        vm_commands = []
        for i in range(len(lines)):
            line = lines[i].strip()
            slash_idx = len(line)
            if '//' in line:
                slash_idx = line.index('//')
            line = line[:slash_idx]
            line = line.rstrip()
            line = line.split(' ')
            line = filter(lambda x:x, line)
            line = ' '.join(line)
            if line == '':
                continue
            print "\tline: ", line
            if not self.valid(line):
                raise Exception("{1}, invalid vm statement in line {0}".format(i+1, vmf))
            vm_commands.append(line)
        return vm_commands

    def valid(self, line):
        return True

    def compile(self):
        if self.WI:
            self.codewriter.writeInit()
        for parser in self.parser:
            self.codewriter.f.write("\n//" + parser.vmf + "\n")
            while parser.hasMoreCommands():
                vm_com = parser.advance()
                comtype = parser.commandType(vm_com)
                # print vm_com, comtype

                if comtype in ["C_PUSH", "C_POP"]:
                    seg   = parser.arg1(vm_com, comtype)
                    index = parser.arg2(vm_com, comtype)
                    self.codewriter.writePushPop(comtype, seg, index)
                    
                elif comtype == "C_ARITHMETIC":
                    self.codewriter.writeArithmetic(vm_com)
                    
                elif comtype == "C_LABEL":
                    label = parser.arg1(vm_com, comtype)
                    self.codewriter.writeLabel(label)
                    
                elif comtype == "C_IF":
                    label = parser.arg1(vm_com, comtype)
                    self.codewriter.writeIf(label)
                    
                elif comtype == "C_GOTO":
                    label = parser.arg1(vm_com, comtype)
                    self.codewriter.writeGoto(label)

                elif comtype == "C_FUNCTION":
                    funcname = parser.arg1(vm_com, comtype)
                    nLocals = parser.arg2(vm_com, comtype)
                    self.codewriter.writeFunction(funcname, nLocals)

                elif comtype == "C_CALL":
                    funcname = parser.arg1(vm_com, comtype)
                    nArgs = parser.arg2(vm_com, comtype)
                    self.codewriter.writeCall1(funcname, nArgs)

                elif comtype == "C_RETURN":
                    self.codewriter.writeReturn()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="none")
    parser.add_argument("prodir", action="store")
    parser.add_argument('-I', action="store_true")
    args = parser.parse_args() #通常
    print args
    backend = BackEndProject8(args.prodir, args.I)
    backend.compile()

#python BackEndProject8.py FunctionCalls\FibonacciElement -I
#python BackEndProject8.py FunctionCalls\NestedCall -I
#python BackEndProject8.py FunctionCalls\SimpleFunction
#python BackEndProject8.py FunctionCalls\StaticTest -I

#python BackEndProject8.py ProgramFlow\BasicLoop
#python BackEndProject8.py ProgramFlow\FibonacciSeries

#python BackEndProject8.py ..\07\MemoryAccess\BasicTest
#python BackEndProject8.py ..\07\MemoryAccess\PointerTest
#python BackEndProject8.py ..\07\MemoryAccess\StaticTest

#python BackEndProject8.py ..\07\StackArithmetic\SimpleAdd
#python BackEndProject8.py ..\07\StackArighmetic\StackTest