# Aurora Architecture Specification (Living Draft)

- 1\. Architectural Goals

- 2\. Programming Model

- 3\. Register File

- 4\. Pipeline and Scoreboarding

- 5\. Instruction Formats

- 6\. Opcode Allocation

- 7\. Scalar Execution

- 8\. Packed DSP Execution

- 9\. Shared Compressor Arithmetic Engine

- 10\. Streams and LIFO

- 11\. Memory System

- 12\. DMA

- 13\. ABI and Calling Convention

- 14\. Interrupts and Exceptions

- 15\. Timing Model

- 16\. Validation Kernels

- 17\. Future Extensions

## Current Frozen Decisions

- Native 32-bit architecture with 16-bit instructions

- 4-stage in-order pipeline

- Memory-focused scoreboard

- Asymmetric dual issue

- R0/R4 stream architecture

- Commodity banked SRAM

- Shared compressor-tree arithmetic engine

- PSR with NZCV+Q

- Standard ABI with SP/LR/PC
