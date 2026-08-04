**Showcase Edition v1.2 (Consolidated)\**
Canonical working instruction reference

# Table of Contents

- 1\. Introduction

- 2\. Programmer's Model

- 3\. Instruction Encoding

- 4\. Instruction Space Overview

- 5\. Pipeline Overview

- 6\. Instruction Families

- 7\. Representative Instruction Entries

- Appendix A - Register Summary

- Appendix B - Opcode Summary

- Appendix C - Glossary

# 1. Introduction

Aurora is a DSP-first embedded processor with deterministic in-order execution, 16-bit instructions, native 32-bit data paths, dual issue, stream engines, shared arithmetic hardware, and a compact, compiler-friendly ISA.

# 2. Programmer's Model

- 16 × 32-bit general-purpose registers (R0-R15)

- A0/A1 accumulators

- Q0/Q1 programmable stream engines with 2D addressing support

- Program Status Register (PSR)

- Little-endian memory model

# 3. Instruction Encoding

Aurora uses a fixed 16-bit base instruction with optional extension words for expanded immediates and encodings.

# 4. Instruction Space Overview

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
Extensions</td>
<td>0xF<br />
Reserved</td>
</tr>
</tbody>
</table>

## 4.2 Opcode Space Allocation

| Family      | Relative Allocation |
|-------------|---------------------|
| Arithmetic  | Largest             |
| Load/Store  | Large               |
| Packed DSP  | Large               |
| Logic       | Medium              |
| Branch      | Medium              |
| Streams     | Medium              |
| System/Mode | Small               |
| Reserved    | Future Expansion    |

## 4.3 Decoder Organization

Instruction Word\
│\
Primary Opcode\
├── Arithmetic\
├── Logic\
├── Memory\
├── Streams\
└── System\
│\
Sub-opcode\
│\
ADD SUB CMP ...

## 4.4 Instruction Family Index

| Family     | Opcode  | Execution Unit    | Chapter |
|------------|---------|-------------------|---------|
| Arithmetic | 0x0     | ALU               | 6       |
| Logic      | 0x1     | ALU               | 6       |
| Shift      | 0x2     | Shifter           | 6       |
| Multiply   | 0x3     | Shared Arithmetic | 6       |
| Load/Store | 0x4-0x5 | LSU               | 6       |
| Branch     | 0x6     | Branch Unit       | 6       |
| Streams    | 0xA     | Stream Engine     | 6       |
| System     | 0xB-0xD | Control           | 6       |

# 5. Pipeline Overview

IF → ID/RR → EX/MEM → WB/RET\
Dual issue • Scoreboarding • Forwarding • In-order retirement

# 6. Instruction Families

## Arithmetic

Family overview, philosophy, representative instructions, pairing guidance, and design notes.

## Logic

Family overview, philosophy, representative instructions, pairing guidance, and design notes.

## Shift/Rotate

Family overview, philosophy, representative instructions, pairing guidance, and design notes.

## Load/Store

Family overview, philosophy, representative instructions, pairing guidance, and design notes.

## Branch

Family overview, philosophy, representative instructions, pairing guidance, and design notes.

## Packed DSP

Family overview, philosophy, representative instructions, pairing guidance, and design notes.

## Streams

Family overview, philosophy, representative instructions, pairing guidance, and design notes.

## System

Family overview, philosophy, representative instructions, pairing guidance, and design notes.

# 7. Representative Instruction Entry

## ADD

### Purpose

Integer addition.

### Syntax

ADD Rd,Rs,Rt\
ADD Rd,Rs,#imm

### Operation

Rd ← Rs + operand

### Flags

Z N C V updated.

### Pipeline

EX/MEM execution, WB/RET retirement.

### Pairing

Pairs with most independent non-conflicting operations.

### Design Insight

Simple orthogonal arithmetic improves compiler scheduling.

# Appendices

- Register Summary

- Opcode Summary

- Glossary

- Future revisions will expand every instruction into this canonical format.
