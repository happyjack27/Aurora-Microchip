# Aurora v1.2 Programmer's Guide and Optimization Manual

This guide demonstrates efficient use of Aurora for embedded control and DSP workloads.

## Compiler philosophy

Write clear C first. The compiler performs the primary scheduling. Aurora's four-entry issue window only repairs short-range pairing opportunities.

## General optimization

- Keep independent arithmetic close together.

- Separate memory accesses from dependent ALU work.

- Prefer streams for sequential data.

- Use paired-64 mode only where required.

- Exploit L8/L16 modes to preserve upper register contents.

## Dual-issue example

Interleave pointer updates, arithmetic, and shuffles so the scheduler can pair independent instructions.

## Streaming FIR filter

Configure Q0 for samples and Q1 for coefficients. Use DOT with fold mode and circular addressing.

## PID controller

Keep gains in registers, use MAC/MAS, update actuator after saturation check.

## memcpy

Use streams plus DMA for large transfers; scalar loop for short copies.

## CRC

Demonstrates packed byte operations and XOR reductions.

## Interrupt handler

Fast ISR preserves minimal state. Longer handlers save DSP state only if used.

## Matrix multiply

Tile into DTCM, double-buffer with DMA, accumulate in A0/A1.

## Optimization checklist

- Minimize MMIO inside tight loops.

- Favor register-layout operations as pairing partners.

- Alternate A0/A1 for independent reductions.

- Use QPEEK when data reuse exceeds one access.

- Reserve TCM for deterministic hot code and data.
