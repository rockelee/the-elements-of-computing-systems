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
        self.f = open(asmfile, 'w')

        self.num_gt = 0
        self.num_eq = 0
        self.num_lt = 0
        self.hasWriteGT = [False]
        self.hasWriteEQ = [False]
        self.hasWriteLT = [False]

        self.return_id = 0
        self.call_id = 0
        self.hasWriteCall = False
        self.hasWriteReturn = False
        self.current_funcname = ''

    def setFileName(self):
        pass

    def close(self):
        self.f.close()

    def writeArithmetic(self, vm_com):
        if   vm_com == 'add': self._add()
        elif vm_com == 'sub': self._sub()
        elif vm_com == 'and': self._and()
        elif vm_com == 'or' : self._or()
        elif vm_com == 'neg': self._neg()
        elif vm_com == 'not': self._not()
        elif vm_com in ['gt', 'eq', 'lt']: 
            self._relation_compare(vm_com)

    def writePushPop(self, comtype, seg, index):
        if comtype == "C_PUSH":
            if seg == "constant":                     self._push_constant(index)
            elif seg == "static":                     self._push_static(index)
            elif seg in dict(self.SEG1, **self.SEG2): self._push_seg(seg, index)
        
        elif comtype == "C_POP":
            if seg == "static":                       self._pop_static(index)
            elif seg in dict(self.SEG1, **self.SEG2): self._pop_seg(seg, index)

    def writeInit(self):
        self.f.write("@256\n" +
                     "D=A \n" +
                     "@SP \n" +
                     "M=D \n")
        self.writeCall1("Sys.init", 0) # call Sys.init 0

    def writeLabel(self, label):
        self.f.write("({0})\n".format(self.current_funcname + '$' + label))

    def writeGoto(self, label):
        self.f.write("@{0} \n".format(self.current_funcname + '$' + label) +
                     "0;JMP\n")

    def writeIf(self, label):
        self.f.write("@SP   \n" +
                     "AM=M-1\n" +
                     "D=M   \n" +
                     "@{0}  \n".format(self.current_funcname + '$' + label) +
                     "D;JNE \n")

    def writeFunction(self, funcname, nLocals):
        self.f.write("//writeFunction {0}\n".format(funcname))
        self.f.write(("({0})\n" +
                      "@{1} \n" +
                      "D=A  \n" +
                      "@R13 \n" +
                      "M=D  \n" +

                      "({0}_push_local)\n" +
                      "@R13    \n" +
                      "D=M     \n" +
                      "@{0}_push_end\n" +
                      "D;JEQ   \n" +
                      "@0      \n" +
                      "D=A     \n" +
                      "@SP     \n" +
                      "A=M     \n" +
                      "M=D     \n" +
                      "@SP     \n" +
                      "M=M+1   \n" +
                      "@R13    \n" +
                      "M=M-1   \n" +
                      "@{0}_push_local\n" +
                      "0;JMP   \n" +
                      "({0}_push_end)\n").format(funcname, nLocals))
        self.current_funcname = funcname

    def writeCall1(self, funcname, nArgs):
        _call_push_seg_return = funcname + str(self.call_id)
        self._keep_return_address(_call_push_seg_return)

        return_address = "return_address" + str(self.return_id)
        self.f.write(("@{0} \n".format(return_address)) +
                      "D=A  \n")# +
                      # "@SP  \n" +
                      # "A=M  \n" +
                      # "M=D  \n" +
                      # "@SP  \n" +
                      # "M=M+1\n")
        if not self.hasWriteCall:
            self.f.write("(_CALL_PUSH_SEG)\n")
            self.f.write("@SP  \n" +
                         "A=M  \n" +
                         "M=D  \n" +
                         "@SP  \n" +
                         "M=M+1\n")
            self._call_push_seg("LCL")
            self._call_push_seg("ARG")
            self._call_push_seg("THIS")
            self._call_push_seg("THAT")
            self.f.write("@SP  \n" +
                         "D=M  \n" +
                         "@5   \n" +
                         "D=D-A\n")
            self._recover_return_address(_call_push_seg_return)
            self.hasWriteCall = True
        else:
            self.f.write("@_CALL_PUSH_SEG\n" + 
                         "0;JMP\n")
            self.f.write("({0})\n".format(_call_push_seg_return))

        # self.f.write(("@SP  \n" +
        #               "D=M  \n" +
        #               "@5   \n" +
        #               "D=D-A\n" +
        self.f.write(("@{0} \n" +
                      "D=D-A\n" +
                      "@ARG \n" +
                      "M=D  \n" +
                     
                      "@SP \n" +
                      "D=M \n" +
                      "@LCL\n" +
                      "M=D \n" +

                      "@{1} \n" +
                      "0;JMP\n").format(nArgs, funcname))
        self.f.write("({0})\n".format(return_address))  # 每个call后都需要有一个唯一符号来标识返回地址
        self.return_id += 1

    def writeCall(self, funcname, nArgs):
        return_address = "return_address" + str(self.return_id)
        self.f.write("//writeCall\n")
        self.f.write(("@{0} \n" +
                      "D=A  \n" +
                      "@SP  \n" +
                      "A=M  \n" +
                      "M=D  \n" +
                      "@SP  \n" +
                      "M=M+1\n").format(return_address))
        
        self._call_push_seg("LCL")
        self._call_push_seg("ARG")
        self._call_push_seg("THIS")
        self._call_push_seg("THAT")
        
        self.f.write(("@SP  \n" +
                      "D=M  \n" +
                      "@5   \n" +
                      "D=D-A\n" +
                      "@{0} \n" +
                      "D=D-A\n" +
                      "@ARG \n" +
                      "M=D  \n" +
                    
                      "@SP \n" +
                      "D=M \n" +
                      "@LCL\n" +
                      "M=D \n" +

                      "@{1} \n" +
                      "0;JMP\n").format(nArgs, funcname))
        self.f.write("({0})\n".format(return_address))  # 每个call后都需要有一个唯一符号来标识返回地址
        self.return_id += 1

    def _call_push_seg(self, seg):
        self.f.write("@{0} \n".format(seg)+
                     "D=M  \n" +
                     "@SP  \n" +
                     "A=M  \n" +
                     "M=D  \n" +
                     "@SP  \n" +
                     "M=M+1\n")

    def writeReturn(self):
        if not self.hasWriteReturn:
            self.f.write("//writeReturn\n")
            self.f.write("(RETURN)\n")
            self.f.write("@LCL  \n" +
                         "D=M   \n" +
                         "@R13  \n" +
                         "M=D   \n" +

                         "@5    \n" +
                         "A=D-A \n" +
                         "D=M   \n" +
                         "@R14  \n" +
                         "M=D   \n" +

                         "@SP   \n" +
                         "A=M-1 \n" +
                         "D=M   \n" +
                         "@ARG  \n" +
                         "A=M   \n" +
                         "M=D   \n" +

                         "@ARG  \n" +
                         "D=M   \n" +
                         "@SP   \n" +
                         "M=D+1 \n")
        
            self._return_pop_seg("THAT")
            self._return_pop_seg("THIS")
            self._return_pop_seg("ARG")
            self._return_pop_seg("LCL")
        
            self.f.write("@R14  \n" +
                         "A=M   \n" +
                         "0;JMP \n")

            self.hasWriteReturn = True
        else:
            self.f.write("@RETURN\n" +
                         "0;JMP\n")

    def _return_pop_seg(self, seg):
        self.f.write("@R13  \n" +
                     "AM=M-1\n" +
                     "D=M   \n" +
                     "@{0} \n".format(seg) +
                     "M=D   \n")

    def add_num_asm_coms(self, num):
        self.num_asm_coms += num

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

    def _relation_compare(self, relation):
        rel_turn = "{0}_RETURN_{1}".format(relation.upper(), eval("self.num_{0}".format(relation)))
        has_write_rel = eval("self.hasWrite{0}".format(relation.upper()))
        exec("self.num_{0}".format(relation) + " += 1")

        self._keep_return_address(rel_turn)
        if not has_write_rel[0]:
            self.f.write("(_fadff_{0})\n".format(relation.upper()))
            self._common_gt_eq_lt("{0}".format(relation.upper()))
            self._recover_return_address(rel_turn)
            has_write_rel[0] = True
        else:
            self.f.write("@_fadff_{0}\n".format(relation.upper())+
                         "0;JMP\n")
            self.f.write("({0})\n".format(rel_turn))

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

    def _keep_return_address(self, relation_return_address):
        self.f.write("@{0}\n".format(relation_return_address) +
                     "D=A   \n" +
                     "@R13  \n" +
                     "M=D   \n")

    def _recover_return_address(self, relation_return_address):
        self.f.write(("@R13 \n" +
                      "A=M  \n" +
                      "0;JMP\n" +
                      "({0})\n").format(relation_return_address))

    def _common_gt_eq_lt(self, relation):
        self.f.write(("@SP        \n" +
                      "AM=M-1     \n" +
                      "D=M        \n" +
                      "@SP        \n" +
                      "A=M-1      \n" +
                      "D=M-D      \n" +
                      "@TRUE_{0}  \n" +
                      "D;J{0}     \n" +
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
                      "(EXIT_{0}) \n").format(relation))

    def _common_neg_not(self):
        self.f.write("@SP  \n" +
                     "A=M-1\n")

    def _push_constant(self, value):
        self.f.write("@{0}\n".format(value) +
                     "D=A\n")
        self._common_push()

    def _push_static(self, index):
        self.f.write("@{0}\n".format(index) +
                     "D=M \n")
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
                     "@{0}   \n".format(index) +
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