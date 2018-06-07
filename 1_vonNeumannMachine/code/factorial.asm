.stack
    size = 30
.program
    out 0x0
    inp 0x1
    j0 0x1 ERROR
    push 0x1
    push IP+3
    push SP-1
    call FAC
    out SP-2        ;there is an answer on current SP-2
    pop 3           ;clear memory
    halt
    FAC proc
        push SP         ;local var for n-1
        sub SP 1
        j0 SP END       ;jump if 0
        push            ;return value
        push IP+3       ;return address
        push SP-2       ;argument
        call FAC
        mov SP-3 SP-2   ;copy answer to local variable
        pop 3           ;clear previous frame
        mul SP SP-1     ;mul local var with arg
        mov SP-3 SP     ;copy local var to place for return value
        pop 1           ;clear local variable
        jump SP-1
    END:
        pop 1           ;n-1 == 0 in this case
        mov SP-2 SP    ;copy to the return value place
        jump SP-1       ;jum to the ret addr
    FAC endp
    ERROR:
        halt
.data
    msg  Hello, I calculate a factorial of a given number. If you wanna try, please enter the number:
    ax 0