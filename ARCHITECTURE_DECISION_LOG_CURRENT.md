**Current consolidated preservation copy • August 3, 2026**

# Purpose and Authority

This preservation copy combines the original ADR register, standalone later ADRs, and late-session decisions that were not yet assigned permanent ADR numbers. Newer records supersede conflicting older wording.

# Original ADR Register

| **ADR ID** | **Decision** | **Status** | **Primary document** | **Notes** |
|----|----|----|----|----|
| ADR-0001 | Mission: MCU + low/mid DSP consolidation | Frozen | AUR-ARCH-001 | Core product identity |
| ADR-0002 | 16-bit base ISA | Frozen | AUR-ARCH-001 | Extension words for larger encodings |
| ADR-0003 | 16 unified 32-bit GPRs | Frozen | AUR-ARCH-001 | Unified register file |
| ADR-0004 | Paired-register 64-bit emulation | Frozen | AUR-ARCH-001 | No native 64-bit core |
| ADR-0005 | R13 LR, R14 SP, R15 PC | Frozen | AUR-ARCH-003 | Conditional LR allocation |
| ADR-0006 | 40-bit accumulators A0/A1 | Frozen | AUR-ARCH-001 | DSP accumulators |
| ADR-0007 | Q0/Q1 stream engines | Frozen | AUR-ARCH-001 | Overlay on R0/R4 |
| ADR-0008 | Packed modes + L8/L16 | Frozen | AUR-ARCH-001 | Lane-preserving modes |
| ADR-0009 | Four-stage pipeline | Frozen | AUR-ARCH-007 | In-order |
| ADR-0010 | Four-entry pairing window | Frozen | AUR-ARCH-007 | Compiler-assisted |
| ADR-0011 | Symmetric dual-issue lanes | Frozen | AUR-ARCH-007 | Shared execution resources |
| ADR-0012 | No renaming / no ROB | Frozen | AUR-ARCH-007 | Deterministic execution |
| ADR-0013 | Backward-taken predictor | Frozen | AUR-ARCH-007 | Simple branch prediction |
| ADR-0014 | Optional ITCM/DTCM | Frozen | AUR-ARCH-006 | Profile-scalable memory |
| ADR-0015 | Single countdown timer | Frozen | AUR-ARCH-006 | Software multiplexing |
| ADR-0016 | Compiler-first scheduling | Frozen | AUR-TOOL-001 | Hardware repairs locally |
| ADR-0017 | Machine-readable ISA as source of truth | Frozen | AUR-ARCH-004 | Generates tools/docs |

# Standalone Later ADR Records

| **ID** | **Record title** | **Current status** | **Repository file** | **Supersession / notes** |
|----|----|----|----|----|
| ADR-2DSTREAM-001 | ADR-2DSTREAM-001 — Sticky MODE Instruction and Two-Dimensional Stream Stepping | Locked/Accepted | architecture-records/ADR_2DSTREAM_001_MODE_and_2D_Stream_Stepping.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-SYS-002 | ADR-SYS-002 — Privilege, Wait/Halt, and Context Transfer Architecture | LOCKED | architecture-records/ADR-SYS-002_Privilege_Wait_Halt_and_Context_Transfer.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-ISA-019 | ADR-ISA-019 — Extension Instructions and Stream/Stack Bounds Faults | LOCKED | architecture-records/ADR-ISA-019_Extension_and_Bounds_Faults.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-ISA-020 | ADR-ISA-020 — NOP-Terminated Hardware Loop | LOCKED | architecture-records/ADR-ISA-020_NOP_Terminated_Hardware_Loop.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-STREAM-006 | ADR-STREAM-006 — Pinned Circular Stream Mode | LOCKED | architecture-records/ADR-STREAM-006_Pinned_Circular_Stream_Mode.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-DSP-011 | ADR-DSP-011 — Complex Multiply Mode and Widened Result Layout | LOCKED | architecture-records/ADR-DSP-011_Complex_Multiply_Mode_and_Widened_Layout.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-DSP-012 | ADR-DSP-012 — COMPLEX16 Result Width and Overflow Handling | LOCKED | architecture-records/ADR-DSP-012_COMPLEX16_Result_Width_and_Overflow.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-DSP-013 | ADR-DSP-013 — Multiply Width and Interpretation Mode Bits | LOCKED | architecture-records/ADR-DSP-013_Multiply_Width_and_Interpretation_Mode_Bits.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-DSP-014 | ADR-DSP-014 — Rounding and Saturation Mode Bits | LOCKED | architecture-records/ADR-DSP-014_Rounding_and_Saturation_Mode_Bits.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-DSP-015 | ADR-DSP-015 — COMPLEX8 Packed Multiply Mode | LOCKED | architecture-records/ADR-DSP-015_COMPLEX8_Packed_Multiply_Mode.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-DSP-016 | ADR-DSP-016 — Unary Complex Conjugate Instruction | LOCKED | architecture-records/ADR-DSP-016_Unary_Complex_Conjugate_Instruction.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-MEM-009 | ADR-MEM-009 — Required Near-Memory DMA and Reduction/Stream Separation | LOCKED | architecture-records/ADR-MEM-009_Required_Near_Memory_DMA_and_Separation.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-ISA-021 | ADR-ISA-021 — Contextual ZR, Unified Compare, and Packed Predicate Flags | LOCKED | architecture-records/ADR-ISA-021_Contextual_ZR_Unified_Compare_and_Predicates.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-STREAM-007 | ADR-STREAM-007 — Explicit Stream Access and Side-Effect-Free Moves | Partially superseded | architecture-records/ADR-STREAM-007_Explicit_Stream_Access_and_Pure_Moves.docx | Pure MOV/CMOV rule retained; stream-access exclusivity superseded by ADR-STREAM-008. |
| ADR-STREAM-008 | ADR-STREAM-008 — Implicit Stream Access for Stream-Capable Computation | LOCKED — SUPERSEDES CONFLICTING PORTIONS OF ADR-STREAM-007 | architecture-records/ADR-STREAM-008_Implicit_Stream_Access_for_Computation.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-FE-006 | ADR-FE-006 — Two-Entry Prefetch Buffer and Eight-Word Hardware Loop | LOCKED | architecture-records/ADR-FE-006_Two_Entry_Prefetch_and_Eight_Word_Loop.docx | Standalone record preserved in decision-logs/architecture-records. |
| ADR-STREAM-009 | ADR-STREAM-009 — POPMETA Opcode Allocation | LOCKED | architecture-records/ADR-STREAM-009_POPMETA_Opcode_Allocation.md | Allocates opcode 0xB9 (format STREAM_POPMETA); supersedes ADR-STREAM-008's "reserved, not allocated" clause. isa/database updated to match. |
| ADR-DSP-017 | ADR-DSP-017 — TRACKMIN/TRACKMAX Fused Compare-and-Track | PROPOSED — OPEN, NOT LOCKED | architecture-records/ADR-DSP-017_TRACKMIN_TRACKMAX_Fused_Compare_and_Track.md | Formal tracking of an explicitly undecided question; no opcode/encoding chosen yet. |
| ADR-ISA-022 | ADR-ISA-022 — LOOPR Register-Count Hardware Loop and AGU Retirement | LOCKED | architecture-records/ADR-ISA-022_LOOPR_Register_Count_Hardware_Loop_and_AGU_Retirement.md | Retires AGUCFG(0xC2)/STRIDE(0xC3); allocates LOOPR at 0xC2 (format LOOP_REG). isa/database updated to match. |
| ADR-DSP-018 | ADR-DSP-018 — MAC/MAS Accumulator Operand Typing | LOCKED (typing + encoding) | architecture-records/ADR-DSP-018_MAC_MAS_Accumulator_Operand_Typing.md | Corrects MAC/MAS operand 0 from GPR dst to accumulator selector; accumulator-selector bit (11, freed from RRR_OR_ACC's subop) resolved 2026-08-04, format RRR_ACC. |

# Late-Session Decisions Pending Formal ADR Numbering

| **Provisional ID** | **Decision** | **Status** | **Source** | **Notes** |
|----|----|----|----|----|
| LATE-STREAM-POPMETA | POPMETA aligned-pair stream consume with value + ORD/ADDR metadata | Superseded by ADR-STREAM-009 | RECENT_DECISIONS_SNAPSHOT.md | Promoted 2026-08-04: opcode 0xB9 allocated, isa/database updated. See ADR-STREAM-009. |
| LATE-DSP-TRACK | Fused TRACKMIN/TRACKMAX compare-and-track pair operation | Promoted to ADR-DSP-017 (still open) | RECENT_DECISIONS_SNAPSHOT.md | Not baseline; compare against POPMETA + CMP + two CMOVs. See ADR-DSP-017 for the tracked open decision. |
| LATE-FE-REPLAY | Resident replay for short backward-relative branches in the eight-word front-end window | Locked | RECENT_DECISIONS_SNAPSHOT.md | Target derived from relative offset; no refetch on hit. |
| LATE-FE-SINGLEENTRY | Compiler-enforced single-entry rule for resident-replay regions | Locked | RECENT_DECISIONS_SNAPSHOT.md | Hardware does not detect or enforce interior entry. |
| LATE-FE-LOOPROLE | Explicit hardware loops retained alongside resident replay | Locked | RECENT_DECISIONS_SNAPSHOT.md | Hardware loop removes decrement/test/branch and final-exit misprediction. |
| LATE-SCHED-001 | Priority-first EDF scheduler with optional latest-safe-start ordering | Design locked | code/programs/scheduler/README.md | Higher priority first; within priority EDF or finish-deadline minus estimated remaining execution. |
| LATE-SCHED-002 | Dependency urgency inheritance and mandatory latest-safe-start preemption | Design locked | code/programs/scheduler/README.md | Inherit highest blocked priority, then earliest urgency at that priority. |
| LATE-RED-COUNT | Comparison-count reduction | Not locked | RECENT_DECISIONS_SNAPSHOT.md | Explicitly retained only as a candidate. |

Governance note: provisional entries are preserved as decisions but should receive permanent ADR identifiers in the next reconciliation pass.
