**Aurora Processor Family**

*Architecture Overview — Phase 1 Working Baseline*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr>
<th><strong>Mission<br />
</strong>Create a DSP-first, MCU-capable processor that maximizes useful work per transistor through deterministic execution, efficient data movement, compact code, and reusable arithmetic hardware rather than speculative complexity.</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1. Product Opportunity

Aurora targets cost-sensitive embedded products that currently choose between a conventional microcontroller, an entry-level DSP, or a two-chip MCU-plus-DSP design. The architecture seeks parity with established low-cost products while offering a more coherent path for control, signal processing, image work, matrix operations, and deterministic real-time systems.

# 2. Product Niche

- Native 32-bit data and registers with compact 16-bit instructions.

- DSP-first execution without giving up ordinary microcontroller programming.

- In-order asymmetric dual issue for predictable compiler scheduling.

- Stream registers, DMA, and small staging buffers that exploit regular memory-access patterns.

- Commodity banked SRAM rather than specialty dual-port memory.

- Shared compressor-tree arithmetic that amortizes multiplier hardware across reductions, SAD, MAC, and dot accumulation.

- Efficient 8-, 16-, 32-, and assisted 64-bit work.

- Deterministic timing, precise exceptions, and modest implementation complexity.

# 3. Why the Product Can Compete

Aurora does not depend on one spectacular benchmark. Its value comes from combining code density, predictable dual issue, strong streaming behavior, packed arithmetic, and system-cost reduction. A design that can perform control and DSP work on one inexpensive core may reduce parts count, memory traffic, firmware complexity, and board cost.

# 4. Major Features

| **Feature** | **Why it matters** |
|----|----|
| **Compact ISA** | Every base instruction is 16 bits, improving code density and fetch efficiency. |
| **32-bit native datapath** | The core operates natively on 32-bit data while supporting packed 2×16 and 4×8 formats. |
| **Stream execution** | R0 and R4 can carry implicit address, stride, count, direction, and buffering state. |
| **Asymmetric dual issue** | A scalar/control instruction can pair with an independent DSP or memory instruction. |
| **Shared arithmetic engine** | The multiplier compressor tree also supports MAC/MSUB, dot accumulation, HADD, and SAD. |
| **Low-cost memory** | Two ordinary SRAM banks provide dual-access-like bandwidth when requests land in different banks. |
| **Precise real-time behavior** | In-order retirement, scoreboarding, precise faults, and deterministic arbitration simplify embedded use. |

# 5. Current Phase 1 Status

| **Area** | **Status** | **Decision / Current Baseline** | **Freeze Note** |
|----|----|----|----|
| Product identity | LOCKED | DSP-first, MCU-capable; 16-bit instructions; native 32-bit data. | Primary differentiator is efficient deterministic dataflow at low cost. |
| Registers | LOCKED | 16 visible 32-bit registers; R13=SP, R14=LR, R15=PC; R0/R4 stream-capable. | 64-bit values use aligned even/odd pairs. |
| Pipeline | LOCKED | 4-stage IF → ID/RR → EX/MEM → WB/RET. | Variable-latency memory and arithmetic extend beyond nominal depth. |
| Issue model | LOCKED | In-order asymmetric dual issue; Slot A scalar/control, Slot B DSP/memory. | No renaming or out-of-order retirement. |
| Scoreboard | LOCKED | Primarily tracks outstanding memory operations; also long multiply/divide. | Independent instructions may continue when safe. |
| Packed formats | LOCKED | 2×16 and 4×8; no baseline 4-bit format. | Lane 0 occupies least-significant bits. |
| Streams | LOCKED | R0/R4 with address, signed stride, count, direction, 8/16/32-bit element widths. | No 4-bit streams. |
| Stream buffers | LOCKED | Two doublewords per stream; R0/R4 may couple into one LIFO buffer. | Exact naming and software-visible control opcodes still need finalization. |
| Memory | LOCKED | Banked commodity SRAM, DMA, ready/valid request-response protocol. | Exact bank mapping and arbitration remain implementation profile details. |
| Arithmetic engine | LOCKED | Shared compressor tree for multiply, MAC/MSUB, HADD, dot accumulation, SAD. | HMIN/HMAX remain comparator-based. |
| Flags | LOCKED | PSR with NZCV and sticky Q plus interrupt/control state. | No per-lane architectural flags. |
| ABI | LOCKED | R0–R3 args, R0 return, R13 SP, R14 LR, R15 PC. | Stream state caller-saved by default. |
| Interrupts | LOCKED | 16 priority levels/vectors with multiple sources per vector. | Exact vector table layout remains to be specified. |
| Branch dual-path prefetch | REJECTED | No split-buffer branch bit or mandatory both-path prefetch. | Use simple single-path prefetch. |
| Exact sub-opcode map | OPEN | Primary 4-bit opcode families are assigned. | Every legal 16-bit encoding and extension word must still be enumerated. |
| Validation benchmarks | OPEN | Kernel list identified. | Instruction traces, cycle models, and comparisons are still required. |
| Formal timing contract | PROVISIONAL | Baseline latencies proposed for multiply, divide, reductions, and packed ALU. | Must be validated against RTL feasibility and target process. |

# 6. Intended Workloads

- FIR and IIR filtering

- FFT and spectral processing

- Audio and communications

- Image filtering, motion/template comparison, and denoising

- Matrix multiplication, PCA/ICA primitives, and embedded inference

- Motor control and industrial automation

- General RTOS and peripheral-control workloads

# 7. Commercial Positioning

The goal is not to outspend or out-speculate incumbent architectures. The goal is parity in ordinary embedded use, with advantages where regular data movement and reusable arithmetic dominate. Aurora should be evaluated on total system cost, code size, deterministic throughput, energy per useful operation, and the ability to consolidate MCU and DSP roles.
