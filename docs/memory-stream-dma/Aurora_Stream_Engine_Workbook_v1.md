*Phase 2 Microarchitecture Baseline v1*

# 1. Purpose

The stream engine converts the architectural behavior of R0 and R4 into a small, deterministic hardware block that hides memory latency, performs implicit address generation, and supplies or accepts data for Slot B without turning the core into an out-of-order machine.

# 2. Frozen Architectural Inputs

- R0 and R4 are 32-bit architectural stream registers when enabled.

- Supported stream element widths are 8, 16, and 32 bits only.

- Each stream has current byte address, signed byte stride, direction, count, enable, completion, and fault state.

- Each stream owns a two-doubleword staging buffer: 128 bits because a native doubleword is 64 bits.

- R0 and R4 can operate independently or couple into one 256-bit logical LIFO buffer.

- A successful access advances address and decrements finite count; stalled or faulting accesses do neither.

- The core has a four-stage pipeline with scoreboarding focused primarily on variable-latency memory operations.

# 3. Chosen Physical Organization

Use two identical stream-engine instances, Stream 0 for R0 and Stream 1 for R4. Each instance contains a 128-bit circular staging buffer, configuration/state registers, a request generator, an element pack/unpack unit, and completion/fault logic.

- Four 32-bit physical buffer lanes per stream.

- Read and write pointers plus a 3-bit occupancy count from 0 to 4 words.

- Byte-valid masks per 32-bit lane to support 8- and 16-bit elements without sub-byte tracking.

- No 4-bit packing hardware.

- One outstanding refill burst and one outstanding drain burst per stream.

- One architectural stream element may be consumed or produced per cycle when the buffer permits.

# 4. Buffer Interpretation

| Element width | Elements per 32-bit lane | Elements per stream buffer | Notes |
|----|----|----|----|
| 8 bits | 4 | 16 | Little-endian byte order |
| 16 bits | 2 | 8 | 1-bit halfword sub-index |
| 32 bits | 1 | 4 | Direct word access |

# 5. Read-Stream State Machine

1\. IDLE: stream disabled or complete.

2\. ARMED: enabled; issue prefetch when occupancy is below the refill threshold.

3\. REFILL: one burst request is outstanding.

4\. READY: at least one configured element is available for R0/R4 consumption.

5\. DRAINED: finite count reached zero and no more elements may be consumed.

6\. FAULT: precise memory or configuration fault; no further advancement until software action.

A read of an enabled stream register completes from the head element. The engine then advances the sub-index or word pointer, updates address/count at retirement, and may trigger refill.

# 6. Write-Stream State Machine

1\. IDLE: stream disabled or complete.

2\. ARMED: accepts produced elements while capacity remains.

3\. BUFFERING: packs 8- or 16-bit elements into a 32-bit lane.

4\. DRAIN: emits full or explicitly flushed lanes toward memory.

5\. FLUSH: completes any partially filled lane using byte enables.

6\. COMPLETE: finite count reached zero and all writes are globally visible.

7\. FAULT: precise bus or configuration fault; failed element remains pending.

# 7. Refill and Drain Policy

- Read refill low-water mark: 2 of 4 words occupied.

- Read refill target: fill to 4 words.

- Write drain high-water mark: 2 of 4 words occupied.

- Write drain target: drain until 1 or 0 words remain, depending on arbitration.

- Maximum stream burst: 4 doublewords / 8 native words as already frozen, but a stream instance normally requests no more than its remaining 4-word local capacity.

- The controller may split requests at protection, device, or bank boundaries.

# 8. Address Generation

Each stream uses a 32-bit byte address and a signed 32-bit byte stride. The address generator computes the next architectural address in parallel with element transfer.

- Positive, zero, and negative stride are supported.

- Default stride equals element size.

- The architectural address advances once per completed element, not once per refill word.

- For packed sub-word elements, the memory byte address still follows the configured stride exactly.

- No modulo/circular addressing in the baseline; this remains a future extension candidate.

# 9. Slot B and Register-File Interface

- When stream mode is disabled, R0/R4 are read or written through the normal register file.

- When enabled, operand decode routes R0/R4 accesses to the stream engine.

- A read stream supplies a zero-extended 8- or 16-bit value or a full 32-bit value.

- Signed extension is performed by the consuming instruction, not by persistent stream state.

- A write stream accepts the low 8, 16, or 32 bits of the source operand.

- The scoreboard marks the relevant stream state busy until the element retires.

# 10. Memory and Scoreboard Integration

- Each refill/drain request receives a memory-operation tag.

- The memory scoreboard tracks stream identity, direction, destination buffer space, and fault status.

- Read returns may fill the staging buffer before the consuming instruction retires.

- Architectural address/count changes occur only at in-order retirement of the stream access.

- Write data may enter the staging buffer at execution, but global visibility remains ordered through the store/memory system.

- A stream fault blocks later accesses to that stream and retires precisely at the faulting instruction.

# 11. Independent R0/R4 Operation

The two stream engines are independent and may issue memory requests concurrently. They share the memory arbiter but not buffer pointers or address state.

- A single Slot B DSP operation may consume both R0 and R4 in one cycle.

- Both reads succeed only if each stream has a ready element.

- If either stream is empty, the paired DSP operation stalls before consuming either operand.

- The two architectural accesses retire atomically with the consuming instruction.

# 12. Coupled LIFO Mode

Coupled mode joins the two 128-bit buffers into one 256-bit logical LIFO while retaining two physical banks. R0 is the architectural data/top register; R4 stream access is illegal.

- Use one 32-bit stack pointer/current address and one element-width field.

- PUSH: decrement pointer by element size, enqueue value, then commit pointer update at retirement.

- POP: return top value, then increment pointer at retirement.

- Newest elements remain in local storage; older elements spill to closely coupled SRAM.

- Spill/fill ordering is strict and uses the same memory tags and precise-fault rules as streams.

- Mode entry requires both engines synchronized, no outstanding requests, and buffers empty or explicitly preserved by the mode-transition sequence.

# 13. Interrupt and Context Behavior

- Interrupts occur only between retired architectural accesses.

- Buffer contents remain implementation state but must be restart-safe.

- Normal handlers that do not touch active stream state need not flush the buffers.

- Handlers that reconfigure R0/R4 save and restore the complete architectural stream state.

- RTOS task switching synchronizes streams before saving state.

# 14. Faults and Corner Cases

| Condition | Result | Architectural update |
|----|----|----|
| Read underflow | Instruction stalls | None |
| Write buffer full | Instruction stalls | None |
| Bus fault | Precise exception | No address/count update |
| Direction misuse | Illegal stream-operation fault | None |
| Count reaches zero | Set complete and disable | After final successful element |
| Misaligned 16/32 access | Precise alignment fault | None |

# 15. Timing and Critical Paths

The intended one-cycle stream-consumption path is: decode/intercept → ready check → buffer select → element extraction → Slot B operand latch. Address/count updates are calculated in parallel and committed later.

- Keep memory-request generation off the stream-consumption critical path.

- Use a shallow 4-word mux per engine.

- Predecode element width to select byte/halfword/word extraction.

- Use registered refill/drain decisions.

- Treat dual-stream availability as a simple AND of per-engine ready signals.

# 16. Power and Area Strategy

- Clock-gate each stream engine independently when disabled.

- Clock only active buffer lanes and pointer state.

- Gate write packing logic for 32-bit streams.

- Gate unused byte-lane extraction logic according to element width.

- The two small buffers use flops or latch arrays in the baseline; SRAM macros are unnecessary at this size.

# 17. RTL Decomposition

- aurora_stream_pair.sv — top-level R0/R4 coordination and coupled mode

- aurora_stream_engine.sv — one independent stream instance

- aurora_stream_buffer.sv — 4×32 data array, byte valids, pointers, occupancy

- aurora_stream_agu.sv — address/stride/count logic

- aurora_stream_pack.sv — 8/16/32 extraction and insertion

- aurora_stream_memif.sv — request/response and burst handling

- aurora_lifo_ctrl.sv — coupled spill/fill and top-of-stack behavior

# 18. Verification Plan

- All widths, positive/zero/negative strides, finite and unbounded counts.

- Random refill/drain backpressure.

- Simultaneous R0/R4 consumption with one or both empty.

- Precise bus faults on every beat position.

- Mode transitions with outstanding requests forbidden.

- Coupled LIFO spill/fill across buffer boundaries.

- Interrupt entry after every possible completed element.

- Formal proof that address/count never advance on stall or fault.

- Formal proof that no element is duplicated or dropped.

# 19. Frozen Baseline

Aurora Phase 2 uses two independent 128-bit stream buffers with 8/16/32-bit element packing, one outstanding refill and one outstanding drain per engine, deterministic low/high-water policies, scoreboarded precise memory interaction, and optional 256-bit coupled LIFO operation.
