This document is the canonical record of the major architectural decisions made during the design of Aurora v1.2. It explains not only what the architecture is, but why it was designed this way and what alternatives were considered.

# Mission

## Chosen

Replace the common MCU + low/mid-range fixed-point DSP pair with one deterministic, low-cost, low-power processor.

## Alternatives Considered

- Compete directly with high-end DSPs.

- Become a desktop/server CPU.

# Instruction Set

## Chosen

16-bit base instructions with extension words for density and embedded flash efficiency.

## Alternatives Considered

- 32-bit fixed-width ISA.

- Variable-length x86-like encoding.

# Registers

## Chosen

Sixteen 32-bit GPRs with unified register file.

## Alternatives Considered

- Separate address/data register files.

- Native 64-bit register file.

# 64-bit Support

## Chosen

Emulated paired-register mode using even/odd pairs. SP and PC remain 32-bit and zero-extend as sources.

## Alternatives Considered

- Native 64-bit architecture.

- Dedicated 64-bit-only register bank.

# Special Registers

## Chosen

R13 link register (conditionally usable as GPR), R14 stack pointer, R15 program counter, optional frame pointer in R12.

## Alternatives Considered

- Dedicated non-addressable LR.

- Dedicated frame-pointer register.

# DSP Features

## Chosen

Two 40-bit accumulators, stream engines, circular addressing, packed arithmetic, reductions, DOT/SAD.

## Alternatives Considered

- Large accumulator bank.

- Floating-point-first design.

# Memory

## Chosen

Unified address space, optional ITCM/DTCM, banked SRAM, DMA, no mandatory cache hierarchy.

## Alternatives Considered

- Mandatory L1/L2 caches.

- TCM-only architecture.

# Execution

## Chosen

Four-stage in-order pipeline with compiler-driven scheduling and four-entry dynamic pairing window.

## Alternatives Considered

- Out-of-order execution.

- Register renaming.

- Large reorder buffer.

# Dual Issue

## Chosen

Two symmetric issue lanes with shared specialized execution resources.

## Alternatives Considered

- Fixed ALU/DSP slots.

# Prediction

## Chosen

Backward branches predicted taken; forward branches predicted not taken.

## Alternatives Considered

- Complex branch predictors.

# Timers

## Chosen

One coarse free-running counter and one coarse OS-managed countdown timer.

## Alternatives Considered

- Many hardware timers.

- Cycle-exact countdown hardware.

# Compiler Philosophy

## Chosen

Compiler performs primary optimization; hardware performs only local pairing repair.

## Alternatives Considered

- Heavy dynamic scheduling in hardware.

# Product Positioning

## Chosen

Low-to-mid-range DSP with integrated MCU-class deterministic control.

## Alternatives Considered

- General-purpose application processor.

- Tiny 8-bit MCU replacement only.

# Guiding Principles

- Prefer simpler hardware over peak benchmark performance.

- Spend transistors on sustained throughput rather than speculative execution.

- Move complexity into the compiler when practical.

- Favor deterministic timing over maximum average performance.

- Reuse execution hardware whenever possible.

- Keep software portability and mainstream toolchain support as first-class goals.

- Allow implementation profiles to scale memory and peripherals without changing the ISA.

# Architecture Freeze Status

Frozen for v1.2: Mission and target market

Frozen for v1.2: Programmer's model

Frozen for v1.2: ABI

Frozen for v1.2: ISA

Frozen for v1.2: Memory map

Frozen for v1.2: Pipeline

Frozen for v1.2: Microarchitecture

Frozen for v1.2: Compiler model

Frozen for v1.2: DSP model

Frozen for v1.2: Interrupt model
