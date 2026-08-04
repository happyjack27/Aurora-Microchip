These pages are intended to appear near the front of the Aurora Instruction Reference, immediately after the instruction encoding chapter. They provide readers with a high-level view of how the ISA is organized before presenting individual instructions.

# 1. Primary Opcode Map

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

# 2. Opcode Space Allocation (Conceptual)

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

# 3. Decoder Organization

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

# 4. Instruction Family Index

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

# 5. ISA Expansion Policy

- Reserved opcode regions remain unused until approved through an Architecture Decision Record.

- Instruction families are kept contiguous where practical to simplify decoder logic.

- Documentation reflects the canonical frozen ISA database.
