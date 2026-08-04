# Aurora v1.2 Assembler

A two-pass assembler for the **Aurora v1.2** 16-bit RISC microarchitecture,
written in portable C (C11).

## Building

```sh
cd code/toolchain/assembler
make
```

The binary `aurora_asm` is produced in the current directory.

Requirements: any C11-capable compiler (`gcc`, `clang`, etc.) plus standard
POSIX headers.

---

## Usage

```
aurora_asm [-o outfile] [-f bin|hex|vhex] infile.asm
```

| Option | Description |
|--------|-------------|
| `-o outfile` | Output file path (default: stdout) |
| `-f bin` | Raw little-endian 16-bit binary words **(default)** |
| `-f hex` | Intel HEX (IHEX) format |
| `-f vhex` | Verilog `$readmemh` format — one 4-hex-digit word per line |

### Examples

```sh
# binary output (suitable for simulation / flash)
aurora_asm -o firmware.bin -f bin firmware.asm

# Intel HEX for a programmer
aurora_asm -o firmware.hex -f hex firmware.asm

# Verilog readmemh for RTL testbenches
aurora_asm -o rom.mem -f vhex firmware.asm
```

---

## Assembly Language Syntax

### Comments

```asm
; semicolon to end of line
// double-slash to end of line
```

### Labels

```asm
my_label:
    ADD R0, R0, R1
```

### Directives

| Directive | Description |
|-----------|-------------|
| `.org addr` | Set current address (byte address) |
| `.word v [, v …]` | Emit raw 16-bit words |
| `.byte v [, v …]` | Emit raw bytes (packed in pairs, little-endian) |
| `.equ name, val` | Define a symbol constant |
| `.set name, val` | Alias for `.equ` |

### Registers

| Name | Number | ABI role |
|------|--------|----------|
| R0–R7 | 0–7 | Temporaries / arguments |
| R8, R10 | 8, 10 | Accumulators A0, A1 |
| R11–R12 | 11–12 | Callee-saved |
| R13 / LR | 13 | Link register |
| R14 / SP | 14 | Stack pointer |
| R15 / PC | 15 | Program counter |

### Immediates

| Syntax | Base |
|--------|------|
| `42` | Decimal |
| `0x2A` | Hexadecimal |
| `0b101010` | Binary |
| `0o52` | Octal |
| `my_sym` | Symbolic (resolved at pass 2) |

---

## Instruction Set Reference

### ALU — Register/Register (format RRR)

> **Hardware constraint:** the destination (`Rd`) and first source (`Ra`) occupy
> the same 4-bit field in the 16-bit word (`Rd_Ra`).  
> Therefore `Rd` **must equal** `Ra` in all RRR instructions (the assembler
> will warn if they differ and encodes `Rd`).

```asm
ADD   Rd, Rd, Rb      ; Rd = Rd + Rb
SUB   Rd, Rd, Rb      ; Rd = Rd - Rb
AND   Rd, Rd, Rb      ; Rd = Rd & Rb
OR    Rd, Rd, Rb      ; Rd = Rd | Rb
XOR   Rd, Rd, Rb      ; Rd = Rd ^ Rb
CMP   Rd, Rd, Rb      ; flags = Rd - Rb  (result discarded)
MIN   Rd, Rd, Rb      ; Rd = min(Rd, Rb)
MAX   Rd, Rd, Rb      ; Rd = max(Rd, Rb)
```

### ALU — Immediate (format RRI, primary 0x1)

4-bit signed immediate; a 12-bit EXT word is prepended automatically
when the value exceeds the 4-bit range.

```asm
ADDI  Rd, imm         ; Rd = Rd + imm
SUBI  Rd, imm         ; Rd = Rd - imm
ANDI  Rd, imm         ; Rd = Rd & imm
ORI   Rd, imm         ; Rd = Rd | imm
XORI  Rd, imm         ; Rd = Rd ^ imm
CMPI  Rd, imm         ; flags = Rd - imm
```

### Shift / Rotate (format SHIFT, primary 0x2)

`count` may be a register name or an immediate 0–15.

```asm
LSL   Rd, count       ; logical shift left
LSR   Rd, count       ; logical shift right
ASR   Rd, count       ; arithmetic shift right
ROL   Rd, count       ; rotate left
ROR   Rd, count       ; rotate right
```

### Multiply / Divide (format RRR_OR_ACC, primary 0x3)

```asm
MUL     Rd, Ra, Rb    ; Rd = Ra * Rb  (low 32 bits)
MULH    Rd, Ra, Rb    ; Rd = (Ra * Rb) >> 32  (high bits)
MAC     Rd, Ra, Rb    ; A0 += Ra * Rb
MAS     Rd, Ra, Rb    ; A0 -= Ra * Rb
DIVSTEP Rd, Ra, Rb    ; iterative division step
DIV     Rd, Ra, Rb    ; Rd = Ra / Rb
```

### DSP Reductions (primary 0x4)

```asm
REDUCE.ADD  A0|A1, Rsrc [, fold] [, local]
REDUCE.AND  A0|A1, Rsrc [, fold] [, local]
REDUCE.OR   A0|A1, Rsrc [, fold] [, local]
REDUCE.XOR  A0|A1, Rsrc [, fold] [, local]
REDUCE.MIN  A0|A1, Rsrc [, fold] [, local]
REDUCE.MAX  A0|A1, Rsrc [, fold] [, local]
REDUCE.ABSMAX A0|A1, Rsrc [, fold] [, local]
REDUCE.COUNT  A0|A1, Rsrc [, fold] [, local]

DOT   A0|A1, Rsrc0, Rsrc1   ; dot product (EXT word emitted)
SAD   A0|A1, Rsrc0, Rsrc1   ; sum of absolute differences (EXT word emitted)
```

Optional qualifiers:
- `fold` — fold result into accumulator instead of overwriting
- `local` — use register operand instead of stream

### Pack / Shuffle / Sign-extend (primary 0x5)

```asm
PACK    Rd, Rs        ; pack lanes
UNPACK  Rd, Rs        ; unpack lanes
ZIP     Rd, Rs        ; interleave lanes
UNZIP   Rd, Rs        ; de-interleave lanes
BSWAP   Rd, Rs        ; byte-swap
WSWAP   Rd, Rs        ; half-word swap
SHUFFLE Rd, Rs        ; lane shuffle
MOV     Rd, Rs        ; register copy
ZEXT8   Rd, Rs        ; zero-extend byte
SEXT8   Rd, Rs        ; sign-extend byte
ZEXT16  Rd, Rs        ; zero-extend half-word
SEXT16  Rd, Rs        ; sign-extend half-word
```

### Load / Store (primary 0x6 / 0x7)

```asm
LD   Rd, [Rb]         ; load 32-bit word
LD   Rd, [Rb+offset]  ; load with immediate offset (EXT emitted if offset≠0)
ST   Rs, [Rb]         ; store 32-bit word
ST   Rs, [Rb+offset]  ; store with offset
```

### Conditional Branches (primary 0x8)

Displacement is PC-relative (word units). An EXT word is prepended
automatically when the target is out of the ±128 range.

```asm
B.EQ  target          ; branch if equal (Z=1)
B.NE  target          ; branch if not equal (Z=0)
B.LT  target          ; branch if less-than signed (N≠V)
B.GE  target          ; branch if greater-or-equal signed (N=V)
B.LTU target          ; branch if less-than unsigned (C=0)
B.GEU target          ; branch if greater-or-equal unsigned (C=1)
B.MI  target          ; branch if minus (N=1)
B.PL  target          ; branch if plus (N=0)
```

### Control Flow (primary 0x9)

```asm
CALL  target          ; call subroutine  (LR ← PC+2)
JMP   target          ; unconditional jump (PC-relative)
RET                   ; return  (PC ← LR)
JMPR  Rs              ; indirect jump via register
```

### Stack (primary 0xA)

```asm
PUSH   Rn             ; push single register
POP    Rn             ; pop single register
PUSHM  mask16         ; push register set by 16-bit mask (EXT word emitted)
POPM   mask16         ; pop  register set by 16-bit mask (EXT word emitted)
```

### Stream Queue (primary 0xB)

```asm
QMASK  Q0|Q1, arg     ; set lane mask
QPEEK  Q0|Q1, arg     ; peek at queue head
QPUSH  Q0|Q1, arg     ; push to queue
QPOP   Q0|Q1, arg     ; pop from queue
QDUP   Q0|Q1, arg     ; duplicate head element
QREPL  Q0|Q1, arg     ; replace head element
QCIRC  Q0|Q1, arg     ; circular buffer operation
QCFG   Q0|Q1, field, Rs|imm   ; configure queue field (EXT word emitted)
QSTEP  Q0|Q1          ; advance queue pointer
```

`QCFG` field names: `ADDR`, `INNER_STRIDE`, `INNER_COUNT`, `OUTER_ADJUST`,
`OUTER_COUNT`, `WIDTH`, `END_MODE` (or numeric 0–6).

### Hardware Loop / AGU (primary 0xC)

```asm
LOOPSET  count        ; set loop count
LOOPEND               ; end of hardware loop body
AGUCFG   args         ; configure address generation unit
STRIDE   args         ; set stride
```

### System (primary 0xD)

```asm
MRS     Rd, sysreg    ; read system register into Rd
MSR     sysreg, Rs    ; write Rs to system register
EI                    ; enable interrupts
DI                    ; disable interrupts
IRET                  ; return from interrupt
ASCALL  imm           ; architecture-specific call
TIMERLOAD Rs          ; load timer from Rs
TIMERVEC  Rs          ; set timer vector from Rs
TIMERCTL  imm         ; timer control
RDCYCLE Rd            ; read cycle counter into Rd
MODE    name|num      ; switch execution mode
WFI                   ; wait for interrupt
WFE                   ; wait for event
HALT                  ; halt processor
CTXSAVE    Rbase, mask  ; save context (EXT word emitted)
CTXRESTORE Rbase, mask  ; restore context (EXT word emitted)
```

Mode names: `SCALAR32`, `PACKED16`, `PACKED8`, `LOW16`, `LOW8`, `PAIRED64`.

### Pseudo-instructions

| Mnemonic | Expands to |
|----------|------------|
| `NOP` | `ADDI R0, 0` |
| `LI Rd, imm` | `ADDI Rd, imm` (with EXT word if needed) |
| `MVR Rd, Rs` | `MOV Rd, Rs` |

---

## EXT Word Mechanism

When an immediate or displacement does not fit in the base instruction's
immediate field, the assembler **automatically** prepends an EXT word
(primary opcode `0xE`).  The EXT word carries the upper 12 bits of the
value; the base word retains the lower bits.

You do **not** need to write EXT words manually.

---

## Known ISA Conflicts

The Aurora v1.2 architecture has an unresolved conflict at primary opcode
`0xC` (LOOP_AGU / LOOP_IMM8) — see `isa/database/aurora_v1_2_encoding.json`
for details.  This assembler implements the **canonical ISA database**
layout (`LOOPSET` / `LOOPEND` / `AGUCFG` / `STRIDE`), not the v1.2g
addendum variant.  Update once the conflict is formally resolved.
