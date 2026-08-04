Showcase Edition v1.1\
\
This revision incorporates the new Instruction Space Overview chapter near the front of the manual.

# Chapter 1 — Introduction

Aurora is a DSP-first embedded processor architecture with deterministic in-order execution, a compact 16-bit instruction encoding, native 32-bit data paths, and stream-oriented memory support.

# Chapter 2 — Programmer's Model

- 16 × 32-bit general-purpose registers

- Program Status Register (PSR)

- A0/A1 accumulators

- Q0/Q1 programmable stream engines

# Chapter 3 — Instruction Encoding

Base instruction formats, extension words, register fields, immediates, and encoding rules.

# Chapter 4 — Instruction Space Overview (NEW)

## 4.1 Primary Opcode Map

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
<col style="width: 25%" />
</colgroup>
<thead>
<tr>
<th>0x0<br />
Arithmetic</th>
<th>0x1<br />
Logic</th>
<th>0x2<br />
Shift</th>
<th>0x3<br />
Mul/Reduce</th>
</tr>
</thead>
<tbody>
<tr>
<td>0x4<br />
Load</td>
<td>0x5<br />
Store</td>
<td>0x6<br />
Branch</td>
<td>0x7<br />
Compare</td>
</tr>
<tr>
<td>0x8<br />
Packed DSP</td>
<td>0x9<br />
SIMD</td>
<td>0xA<br />
Streams</td>
<td>0xB<br />
System</td>
</tr>
<tr>
<td>0xC<br />
Control</td>
<td>0xD<br />
Mode</td>
<td>0xE<br />
Extension</td>
<td>0xF<br />
Reserved</td>
</tr>
</tbody>
</table>

## 4.2 Opcode Space Allocation

The ISA dedicates the largest portion of opcode space to arithmetic, memory access, and DSP-oriented instructions. Reserved regions are intentionally retained for future architectural expansion.

| Family      | Relative Space |
|-------------|----------------|
| Arithmetic  | Largest        |
| Load/Store  | Large          |
| Packed DSP  | Large          |
| Logic       | Medium         |
| Branch      | Medium         |
| Streams     | Medium         |
| System/Mode | Small          |
| Reserved    | Remaining      |

## 4.3 Decoder Organization

Instruction Word\
│\
Primary Opcode\
┌────┼────┐\
Arithmetic Logic Memory\
│\
Sub-opcode\
│\
ADD SUB CMP ...

## 4.4 Instruction Family Index

| Family             | Opcode  | Execution Unit    | Chapter |
|--------------------|---------|-------------------|---------|
| Arithmetic         | 0x0     | Integer ALU       | 5       |
| Logic              | 0x1     | Integer ALU       | 6       |
| Shift/Rotate       | 0x2     | Shifter           | 7       |
| Multiply/Reduction | 0x3     | Shared Arithmetic | 8       |
| Load/Store         | 0x4-0x5 | LSU               | 9       |
| Branch             | 0x6     | Branch Unit       | 10      |
| Streams            | 0xA     | Stream Engine     | 11      |
| System             | 0xB-0xD | Control           | 12      |

# Remaining Chapters

The remainder of the manual follows with instruction-family chapters, appendices, opcode tables, timing information, and examples.
