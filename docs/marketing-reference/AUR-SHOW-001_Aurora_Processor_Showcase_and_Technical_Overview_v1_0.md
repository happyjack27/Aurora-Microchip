Showcase Edition v1.0\
Audience: Engineers, students, technically inclined readers, and prospective users.\
\
This document introduces Aurora at a high level before diving into the detailed architecture manuals.

# 1. Why Aurora Exists

Imagine designing a robot that must continuously sample sensors, filter data, control motors, communicate with peripherals, and respond immediately to interrupts. Traditional microcontrollers are simple and inexpensive but often struggle with DSP-heavy workloads. Full DSP processors offer excellent signal-processing performance but can add complexity and cost. Aurora was designed to bridge that gap: a low-cost embedded processor with DSP-class capabilities where they matter most.

# 2. Design Philosophy

- DSP-first architecture with microcontroller simplicity.

- Compact 16-bit instruction encoding and native 32-bit data path.

- Deterministic in-order execution.

- High sustained throughput on embedded workloads.

- Small silicon area through shared execution resources.

- Compiler-friendly architecture.

# 3. Where Aurora Fits

| Excellent Fit | Generally Not the Best Fit |
|----|----|
| Motor control | High-end application processors |
| Industrial automation | Desktop/server workloads |
| Sensors and instrumentation | Large operating systems |
| Communications | Massively parallel AI training |
| Imaging | Ultra-low-end 8-bit control applications |
| Robotics |  |
| DSP-heavy embedded systems |  |
| General embedded firmware with significant math |  |

# 4. Meet Aurora

## Registers

16 general-purpose 32-bit registers plus accumulators, stream engines, and a program status register.

## Pipeline

Four-stage dual-issue in-order pipeline emphasizing deterministic timing.

## Stream Engines

Hardware-assisted sequential memory access for DSP kernels.

## Shared Arithmetic

Multiply, MAC, dot-product, and reduction hardware shared between execution lanes.

## Memory

Unified address space with optional tightly coupled memory, banked SRAM, DMA, and memory-mapped peripherals.

# 5. What Makes Aurora Different?

- Combines low-cost microcontroller characteristics with mid-range DSP capability.

- Uses scoreboarding instead of out-of-order execution.

- Employs a compact ISA for good code density.

- Uses a small DIVSTEP unit instead of a large hardware divider to reduce area.

- Prioritizes deterministic execution over maximum peak benchmark performance.

# 6. A Tiny Example

Increment every 32-bit element in an array:\
\
loop:\
LD R1,\[R0\]\
ADD R1,R1,#1\
ST \[R0\],R1\
ADD R0,R0,#4\
BNE loop

# 7. Documentation Roadmap

- AUR-ARCH-005 — Instruction Reference Manual

- AUR-ARCH-006 — Assembly Language Programmer's Guide

- AUR-ARCH-007 — Software Optimization Guide

- AUR-ARCH-008 — Assembly Programming Cookbook

- AUR-HW-012 — Hardware Block Catalog

- AUR-HW-014 — Floorplan & Interconnect Atlas

# 8. Final Thoughts

Aurora is designed to occupy the space between traditional microcontrollers and conventional DSPs. Its emphasis on deterministic execution, compact encoding, shared arithmetic hardware, and stream-oriented memory access makes it particularly well suited to embedded systems that need substantial numerical processing without the cost and complexity of a larger processor.
