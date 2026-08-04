**Aurora v1.2 Validation & Benchmark Suite Specification**

*AUR-VER-001 \| Canonical Draft 1*

# 1. Purpose

Define the tests and performance workloads required to validate the ISA, ABI, pipeline, streams, memory system, interrupts, compiler, simulator, and RTL.

# 2. Test Layers

- Level 0: instruction semantic unit tests

- Level 1: architectural-state and exception tests

- Level 2: pipeline hazard and pairing-window tests

- Level 3: memory, stream, DMA and interrupt integration tests

- Level 4: compiler and ABI conformance tests

- Level 5: benchmark kernels and end-to-end embedded workloads

# 3. ISA Conformance

- Every opcode/subfunction in the machine-readable ISA database

- All scalar, packed, L8/L16 and paired-64 modes

- All flag combinations and signed/unsigned corner cases

- Extension-word decoding and illegal-encoding traps

- Pair aliasing, odd-base faults and R12:R13 LR-liveness cases

# 4. Pipeline and Pairing Tests

- RAW/WAR/WAW across every relative window position

- One- and two-issue refill/compaction

- Branch misprediction with younger issued instructions

- Shared-resource conflicts for multiply, reduction, divide, LSU and streams

- Precise interrupt injection during every stage and multi-cycle phase

# 5. Benchmark Kernels

| Category | Kernel | Primary metric | Architecture feature |
|----|----|----|----|
| DSP | FIR / IIR | cycles/sample | streams, MAC, circular addressing |
| DSP | FFT butterfly | cycles/butterfly | packed arithmetic, shuffles |
| DSP | INT8/INT16 matrix multiply | MACs/cycle | DOT, reductions, dual issue |
| Control | PID and Clarke/Park | cycles/control step | deterministic ALU/MAC |
| Memory | memcpy/memmove | bytes/cycle | streams, DMA, SRAM banks |
| Protocol | CRC / packet parse | bytes/cycle | L8, packed logic, shuffles |
| Crypto | AES / SHA-256 | cycles/block | rotate, XOR, layout ops |
| RTOS | context switch | cycles/switch | ABI, stack, interrupts |
| System | DMA double buffer | sustained bandwidth | DMA, TCM, streams |

# 6. Pass Criteria

- Bit-exact agreement among reference model, functional simulator and RTL

- Cycle-exact agreement among timing model and cycle-accurate RTL tests

- No unreviewed benchmark regressions above 3%

- 100% opcode and architectural-state coverage

- Formal proof of key safety properties where practical
