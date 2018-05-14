inp
push
push IP+2
call FAC
out
halt
FAC proc
    load SP-2
    sub 1
    j0 END
    push
    push IP+2
    call FAC
    mul SP-2
    ret 2
END:
    add 1
    ret 0
FAC endp