**AUR-ARCH-005 — Aurora Instruction Reference Manual**

*Showcase Bytecode Edition v1.1 • Aurora Architecture v1.2b*

This edition adds programmer-visible machine-code encodings to the presentable Aurora instruction reference. The machine-readable ISA database remains the canonical source for opcode assignments. Full DIV is a compiler/runtime pseudo-operation; DIVSTEP is the encoded hardware primitive.

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
