**Compact MCU/DSP Architecture Ledger**

*Canonical design baseline • working document*

**Purpose.** This ledger is the authoritative compact record of decisions that have been explicitly locked in. It separates settled architecture from rationale, rejected alternatives, and unresolved work so future discussion can remain consistent and efficient.

| **LOCKED** | **PROVISIONAL** | **OPEN** | **REJECTED / DEFERRED** |
|------------|-----------------|----------|-------------------------|

# 1. Executive Baseline

| **Area** | **Locked baseline** |
|----|----|
| **Core identity** | One compact ISA/core intended to span low-cost microcontroller and DSP-oriented implementations through different surrounding memory/peripheral wrappers. |
| **Primary design goal** | Reach practical parity with existing low-cost MCU/DSP solutions while gaining advantages in stream efficiency, deterministic behavior, programmability, and total system cost. |
| **Cost constraint** | Commodity components are the default. The architecture must not depend on exotic external memory or specialty dual-port SRAM. |
| **Register model** | 16 visible registers, R0-R15. R0 and R4 are the two existing stream registers. |
| **Memory philosophy** | Small local state and buffers feed closely coupled SRAM; larger/slower backing memory follows where appropriate. Banked commodity SRAM supplies low-cost parallel bandwidth. |
| **DSP philosophy** | Favor regular streaming, local accumulation, packed operations, and predictable dataflow over a large collection of specialized opcodes or a large fixed systolic array. |

# 2. Register and Stream Architecture

## Visible register file

- 16 architectural registers: R0 through R15.

- No hidden larger register pool and no register-bank swap instructions at this stage.

- R0 and R4 remain ordinary visible registers with attached stream semantics/state.

## Stream-register placement

- R0 and R4 are the two stream registers.

- This is strictly a reassignment of the existing stream registers; it does not create new opcodes, lane groups, subregister banks, or altered instruction semantics.

- The R0/R4 placement is preferred because their encodings differ cleanly and align better with existing PACK, UNPACK, and SIMD-mode decoding.

## Coupled operation

- R0 and R4 may operate independently as streams or be coupled for LIFO operation.

- The attached implicit stream state means the architecture has more useful state than the raw count of 16 registers suggests.

## Local stream/stack buffers

- Each relevant stream/stack cache is a two-doubleword staging buffer.

- These are tiny deterministic buffers, not conventional associative caches.

- They are backed by closely coupled SRAM, followed by larger/slower backing memory such as eMRAM where applicable.

# 3. Arithmetic, SIMD, and Reduction

## Existing direction

- Packed/SIMD arithmetic, PACK/UNPACK, packed multiply, and horizontal add/reduction are part of the working design.

- Packed multiply followed by horizontal add is the preferred current construction for dot products; no dedicated dot-product instruction is added yet.

## Reduction/access patterns

- Packed arithmetic across registers preserves lanes and naturally reduces across rows/registers.

- Horizontal reduction within a register reduces across lanes and naturally completes row or dot-product reductions.

- PACK/UNPACK and stream stride/orientation should handle row-versus-column organization rather than proliferating special matrix opcodes.

- For long dot products, accumulate packed lanes through the loop and horizontally reduce once near the end to preserve parallel accumulators and avoid a serial dependency chain.

## Rounded right shift

- Right shift includes an optional rounding bit in its instruction encoding, even if this reduces operand/immediate bits.

- Rounding uses the standard conditional increment based on the highest discarded bit.

- There is no persistent/global rounding flag and no cheap round-to-odd or force-LSB approximation.

- No further change is being made to this subject at present.

## Deferred arithmetic additions

- No set-bit/power-of-two instruction for now because powers of two can already be created in two instructions.

- No dedicated multiply-accumulate, complex multiply, butterfly, or dot-product opcode is locked in yet.

- Saturating narrow/pack and pairwise widening reductions remain candidates for workload-driven evaluation, not settled features.

# 4. DSP Dataflow and Systolic-Like Behavior

## Target behavior

- The architecture should capture useful systolic-array properties without requiring a large fixed array.

- Target benefits: regular data movement, local operand reuse, persistent partial sums, overlapped transfer and compute, predictable latency, and low loop-control overhead.

## Mechanisms

- Stream registers provide implicit address progression and regular operand supply.

- Packed multiply/add and horizontal reduction provide vector and matrix inner-loop primitives.

- DMA and banked SRAM keep the datapath supplied while reducing explicit load/store and address-generation work.

- Independent stream stride is a high-value architectural direction because it supports row/column, FIR, convolution, FFT, and matrix access patterns.

# 5. Memory System and External Interface

## Core-facing protocol

- The core should see a simple request/response memory interface: address, read/write control, write data, read data, valid/request, and ready/acknowledge.

- The handshake permits one core to tolerate one-cycle SRAM, slower flash, external memory, or memory-mapped peripherals without ISA changes.

## Commodity banked SRAM

- Do not require specialty true dual-port external SRAM.

- Use two or more ordinary SRAM banks with independent hardware paths.

- Two simultaneous reads are available when the operands reside in different banks.

- Bank conflicts are acceptable; DMA, linker/compiler placement, or stream setup should mitigate them.

## System variants

- Microcontroller wrapper: simple deterministic memory/peripheral bus, internal or commodity SRAM/flash, timers, GPIO, serial peripherals, and interrupt controller.

- DSP wrapper: multiple SRAM banks, DMA channels, stream controllers, burst transfers, and possibly separate instruction/data paths.

- The ISA and main core remain common between the variants.

## Hierarchy

- Architectural registers and implicit stream state at the top.

- Two-doubleword local stream/stack staging buffers.

- Closely coupled SRAM as the main deterministic working store.

- Optional larger/slower backing memory beyond SRAM.

# 6. DMA, Interrupts, and Real-Time Behavior

## DMA

- DMA is a central DSP and system-cost feature, not a peripheral afterthought.

- DMA should move blocks between external interfaces, SRAM banks, and stream buffers while the core computes.

- Interrupts should normally occur at block boundaries or DMA completion rather than for every sample.

## Interrupt model

- 16 interrupt vectors, with lower vector number representing higher priority.

- Multiple interrupt sources may map to a vector, yielding effectively many sources across 16 priority levels.

- Interrupt capability is essential for microcontroller use and still valuable for DSP block-completion, timer synchronization, and exceptional events.

- No extra DSP-specific interrupt machinery is locked in beyond fast, predictable entry/exit and clear stream/cache state behavior.

# 7. Decision Log

| **Decision** | **Status** | **Reason / consequence** |
|----|----|----|
| **Stream registers moved to R0 and R4** | Locked | Cleaner alignment with existing encoding and modes; no semantic expansion. |
| **16 visible registers retained** | Locked | Sufficient when R0/R4 implicit stream state is included; avoids hidden-bank complexity. |
| **Two-doubleword stream/stack buffers** | Locked | Enough local staging with closely coupled SRAM; keeps area and power low. |
| **Rounded right shift modifier** | Locked | Useful for fixed-point DSP and image scaling; instruction-local state is cleaner than a global flag. |
| **Power-of-two/set-bit instruction** | Deferred | Already expressible in two instructions; not worth opcode pressure yet. |
| **Dedicated dot product** | Deferred | Packed multiply plus horizontal add already supplies the operation. |
| **Specialty external dual-port SRAM** | Rejected as requirement | Available but non-commodity and expensive per bit; banked ordinary SRAM is preferred. |
| **Banked commodity SRAM** | Locked | Industry-standard, low-cost path to parallel reads with manageable bank conflicts. |
| **Single universal external implementation** | Rejected | Keep one core/ISA but allow MCU- and DSP-oriented wrappers. |
| **Large fixed systolic array** | Deferred | Seek systolic-like benefits through streams, local accumulation, and DMA first. |

# 8. Canonical Opcode and Bit-Field Worksheet

Status: partially consolidated. The architecture-level instruction families and modifier requirements are known, but the exact original binary opcode assignments are not present in the retained design history. The table below is authoritative about what must be encoded and explicitly leaves unverified bit positions unassigned.

## 8.1 Encoding Constraints Already Locked In

- Sixteen visible registers require a four-bit register identifier wherever a full register operand is encoded.

- R0 and R4 are the stream-register encodings; this does not alter the ordinary register-number field.

- Right-shift instructions require an in-instruction rounding modifier. It is not a global processor flag.

- PACK, UNPACK, packed/SIMD arithmetic, packed multiply, and horizontal reduction must remain encodable without introducing hidden register-bank semantics.

- No opcode space is reserved for a power-of-two/set-bit instruction, hidden-register swapping, or a dedicated dot-product instruction at this stage.

- Instruction encoding should favor existing orthogonal operation families and mode bits over isolated one-off opcodes.

## 8.2 Required Instruction Families

| **Family** | **Required distinctions** | **Encoding status** |
|----|----|----|
| Register/ALU | register operands; scalar arithmetic and logic | Exact opcode and operand positions not recovered |
| Shift | left/right; logical/arithmetic as already designed; right-shift rounding modifier | Rounding modifier locked; bit position unresolved |
| Packed/SIMD | packed arithmetic modes and lane interpretation | Family locked; exact mode field unresolved |
| PACK / UNPACK | existing packing and unpacking semantics | Family locked; exact opcode values unresolved |
| Packed multiply | packed lane multiply | Family locked; exact opcode unresolved |
| Horizontal reduction | within-register reduction; used after packed accumulation | Family locked; exact opcode and reduction-width field unresolved |
| Stream operations | existing R0/R4 implicit stream behavior | Register mapping locked; exact control encoding unresolved |
| Control flow | branches, calls, returns, and interrupt-related control | Not reconstructed in retained context |
| Memory | loads/stores and interaction with ready/ack interface | Not reconstructed in retained context |

## 8.3 Field Assignment Template

The exact instruction width and original opcode values must be supplied or recovered before this section can become a binary-compatible specification. Until then, use the following field checklist for every format:

- Primary opcode or instruction-family selector.

- Destination register field: four bits when a full R0–R15 destination is present.

- Source register field(s): four bits each when full register selection is present.

- Immediate, shift amount, lane mode, or sub-operation field as applicable.

- Right-shift rounding bit in the right-shift format.

- Packed/SIMD lane-size and signedness controls where required.

- Any stream-specific mode must preserve ordinary R0/R4 register identity and may not imply new register banks.

- Reserved encodings must remain explicitly reserved rather than silently assigned.

## 8.4 Opcode-Space Change Rule

No further opcode or mode-bit allocation should be called locked until the current binary opcode table is pasted into or reconstructed within this ledger. Proposed additions may be evaluated conceptually, but their exact encoding remains provisional.

# 9. Open Questions / Next Analysis

1.  Recover or supply the original binary opcode table and instruction width, then replace the unresolved entries in Section 8 with exact bit positions and opcode values.

2.  Exact register width, packed lane widths, and supported signed/unsigned lane combinations.

3.  Precise stream-state fields: base/current address, increment or stride, bounds/count, direction, read/write mode, and LIFO coupling semantics.

4.  Buffer refill/drain rules, blocking behavior, coherency, interrupt visibility, and context-save requirements.

5.  Bank-selection scheme and whether software placement alone is sufficient or lightweight hardware interleaving is worthwhile.

6.  DMA channel count, arbitration, descriptor format, burst length, and interaction with stream buffers.

7.  Whether PACK should eventually gain signed/unsigned saturation modes.

8.  Whether pairwise widening horizontal add, fused multiply-accumulate, or FFT butterfly support is justified by measured kernel instruction counts.

9.  Exact MCU and DSP wrapper pin/bus standards and which commodity memories define the first implementation target.

10. Cycle-accurate benchmark kernels: FIR, FFT butterfly, small matrix multiply, image convolution, pixel scale/pack, and interrupt/DMA latency.

# 10. Change-Control Rules

- “Lock it in” moves an item into this ledger as a settled baseline.

- New ideas remain OPEN or PROVISIONAL until explicitly accepted.

- A new instruction must justify opcode cost, decode cost, datapath cost, and measured reduction in instruction count or memory traffic.

- Prefer orthogonal reuse of existing stream, PACK/UNPACK, SIMD, shift, DMA, and banked-memory mechanisms over one-off opcodes.

- Prefer commodity implementation and lower total system cost over theoretical peak performance.

- When a settled choice is replaced, retain the old choice in the decision log as superseded rather than silently deleting its rationale.
