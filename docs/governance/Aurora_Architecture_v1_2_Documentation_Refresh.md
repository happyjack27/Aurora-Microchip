# Aurora Architecture v1.2 - Documentation Refresh

**Positioning**\
Aurora is a unified embedded processor architecture designed to bridge the gap between traditional microcontrollers and real-time DSPs. It emphasizes deterministic execution, low implementation cost, compact 16-bit instructions, native 32-bit execution, and efficient streaming data processing.

## Canonical Architecture

- Native 32-bit architecture with compact 16-bit ISA.

- 64-bit support is paired-register emulation; extra capability comes from additional cycles rather than substantially more hardware.

- Four-stage pipeline with scoreboard support for multi-cycle memory and DSP operations.

- Two radix-4 multiplier/compressor clusters plus a dedicated reduction tree.

- Two 40-bit accumulators: A0 (R8) and A1 (R10).

- Stream engines Q0 (R0/R1) and Q1 (R4/R5) with atomic 64-bit transfers.

- One-cycle stream enable mask plus per-instruction local/consume override.

- QPEEK, QPUSH, QPOP, QDUP, and QREPL queue operations.

- Power-of-two aligned circular addressing with signed stride.

- SIMD modes for packed 8-bit, packed 16-bit, and paired 64-bit emulation.

- Paired 64-bit shifts/rotates reuse existing 32-bit hardware and are permitted to take multiple cycles.

- Reduction operations support overwrite and fold (accumulate) semantics for ADD, DOT, SAD, AND, OR, XOR, MIN, MAX, ABSMAX, and COUNT.

## Commercial Position

Aurora targets deterministic embedded systems that combine control and signal processing: motor control, robotics, industrial automation, sensor fusion, communications, audio, imaging, and edge-AI preprocessing. The design goal is to replace the common MCU+DSP pairing with one efficient architecture.

## Design Philosophy

- Spend silicon where it benefits common real-time workloads.

- Prefer compiler assistance over excessive hardware complexity.

- Favor additional cycles over duplicated wide datapaths for infrequent 64-bit operations.

- Maintain deterministic timing and bounded multi-cycle execution.
