// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

@3
M=1 //R3=1

@2
M=0 //R2=0

(LOOP)
@1
D=M
@3
D=M-D
@END
D;JGT  //if R3-R1 > 0 then goto END

@0
D=M  
@2
M=D+M   // R2+=R0
@3
M=M+1   //R3+=1
@LOOP   
0;JMP  //goto LOOP

(END)

