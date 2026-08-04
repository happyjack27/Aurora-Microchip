# Processor

16-bit instruction encoding; native 32-bit architecture; dual-issue in-order; deterministic interrupts.

# Registers

- R0-R15 general registers

- R13 Link Register

- R14 Stack Pointer

- R15 Program Counter

- A0/A1 accumulators

- Q0/Q1 stream engines

- PSR status register

# Pipeline

- IF

- ID/RR

- EX/MEM

- WB/RET

# Instruction Formats

- 16-bit base instruction

- Extension words for larger immediates

# Opcode Families

- Arithmetic

- Logic

- Shift/Rotate

- Load/Store

- Branch

- Packed DSP

- Stream

- System

# Calling Convention

- Arguments: R0-R3

- LR: R13

- SP: R14

- PC: R15

# Interrupts

- 16 priority levels

- Single programmable countdown timer

- Precise exceptions

# Memory

- Unified address space

- Optional ITCM/DTCM

- Banked SRAM

- DMA
