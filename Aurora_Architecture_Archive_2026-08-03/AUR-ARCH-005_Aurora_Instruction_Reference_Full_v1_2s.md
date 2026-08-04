AUR-ARCH-005 — Aurora Instruction Reference Manual

Full Bytecode & Instruction-Space Edition v1.2d • Aurora Architecture v1.2c

This consolidated edition retains the complete encoded instruction inventory, operand-format diagrams, machine-code examples, MODE instruction, and two-dimensional stream configuration, and adds a visual instruction-space overview near the front of the manual.

# 1. How Aurora Instructions Are Encoded

Every base instruction is one 16-bit little-endian word. Bits 15:12 select one of sixteen primary opcode families. For most families, bits 11:8 select the operation within the family. Bits 7:0 hold registers, immediates, conditions, or format control. A word beginning with primary opcode 0xE is an extension word attached to the preceding base instruction; it is never an independently executed instruction.

<table>
<caption><p>Generic base instruction</p></caption>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>15:12</strong></th>
<th style="text-align: center;"><strong>11:8</strong></th>
<th style="text-align: center;"><strong>7:0</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;"><strong>PRIMARY<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>SUBOP<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>OPERAND / FORMAT<br />
(8 bits)</strong></td>
</tr>
</tbody>
</table>

The compact opcode key shown throughout this manual is PRIMARY:SUBOP. For example, ADD has key 0x00 and DIVSTEP has key 0x34. The complete 16-bit bytecode additionally includes the operand bits.

# 2. Primary Opcode Map

| **Hex** | **Binary** |   **Family**    |               **Purpose**                |
|:-------:|:----------:|:---------------:|:----------------------------------------:|
|   0x0   |    0000    |     ALU_REG     |  Register arithmetic, logic and compare  |
|   0x1   |    0001    |     ALU_IMM     |      Immediate arithmetic and logic      |
|   0x2   |    0010    |  SHIFT_ROTATE   |             Shift and rotate             |
|   0x3   |    0011    |     MULDIV      |      Multiply, MAC/MAS and DIVSTEP       |
|   0x4   |    0100    |   DSP_REDUCE    |         Reductions, DOT and SAD          |
|   0x5   |    0101    |  PACK_SHUFFLE   |       Layout, packing and movement       |
|   0x6   |    0110    |      LOAD       |                  Loads                   |
|   0x7   |    0111    |      STORE      |                  Stores                  |
|   0x8   |    1000    |   BRANCH_COND   |           Conditional branches           |
|   0x9   |    1001    |  CONTROL_FLOW   |          Call, jump and return           |
|   0xA   |    1010    |      STACK      |       Push/pop and register masks        |
|   0xB   |    1011    |     STREAM      |      Q0/Q1 stream and queue control      |
|   0xC   |    1100    |    LOOP_AGU     |       Loops and address generation       |
|   0xD   |    1101    |     SYSTEM      |   System, interrupt and ASC operations   |
|   0xE   |    1110    |    EXTENSION    | Extension word for preceding instruction |
|   0xF   |    1111    | CUSTOM_RESERVED |          Reserved/custom space           |

# 2A. Primary Opcode Map — Category View

<table style="width:82%;">
<colgroup>
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
</colgroup>
<thead>
<tr>
<th>0x0<br />
Arithmetic</th>
<th>0x1<br />
Logic</th>
<th>0x2<br />
Shift/<br />
Rotate</th>
<th>0x3<br />
Multiply/<br />
Reduction</th>
</tr>
</thead>
<tbody>
<tr>
<td>0x4<br />
Load</td>
<td>0x5<br />
Store</td>
<td>0x6<br />
Branch/<br />
Control</td>
<td>0x7<br />
Compare</td>
</tr>
<tr>
<td>0x8<br />
Packed DSP</td>
<td>0x9<br />
SIMD /<br />
Packed</td>
<td>0xA<br />
Streams</td>
<td>0xB<br />
System</td>
</tr>
<tr>
<td>0xC<br />
Control /<br />
Special</td>
<td>0xD<br />
Mode</td>
<td>0xE<br />
Extensions</td>
<td>0xF<br />
Reserved</td>
</tr>
</tbody>
</table>

# 2B. Opcode Space Allocation by Category

Approximate emphasis of the Aurora ISA. Final percentages track the frozen opcode database.

| Instruction Family | Relative Allocation |
|--------------------|---------------------|
| Integer Arithmetic | Largest             |
| Load / Store       | Large               |
| Packed DSP         | Large               |
| Logic              | Medium              |
| Branch / Control   | Medium              |
| Streams            | Medium              |
| System             | Small               |
| Reserved / Future  | Remaining           |

# 2C. Decoder Organization

Instruction Word\
│\
▼\
Primary Opcode\
│\
┌──────┼──────┐\
▼ ▼ ▼\
Arithmetic Logic Memory\
│\
Sub-opcode\
│\
ADD SUB CMP ...

# 2D. Instruction Family Index

| Family | Primary Opcode | Functional Unit | Pipeline | Reference Chapter |
|----|----|----|----|----|
| Arithmetic | 0x0 | Integer ALU | EX/MEM | 5 |
| Logic | 0x1 | Integer ALU | EX/MEM | 6 |
| Shift/Rotate | 0x2 | Shifter | EX/MEM | 7 |
| Multiply/Reduction | 0x3 | Shared Arithmetic | EX/MEM | 8 |
| Load/Store | 0x4-0x5 | LSU | EX/MEM | 9 |
| Branch | 0x6 | Branch Unit | EX/MEM | 10 |
| Streams | 0xA | Stream Engine | EX/MEM | 11 |
| System | 0xB-0xD | Control | WB/RET | 12 |

# 2E. ISA Expansion Policy

- Reserved opcode regions remain unused until approved through an Architecture Decision Record.

- Instruction families are kept contiguous where practical to simplify decoder logic.

- Documentation reflects the canonical frozen ISA database.

# 3. Operand Format Diagrams

## RRR — three-register operation

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>15:12</strong></th>
<th style="text-align: center;"><strong>11:8</strong></th>
<th style="text-align: center;"><strong>7:4</strong></th>
<th style="text-align: center;"><strong>3:0</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;"><strong>PRIMARY<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>SUBOP<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>Rd / Ra<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>Rb<br />
(4 bits)</strong></td>
</tr>
</tbody>
</table>

Used by compact two-address arithmetic: the destination field also supplies source A where the format requires it.

## RRI — register plus immediate

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>15:12</strong></th>
<th style="text-align: center;"><strong>11:8</strong></th>
<th style="text-align: center;"><strong>7:4</strong></th>
<th style="text-align: center;"><strong>3:0</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;"><strong>PRIMARY<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>SUBOP<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>Rd / Ra<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>IMM4<br />
(4 bits)</strong></td>
</tr>
</tbody>
</table>

Long immediates attach an 0xE extension word.

## SHIFT — shift/rotate

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>15:12</strong></th>
<th style="text-align: center;"><strong>11:8</strong></th>
<th style="text-align: center;"><strong>7:4</strong></th>
<th style="text-align: center;"><strong>3:0</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;"><strong>PRIMARY<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>SUBOP<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>Rd / Ra<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>COUNT / Rs<br />
(4 bits)</strong></td>
</tr>
</tbody>
</table>

The low field selects an immediate count or count register according to the form.

## MEM — load/store

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>15:12</strong></th>
<th style="text-align: center;"><strong>11:8</strong></th>
<th style="text-align: center;"><strong>7:4</strong></th>
<th style="text-align: center;"><strong>3:0</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;"><strong>PRIMARY<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>MODE / WIDTH<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>Rd / Rs<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>BASE / OFF<br />
(4 bits)</strong></td>
</tr>
</tbody>
</table>

Additional displacement bits may be supplied by an extension word.

## BR — conditional branch

<table>
<colgroup>
<col style="width: 33%" />
<col style="width: 33%" />
<col style="width: 33%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>15:12</strong></th>
<th style="text-align: center;"><strong>11:8</strong></th>
<th style="text-align: center;"><strong>7:0</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;"><strong>PRIMARY<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>COND<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>DISP8<br />
(8 bits)</strong></td>
</tr>
</tbody>
</table>

The signed displacement is PC-relative; backward displacements are predicted taken.

## STREAM / SYSTEM

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>15:12</strong></th>
<th style="text-align: center;"><strong>11:8</strong></th>
<th style="text-align: center;"><strong>7:6</strong></th>
<th style="text-align: center;"><strong>5:0</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;"><strong>PRIMARY<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>SUBOP<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>SELECT<br />
(2 bits)</strong></td>
<td style="text-align: center;"><strong>CONTROL / ARG<br />
(6 bits)</strong></td>
</tr>
</tbody>
</table>

Exact low-field interpretation is instruction-specific.

# 4. Complete Encoded Instruction Inventory

The table lists every encoded instruction currently present in the frozen v1.2 ISA inventory. “Opcode key” combines the four-bit primary opcode and four-bit subopcode. Operand bits are format-dependent. DIV does not appear because it expands to DIVSTEP instructions or an ASC/runtime helper.

## 0x0 — ALU_REG

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **ADD** | 0x00 | 0000 0000 | RRR | Rd, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | Rd = Ra + Rb |
| **SUB** | 0x01 | 0000 0001 | RRR | Rd, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | Rd = Ra - Rb |
| **AND** | 0x02 | 0000 0010 | RRR | Rd, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | Rd = Ra & Rb |
| **OR** | 0x03 | 0000 0011 | RRR | Rd, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | Rd = Ra \| Rb |
| **XOR** | 0x04 | 0000 0100 | RRR | Rd, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | Rd = Ra ^ Rb |
| **CMP** | 0x05 | 0000 0101 | RRR | Rd, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | flags = Ra - Rb |
| **MIN** | 0x06 | 0000 0110 | RRR | Rd, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | Rd = min(Ra,Rb) |
| **MAX** | 0x07 | 0000 0111 | RRR | Rd, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | Rd = max(Ra,Rb) |

## 0x1 — ALU_IMM

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **ADDI** | 0x10 | 0001 0000 | RRI | Rd/Ra, imm | SCALAR32 / LOW16 / LOW8 | 1 | ADD with immediate |
| **SUBI** | 0x11 | 0001 0001 | RRI | Rd/Ra, imm | SCALAR32 / LOW16 / LOW8 | 1 | SUB with immediate |
| **ANDI** | 0x12 | 0001 0010 | RRI | Rd/Ra, imm | SCALAR32 / LOW16 / LOW8 | 1 | AND with immediate |
| **ORI** | 0x13 | 0001 0011 | RRI | Rd/Ra, imm | SCALAR32 / LOW16 / LOW8 | 1 | OR with immediate |
| **XORI** | 0x14 | 0001 0100 | RRI | Rd/Ra, imm | SCALAR32 / LOW16 / LOW8 | 1 | XOR with immediate |
| **CMPI** | 0x15 | 0001 0101 | RRI | Rd/Ra, imm | SCALAR32 / LOW16 / LOW8 | 1 | CMP with immediate |

## 0x2 — SHIFT_ROTATE

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **LSL** | 0x20 | 0010 0000 | SHIFT | Rd/Ra, count | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 2 | LSL by immediate or register count |
| **LSR** | 0x21 | 0010 0001 | SHIFT | Rd/Ra, count | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 2 | LSR by immediate or register count |
| **ASR** | 0x22 | 0010 0010 | SHIFT | Rd/Ra, count | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 2 | ASR by immediate or register count |
| **ROL** | 0x23 | 0010 0011 | SHIFT | Rd/Ra, count | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 2 | ROL by immediate or register count |
| **ROR** | 0x24 | 0010 0100 | SHIFT | Rd/Ra, count | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 2 | ROR by immediate or register count |

## 0x3 — MULDIV

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **MUL** | 0x30 | 0011 0000 | RRR_OR_ACC | dst, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / PAIRED64 | 3 | full-width product |
| **MULH** | 0x31 | 0011 0001 | RRR_OR_ACC | dst, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / SCALAR32 | 3 | high half of product |
| **MAC** | 0x32 | 0011 0010 | RRR_OR_ACC | dst, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / SCALAR32 | 3 | A = A + Ra\*Rb |
| **MAS** | 0x33 | 0011 0011 | RRR_OR_ACC | dst, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / SCALAR32 | 3 | A = A - Ra\*Rb |
| **DIVSTEP** | 0x34 | 0011 0100 | RRR_OR_ACC | dst, Ra, Rb | SCALAR32 / PACKED16 / PACKED8 / SCALAR32 | 1 | one radix divide step |

## 0x4 — DSP_REDUCE

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **REDUCE.ADD** | 0x40 | 0100 0000 | DSP_RED | A0/A1, src, overwrite/fold, consume/local | PACKED16 / PACKED8 | 2 | Reduce active lanes with ADD; fold form combines with accumulator using operator-specific rule |
| **REDUCE.AND** | 0x41 | 0100 0001 | DSP_RED | A0/A1, src, overwrite/fold, consume/local | PACKED16 / PACKED8 | 2 | Reduce active lanes with AND; fold form combines with accumulator using operator-specific rule |
| **REDUCE.OR** | 0x42 | 0100 0010 | DSP_RED | A0/A1, src, overwrite/fold, consume/local | PACKED16 / PACKED8 | 2 | Reduce active lanes with OR; fold form combines with accumulator using operator-specific rule |
| **REDUCE.XOR** | 0x43 | 0100 0011 | DSP_RED | A0/A1, src, overwrite/fold, consume/local | PACKED16 / PACKED8 | 2 | Reduce active lanes with XOR; fold form combines with accumulator using operator-specific rule |
| **REDUCE.MIN** | 0x44 | 0100 0100 | DSP_RED | A0/A1, src, overwrite/fold, consume/local | PACKED16 / PACKED8 | 2 | Reduce active lanes with MIN; fold form combines with accumulator using operator-specific rule |
| **REDUCE.MAX** | 0x45 | 0100 0101 | DSP_RED | A0/A1, src, overwrite/fold, consume/local | PACKED16 / PACKED8 | 2 | Reduce active lanes with MAX; fold form combines with accumulator using operator-specific rule |
| **REDUCE.ABSMAX** | 0x46 | 0100 0110 | DSP_RED | A0/A1, src, overwrite/fold, consume/local | PACKED16 / PACKED8 | 2 | Reduce active lanes with ABSMAX; fold form combines with accumulator using operator-specific rule |
| **REDUCE.COUNT** | 0x47 | 0100 0111 | DSP_RED | A0/A1, src, overwrite/fold, consume/local | PACKED16 / PACKED8 | 2 | Reduce active lanes with COUNT; fold form combines with accumulator using operator-specific rule |
| **DOT** | 0x48 | 0100 1000 | DSP_DOT | A0/A1, src0, src1, overwrite/fold, consume/local | PACKED16 / PACKED8 | 3 | Sum lane products into selected accumulator |
| **SAD** | 0x49 | 0100 1001 | DSP_SAD | A0/A1, src0, src1, overwrite/fold, consume/local | PACKED16 / PACKED8 | 3 | Sum absolute lane differences into selected accumulator |

## 0x5 — PACK_SHUFFLE

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **PACK** | 0x50 | 0101 0000 | RR_OR_UNARY | Rd, Rs/Ra, Rb? | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | PACK register layout operation |
| **UNPACK** | 0x51 | 0101 0001 | RR_OR_UNARY | Rd, Rs/Ra, Rb? | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | UNPACK register layout operation |
| **ZIP** | 0x52 | 0101 0010 | RR_OR_UNARY | Rd, Rs/Ra, Rb? | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | ZIP register layout operation |
| **UNZIP** | 0x53 | 0101 0011 | RR_OR_UNARY | Rd, Rs/Ra, Rb? | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | UNZIP register layout operation |
| **BSWAP** | 0x54 | 0101 0100 | RR_OR_UNARY | Rd, Rs/Ra, Rb? | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | BSWAP register layout operation |
| **WSWAP** | 0x55 | 0101 0101 | RR_OR_UNARY | Rd, Rs/Ra, Rb? | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | WSWAP register layout operation |
| **SHUFFLE** | 0x56 | 0101 0110 | RR_OR_UNARY | Rd, Rs/Ra, Rb? | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | SHUFFLE register layout operation |
| **MOV** | 0x57 | 0101 0111 | RR_OR_UNARY | Rd, Rs/Ra, Rb? | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | MOV register layout operation |

## 0x6 — LOAD

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **LD** | 0x60 | 0110 0000 | MEM | Rd, \[base+offset\] | SCALAR32 / LOW16 / LOW8 / PAIRED64 | 2 | Load scalar or pair according to mode |

## 0x7 — STORE

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **ST** | 0x70 | 0111 0000 | MEM | Rs, \[base+offset\] | SCALAR32 / LOW16 / LOW8 / PAIRED64 | 1 | Store scalar or pair according to mode |

## 0x8 — BRANCH_COND

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **B.EQ** | 0x80 | 1000 0000 | BR | target | SCALAR32 | 1 | Conditional branch EQ |
| **B.NE** | 0x81 | 1000 0001 | BR | target | SCALAR32 | 1 | Conditional branch NE |
| **B.LT** | 0x82 | 1000 0010 | BR | target | SCALAR32 | 1 | Conditional branch LT |
| **B.GE** | 0x83 | 1000 0011 | BR | target | SCALAR32 | 1 | Conditional branch GE |
| **B.LTU** | 0x84 | 1000 0100 | BR | target | SCALAR32 | 1 | Conditional branch LTU |
| **B.GEU** | 0x85 | 1000 0101 | BR | target | SCALAR32 | 1 | Conditional branch GEU |
| **B.MI** | 0x86 | 1000 0110 | BR | target | SCALAR32 | 1 | Conditional branch MI |
| **B.PL** | 0x87 | 1000 0111 | BR | target | SCALAR32 | 1 | Conditional branch PL |

## 0x9 — CONTROL_FLOW

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **CALL** | 0x90 | 1001 0000 | CTRL | target/reg | SCALAR32 | 1 | R13 = return address; PC = target |
| **JMP** | 0x91 | 1001 0001 | CTRL | target/reg | SCALAR32 | 1 | PC = target |
| **RET** | 0x92 | 1001 0010 | CTRL | target/reg | SCALAR32 | 1 | PC = R13 |
| **JMPR** | 0x93 | 1001 0011 | CTRL | target/reg | SCALAR32 | 1 | PC = register |

## 0xA — STACK

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **PUSH** | 0xA0 | 1010 0000 | STACK | reg/mask | SCALAR32 / PAIRED64 | 2 | PUSH using R14 stack pointer |
| **POP** | 0xA1 | 1010 0001 | STACK | reg/mask | SCALAR32 / PAIRED64 | 2 | POP using R14 stack pointer |
| **PUSHM** | 0xA2 | 1010 0010 | STACK | reg/mask | SCALAR32 / PAIRED64 | 2 | PUSHM using R14 stack pointer |
| **POPM** | 0xA3 | 1010 0011 | STACK | reg/mask | SCALAR32 / PAIRED64 | 2 | POPM using R14 stack pointer |

## 0xB — STREAM

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **QMASK** | 0xB0 | 1011 0000 | STREAM | Q0/Q1, args | SCALAR32 / PACKED16 / PACKED8 / PAIRED64 | 1 | QMASK stream/queue operation |
| **QPEEK** | 0xB1 | 1011 0001 | STREAM | Q0/Q1, args | SCALAR32 / PACKED16 / PACKED8 / PAIRED64 | 1 | QPEEK stream/queue operation |
| **QPUSH** | 0xB2 | 1011 0010 | STREAM | Q0/Q1, args | SCALAR32 / PACKED16 / PACKED8 / PAIRED64 | 2 | QPUSH stream/queue operation |
| **QPOP** | 0xB3 | 1011 0011 | STREAM | Q0/Q1, args | SCALAR32 / PACKED16 / PACKED8 / PAIRED64 | 2 | QPOP stream/queue operation |
| **QDUP** | 0xB4 | 1011 0100 | STREAM | Q0/Q1, args | SCALAR32 / PACKED16 / PACKED8 / PAIRED64 | 1 | QDUP stream/queue operation |
| **QREPL** | 0xB5 | 1011 0101 | STREAM | Q0/Q1, args | SCALAR32 / PACKED16 / PACKED8 / PAIRED64 | 1 | QREPL stream/queue operation |
| **QCFG** | 0xB6 | 1011 0110 | STREAM | Q0/Q1, args | SCALAR32 / PACKED16 / PACKED8 / PAIRED64 | 2 | QCFG stream/queue operation |
| **QCIRC** | 0xB7 | 1011 0111 | STREAM | Q0/Q1, args | SCALAR32 / PACKED16 / PACKED8 / PAIRED64 | 2 | QCIRC stream/queue operation |

## 0xC — LOOP_AGU

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **LOOPSET** | 0xC0 | 1100 0000 | LOOP_AGU | args | SCALAR32 | 1 | LOOPSET low-overhead loop or address-generation control |
| **LOOPEND** | 0xC1 | 1100 0001 | LOOP_AGU | args | SCALAR32 | 1 | LOOPEND low-overhead loop or address-generation control |
| **AGUCFG** | 0xC2 | 1100 0010 | LOOP_AGU | args | SCALAR32 | 1 | AGUCFG low-overhead loop or address-generation control |
| **STRIDE** | 0xC3 | 1100 0011 | LOOP_AGU | args | SCALAR32 | 1 | STRIDE low-overhead loop or address-generation control |

## 0xD — SYSTEM

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **MRS** | 0xD0 | 1101 0000 | SYSTEM | args | SCALAR32 | 1 | MRS system operation |
| **MSR** | 0xD1 | 1101 0001 | SYSTEM | args | SCALAR32 | 1 | MSR system operation |
| **EI** | 0xD2 | 1101 0010 | SYSTEM | args | SCALAR32 | 1 | EI system operation |
| **DI** | 0xD3 | 1101 0011 | SYSTEM | args | SCALAR32 | 1 | DI system operation |
| **IRET** | 0xD4 | 1101 0100 | SYSTEM | args | SCALAR32 | 1 | IRET system operation |
| **ASCALL** | 0xD5 | 1101 0101 | SYSTEM | args | SCALAR32 | 1 | ASCALL system operation |
| **TIMERLOAD** | 0xD6 | 1101 0110 | SYSTEM | args | SCALAR32 | 1 | TIMERLOAD system operation |
| **TIMERVEC** | 0xD7 | 1101 0111 | SYSTEM | args | SCALAR32 | 1 | TIMERVEC system operation |
| **TIMERCTL** | 0xD8 | 1101 1000 | SYSTEM | args | SCALAR32 | 1 | TIMERCTL system operation |
| **RDCYCLE** | 0xD9 | 1101 1001 | SYSTEM | args | SCALAR32 | 1 | RDCYCLE system operation |

## 0xE — EXTENSION

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **EXT** | 0xE0 | 1110 0000 | EXT | extension_word | SCALAR32 / PACKED16 / PACKED8 / LOW16 / LOW8 / PAIRED64 | 1 | Extension escape for long immediates, masks, addresses, and system forms |

## 0xF — CUSTOM_RESERVED

| **Mnemonic** | **Opcode key** | **Binary key** | **Format** | **Operands** | **Modes** | **Latency** | **Semantics** |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **CUSTOM** | 0xF0 | 1111 0000 | CUSTOM | implementation_defined | SCALAR32 | 1 | Reserved implementation/profile extension |

# 5. Reading a Complete Bytecode

## Example: ADD R1, R1, R2

ADD uses primary 0x0 and subopcode 0x0. In the compact two-address RRR form, bits 7:4 encode R1 (destination and source A) and bits 3:0 encode R2 (source B).

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>15:12</strong></th>
<th style="text-align: center;"><strong>11:8</strong></th>
<th style="text-align: center;"><strong>7:4</strong></th>
<th style="text-align: center;"><strong>3:0</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;"><strong>0x0 ADD/ALU<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>0x0 ADD<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>R1<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>R2<br />
(4 bits)</strong></td>
</tr>
</tbody>
</table>

Binary: 0000 0000 0001 0010 Hex word: 0x0012 Memory bytes (little endian): 12 00

## Example: DIVSTEP R1, R1, R2

DIVSTEP uses primary 0x3 and subopcode 0x4. It performs one divide iteration using the ordinary register/ALU datapath rather than a dedicated full divider.

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>15:12</strong></th>
<th style="text-align: center;"><strong>11:8</strong></th>
<th style="text-align: center;"><strong>7:4</strong></th>
<th style="text-align: center;"><strong>3:0</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center;"><strong>0x3 MULDIV<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>0x4 DIVSTEP<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>R1<br />
(4 bits)</strong></td>
<td style="text-align: center;"><strong>R2<br />
(4 bits)</strong></td>
</tr>
</tbody>
</table>

Binary: 0011 0100 0001 0010 Hex word: 0x3412 Memory bytes (little endian): 12 34

# 6. Encoding Rules and Caveats

- Opcode assignments are frozen at the primary/subopcode level in the machine-readable ISA database.

- Fields below bit 8 are format-dependent; instruction-specific pages must state their exact interpretation.

- 0xE extension words belong to the preceding base instruction and cannot be branch targets.

- 0xF is reserved for implementation-defined/custom expansion and must trap when unsupported.

- Paired-64 encodings name aligned even/odd pairs; R14 (SP) and R15 (PC) are legal zero-extended sources but not paired destinations.

- Full DIV is not a hardware bytecode. Assemblers may accept DIV as a pseudo-instruction and emit DIVSTEP/runtime sequences.

# 7. Documentation Status

This bytecode edition is suitable for showing the basic ISA organization and encoded inventory. Future instruction-family revisions will add complete per-instruction operand-field diagrams, formal pseudocode, flag corner cases, exceptions, forwarding, and scheduling examples without changing the frozen opcode assignments except through an Architecture Decision Record.

Revision 1.2c Additions: MODE and Two-Dimensional Streams

This section is normative and supersedes any earlier omission or vague stream-configuration wording.

# MODE — Set Arithmetic Mode

Bytecode key: 0xDA (primary 0xD, sub-opcode 0xA).

| Bits  | Field      | Value   | Meaning                                            |
|-------|------------|---------|----------------------------------------------------|
| 15:12 | primary    | 1101    | System/control family                              |
| 11:8  | sub-opcode | 1010    | MODE                                               |
| 7:5   | mode       | 000-101 | SCALAR32, PACKED16, PACKED8, LOW16, LOW8, PAIRED64 |
| 4:0   | reserved   | 00000   | Must be zero                                       |

Syntax: MODE \#mode

Alias: MODECLR is MODE \#SCALAR32.

MODE changes the sticky arithmetic interpretation used by later mode-sensitive instructions. It does not modify GPR contents. Layout operations such as byte/word swaps remain full-register operations regardless of the selected arithmetic mode.

# Two-Dimensional Stream Address Generation

Each stream now supports a nested-loop access pattern equivalent to an inner element loop inside an outer row loop. The two newly added programmable values are OUTER_ADJUST and OUTER_COUNT.

| State        | Meaning                                  | QCFG alias |
|--------------|------------------------------------------|------------|
| ADDRESS      | Current byte address                     | QSETADDR   |
| INNER_STRIDE | Signed byte increment after each element | QSETSTRIDE |
| INNER_COUNT  | Elements per row; reload value           | QSETCOUNT  |
| OUTER_ADJUST | Extra signed byte delta after a row      | QSETROWADJ |
| OUTER_COUNT  | Number of rows / outer iterations        | QSETROWS   |
| WIDTH        | 8, 16, or 32-bit element width           | QSETWIDTH  |
| END_MODE     | Stop, wrap, predicate, or signal         | QSETEND    |

## Address-update pseudocode

on consume:\
address += inner_stride\
inner_remaining -= 1\
if inner_remaining == 0:\
if outer_remaining \> 1:\
address += outer_adjust\
inner_remaining = inner_count_reload\
outer_remaining -= 1\
else:\
perform configured end behavior

OUTER_ADJUST is the extra correction applied after the ordinary final inner stride. Software computes it directly, avoiding a row-width multiplication in the stream engine.

# QCFG — Configure Stream Field

Existing bytecode key: 0xB6. QCFG is now explicitly defined as a field-selecting configuration instruction.

Syntax: QCFG Qn, field, Rs/imm

Assembler aliases improve readability but encode as QCFG: QSETADDR, QSETSTRIDE, QSETCOUNT, QSETROWADJ, QSETROWS, QSETWIDTH, and QSETEND.

## Example: 2D image row walk

QSETADDR Q0, R0 ; first pixel\
QSETSTRIDE Q0, \#1 ; next byte/pixel\
QSETCOUNT Q0, \#320 ; 320 pixels per row\
QSETROWADJ Q0, \#32 ; skip 32 bytes of row padding\
QSETROWS Q0, \#240 ; 240 rows\
QSETWIDTH Q0, \#8

# 8. Revision 1.2d Consolidation Note

Revision 1.2d restores the complete bytecode and format material as the canonical base, incorporates the instruction-space overview pages, and retains the normative v1.2c MODE and two-dimensional stream additions. Earlier showcase-only consolidated files that omitted the encoded inventory are superseded.

# System Architecture Update — Aurora v1.2e

This section incorporates the locked two-level privilege model, IRET semantics, low-power wait/halt instructions, and the context save/restore sequencer.

# Extension and Bounds-Fault Update — Aurora v1.2f

# Hardware Loop Update — Aurora v1.2g

# Pinned Circular Stream Update — Aurora v1.2h

# Complex Multiply Mode Update — Aurora v1.2i

# COMPLEX16 Result-Width Revision — Aurora v1.2j

This revision supersedes the v1.2i four-register exact-result layout for COMPLEX16 MUL. The canonical result is now one aligned 64-bit pair with sticky per-component overflow reporting.

# Multiply Mode-Bit Update — Aurora v1.2k

# Rounding and Saturation Update — Aurora v1.2l

# COMPLEX8 Mode Update — Aurora v1.2m

# DMA and Near-Memory Integration Update — Aurora v1.2o

# Contextual ZR and Packed Predicate Update — Aurora v1.2p

# Explicit Stream Access Update — Aurora v1.2q

# Superseding Stream-Access Rule — Aurora v1.2r

The following correction is normative and supersedes conflicting v1.2q wording.

# Two-Entry Prefetch and Eight-Word Loop Update — Aurora v1.2s

AUR-ARCH-005 Addendum — System Instructions v1.2e

Locked privilege, wait/halt, and context-transfer instructions

# System Opcode Allocation

Primary opcode 0xD contains system and mode instructions. Existing assignments 0xD0-0xDA remain unchanged. The final five sub-opcodes are now allocated as follows.

| Key | Mnemonic | Access | Operands | Summary |
|----|----|----|----|----|
| 0xDB | WFI | User/Supervisor\* | \- | Wait for serviceable interrupt |
| 0xDC | WFE | User/Supervisor\* | \- | Wait for architectural event |
| 0xDD | HALT | Supervisor | \- | Halt until allowed wake/reset/debug |
| 0xDE | CTXSAVE | Supervisor | Rbase, mask | Save selected context |
| 0xDF | CTXRESTORE | Supervisor | Rbase, mask | Restore selected context atomically |

\* Supervisor control may prohibit User-mode WFI/WFE.

# Generic Encoding

15 12 11 8 7 0\
+--------------+--------------+---------------------------+\
\| 1101 \| subop \| instruction-specific bits \|\
+--------------+--------------+---------------------------+\
Primary opcode = 0xD; sub-opcodes B-F select the instructions above.

# WFI — Wait for Interrupt

| Bytecode  | 0xDB                           |
|-----------|--------------------------------|
| Syntax    | WFI                            |
| Privilege | User/Supervisor\*              |
| Class     | Serializing system instruction |

Retire all older instructions and enter a low-power wait state. Resume when an enabled pending interrupt is serviceable. Masked interrupts may become pending without waking the core.

# WFE — Wait for Event

| Bytecode  | 0xDC                           |
|-----------|--------------------------------|
| Syntax    | WFE                            |
| Privilege | User/Supervisor\*              |
| Class     | Serializing system instruction |

Retire all older instructions and enter an event-wait state. Resume on an interrupt or a selected architectural event such as DMA completion, peripheral event, or an explicit event signal.

# HALT — Privileged Halt

| Bytecode  | 0xDD                           |
|-----------|--------------------------------|
| Syntax    | HALT                           |
| Privilege | Supervisor                     |
| Class     | Serializing system instruction |

Stop normal instruction execution. Resume only through reset, debug resume, or a wake source explicitly permitted by system control.

# CTXSAVE — Context Save

| Bytecode  | 0xDE                           |
|-----------|--------------------------------|
| Syntax    | CTXSAVE Rbase, mask            |
| Privilege | Supervisor                     |
| Class     | Serializing system instruction |

At a precise retirement boundary, block normal issue and save the selected state groups through the shared stream-style local-memory path. Architectural Q0/Q1 state is not consumed or overwritten. Maskable interrupts remain pending until completion.

# CTXRESTORE — Context Restore

| Bytecode  | 0xDF                           |
|-----------|--------------------------------|
| Syntax    | CTXRESTORE Rbase, mask         |
| Privilege | Supervisor                     |
| Class     | Serializing system instruction |

At a precise retirement boundary, block normal issue and restore the selected state groups. GPRs and optional extended state are restored first. PSR and resume PC commit last as one architectural transition.

# Context Mask Groups

| Bit | Group | Architectural state |
|----|----|----|
| 0 | VOLATILE_GPR | R0-R7 |
| 1 | NONVOLATILE_GPR | R8-R13 |
| 2 | CONTROL | saved PC and PSR |
| 3 | ACCUMULATORS | A0 and A1, full 40-bit state |
| 4 | STREAM_CONFIG | Q0/Q1 address, strides, 2D counts, row adjustment, width, end mode |
| 5 | STREAM_STAGING | Q0/Q1 staging contents and head/tail/fill state |
| 6 | IMPLEMENTATION_EXT | optional implementation-defined context |
| 7 | FULL | assembler convenience selecting all implemented groups |

AUR-ARCH-005 Addendum — Extension and Bounds Faults v1.2f

# Unary Extension Instructions

| Key | Mnemonic | Syntax | Operation | Flags | Resource |
|----|----|----|----|----|----|
| 0x58 | ZEXT8 | ZEXT8 Rd, Rs | Rd = zero_extend(Rs\[7:0\], 32) | Z,N | layout/pass-through |
| 0x59 | SEXT8 | SEXT8 Rd, Rs | Rd = sign_extend(Rs\[7:0\], 32) | Z,N | layout/pass-through |
| 0x5A | ZEXT16 | ZEXT16 Rd, Rs | Rd = zero_extend(Rs\[15:0\], 32) | Z,N | layout/pass-through |
| 0x5B | SEXT16 | SEXT16 Rd, Rs | Rd = sign_extend(Rs\[15:0\], 32) | Z,N | layout/pass-through |

These instructions use unused sub-opcodes in the 0x5 register-layout family. They may issue in either lane and are strong pairing candidates because they require only selection and replication wiring.

# Stack Bounds

- STKLOW: lowest legal byte address for the active stack interval.

- STKHIGH: first byte address above the legal stack interval.

- STKCTL.BOUNDS_EN: enables architectural stack-bound checking.

- The legal interval is STKLOW \<= address \< STKHIGH.

- PUSH/PUSHM check the decremented candidate address before any store.

- POP/POPM check the current address before any load and validate the resulting SP.

- Violation raises STACK_BOUNDS as a precise synchronous exception.

# Non-Circular Stream End Fault

Each Q stream end-mode field includes END_FAULT. When circular mode is disabled and END_FAULT is selected, an attempt to access beyond the configured finite 1D or 2D traversal raises STREAM_BOUNDS. Reaching the final valid element is legal; the following consume, pop, push, load, or store attempt faults.

Circular mode reloads/wraps the configured address/count state and therefore does not generate STREAM_BOUNDS from normal wrap. Alignment, access-permission, and physical memory faults remain possible in either mode.

# Precise Fault Ordering

Bounds are checked before architectural side effects. On a fault, no GPR, PSR arithmetic flag, SP, Q address, Q count, staging pointer, memory location, or destination register is modified. Older instructions retire; younger instructions are flushed. The exception return PC identifies the failing instruction for restart or emulation.

# Fault Causes

| Cause | Trigger | FAULT_ADDR | FAULT_INFO |
|----|----|----|----|
| STACK_BOUNDS | PUSH/POP candidate outside enabled stack interval | candidate stack address | operation, width, multiple-register index |
| STREAM_BOUNDS | non-circular END_FAULT access after terminal state | candidate stream address | Q0/Q1, direction, width, inner/outer terminal state |

AUR-ARCH-005 Addendum — Hardware Loop v1.2g

# Opcode Allocation

| Key | Mnemonic | Format | Operands | Privilege | Summary |
|----|----|----|----|----|----|
| 0xC0 | LOOP | LOOP_IMM8 | \#count | Any | Repeat the following 1-4 instructions; ordinary NOP terminates |
| 0xC1 | NOP | NONE | \- | Any | No effect; terminates an active hardware loop |

# LOOP Encoding

15 12 11 8 7 0\
+--------------+--------------+---------------------------+\
\| 1100 \| 0000 \| count_minus_one \|\
+--------------+--------------+---------------------------+\
Iterations = count_minus_one + 1, giving a range of 1-256.

# NOP Encoding

15 12 11 8 7 0\
+--------------+--------------+---------------------------+\
\| 1100 \| 0001 \| 00000000 \|\
+--------------+--------------+---------------------------+

# Programming Form

LOOP \#16\
DIVSTEP R0, R1, R2\
NOP\
\
LOOP \#8\
ASR R4, R1, R3\
ADD R0, R0, R4\
SUB R1, R1, R5\
NOP

# Execution Semantics

- LOOP arms hidden loop state and identifies the next instruction as the body start.

- Up to four body instructions are fetched/decoded and retained.

- NOP retires as the body boundary.

- If another iteration remains, the retained body replays with no branch instruction and no instruction-memory fetch.

- The loop counter decrements only when the terminating NOP retires.

- NOP outside an active loop is an ordinary no-op.

# Restrictions

- One active hardware loop; no nesting.

- Body length: 1-4 instructions, excluding NOP.

- No branch, call, return, IRET, LOOP, ASC, wait/halt, context-transfer, fence, or other serializing/control-transfer instruction.

- The body must not contain an earlier NOP because the first NOP is always the terminator.

- Normal register, flag, accumulator, stream, memory, and shared-resource hazards still apply.

# Interrupts, Faults, and Context

The loop is interruptible between retired operations. Exception entry preserves the active-loop state, remaining count, buffered body, and replay position. IRET resumes precisely. CTXSAVE/CTXRESTORE include this state in the CONTROL context group. A body exception does not decrement the loop count until the terminating NOP retires.

AUR-ARCH-005 Addendum — Pinned Circular Streams v1.2h

# Instruction and Configuration Summary

| Key | Mnemonic | Syntax | Class | Advances phase | Purpose |
|----|----|----|----|----|----|
| 0xB6 | QCFG / QSETPIN | QSETPIN Qn, \#ON\|OFF | configuration | No | Enable or disable pinned mode; clears pin-valid |
| 0xB1 | QPEEK | QPEEK Rd, Qn | read | No | Read current resident element without consuming |
| stream read | Q consume | operation-specific | read | On success | Read current element and advance/wrap |
| 0xB8 | QSTEP | QSTEP Qn | control | Yes | Advance pinned phase without transferring data |

# QSTEP Encoding

15 12 11 8 7 4 3 0\
+--------------+--------------+----------+-----------------+\
\| 1011 \| 1000 \| Qn / 0 \| reserved \|\
+--------------+--------------+----------+-----------------+\
Opcode key 0xB8. Reserved bits must be zero.

# Pinned Capacity

| Element width | Maximum pinned elements | Total resident bits |
|---------------|-------------------------|---------------------|
| 8             | 16                      | 128                 |
| 16            | 8                       | 128                 |
| 32            | 4                       | 128                 |

# Operational Semantics

- Enable pinned mode only for a finite circular read stream whose configured count fits the staging buffer.

- The engine fills all elements before setting PIN_VALID.

- A consuming read returns element\[phase\], then phase = (phase + 1) modulo pinned_count.

- QPEEK returns element\[phase\] and leaves phase unchanged.

- QSTEP performs phase = (phase + 1) modulo pinned_count and transfers no data.

- If PIN_VALID is false, a consuming read follows normal refill/stall rules; QSTEP before validity raises STREAM_CONFIG.

- No phase change occurs when an operation stalls, faults, is squashed, or fails to retire.

- Pinned replay is local and generates no memory request.

# Invalidation and Coherence

- Changing stream address, width, stride, count, circular setup, or pin enable clears PIN_VALID.

- Reset and explicit stream invalidation clear PIN_VALID.

- A context restore that omits STREAM_STAGING clears PIN_VALID.

- Software must invalidate/refill if another agent may have modified the underlying memory.

- The baseline mode is read-only; write-through pinned streams are reserved for future definition.

# Example

; Alternate two 32-bit coefficients indefinitely from Q0\
QSETADDR Q0, R8\
QSETWIDTH Q0, \#32\
QSETSTRIDE Q0, \#4\
QSETCOUNT Q0, \#2\
QCIRC Q0, \#2\
QSETPIN Q0, \#ON\
\
LOOP \#16\
MAC A0, R2, Q0\
NOP

AUR-ARCH-005 Addendum — COMPLEX16 Multiply Mode v1.2i

# Mode Definition

| Mode | Source representation | Affected operations | Result | Destination |
|----|----|----|----|----|
| COMPLEX16 | \[imaginary:16 \| real:16\] | MUL, MAC, MAS, eligible DOT/reduction | Exact signed real and imaginary components | Two consecutive aligned 64-bit register pairs, or A0/A1 for accumulation |

# Mathematical Operation

A = Ar + jAi\
B = Br + jBi\
\
Real = Ar × Br - Ai × Bi\
Imag = Ar × Bi + Ai × Br\
\
Each 16×16 product is signed 32-bit. Combining two products requires an exact signed 33-bit component.

# Widened Register Result

For an aligned destination Rd:\
\
Rd:Rd+1 \<- sign_extend_64(Real)\
Rd+2:Rd+3 \<- sign_extend_64(Imag)\
\
The real and imaginary values are contiguous, not interleaved. Rd must permit a legal aligned four-register group.

# Relationship to Ordinary Packed Multiply

| Operation | Input lanes | Mathematical outputs | Register layout |
|----|----|----|----|
| Packed 2x16 MUL | A1:A0 and B1:B0 | P0=A0\*B0; P1=A1\*B1 | one 64-bit pair containing two widened 32-bit products |
| COMPLEX16 MUL | Ai:Ar and Bi:Br | Real and Imag cross-combinations | one 64-bit pair per exact component; four registers total |

# Complex Accumulation

In COMPLEX16 mode:\
A0 \<- A0 + Real\
A1 \<- A1 + Imag\
\
MAS applies the instruction's subtract convention to the paired complex accumulation. Accumulator overflow and sticky status follow the existing accumulator rules.

# Conjugation Modifiers

- CONJ_A negates Ai before cross-product routing.

- CONJ_B negates Bi before cross-product routing.

- A × conjugate(B) therefore computes Real = Ar\*Br + Ai\*Bi and Imag = Ai\*Br - Ar\*Bi.

- Conjugation is mode state and does not consume a separate opcode.

# Restrictions and Hazards

- The destination reserves two consecutive aligned register pairs.

- Source/destination overlap is permitted only where the implementation guarantees all source reads precede writeback; otherwise the assembler/compiler must use a temporary destination.

- Complex multiply uses the shared multiply/reduction resource and is scoreboarded until both components complete.

- COMPLEX32 is reserved for a future profile.

AUR-ARCH-005 Addendum — COMPLEX16 Overflow Semantics v1.2j

# COMPLEX16 MUL

Sources are packed as \[imaginary:16 \| real:16\]. The multiplier computes exact signed 33-bit real and imaginary components internally.

| Item | Real component | Imaginary component | Architectural treatment |
|----|----|----|----|
| Equation | Ar\*Br - Ai\*Bi | Ar\*Bi + Ai\*Br | exact 33-bit internal values |
| Destination | Rd | Rd+1 | low 32 bits written |
| Overflow status | COVR | COVI | sticky when exact value does not fit signed 32 bits |

# Overflow Status

- COVR: sticky overflow indication for the real component.

- COVI: sticky overflow indication for the imaginary component.

- COV: aggregate condition equal to COVR OR COVI.

- The sticky bits remain set until cleared by the existing DSP-status clear mechanism.

- Normal execution continues after overflow.

- Optional privileged trap enable may request a precise DSP-overflow exception when a new complex overflow is detected.

# Complex MAC and MAS

MAC and MAS do not first truncate the complex product to 32 bits. The exact widened real and imaginary components are accumulated directly into A0 and A1. Accumulator overflow follows the existing sticky accumulator-status rules.

# Superseded Layout

The v1.2i layout using one 64-bit pair for real and a second 64-bit pair for imaginary is removed. COMPLEX16 MUL now returns both 32-bit components in one aligned 64-bit destination pair.

AUR-ARCH-005 Addendum — Multiply Mode Bits v1.2k

# Mode Bits

- MUL_WIDE: 0 = narrow result; 1 = widened result for ordinary real/packed MUL.

- MUL_COMPLEX: 0 = ordinary real/packed interpretation; 1 = COMPLEX16 interpretation.

- MAC/MAS are selected by opcode and are never selected by a mode bit.

# Behavior Matrix

| Mode | MUL semantics | Result layout | Notes |
|----|----|----|----|
| REAL + NARROW | ordinary scalar/packed product | normal-width destination | low-width result |
| REAL + WIDE | ordinary scalar/packed product | double-width pair/lane layout | exact product |
| COMPLEX16 + NARROW | cross-products | real32 and imag32 in one pair | COVR/COVI report lost range |
| COMPLEX16 + WIDE | reserved | none | illegal in baseline v1.2k |

# Complex MAC/MAS

When MUL_COMPLEX=1, MAC and MAS form exact signed 33-bit real and imaginary product components and inject them directly into A0 and A1. MUL_WIDE does not alter this explicit accumulator behavior.

AUR-ARCH-005 Addendum — ROUND and SAT Modes v1.2l

# Mode Bits

| Bit | Meaning | Affected operations | Default |
|----|----|----|----|
| ROUND | Enable round-to-nearest-even when low bits are discarded | DSP narrowing shifts, PACK/NARROW, accumulator extraction | 0 |
| SAT | Clamp values that do not fit the destination width | PACK/NARROW, accumulator extraction | 0 |

# Operation Ordering

For an affected conversion:\
\
1. Select and align the wide source value.\
2. Apply the requested right shift or scale reduction.\
3. If ROUND=1, round the retained result to nearest, ties to even.\
4. If SAT=1, clamp the rounded result to the signed or unsigned destination range.\
5. Write or pack the final result.\
6. If clamping occurred, set sticky SAT_OCCURRED.

# Instruction Coverage

| Instruction class | ROUND honored | SAT honored | Typical use |
|----|----|----|----|
| ASR / LSR / ordinary shifts | No | No | Exact bit manipulation |
| SHRN / DSP narrowing shift | Yes | No | Fixed-point rescaling without packing |
| NARROW | Yes | Yes | 64-\>32, 32-\>16, 16-\>8 conversion |
| PACK16 / PACK8 | Yes | Yes | Pack widened lanes into smaller sample lanes |
| ACCMOV / accumulator extraction | Yes | Yes | Convert A0/A1 to scalar or packed outputs |

# Timing

Implementations may complete ROUND/SAT conversions in the ordinary latency or may add one execution cycle. The operation remains a single architectural instruction. The scoreboard marks the destination unavailable until the rounded/saturated result is complete.

# Example: Q15 Multiply Result

MODE \#MUL_WIDE\|ROUND\|SAT\
MUL R2:R3, R0, R1 ; exact widened product\
PACK16 R4, R2:R3, \#15 ; round to nearest-even, then clamp to signed 16-bit

# Example: Accumulator Output

MODE \#ROUND\|SAT\
ACCMOV R0, A0, \#15 ; rounded and saturated fixed-point extraction

# Status and Traps

- SAT_OCCURRED is sticky until explicitly cleared.

- Saturation is normal DSP behavior and does not trap by default.

- A privileged implementation option may trap on a newly detected saturation event.

- ROUND does not alter arithmetic overflow flags for ordinary scalar instructions.

AUR-ARCH-005 Addendum — COMPLEX8 Mode v1.2m

# Mode Definition

| Mode | Source layout | Values per register | MUL result | MAC/MAS behavior |
|----|----|----|----|----|
| COMPLEX8 | \[imag1:8\|real1:8\|imag0:8\|real0:8\] | 2 signed complex values | \[imag1:16\|real1:16\|imag0:16\|real0:16\] in one aligned 64-bit pair | horizontal two-lane complex reduction into A0(real) and A1(imag) |

# Mathematical Semantics

For k in {0,1}:\
Real_k = Ar_k × Br_k - Ai_k × Bi_k\
Imag_k = Ar_k × Bi_k + Ai_k × Br_k\
\
Each component is computed exactly at 17-bit signed precision internally.

# Result and Overflow

- The low 16 bits of each component are written to the packed 64-bit destination pair.

- COVR becomes sticky if either Real_0 or Real_1 does not fit signed 16 bits.

- COVI becomes sticky if either Imag_0 or Imag_1 does not fit signed 16 bits.

- COV is the aggregate OR of COVR and COVI.

- Normal execution continues unless an optional privileged complex-overflow trap enable is active.

# Complex MAC/MAS

COMPLEX8 MAC/MAS performs a two-lane complex dot step:\
A0 += Real_0 + Real_1\
A1 += Imag_0 + Imag_1\
\
The exact widened products and horizontal sums are accumulated before any narrowing.

# Conjugation

CONJ_A and CONJ_B negate the selected source's imaginary lanes before cross-product routing. The modifiers apply to both packed complex lanes.

# Relationship to COMPLEX16

| Mode | Complex values/source register | Exact component width | Narrow MUL destination |
|----|----|----|----|
| COMPLEX8 | 2 | 17 bits | four 16-bit components in one 64-bit pair |
| COMPLEX16 | 1 | 33 bits | real32 and imag32 in one 64-bit pair |

AUR-ARCH-005 Addendum — CONJ Instruction v1.2n

# CONJ — Complex Conjugate

| Bytecode key       | 0x5C                         |
|--------------------|------------------------------|
| Format             | UNARY_RR                     |
| Syntax             | CONJ Rd, Rs                  |
| Execution resource | Packed ALU / negate datapath |
| Nominal latency    | 1 cycle                      |

## Purpose

Copy the real component or components unchanged while negating the imaginary component or components.

## COMPLEX16 Form

Source: \[ imaginary:16 \| real:16 \]\
Destination: \[ -imaginary:16 \| real:16 \]

## COMPLEX8 Form

Source: \[ imag1:8 \| real1:8 \| imag0:8 \| real0:8 \]\
Destination: \[ -imag1:8 \| real1:8 \| -imag0:8 \| real0:8 \]

## Overflow

If an imaginary lane contains the most-negative signed value (-128 for 8-bit or -32768 for 16-bit), its negation wraps to the same bit pattern and the corresponding packed overflow status is set. CONJ does not saturate and does not honor ROUND or SAT.

## Pairing and Hazards

CONJ is a unary packed-ALU instruction and is a strong dual-issue candidate. It cannot pair with another operation that writes the same destination or contends for the same packed negate resource in an implementation with only one.

## Examples

MODE \#PACKED16\
CONJ R1, R0\
\
MODE \#PACKED8\
CONJ R3, R2

AUR-ARCH-005 Addendum — DMA and Reduction/Stream Separation v1.2o

# Architectural Separation

| Mechanism | Primary role | Consumes instructions? | Walks memory autonomously? |
|----|----|----|----|
| Packed reduction | Compute over register/packed operands | Yes | No |
| Q0/Q1 stream | Address generation, staging, circular/pinned traversal | Triggered by stream-register operations | Prefetch/refill only within configured stream |
| DMA | Independent block transport | Only for setup/control | Yes |

# Baseline DMA Channels

- Channel 0: real-time/high-priority streaming transfer.

- Channel 1: background/general transfer.

- Both channels support 8/16/32-bit elements, 1D and 2D addressing, signed strides, row adjustments, inner/outer counts, half-transfer, completion, and error events.

# Near-Memory Connection

External/peripheral fabric -\> DMA channels -\> local-memory arbiter -\> DTCM/SRAM bank 0 and bank 1 -\> LSU and Q0/Q1 consumers.

# Synchronization Rules

- Complete core writes and issue FENCE/FENCE.IO as required before enabling a DMA read of those locations.

- Wait for DMA completion status/event, then issue the required fence before core or stream consumption of DMA-written data.

- Invalidate or reconfigure pinned streams whose backing memory was modified by DMA.

- DMA events may wake WFE and may also be routed to configured interrupt vectors.

# DMA Fault Model

| Fault | Meaning | Architectural response |
|----|----|----|
| DMA_ALIGN | Element/address alignment violation | Channel stops; error event/interrupt |
| DMA_BOUNDS | Protection or configured-region violation | Channel stops; fault address/status recorded |
| DMA_BUS | External/local target error | Channel stops; bus status recorded |
| DMA_CFG | Invalid descriptor or unsupported mode | Transfer does not start or stops precisely |

# No Core Datapath Redesign

The DMA block adds memory-fabric ports, arbitration, descriptor state, address adders/counters, small optional FIFOs, and event wiring. It does not change the architectural register file, arithmetic lanes, multiply modes, or calling convention.

AUR-ARCH-005 Addendum — Contextual ZR and Packed Predicates v1.2p

# Contextual ZR Encoding

Register field code 0xF has format-dependent meaning:\
\
- In control-flow and explicit-PC formats: R15 / PC.\
- In approved ordinary ALU operand positions where PC is prohibited: ZR.\
\
ZR reads as zero and discards writes. It has no saved architectural storage.

# Unified Compare and Test

| Mnemonic | Canonical encoding | Scalar mode | Packed mode |
|----|----|----|----|
| CMP Ra, Rb | SUB ZR, Ra, Rb | Updates Z/N/C/V | Updates per-lane predicate flags |
| TST Ra, Rb | AND ZR, Ra, Rb | Updates defined logical flags | Updates per-lane nonzero/zero predicates |

# Packed Predicate State

- Packed predicate state is current-result state, not sticky status.

- 4x8 operations produce P0-P3; 2x16 operations produce P0-P1.

- Wide 8x8 operations produce P0-P7; wide 4x16 operations produce P0-P3.

- Lane numbering follows the existing least-significant-lane-is-lane-0 convention.

- Inactive predicate bits are cleared.

- Interrupt and full context state preserve the active predicate mask and its packed-width interpretation.

# Conditional Move

The ordinary CMOV condition form is reused. In scalar mode it conditionally replaces the entire destination. In packed mode it conditionally replaces each destination lane according to the corresponding current predicate bit.

Scalar example:\
CMP R2, R3\
CMOV.GT R4, R5\
\
Packed example:\
MODE \#PACKED8\
CMP Rbest, Rnew\
CMOV.LT Rbest, Rnew\
CMOV.LT Rindex, Rnewindex

# Hardware-Loop Use

Because compare and both associated conditional updates are ordinary branchless instructions, a packed running minimum/maximum update can fit in a short hardware-loop body when current packed indices are supplied or updated outside the body:\
\
LOOPR Rcount\
MOV Rnew, Q0\
CMP Rbest, Rnew\
CMOV.LT Rbest, Rnew\
CMOV.LT Rindex, Rnewindex\
; four-instruction body ends at buffer capacity

# ZR Legality Summary

| Use | Baseline rule | Reason |
|----|----|----|
| ALU source | Allowed where PC source is prohibited | zero, copy, negate, compare-to-zero |
| ALU destination | Allowed where PC destination is prohibited | discard result while retaining flags |
| Store data | Allowed | store zero |
| Load destination | Prohibited | avoid ambiguous discarded loads and MMIO side effects |
| Register pair | Prohibited | ZR has no storage and must not break pair semantics |
| Branch/control field | Not ZR; remains R15/PC | preserve control-flow semantics |

AUR-ARCH-005 Addendum — Explicit Stream Access v1.2q

# Stream Data Instructions

| Mnemonic | Syntax | Consumes/produces | State advancement | Fault behavior |
|----|----|----|----|----|
| POP | POP Rd, Qn | Consumes one element | After successful completion | No GPR or stream-state update on fault |
| PEEK | PEEK Rd, Qn | Neither | Never | No GPR update on fault |
| PUSH | PUSH Qn, Rs | Produces one element | After successful completion | No memory or stream-state update on fault |

# Pure Register Moves

- MOV Rd, Rs accepts GPR operands only.

- CMOV.cond Rd, Rs accepts GPR operands only.

- CMOV false leaves Rd unchanged; CMOV true copies Rs to Rd.

- Neither path may differ in stream, memory, MMIO, address, count, ordinal, exception, or system-state effects.

- Packed CMOV performs lane-wise GPR selection from predicate state but cannot consume or produce stream elements.

# Stream Position System Registers

| System register | Meaning | Changes when |
|----|----|----|
| Qn.ADDR_NEXT | Address of the next element to be transferred | After successful POP/PUSH |
| Qn.ADDR_LAST | Address of the most recently transferred element | On successful POP/PUSH |
| Qn.ORD_NEXT | Linear ordinal of the next logical element | After successful POP/PUSH |
| Qn.ORD_LAST | Linear ordinal of the most recently transferred logical element | On successful POP/PUSH |

These values are read through the existing system-register transfer instruction, for example:\
\
MRS R6, Q0.ORD_LAST\
MRS R7, Q0.ADDR_LAST

# Packed Ordinal Rule

When one POP transfers a packed group, ORD_LAST identifies the first scalar lane in that group. The global scalar ordinal for lane k is ORD_LAST + k.

# Hardware-Loop Implication

A branchless stream-search loop must first POP the candidate into a GPR, then compare and conditionally update ordinary GPR state. A separate MRS may read the last address or ordinal. A future atomic POP-with-metadata form is reserved for consideration but is not baseline v1.2q.

# R13 Link-Register Convention

R13 is the conventional link register when a live return address is required. Leaf functions and functions that have saved or killed the return address may allocate R13 as an ordinary GPR. Compiler call analysis governs this use.

AUR-ARCH-005 Correction — Stream Access Semantics v1.2r

This section supersedes the v1.2q statement that POP, PUSH, and PEEK are the only stream-access instructions.

# Three Instruction Categories

| Category | Examples | Stream behavior | Rule |
|----|----|----|----|
| Stream-capable computation | ADD, SUB, packed ALU, MUL, MAC/MAS, REDUCE, DOT, SAD | Implicit consume/produce when Q0/Q1 is selected | Side effect is part of the computation |
| Standalone stream transfer | POP, PUSH, PEEK | Explicit consume, produce, or non-consuming read | Used when no fused computation is desired |
| Pure register/control | MOV, CMOV, branches, unrelated system operations | Never accesses stream data | Predicate outcome cannot change stream progression |

# Reduction Formats

One-source reductions accept one GPR or supported stream source and write A0 or A1. Two-source reductions accept the combinations defined by their encoding, with Q0/Q1 paired consumption prioritized. The selected accumulator is read implicitly only when ACC=1; INIT=1 replaces the accumulator with the current reduction result.

Examples:\
REDUCE.ADD A0, Q0, ACC\
REDUCE.XOR A1, Q1, INIT\
DOT A0, Q0, Q1, ACC\
SAD A1, R4, Q0, ACC ; only if the mixed form is defined by the final encoding

# Atomicity

- A stream source advances once only when the instruction successfully retires.

- A stream destination advances once only when the produced result successfully retires.

- Two stream sources advance together or not at all.

- A consume-plus-produce instruction updates both participating streams and its architectural result atomically.

- Faults, flushes, and interrupted unretired instructions leave all participating streams unchanged.

# MOV and CMOV

MOV and CMOV accept only GPR values. Packed CMOV performs lane-wise selection using packed predicate flags, but it cannot name Q0/Q1. Therefore both predicate outcomes have identical stream and address side effects: none.

# Reserved POPMETA Form

POPMETA Rd:Rd+1, Qn, meta remains a reserved encoding concept. If allocated later, Rd:Rd+1 is an aligned pair: Rd receives popped data and Rd+1 receives selected metadata such as ORD_LAST or ADDR_LAST.

AUR-ARCH-005 Addendum — Prefetch and Eight-Word Hardware Loops v1.2s

# Instruction Prefetch

The front end fetches 32 bits per cycle and contains two 32-bit prefetch entries. Together these entries retain four adjacent 16-bit instruction words.

# Captured Hardware-Loop Window

A captured hardware loop may contain up to eight contiguous 16-bit instruction words:\
\
words 0-3: decoded replay buffer\
words 4-7: pinned raw prefetch entries\
\
Words 4-7 pass through the normal decoder on every replay but do not require instruction-memory or I-cache access.

# Instruction Boundaries

- Extension words count toward the eight-word limit.

- Replay begins only at a base instruction.

- The final captured word must complete an instruction.

- The assembler diagnoses any loop whose extension sequence crosses the eight-word boundary.

# Loop Completion and Replay

- A body that uses all eight words terminates implicitly at capacity.

- A shorter body uses the established loop-end marker or encoded body-length mechanism.

- The loop sequencer decrements the count and selects the captured start without branch prediction.

- No instruction pair may span the iteration wrap.

- Normal dual-issue pairing is allowed across the word-3/word-4 storage boundary.

# Fallback

Bodies longer than eight words are not captured in the local replay window. They execute through the ordinary fetch path while retaining the architecture's loop-count and backward-loop control behavior.

# Example: Six-Instruction Argmax Loop

LOOPR Rcount\
POPMETA R4:R5, Q0, ORD\
ABS R4, R4\
CMP Rbest, R4\
CMOV.LT Rbest, R4\
CMOV.LT Rbestidx, R5\
REDUCE.ADD A0, R4, ACC\
; six one-word instructions occupy six of eight loop words
