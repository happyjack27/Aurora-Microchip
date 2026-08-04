# Aurora Design Journal (Working)

This document records the reasoning behind architectural decisions so future changes can be evaluated against the original design philosophy.

## Current Accepted Decisions

- DSP-first rather than MCU-first positioning.

- 32-bit native datapath retained despite 16-bit instruction encoding.

- Commodity SRAM banks instead of specialty dual-port SRAM.

- R0/R4 stream registers with optional coupled LIFO mode.

- 4-stage pipeline with scoreboarding for variable-latency memory operations.

- General-purpose shared compressor tree instead of multiply-only compressor network.

- Packed SIMD limited to 2×16 and 4×8 lanes.

- No baseline 4-bit streams or packed format.

- Explicit saturation and rounded right shifts.

## Architecture Review Checklist

- Which workloads benefit?

- Can the compiler already synthesize it efficiently?

- How many instructions are saved?

- What is the silicon cost?

- What is the timing impact?

- Can existing hardware be reused?

- Does it complicate decoding or pipelining?

- Does it fit the DSP-first, low-cost philosophy?

- Should it be baseline or extension?
