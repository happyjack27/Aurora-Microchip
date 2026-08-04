**AURORA**

**Memory Scoreboard and Variable-Latency Completion**

*Phase 2 Microarchitecture Workbook — Version 1.0*

# 1. Executive Summary

Aurora uses a compact scoreboard primarily to allow memory operations to outlive the nominal four-stage pipeline. Multiply and divide reuse the same dependency machinery, but the design is optimized around loads, stores, stream accesses, and memory backpressure. The core remains in-order issue and in-order retirement; there is no renaming or general dynamic scheduling.

# 2. Design Goals

- Allow independent instructions to continue while a load, store, stream access, multiply, or divide remains outstanding.

- Stall exactly on true register, flag, stream-state, ordering, or structural dependencies.

- Preserve precise exceptions and program-order store visibility.

- Keep hardware substantially smaller than a reorder buffer or reservation-station design.

- Support deterministic worst-case timing for MCU and real-time DSP software.

# 3. Frozen Baseline Organization

The baseline uses an eight-entry completion queue. Entries are allocated in issue order and retired strictly from the head. The queue is not a reorder buffer: it stores only the metadata needed to track unfinished operations and precise completion.

| **Field** | **Width / form** | **Purpose** |
|----|----|----|
| **Valid / done / fault** | 1 bit each | Entry lifecycle and precise exception state |
| **Destination register** | 4 bits + write-enable | Register dependency and writeback |
| **Destination pair** | 1 bit | Marks even/odd 64-bit result |
| **Flags write mask** | NZCVQ mask | Pending status dependencies |
| **Operation class** | Memory / compressor / divide / stream / system | Completion routing and serialization |
| **Sequence age** | Queue position | In-order retirement; no associative age compare required |
| **Memory attributes** | Load/store, size, bank, device, ordering | Ordering and fault handling |
| **Stream identifier** | R0 / R4 / coupled LIFO / none | Hidden-state dependency tracking |
| **Result tag** | Small unit-local tag | Matches returning data to the queue entry |

# 4. Register Busy Tracking

A 16-bit register-busy vector is derived from non-retired queue entries. Each register also stores the producing queue index so returning results and forwarding can be matched without a content-addressable reservation station.

- A 32-bit destination marks one register busy.

- A 64-bit result marks the named even register and implied odd register busy.

- An instruction stalls in ID/RR if any source register is busy and its value is not available through an approved forwarding path.

- WAW hazards stall because there is no register renaming.

- WAR hazards do not arise after operands are captured in ID/RR, but a paired instruction is rejected if same-cycle semantics would conflict.

# 5. Memory Operation Tracking

Four of the eight completion entries may be outstanding memory-class operations. This limit bounds load/store queues and memory-side tags while leaving room for arithmetic operations.

- Loads may complete out of execution order but write architectural registers only when their queue entry reaches retirement; forwarding may expose completed load data to younger dependent instructions after all older fault conditions are known.

- Stores capture address, data, byte enables, and fault status in a two-entry store buffer. They become globally visible in program order.

- An unresolved older store blocks a younger load when addresses may alias. If both addresses and byte enables are known and non-overlapping, the load may proceed.

- Memory-mapped device accesses are serializing and do not bypass older memory operations.

- Bank conflicts delay acceptance but do not require extra architectural rules.

- A bus fault marks the owning entry faulted; no address, count, register, or flag update retires for that instruction.

# 6. Stream Dependencies

- R0 and R4 each have a stream-busy bit associated with an outstanding architectural stream access.

- Reconfiguration, synchronization, flush, enable/disable, and coupled-LIFO transitions wait for all older accesses to the affected stream.

- Independent R0 and R4 accesses may overlap.

- A scalar use of R0 or R4 conflicts with a pending stream write to the same architectural register.

- Address/count advancement is committed with the owning instruction at retirement, while prefetch-buffer movement remains restart-safe implementation state.

# 7. Flags and Branches

- Pending NZCV producers are tracked by the oldest not-yet-retired flag-writing entry.

- A branch stalls until the NZCV version it consumes is complete and architecturally safe.

- Sticky Q may be accumulated in completed entries but is ORed into PSR only at retirement.

- PSR writes, synchronization operations, calls that require precise memory state, and exception return are serializing.

# 8. Issue, Completion, and Retirement

| **Event** | **Allowed condition** | **Action** | **Stall cause** |
|----|----|----|----|
| Issue | Queue entry available; sources/resources legal | Allocate one or two adjacent entries in program order | Full queue or hazard |
| Unit completion | Matching result tag returns | Mark done; capture result/fault | Completion port busy |
| Forward | Result done and no older exception can invalidate use | Provide result to ID/RR or EX/MEM | Result not ready |
| Retire | Head entry done and not blocked by older pair semantics | Commit register/flags/stream/store effects | Head not done |
| Exception | Head entry faulted | Discard younger entries; vector precisely | None once at head |

# 9. Completion Ports

The baseline has two completion-result paths: one memory/stream return path and one arithmetic path shared by the compressor engine and divider. If two units complete on the same path in one cycle, the lower-priority unit holds its valid result until accepted. Completion is decoupled with valid/ready handshakes.

# 10. Precise Exception Rules

- Only the head entry may create an architectural exception.

- Younger completed results remain buffered and are discarded on an older fault.

- Stores do not become visible before all older potentially faulting instructions are safe.

- Interrupts are accepted only at a retirement boundary with no partially retired dual-issue pair.

- A prefix/consumer instruction group occupies one logical retirement unit.

# 11. Gate-Cost and Timing Expectations

Planning estimate: eight compact metadata entries, a 16-register producer table, small flag/stream busy state, two completion arbiters, and a two-entry store buffer. The likely critical path is ID/RR hazard checking, not queue storage. The design avoids full associative wakeup/select logic.

- Use direct register-indexed producer tags rather than scanning every queue entry for RAW hazards.

- Use queue-head comparisons for retirement and store ordering.

- Keep device/serialization checks in a separate slow control path when possible.

- Pipeline or predecode opcode class bits in IF to reduce ID/RR pairing and scoreboard delay.

# 12. Verification Plan

- Random variable memory latency with bank conflicts and bus backpressure.

- Load-use, WAW, flag-use, stream-state, and structural hazard tests.

- Older-fault/younger-complete precise exception tests.

- Store-to-load forwarding and ambiguous-alias stalls.

- Dual-issued pair retirement and fault ordering.

- Queue-full, completion collision, flush, interrupt, and reset cases.

- Formal proof that architectural retirement order equals program order.

# 13. Architecture Review Result

PASS — An eight-entry in-order completion queue with direct producer tags gives Aurora most of the latency-hiding benefit needed for memory and stream operations without introducing out-of-order scheduling or renaming. It is appropriately bounded for a low-cost deterministic core.
