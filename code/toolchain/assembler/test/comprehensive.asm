; Aurora v1.2 assembler comprehensive test
; Exercises every major instruction format

.equ  STACK_TOP, 0x1000

.org 0x0000

; ----- ALU register-register -----
    ADD   R0, R0, R1          ; R0 = R0 + R1
    SUB   R2, R2, R3          ; R2 = R2 - R3
    AND   R4, R4, R5          ; R4 = R4 & R5
    OR    R6, R6, R7          ; R6 = R6 | R7
    XOR   R8, R8, R9          ; R8 = R8 ^ R9
    CMP   R0, R0, R1          ; flags = R0 - R1
    MIN   R0, R0, R1          ; R0 = min(R0,R1)
    MAX   R0, R0, R1          ; R0 = max(R0,R1)

; ----- ALU immediate -----
    ADDI  R0, 5               ; R0 += 5
    SUBI  R1, 3               ; R1 -= 3
    ANDI  R2, 0xF             ; R2 &= 0xF
    ORI   R3, 1               ; R3 |= 1
    XORI  R4, 7               ; R4 ^= 7
    CMPI  R0, 0               ; compare R0 with 0
    LI    R5, 0x100           ; load wider immediate (uses EXT)

; ----- Shifts -----
    LSL   R0, 4               ; R0 <<= 4
    LSR   R1, 2               ; R1 >>= 2 (logical)
    ASR   R2, 1               ; R2 >>= 1 (arithmetic)
    ROL   R3, 8               ; R3 rol 8
    ROR   R3, 8               ; R3 ror 8

; ----- Multiply / Divide -----
    MUL   R0, R0, R1
    MULH  R2, R2, R3
    DIV   R4, R4, R5

; ----- Pack / Shuffle / Extend -----
    MOV   R0, R1
    BSWAP R2, R3
    ZEXT8 R4, R5
    SEXT16 R6, R7

; ----- Load / Store -----
    LI    SP, STACK_TOP       ; set SP = 0x1000 (uses EXT)
    ST    R0, [SP]            ; store R0 at [SP+0]
    LD    R1, [SP]            ; load R1 from [SP+0]

; ----- Branches -----
    B.EQ  target_eq
    B.NE  target_eq
    B.LT  target_eq
    B.GE  target_eq
    B.LTU target_eq
    B.GEU target_eq
    B.MI  target_eq
    B.PL  target_eq

target_eq:
    NOP

; ----- Control flow -----
    CALL  sub_routine
    JMP   after_sub

sub_routine:
    NOP
    RET

after_sub:
    JMPR  R13                 ; indirect jump via LR

; ----- Stack -----
    PUSH  R0
    POP   R1
    PUSHM 0x00FF              ; push R0-R7
    POPM  0x00FF              ; pop R0-R7

; ----- System -----
    EI
    DI
    WFI
    WFE
    HALT

; ----- Mode switch -----
    MODE  PACKED16
    MODE  SCALAR32
