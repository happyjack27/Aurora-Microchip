# Aurora Processor Architecture Booklet

## Executive Summary

Aurora is a DSP-first, MCU-capable embedded processor designed to maximize useful work per transistor. It combines compact 16-bit instructions with native 32-bit registers, deterministic execution, stream-oriented memory access, dual issue, DMA, and efficient packed arithmetic while remaining suitable for low-cost systems.

## Key Differentiators

- 16-bit instruction encoding with 32-bit native datapath

- DSP-first while remaining microcontroller capable

- In-order asymmetric dual issue

- R0/R4 stream registers with hidden stream state

- Small stream and stack staging buffers

- Commodity banked SRAM rather than specialty dual-port SRAM

- Scoreboarded variable-latency memory operations

- Packed SIMD (2×16 and 4×8) with widening arithmetic

- 64-bit support through register pairs

- Shared compressor-tree arithmetic engine

## Vision

Rather than pursuing aggressive speculation or large out-of-order hardware, Aurora invests silicon in deterministic data movement, reusable arithmetic hardware, and compiler-friendly execution. The result is a processor aimed at replacing separate MCU and entry-level DSP devices in many embedded products.
