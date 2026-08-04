**AUR-RTL-002B Decode & Issue Window**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Decode fetched Aurora instructions, form complete instructions with extension words, maintain the four-entry decoded window, select up to two legal instructions each cycle, and compact/refill the window while preserving program order.

# 2. External Ports

| Signal | Dir | Width | Meaning |
|----|----|----|----|
| clk_i | in | 1 | Core clock |
| rst_i | in | 1 | Synchronous reset |
| fetch_valid_i | in | 2 | Up to two fetched base/extension words available |
| fetch_word0_i/fetch_word1_i | in | 16 each | Fetched words |
| fetch_pc0_i/fetch_pc1_i | in | 32 each | Associated PCs |
| fetch_ready_o | out | 1 | Front end may send words |
| mode_i | in | 3 | Current arithmetic mode |
| scoreboard_busy_i | in | resource masks | Busy destinations/resources |
| forward_ready_i | in | resource masks | Operands available through bypass |
| issue_ready_i | in | 2 | Execution lanes able to accept |
| issue0_o/issue1_o | out | decoded op | Selected instructions |
| issue_valid_o | out | 2 | Issue valid bits |
| flush_i | in | 1 | Branch/exception/interrupt flush |
| flush_pc_i | in | 32 | Recovery PC |
| window_state_o | out | debug | Optional trace/debug visibility |

# 3. Window Entry State

| Field | Width | Use |
|----|----|----|
| valid | 1 | Entry contains a decoded instruction |
| pc | 32 | Base instruction PC |
| length_words | 2 | 1-3 instruction words |
| opcode/subop | implementation | Decoded operation |
| src_mask | resource mask | GPR/pair/flags/accumulator/stream sources |
| dst_mask | resource mask | Architectural destinations |
| unit_mask | resource mask | ALU, LSU, multiplier, reduction, divider, stream, branch |
| may_fault | 1 | Potentially faulting/serializing |
| barrier_class | enum | Memory, MMIO, control, privileged, stream-config |
| age | 2 | Program-order index after compaction |

# 4. Decode Rules

- Base opcode is bits 15:12.

- Extension escape 0xE attaches to the immediately preceding base instruction.

- Layout operations carry ignores_lane_mask=1 and does_not_consume_stream=1.

- Paired-64 destinations require legal even pairs; R14/R15 may be zero-extended sources only.

- R12:R13 destination legality depends on LR-live metadata from the compiler-visible call state and dynamic scoreboard.

# 5. Pair Selection Algorithm

anchor = oldest valid, unissued, ready entry\
partner = none\
for candidate in entries younger than anchor, oldest first:\
if conflicts(candidate, anchor): continue\
if conflicts(candidate, any skipped older entry): continue\
if resource_capacity(anchor + candidate) exceeded: continue\
if candidate crosses barrier/control/memory ordering rule: continue\
partner = candidate\
break\
issue anchor\
if partner != none: issue partner\
compact remaining entries in original order\
refill up to number issued

# 6. Conflict Function

- RAW: younger source intersects older destination.

- WAR: younger destination intersects older source.

- WAW: destinations intersect.

- Pair alias expands to both halves.

- Flags, A0/A1, Q0/Q1 and control state are explicit resources.

- Only one unresolved branch, one MMIO, and one serializing privileged operation may issue in a group.

# 7. Timing

| Path | Target |
|----|----|
| Decode + mask generation | Within ID/RR stage |
| Four-entry dependency comparison | Single cycle |
| Partner select + compaction control | Single cycle |
| Flush | Clear all younger entries on next edge |

# 8. Assertions

- No two issued instructions have RAW/WAR/WAW conflict.

- Unissued entries preserve program order after compaction.

- At most two entries issue per cycle.

- An extension word is never visible as an independent instruction.

- No instruction crosses a serializing barrier illegally.

- Flush removes all younger window entries.

# 9. Verification

| Test                             | Method                        |
|----------------------------------|-------------------------------|
| All 4-entry pairing combinations | Directed + constrained random |
| Extension-word boundaries        | Directed                      |
| Flush during one/two issue       | Directed                      |
| Pair alias hazards               | Exhaustive                    |
| Barrier crossing                 | Formal property               |
