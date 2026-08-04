**Canonical Draft 1 - August 2026**

This specification defines the baseline four-stage pipeline, four-entry dynamic pairing window, issue and retirement rules, scoreboard structure, forwarding, completion handling, branch recovery, memory arbitration, stream/DMA interaction, and precise interrupt behavior for Aurora v1.2.

# 1. Implementation Goals

- Preserve deterministic embedded behavior while recovering short-range dual-issue opportunities.

- Keep the architecture fundamentally in order: no register renaming and no general reorder buffer.

- Allow multi-cycle DSP, memory, divide and paired-64 operations to remain outstanding under scoreboard control.

- Use compiler scheduling as the primary optimization mechanism and hardware lookahead as a local repair mechanism.

- Avoid placing 64-bit emulation, timers, DMA or optional memory features on the scalar critical path.

- Maintain precise exceptions and bounded interrupt entry.

# 2. Top-Level Datapath

Fetch / Prefetch\
\|\
4-entry decoded pairing window\
\|\
Register read + dependency/resource selection\
\|\
Slot A: scalar/control/address Slot B: memory/DSP/multiply/reduce/stream\
\\\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_/\
\|\
scoreboard/completion\
\|\
writeback/retire

# 3. Four Pipeline Stages

| Stage | Name | Primary work | State produced | Typical stalls |
|----|----|----|----|----|
| 1 | IF | Fetch one or two adjacent 16-bit words; extension-word assembly; single-path prefetch | Fetched words and PCs | Memory wait, taken branch recovery, full decode window |
| 2 | ID/RR | Decode, mode interpretation, four-entry compaction, dependency/resource checks, register read | Up to two issued micro-ops | RAW/WAR/WAW, unavailable unit, stream ordering, scoreboard conflict |
| 3 | EX/MEM | ALU, branch resolution, address generation, packed/DSP execution launch, memory request | Results or outstanding completion records | Memory ready, multi-cycle unit occupancy, bank conflict |
| 4 | WB/RET | Register/flag writeback, completion commit, ordered architectural retirement | Architectural state update | Older faulting instruction, writeback conflict, completion not ready |

# 4. Fetch and Prefetch

- The baseline front end fetches up to two adjacent 16-bit instruction words per cycle.

- Extension words are attached to their base instruction before the decoded instruction enters the pairing window.

- The prefetch buffer follows one predicted path only; there is no dual-path fetch.

- Backward conditional branches are predicted taken; forward conditional branches are predicted not taken.

- A taken branch resolved in EX/MEM invalidates younger fetched and decoded entries.

- Instruction fetch has a dedicated ITCM path where implemented and otherwise arbitrates for general memory.

# 5. Four-Entry Dynamic Pairing Window

The decoded window contains four valid entries in original program order. The oldest unissued entry anchors each issue group. A second compatible instruction may be selected from any younger entry in the window.

| Entry field | Minimum contents | Purpose | Architectural? |
|----|----|----|----|
| PC / length | 32-bit PC, base plus extension length | Restart, branch and retirement ordering | Yes |
| Decoded operation | Opcode/subfunction/mode | Execution selection | Yes |
| Source masks | GPR, pair, accumulator, stream, flags | RAW/WAR checks | No |
| Destination masks | GPR, pair, accumulator, flags | WAW/WAR checks | No |
| Resource mask | Slot/unit/memory/stream requirements | Pair legality | No |
| Status | valid, issued, complete, fault, killed | Compaction and retirement | No |

## 5.1 Selection rule

- The oldest ready instruction is selected first unless a serializing or faulting older instruction blocks issue.

- The partner may be entry +1, +2 or +3.

- The partner must not conflict with the anchor or with any skipped older unissued entry.

- Skipped entries retain their original order after issue and compaction.

- At most two instructions issue per cycle.

- If one instruction issues, one new decoded entry may be admitted; if two issue, two may be admitted.

## 5.2 Preferred pass-through candidates

- BSWAP, WSWAP, SHUFFLE, PACK, UNPACK, ZIP and UNZIP.

- MOV and simple unary register operations.

- Independent scalar ADD/SUB/logic/compare/shift operations.

- Register-layout operations ignore stream interception and L8/L16 masking unless explicitly specified.

- Memory, MMIO, privileged, stream-configuration and unresolved control operations are not preferred bypass candidates.

# 6. Dependency Rules

| Hazard | Example | Rule |
|----|----|----|
| RAW | I0 writes R2; I2 reads R2 | I2 waits or uses an architecturally defined forward. |
| WAR | I0 reads R2; I2 writes R2 | I2 may not pass I0 without renaming; Aurora does not rename. |
| WAW | I0 and I2 both write R2 | Writes remain ordered. |
| Pair alias | I0 writes R2:R3; I2 reads R3 | Whole pair aliases both halves. |
| Accumulator | I0 folds A0; I2 reads/writes A0 | Respect accumulator feedback latency. |
| Flags | I0 writes flags; I2 reads or overwrites flags | Treat flags as an architectural register. |
| Stream | I0 consumes Q0; I2 consumes Q0 | Consumption remains ordered per stream. |

# 7. Issue Slots and Functional Resources

| Resource | Primary slot | Concurrent use | Notes |
|----|----|----|----|
| Scalar ALU / flags | A | One scalar op per cycle | L8/L16 read-modify-write uses same path. |
| Branch/control | A | May pair with independent Slot B work | Branch resolves in EX/MEM. |
| AGU | A or B by instruction | One architectural address launch per cycle baseline | Streams have private address state. |
| Load/store port | B | One memory operation launched per cycle baseline | Banked SRAM may sustain more internally. |
| Multiplier/compressor cluster | B | Pipelined initiation interval normally 1 | Long latency is scoreboarded. |
| Reduction tree | B | One DOT/SAD/REDUCE launch per cycle | Shared with relevant multiply reductions. |
| Divider | B | One outstanding divide baseline | Multi-cycle, non-pipelined baseline. |
| Stream engines Q0/Q1 | B | Independent engines may advance together when one instruction uses both | Per-stream order preserved. |

# 8. Scoreboard

The scoreboard tracks unavailable architectural destinations and outstanding resources. It is not a rename map.

- One busy bit per GPR plus pair alias expansion.

- Busy state for A0, A1, PSR flags, Q0 and Q1 visible/buffered state.

- Outstanding records for load, multiply, reduction, divide, paired-64 and other multi-cycle results.

- Each record stores destination mask, producing unit, completion age and fault state.

- Consumers may issue when the result is available through an approved forwarding path; otherwise they wait.

- A write to one half of a busy pair conflicts with the entire pair.

# 9. Forwarding and Bypass

| Path | Allowed | Baseline behavior |
|----|----|----|
| EX/MEM to next ID/RR | Yes | Single-cycle scalar ALU result may feed the next dependent instruction. |
| WB/RET to ID/RR | Yes | Normal writeback bypass. |
| Multiply/reduction completion | Yes when ready | Forward from completion bus; otherwise scoreboard stalls. |
| Load data | Profile-dependent timing | Minimum one completion cycle after memory response. |
| Pair result | Atomic pair forward | Both halves become available together. |
| Partial L8/L16 update | Whole-register forward | Merged 32-bit value is forwarded; no lane-granular scoreboard. |

# 10. Completion and Retirement

Execution may complete locally out of program order, but architectural retirement remains in program order.

- Non-faulting one-cycle register operations may write directly when no older potentially faulting instruction can invalidate them.

- Potentially faulting or multi-cycle operations retain a small completion record until they are safe to commit.

- A completion record is tied to a decoded-window age tag; it is not a general speculative reorder buffer.

- Stores become externally visible only in program order.

- A fault kills all younger instructions and completion records.

- At most two architectural instructions retire per cycle when both are complete and ordered.

# 11. Branch Prediction and Recovery

- Backward conditional branches are predicted taken; forward branches are predicted not taken.

- Unconditional direct control transfers are predicted taken when target formation is available.

- Branch resolution occurs in EX/MEM.

- On misprediction, younger decoded-window entries, issued noncommitted operations and prefetched words are invalidated.

- Committed stores or MMIO effects may never exist on a mispredicted path.

- The architectural branch penalty is the number of cycles required to redirect fetch and refill the decoded window; the exact value is implementation-profiled.

# 12. Memory Arbitration

The internal fabric arbitrates instruction fetch, scalar loads/stores, Q0/Q1, DMA and external-memory traffic.

- ITCM and DTCM have dedicated core-facing paths when implemented.

- General SRAM is banked and interleaved at native 16-bit word granularity.

- CPU retirement-critical accesses receive bounded priority over background DMA.

- Stream refill may receive deterministic reservations to sustain DSP kernels.

- DMA may use remaining bandwidth and explicit burst grants.

- MMIO is strongly ordered and acts as an issue/retirement barrier.

- External ready/acknowledge targets may insert wait states; outstanding accesses remain scoreboarded.

# 13. Stream and DMA Coherence

- Q0/Q1 and DMA use physical addresses from the unified address map.

- Software owns buffer handoff. DMA completion and stream consumption are synchronized through explicit status and barriers.

- A simultaneous QPUSH/QPOP replacement may be optimized internally without spilling the unchanged queue depth.

- Stream configuration changes serialize later stream-consuming instructions.

- Register-only operations naming R0/R4 do not consume streams.

- Circular addressing updates are atomic with the associated stream transfer.

# 14. Precise Interrupt and Exception Behavior

- Interrupt recognition occurs between architectural retirement groups.

- A higher-priority interrupt may be recognized once all older instructions are retired or safely restartable.

- Younger decoded entries are discarded on interrupt entry.

- Outstanding nonfaulting operations may either complete before entry or be canceled and restarted according to their documented class.

- Stores and MMIO writes must be retired before the interrupt frame is exposed.

- Hardware saves at least PC and PSR; ASC or the handler saves additional state.

- The maximum recognition delay is bounded by the longest non-abortable operation; long-latency units should provide abort/restart points where practical.

- Stream and accumulator extended state may be lazily saved using dirty bits.

# 15. Multi-Cycle and Abort Policy

| Operation class | Abortable? | Interrupt policy | Restart behavior |
|----|----|----|----|
| Scalar ALU / shuffle | N/A | Retire immediately | No restart needed |
| Load | Yes before commit | Cancel outstanding request if fabric permits | Restart from instruction PC |
| Store/MMIO | No after acceptance | Retire before interrupt | Never duplicate visible write |
| Multiply/reduction | Implementation choice | Finish or checkpoint | Precise restart if canceled |
| Divide | Recommended checkpoint/abort | Bound recognition delay | Restart or resume from hidden state |
| Paired-64 shift/ALU | Recommended abortable between internal steps | Short bounded delay | Restart whole instruction |

# 16. Determinism Requirements

- Every instruction class has a documented minimum and maximum latency.

- Dynamic pairing decisions are deterministic for a given machine state and instruction sequence.

- Arbitration policies are fixed or configured through privileged state, not randomized.

- Worst-case interrupt recognition includes current instruction completion, retirement, vector fetch and ASC entry.

- Optional profiles may improve average performance but must publish worst-case timing.

- Compiler scheduling never changes architectural correctness; hardware lookahead only selects legal independent pairs.

# 17. Baseline Timing Targets

| Class | Latency target | Initiation interval | Comment |
|----|----|----|----|
| Scalar ALU / compare / layout | 1 | 1 | Forwardable |
| Branch | 1 resolve | 1 | Refill penalty profile-dependent |
| Load from TCM | 2 | 1 | Address plus return/writeback |
| Store to TCM | 1 launch | 1 | Retires in order |
| Packed add/logic | 1 | 1 | Mode-controlled |
| Multiply/MAC | 3 | 1 | Scoreboarded pipeline |
| DOT/SAD | 3 | 1 | Shared reduction infrastructure |
| REDUCE | 2 | 1 | Operator-specific fold supported |
| Paired-64 shift | 2+ | 1 or 2 | Reuse 32-bit shifter |
| Divide | Implementation target 8-32 | Same as latency baseline | Radix-step implementation |

# 18. RTL Partitioning Recommendation

- front_end: fetch, prefetch, branch prediction and extension-word assembly

- issue_window: four entries, dependency comparators, partner selection and compaction

- regfile: 16 x 32 with two read ports and planned writeback arbitration

- slot_a: scalar ALU, control and selected layout operations

- slot_b: LSU, multiplier, divider, reduction and stream dispatch

- scoreboard: destination/resource busy tracking and completion tags

- completion: multi-cycle result/fault capture and ordered commit gating

- memory_fabric: TCM, banked SRAM, MMIO, DMA and external arbitration

- interrupt_unit: priority encoder, retirement boundary recognition and vector entry

# 19. Verification Requirements

- Exhaustive RAW/WAR/WAW tests across all four window positions.

- Random legal/illegal pairing tests with resource and flag conflicts.

- Branch misprediction tests with outstanding noncommitted operations.

- Precise fault tests for loads, stores, MMIO and privileged instructions.

- Interrupt injection at every pipeline stage and every multi-cycle operation phase.

- Pair alias and L8/L16 whole-register hazard tests.

- Q0/Q1 order, peek/consume and circular-boundary tests.

- DMA/CPU/stream arbitration and memory-barrier tests.

- Cycle-accurate comparison against the machine-readable ISA database.

# 20. Freeze Checklist

PASS - Four stages and their boundaries defined.

PASS - Four-entry dynamic pairing and compaction defined.

PASS - No renaming / no general ROB policy defined.

PASS - Scoreboard and completion records defined.

PASS - Forwarding and pair alias behavior defined.

PASS - Branch prediction and recovery defined.

PASS - Memory and stream arbitration principles defined.

PASS - Precise interrupt and abort behavior defined.

PASS - Baseline timing targets and verification requirements defined.
