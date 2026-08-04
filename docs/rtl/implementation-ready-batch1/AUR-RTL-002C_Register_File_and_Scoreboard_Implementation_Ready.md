**AUR-RTL-002C Register File & Scoreboard**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Provide architectural register storage, reads, writes, pair aliasing, whole-register L8/L16 merge semantics, and busy/completion tracking for all outstanding operations.

# 2. Register File Organization

- 16 x 32-bit architectural GPRs.

- Two combinational or registered read ports minimum; two architectural writebacks per cycle target.

- R13 is LR plus conditional GPR; R14 SP; R15 PC.

- R8/R10 expose accumulator low 32-bit views.

- Paired writes update both halves atomically.

# 3. Ports

| Signal | Dir | Width | Meaning |
|----|----|----|----|
| ra0_i, rb0_i, ra1_i, rb1_i | in | 4x4 | Source register indices for two issued instructions |
| rdata\_\*\_o | out | 4x32 | Read data |
| wb0_valid_i/wb1_valid_i | in | 2 | Writeback valids |
| wb\*\_rd_i | in | 4 | Destination register |
| wb\*\_data_i | in | 32 | Writeback data |
| wb\*\_mask_i | in | 4 | Byte write mask for L8/L16/full writes |
| pair_wb_i | in | pair bundle | Atomic paired result |
| busy_set_i/busy_clear_i | in | resource masks | Scoreboard updates |
| busy_o | out | resource masks | Current hazards |

# 4. Write Arbitration

- Two unrelated scalar writes may commit together.

- A paired write consumes both architectural write slots unless implemented with a dedicated pair port.

- If both writes target the same register, the older architectural write wins first; younger commit waits.

- L8/L16 writes read old destination and merge by byte mask before architectural commit.

- R15 writes only from control/retirement path; ordinary GPR write attempts trap or are blocked.

# 5. Scoreboard Resources

| Resource        | Storage    | Rule                                   |
|-----------------|------------|----------------------------------------|
| GPR busy        | 16 bits    | One per register                       |
| Pair busy       | derived    | OR of both halves; writes reserve both |
| A0/A1           | 2 bits     | Accumulator result not ready           |
| Flags           | 1 bit      | PSR arithmetic flags pending           |
| Q0/Q1           | 2 bits     | Stream state/data pending              |
| LSU/MUL/RED/DIV | unit state | Outstanding shared resource            |

# 6. Merge Semantics

full: new = result\
L16: new = (old & 0xFFFF0000) \| (result & 0x0000FFFF)\
L8: new = (old & 0xFFFFFF00) \| (result & 0x000000FF)

# 7. Forwarding

- EX result may bypass next-cycle reads.

- Completion-bus results bypass once ready.

- Pair forwarding presents both halves atomically.

- Partial writes forward the merged 32-bit value, never an isolated lane.

# 8. Assertions

- No architectural register changes without a committed write.

- R14/R15 cannot be paired destinations.

- Pair busy implies both halves unavailable.

- Partial write preserves all masked-off bytes.

- Simultaneous writes cannot create ambiguous final state.
