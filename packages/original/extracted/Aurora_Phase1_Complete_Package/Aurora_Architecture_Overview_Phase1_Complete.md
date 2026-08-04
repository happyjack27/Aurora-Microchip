**Aurora Processor Family - Architecture Overview**

Phase 1 Baseline, Revision 1.0

# Executive proposition

Aurora is a DSP-first, MCU-capable embedded processor intended to achieve product parity with established low-cost DSP/MCU families while differentiating through compact code, deterministic dual issue, stream-aware execution, and unusually efficient reuse of modest arithmetic and memory hardware.

# Product niche

- Native 32-bit registers and data with compact 16-bit instructions.

- Efficient 8-, 16-, 32-, and assisted 64-bit processing.

- DSP-first data movement and packed arithmetic without giving up ordinary control, interrupt, and peripheral workloads.

- One in-order core that can replace a separate MCU plus entry-level DSP in cost-sensitive equipment.

- Commodity banked SRAM and DMA rather than specialty true-dual-port memory.

- Predictable timing, precise exceptions, and compiler-visible scheduling rather than speculative complexity.

# Major architectural features

- 16 visible 32-bit registers; R13=SP, R14=LR, R15=PC.

- R0 and R4 can operate as stream registers with hidden address, stride, count, direction, and buffering state.

- R0/R4 can be coupled into a specialized LIFO path; the normal ABI stack remains R13-based.

- Four-stage front end: IF, ID/RR, EX/MEM, WB/RET.

- In-order asymmetric dual issue: scalar/control Slot A plus DSP/memory Slot B.

- Memory-focused scoreboard allows long-latency loads, stores, streams, multiply, and divide to extend beyond the nominal pipeline.

- Packed 2x16 and 4x8 SIMD, widening multiply, MAC/MSUB, explicit saturation, rounded right shifts, reductions, and SAD.

- A shared compressor-tree engine supports multiply, MAC/MSUB, dot products, HADD, SAD, and multioperand accumulation.

- Two interleaved commodity SRAM banks provide two-word-per-cycle bandwidth when requests hit different banks.

- At least two DMA channels with independent source/destination strides and 8/16/32-bit elements.

- 64-bit arithmetic through aligned even/odd pairs with carry, borrow, through-carry shifts, and full 32x32-to-64 multiply.

# Why this is a credible product

Aurora does not depend on a single exotic feature. Its advantage comes from several inexpensive mechanisms that reinforce one another: compact instruction fetch, static scheduling, stream-fed operands, banked memory, a reusable compressor engine, and DMA. These features raise sustained useful throughput while preserving a small, understandable implementation.

# Target workloads

- FIR/IIR filtering and audio

- FFT and spectral analysis

- Image filtering, SAD-based matching, and motion estimation

- Matrix multiply, PCA/ICA primitives, and compact inference

- Motor control and industrial automation

- Communications and software-defined radio

- RTOS-based general embedded control

# Phase 1 status

The architectural baseline is frozen at Revision 1.0. Reserved encodings remain intentionally unused. Performance claims are limited to analytical instruction and cycle models until RTL synthesis and compiler measurements are available.
