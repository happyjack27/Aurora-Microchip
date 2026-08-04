**Aurora Architecture Specification**

Phase 1 Frozen Baseline, Revision 1.0

# 1. Mission and scope

DSP-first, MCU-capable; compact code, deterministic throughput, commodity memory, and cost discipline.

# 2. Programming model

16 visible 32-bit registers. R13 SP, R14 LR, R15 PC. R0/R4 stream-capable. 64-bit values in aligned even/odd pairs.

# 3. Data formats

Scalar 32-bit; packed 2x16 and 4x8; 64-bit paired. Little-endian. Streams support 8, 16, and 32 bits only.

# 4. Pipeline

Four stages: IF, ID/RR, EX/MEM, WB/RET. Branches resolve in EX/MEM. In-order retirement and precise exceptions.

# 5. Scoreboard

Focused primarily on variable-latency memory, stream, multiply, divide, and reduction operations. Tracks register, flag, stream, memory-order, and execution-resource hazards. No renaming or dynamic reordering.

# 6. Dual issue

Slot A scalar/control; Slot B DSP/memory/stream. Compiler schedules adjacent independent pairs. Illegal pairs issue singly.

# 7. Arithmetic engine

Shared compressor tree for scalar/packed multiply, MAC/MSUB, dot products, HADD, SAD, and widened accumulation. Comparator path handles min/max.

# 8. Stream subsystem

R0/R4 independent streams with address, signed stride, count, direction, width, status, and 64-bit staging buffer each. Coupled LIFO creates one 128-bit logical buffer.

# 9. Memory subsystem

Two interleaved 32-bit SRAM banks. Word address bit 0 selects bank. Naturally aligned 64-bit data spans both banks. Same-bank conflicts serialize deterministically.

# 10. DMA

At least two channels; 8/16/32-bit elements; signed source and destination stride; memory/peripheral transfers; precise completion/fault state.

# 11. PSR

NZCV, sticky Q, IE, IPL, supervisor, trace, and exception summary. Flags retire in order.

# 12. ABI

R0-R3 arguments, R0 or R0:R1 return, R0-R7/R12 caller-saved, R8-R11 callee-saved, R13 SP, R14 LR, R15 PC. 8-byte call-boundary stack alignment.

# 13. Interrupts

16 priority levels/vectors with multiple sources per vector. Hardware saves PC and PSR; handlers save used registers. Separate privileged interrupt stack.

# 14. External interface

Request/ready and response-valid/ready protocol with byte address, byte enables, data, and fault. Supports SRAM, peripherals, and bridges.

# 15. Baseline implementation profile

32-bit data path; 16-bit instruction fetch; two 32-bit SRAM banks; 8-entry instruction prefetch buffer; two DMA channels; one shared compressor engine; one iterative divider; no caches beyond stream/stack staging and instruction prefetch.

# 16. Compatibility contract

Faster implementations may pipeline or duplicate resources but may not change instruction semantics, precise state, ordering, pair legality baseline, or exception behavior.

# 17. Memory ordering

- Scalar instructions retire in order; stores become globally visible in program order.

- Each stream and DMA channel is internally ordered.

- Independent streams and DMA channels may overlap; SYNC/STRSYNC/DMASYNC establish required cross-agent ordering.

- Memory-mapped device accesses are strongly ordered and never prefetched.

- Self-modifying or DMA-written code requires ISYNC before execution.

# 18. Fault model

- Misaligned 32- or 64-bit baseline accesses fault; implementations may optionally support unaligned accesses only under a documented extension.

- Divide by zero, illegal pair bases, unsupported widths/formats, malformed extension groups, protection faults, and bus errors are precise.

- A faulting stream access does not advance address or count.

- A faulting DMA element remains pending and the channel stops with prior elements committed.

# 19. Frozen versus reserved

| **Status** | **Meaning** |
|----|----|
| Frozen | Semantics and compatibility contract are normative for Phase 1. |
| Reserved | Encoding is unavailable to software and traps; may become a future extension. |
| Implementation choice | Latency/resource duplication may vary while preserving the baseline contract. |
| Not claimed | Absolute MHz, area, power, and market superiority await RTL/compiler evidence. |
