Companion to the Aurora Instruction Reference. This guide focuses on writing efficient, readable, and high-performance Aurora assembly rather than defining instruction semantics.

# 1. Getting Started

- Assembly file structure

- Sections and symbols

- Assembler directives

- Calling conventions overview

# 2. Register Usage

- General-purpose registers

- Link, stack, and program counter

- Accumulators A0/A1

- Stream engines Q0/Q1

- PSR usage

# 3. Instruction Selection

- Choosing arithmetic vs packed operations

- Using DIVSTEP sequences

- Efficient load/store forms

- Layout and shuffle operations

# 4. Dual-Issue Scheduling

- Keep independent operations adjacent

- Avoid scoreboard conflicts

- Balance shared resources

- Exploit forwarding opportunities

# 5. Stream Programming

- Configuring Q0/Q1

- Circular buffers

- DMA interaction

- Producer/consumer patterns

# 6. Interrupts and Exceptions

- Prologue/epilogue patterns

- Saving registers

- Latency considerations

- Timer-driven scheduling

# 7. DSP Programming

- FIR filters

- MAC loops

- Dot products

- Horizontal reductions

- SAD kernels

# 8. Performance Tuning

- Minimize memory stalls

- Prefer stream accesses

- Reduce writeback conflicts

- Use packed arithmetic when applicable

# 9. Coding Idioms

- memcpy

- memset

- Checksum

- CRC

- Loop counters

- Function prologues/epilogues

# 10. Debugging

- Reading PSR

- Diagnosing hazards

- Common programming mistakes

# Future Companion Material

- Cycle timing cheat sheet

- Instruction pairing quick reference

- DSP optimization cookbook

- Compiler scheduling guide

- Porting guide from ARM Cortex-M

- Porting guide from dsPIC
