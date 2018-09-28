# -*- coding: utf-8 -*-

import os

class CodeWriter(object):
    SEG1 = {"local" :   "LCL",
            "argument": "ARG",
            "this":     "THIS",
            "that":     "THAT"}
    SEG2 = {"pointer":  "R3",
            "temp":     "R5"}

    def __init__(self, asmfile):
        self.f = open(asmfile, "w")
        self.num_gt_eq_lt = 0

        asm_name = os.path.basename(asmfile)
        self.static_var_name_pre = asm_name

    def setFileName(self):
        pass

    def writeArithmetic(self, vm_com):
        if   vm_com == 'add': self._add()
        elif vm_com == 'sub': self._sub()
        elif vm_com == 'and': self._and()
        elif vm_com == 'or' : self._or()
        elif vm_com == 'gt' : self._gt()
        elif vm_com == 'eq' : self._eq()
        elif vm_com == 'lt' : self._lt()
        elif vm_com == 'neg': self._neg()
        elif vm_com == 'not': self._not()

    def writePushPop(self, comtype, seg, index):
        if comtype == "C_PUSH":
            if seg == "constant":                     self._push_constant(index)
            elif seg == "static":                     self._push_static(index)
            elif seg in dict(self.SEG1, **self.SEG2): self._push_seg(seg, index)
        
        elif comtype == "C_POP":
            if seg == "static":                       self._pop_static(index)
            elif seg in dict(self.SEG1, **self.SEG2): self._pop_seg(seg, index)

    def close(self):
        self.f.close()

    def _add(self):
        self._common_add_sub_and_or()
        self.f.write("M=D+M\n")

    def _sub(self):
        self._common_add_sub_and_or()
        self.f.write("M=M-D\n")

    def _and(self):
        self._common_add_sub_and_or()
        self.f.write("M=D&M\n")

    def _or(self):
        self._common_add_sub_and_or()
        self.f.write("M=D|M\n")

    def _gt(self):
        self._common_gt_eq_lt('GT')

    def _eq(self):
        self._common_gt_eq_lt('EQ')

    def _lt(self):
        self._common_gt_eq_lt('LT')

    def _neg(self):
        self._common_neg_not()
        self.f.write("M=-M\n")

    def _not(self):
        self._common_neg_not()
        self.f.write("M=!M\n")

    def _common_add_sub_and_or(self):
        self.f.write("@SP   \n" +
                     "AM=M-1\n" +
                     "D=M   \n" +
                     "@SP   \n" +
                     "A=M-1 \n")

    def _common_gt_eq_lt(self, relation):
        self.f.write(("@SP        \n" +
                      "AM=M-1     \n" +
                      "D=M        \n" +
                      "@SP        \n" +
                      "A=M-1      \n" +
                      "D=M-D      \n" +
                      "@TRUE_{0}  \n" +
                      "D;J{1}     \n" +
                      "(FALSE_{0})\n" +
                      "@SP        \n" +
                      "A=M-1      \n" +
                      "M=0        \n" +
                      "@EXIT_{0}  \n" +
                      "0;JMP      \n" +
                      "(TRUE_{0}) \n" +
                      "@SP        \n" +
                      "A=M-1      \n" +
                      "M=-1       \n" +
                      "(EXIT_{0}) \n").format(str(relation) + str(self.num_gt_eq_lt), relation))
        self.num_gt_eq_lt += 1

    def _common_neg_not(self):
        self.f.write("@SP  \n" +
                     "A=M-1\n")

    def _push_constant(self, value):
        self.f.write("@{0}\n".format(value) +
                     "D=A\n")
        self._common_push()

    def _push_static(self, index):
        self.f.write("@{0}\n".format(self.static_var_name_pre + str(index)) +
                     "D=M\n")
        self._common_push()

    def _common_push(self):
        self.f.write("@SP   \n" +
                     "A=M   \n" +
                     "M=D   \n" +
                     "@SP   \n" +
                     "M=M+1 \n")

    def _push_seg(self, seg, index):
        if   seg in self.SEG1: self.f.write("@{0}\n".format(self.SEG1[seg]) + "D=M\n")
        elif seg in self.SEG2: self.f.write("@{0}\n".format(self.SEG2[seg]) + "D=A\n")
        self._common_push_seg(index)

    def _common_push_seg(self, index):
        self.f.write("@{0}\n".format(index) +
                     "A=D+A\n" +
                     "D=M  \n" +
                     "@SP  \n" +
                     "A=M  \n" +
                     "M=D  \n" +
                     "@SP  \n" +
                     "M=M+1\n")

    def _pop_static(self, index):
        self.f.write("@SP    \n" + 
                     "AM=M-1 \n" +
                     "D=M    \n" +
                     "@{0}   \n".format(self.static_var_name_pre + str(index)) +
                     "M=D    \n")

    def _pop_seg(self, seg, index):
        if   seg in self.SEG1: self.f.write("@{0}\n".format(self.SEG1[seg]) + "D=M\n")
        elif seg in self.SEG2: self.f.write("@{0}\n".format(self.SEG2[seg]) + "D=A\n")
        self._common_pop_seg(index)

    def _common_pop_seg(self, index):
        self.f.write("@{0}  \n".format(index) +
                     "D=D+A \n" +
                     "@R13  \n" +
                     "M=D   \n" +
                     "@SP   \n" +
                     "AM=M-1\n" +
                     "D=M   \n" +
                     "@R13  \n" +
                     "A=M   \n" +
                     "M=D   \n")