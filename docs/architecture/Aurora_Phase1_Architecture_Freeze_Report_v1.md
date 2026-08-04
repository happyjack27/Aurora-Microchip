**Aurora Phase 1 Architecture Freeze Report**

*Formal Readiness Assessment*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr>
<th><strong>Overall result<br />
</strong>CONDITIONAL FREEZE. The architectural identity and major subsystems are coherent and documented, but exact sub-opcode enumeration, validation traces, and final timing evidence still block a complete ISA freeze.</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1. Freeze Objectives

- Define the product niche and architectural mission.

- Freeze the programmer-visible data model and major subsystems.

- Establish a complete encoding framework.

- Define baseline timing and exception principles.

- Validate the ISA against representative kernels.

- Identify all remaining blockers before implementation freeze.

# 2. Freeze Matrix

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

# 3. Blocking Items

| **Blocker** | **Required output** | **Exit criterion** |
|----|----|----|
| **Exact binary sub-opcode table** | Enumerate every legal 16-bit instruction, extension word, reserved value, and illegal combination. | Reviewed, documented, and marked LOCKED. |
| **Instruction semantic reference** | For each opcode: operands, pseudocode, flags, faults, privilege, pairability, and timing class. | Reviewed, documented, and marked LOCKED. |
| **Validation kernels** | Produce hand-scheduled instruction traces and cycle estimates for FIR, FFT, image convolution/SAD, matrix multiply, memcpy, control loop, and RTOS context switch. | Reviewed, documented, and marked LOCKED. |
| **Memory profile** | Select at least one concrete baseline SRAM topology and define bank mapping, instruction/data placement, and arbitration bounds. | Reviewed, documented, and marked LOCKED. |
| **RTL feasibility estimates** | Estimate compressor-tree muxing, scoreboard depth, stream-buffer logic, multiplier latency, and critical paths. | Reviewed, documented, and marked LOCKED. |
| **Toolchain contract** | Finalize assembler syntax, register-pair notation, stream configuration model, and ABI details needed by compiler and debugger. | Reviewed, documented, and marked LOCKED. |

# 4. Validation Kernel Plan

| **Kernel** | **Architectural coverage** | **Required result** |
|----|----|----|
| **FIR filter** | Stream reads, packed MAC, accumulator dependency, rounded narrowing. | Instruction trace, bytes, cycles, stalls, and baseline comparison. |
| **FFT radix-2 butterfly** | Packed multiply, add/subtract, lane rearrangement, scaling. | Instruction trace, bytes, cycles, stalls, and baseline comparison. |
| **Image SAD block** | Absolute difference path plus shared compressor reduction. | Instruction trace, bytes, cycles, stalls, and baseline comparison. |
| **Matrix multiply** | Two stream operands, packed MAC, HADD/dot accumulation, bank behavior. | Instruction trace, bytes, cycles, stalls, and baseline comparison. |
| **PCA/ICA primitive** | Covariance/dot accumulation, normalization support, multiword precision. | Instruction trace, bytes, cycles, stalls, and baseline comparison. |
| **Memcpy/memset** | DMA, banked SRAM, alignment, stream write behavior. | Instruction trace, bytes, cycles, stalls, and baseline comparison. |
| **MCU control loop** | Branches, peripheral ordering, interrupts, scalar code density. | Instruction trace, bytes, cycles, stalls, and baseline comparison. |
| **RTOS context switch** | ABI, PSR, stream state, stack, precise synchronization. | Instruction trace, bytes, cycles, stalls, and baseline comparison. |

# 5. Architecture Review Gate

No OPEN item may be promoted directly to LOCKED. It must pass the checklist contained in the Design Journal and Review Checklist document. Timing-sensitive items also require either synthesis evidence or a conservative implementation estimate.

# 6. Phase 1 Exit Definition

- All sub-opcodes are enumerated and conflict-free.

- Every instruction has normative semantics.

- Representative kernels have trace-based validation.

- No unresolved contradiction exists among overview, specification, ABI, pipeline, memory, and arithmetic definitions.

- All remaining non-baseline ideas are explicitly classified as optional extensions.

- The freeze report is revised from CONDITIONAL FREEZE to FROZEN.
