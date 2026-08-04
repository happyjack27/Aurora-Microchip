Canonical hierarchical decomposition of every major hardware block in the Aurora processor. This document is the implementation reference for RTL, floorplanning, verification, and physical design.

# Front End

- Instruction fetch

- Program counter / next-PC

- Prefetch buffer

- Branch predictor

- Instruction aligner

- Decoder

- Immediate generator

- Control generation

# Issue System

- 4-entry issue window

- Oldest-anchor logic

- Partner search

- Hazard comparators

- Scoreboard

- Window compaction

- Dispatch muxes

# Register System

- 16×32 register file

- Read decoders

- Read muxes

- Write decoders

- Dual write ports

- Writeback muxes

- Pair alias logic

- L8/L16 merge logic

- PSR

- Configuration registers

# Operand Routing

- Operand muxes

- Cross-lane forwarding

- Bypass network

- Immediate muxes

- Shared-unit request muxes

- Shared-unit result demuxes

# Execution

- Lane 0

- Lane 1

- ALUs

- Logic units

- Compare

- Barrel shifters

- Packed arithmetic

- Byte/word shuffle

- Branch evaluation

- Address assist

# Shared Arithmetic

- Multiplier

- Dadda reduction tree

- MAC/MAS

- DOT

- SAD

- Horizontal reduction

- A0 accumulator

- A1 accumulator

- Accumulator muxes

# Division

- DIVSTEP assist

- Shift/alignment

- Conditional subtract

- Quotient update

- Remainder update

- Divide-by-zero detection

# Memory

- LSU

- Alignment logic

- Store buffer

- Load tracking

- Q0 stream

- Q1 stream

- Memory fabric

- DMA interfaces

- Address decoder

- MMIO decoder

# Retirement

- Completion records

- Age ordering

- Commit arbiter

- Fault handling

- Writeback buses

- Flush generation

# Control

- Interrupt controller

- Priority encoder

- Vector logic

- Free-running counter

- Countdown timer

- Debug

- Reset

- Clock control

# Physical

- Clock tree

- Reset tree

- Power grid

- Pad ring

- SRAM macros

- Routing channels

- DFT/scan

- Spare cells
