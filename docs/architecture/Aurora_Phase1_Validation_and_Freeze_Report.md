**Aurora Phase 1 Validation and Architecture Freeze Report**

Revision 1.0

# 1. Freeze decision

Phase 1 is APPROVED as an architectural baseline. Approval means that programming-model semantics, instruction families, exact Phase 1 sub-opcode allocation, ABI, exceptions, ordering, streams, memory profile, and baseline timing classes are frozen. It does not constitute RTL sign-off or a guaranteed performance claim.

# 2. Architecture review checklist

| **Gate** | **Status** | **Evidence / limitation** |
|----|----|----|
| Product niche defined | PASS | DSP-first, MCU-capable, low-cost deterministic embedded processor. |
| Representative workloads identified | PASS | FIR, FFT, image/SAD, matrix, PCA/ICA primitives, control, RTOS. |
| Compiler synthesis considered | PASS | No dedicated PCA/ICA/FFT opcodes; general packed, MAC, reduction, stream primitives. |
| Instruction savings plausible | PASS | Streams remove address instructions; MAC/dot/SAD fuse common sequences; dual issue overlaps scalar control. |
| Silicon reuse maximized | PASS | Shared compressor tree; banked commodity SRAM; one iterative divider. |
| Critical-path risks bounded | CONDITIONAL | Muxing into compressor tree must be checked during RTL synthesis. |
| Opcode cost controlled | PASS | Unused encodings explicitly reserved; no split-prefetch bit or 4-bit lane mode. |
| Precise exceptions defined | PASS | In-order retirement; faulting operations have no partial architectural update. |
| Memory ordering defined | PASS | Per-agent ordering plus explicit synchronization. |
| ABI and interrupt contract defined | PASS | Register classes, stack, stream ownership, and interrupt frame specified. |
| Toolchain contract defined | PASS | Assembler, compiler, debugger, and simulator requirements listed below. |
| Trace validation completed | PASS-ANALYTICAL | Hand-scheduled kernels and cycle models completed; RTL traces remain Phase 2. |
| Documentation complete | PASS | Overview, architecture spec, ISA reference, validation/freeze report, journal/checklist. |

# 3. Baseline implementation profile

- 32-bit register/data path; 16-bit instructions; eight-word instruction prefetch buffer.

- Four-stage IF, ID/RR, EX/MEM, WB/RET pipeline.

- In-order asymmetric dual issue with scalar Slot A and DSP/memory Slot B.

- Two interleaved 32-bit closely coupled SRAM banks.

- Two DMA channels.

- One shared compressor/reduction engine and one iterative divider.

- R0/R4 64-bit staging buffers and 128-bit coupled LIFO buffer.

- Static backward-taken/forward-not-taken prediction; no dual-path prefetch.

# 4. Analytical kernel schedules

## 4.1 Four-tap packed FIR inner iteration

Assumption: R0 streams four signed 8-bit samples per access, R4 streams four signed 8-bit coefficients, and accumulator pair A0 is independent from the loop counter.

| **Cycle** | **Slot A** | **Slot B** | **Comment** |
|----|----|----|----|
| 0 | SUBS count, count, \#1 | PMAC8 A0, R0, R4 | Consume both streams and accumulate four products |
| 1 | BNE loop | \- | Branch issues alone; predicted taken |
| 2 | pointer/control work | PMAC8 next accumulator | Independent accumulator hides 2-cycle dependency where unrolled |
| Final | \- | HADDW8 result, A0 | Reduce widened lanes |

Result: one four-lane MAC per computational issue cycle; loop-control cost is reduced by unrolling and scalar/DSP pairing. Zero-overhead loops remain a possible future extension only if measured branch overhead justifies it.

## 4.2 FFT butterfly primitive

| **Step** | **Operations** | **Expected class** |
|----|----|----|
| 1 | PMUL16 twiddle products | 2-cycle compressor operation |
| 2 | PACK/UNPACK or ZIP lane arrangement | 1-cycle packed operation |
| 3 | PADD16 / PSUB16 butterfly outputs | 1-cycle packed operation |
| 4 | PRSHR16 optional fixed-point normalization | 1-cycle packed rounded shift |
| 5 | Stream stores | Scoreboarded memory operations |

No dedicated butterfly opcode is required for Phase 1. The kernel exercises packed multiply, lane rearrangement, add/subtract, rounded shift, and dual stream output.

## 4.3 Image block SAD

| **Cycle** | **Slot A**             | **Slot B**                           |
|-----------|------------------------|--------------------------------------|
| 0         | loop/index update      | SAD8 sum0, R0, R4                    |
| 1         | address/control        | SAD8 sum1, R0, R4                    |
| 2         | ADD total, total, sum0 | stream/memory preparation            |
| 3         | ADD total, total, sum1 | next SAD8 if independent destination |

SAD8 reuses packed subtract/absolute logic and the shared compressor tree. It avoids materializing four lane differences and a separate HADD instruction.

## 4.4 Matrix/PCA covariance dot product

| **Cycle** | **Slot A** | **Slot B** |
|----|----|----|
| 0 | loop/index update | DOT16 pair0, R0, R4 |
| 1 | independent scalar work | DOT16 pair1, R0, R4 |
| 2 | ADD/ADC accumulator low/high | stream refill or next independent operation |
| Final | normalization preparation | HADD/shift as needed |

PCA and ICA receive acceleration from streams, widening dot products, MAC/MSUB, CLZ for normalization, rounded shifts, and matrix-friendly strides without dedicated algorithm-specific opcodes.

## 4.5 MCU control loop

| **Cycle** | **Slot A**            | **Slot B**                 |
|-----------|-----------------------|----------------------------|
| 0         | CMP sensor, threshold | LDW next_sample, \[base\]  |
| 1         | conditional branch    | \-                         |
| 2         | ADD controller state  | STW output, \[peripheral\] |

The same core supports ordinary control flow and strongly ordered peripheral access. DSP features do not replace the standard MCU execution model.

# 5. Toolchain and debug contract

- Assembler must reject odd register-pair bases and unsupported lane/stream widths.

- Assembler emits extension groups atomically and marks relocation records for long immediates, branches, streams, and DMA descriptors.

- Linker preserves 2-byte instruction alignment and 8-byte ABI stack/data alignment where required.

- Compiler backend models Slot A/Slot B pairing, scoreboard latency classes, stream ownership, caller/callee saves, and sticky Q.

- Compiler correctness never depends on dual issue; every pair must remain valid as sequential instructions.

- Debugger presents R0-R15, PSR, stream descriptors, DMA state, and paired 64-bit values.

- Single-step treats extension prefix plus consumer as one architectural instruction group.

- Simulator must model bank conflicts, stream underflow/write backpressure, exact faults, and configurable memory wait states.

- Performance tools report issue-slot utilization, scoreboard stalls, bank conflicts, stream stalls, compressor occupancy, and branch penalties.

# 6. Phase 2 entry criteria

- RTL skeleton implements decode, four-stage flow, scoreboard, SRAM-bank arbitration, and precise retirement.

- Synthesis estimates quantify decoder, scoreboard, compressor muxing, SRAM interfaces, and critical paths.

- Instruction-set simulator passes normative corner-case tests.

- Assembler encodes every allocated opcode and rejects every reserved/illegal combination.

- Kernel traces are reproduced cycle-accurately in simulation.

- Architecture changes after this point require review-checklist approval and a versioned compatibility decision.
