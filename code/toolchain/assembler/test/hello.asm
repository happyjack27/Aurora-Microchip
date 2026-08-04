; Aurora v1.2 assembler test program
; Computes the sum of 1+2+..+10 and stores in R0

.org 0x0000

start:
    LI    R0, 0       ; sum = 0
    LI    R1, 1       ; i = 1
    LI    R2, 10      ; limit = 10

loop:
    ADD   R0, R0, R1  ; sum += i (note: Rd must equal Ra)
    ADDI  R1, 1       ; i++
    CMP   R1, R1, R2  ; compare i, limit
    B.LT  loop        ; if i < limit goto loop

done:
    ST    R0, [SP]    ; store result
    HALT
