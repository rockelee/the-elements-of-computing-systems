// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

@24575
D=A
@screenend  //16
M=D

(KEYPRESSED)
    @KBD
    D=M
    @NOTKEYPRESSED
    D;JEQ

    @SCREEN
    D=A
    @SCREENINDEX  //17
    M=D 

    // color screen black
    (BLACK)
        @SCREENINDEX
        A=M
        M=-1
        @SCREENINDEX
        M=M+1
    @SCREENINDEX
    D=M
    @screenend
    D=M-D
    @BLACK
    D;JGE

@KEYPRESSED
0;JMP

(NOTKEYPRESSED)
    @KBD
    D=M
    @KEYPRESSED
    D;JNE

    @SCREEN
    D=A
    @SCREENINDEX
    M=D

    // color screen white
    (WHITE)
        @SCREENINDEX
        A=M
        M=0
        @SCREENINDEX
        M=M+1
    @SCREENINDEX
    D=M
    @screenend
    D=M-D
    @WHITE
    D;JGE

@NOTKEYPRESSED
0;JMP