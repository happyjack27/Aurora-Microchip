**Aurora v1.2 RTL Architecture Specification**

*AUR-RTL-001 \| Canonical Draft 1*

# 1. Module Hierarchy

| Module | Responsibility |
|----|----|
| aurora_core_top | Top-level core integration |
| aurora_front_end | Fetch, prefetch, branch prediction, extension assembly |
| aurora_issue_window | Four-entry decode window, selection, compaction |
| aurora_regfile | 16 x 32 register file and writeback arbitration |
| aurora_lane0 / aurora_lane1 | Symmetric general execution lanes |
| aurora_lsu | Load/store unit and address generation |
| aurora_mul_reduce | Multiplier, compressor and reduction resources |
| aurora_divider | Multi-cycle divider |
| aurora_stream_q0/q1 | Stream state, staging, circular addressing |
| aurora_scoreboard | Busy state and completion tags |
| aurora_commit | In-order retirement and precise fault handling |
| aurora_interrupt | Priority arbitration and vector entry |
| aurora_memory_fabric | TCM/SRAM/MMIO/DMA/external arbitration |

# 2. Interface Rules

- Ready/valid request-response interfaces between decoupled units

- Explicit age tags for issued/completion records

- No combinational path from external ready to fetch critical control

- Symmetric lane dispatch; shared resources selected by resource masks

- Pair destinations write both halves atomically

# 3. Clock and Reset

- Single core clock baseline; optional peripheral/timer clock domains

- Synchronous active-high internal reset preferred

- All cross-domain status signals synchronized

- Timer and DMA domains must not create variable interrupt semantics

# 4. Coding and Synthesis Rules

- SystemVerilog synthesizable subset

- No inferred latches

- Parameterized SRAM/TCM interfaces

- Assertions for protocol, ordering and pair-alias rules

- Generated constants from the machine-readable ISA database
