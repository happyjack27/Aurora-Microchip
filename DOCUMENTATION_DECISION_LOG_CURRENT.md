**Current consolidated preservation copy • August 3, 2026**

# Purpose and Authority

This preservation copy combines the original Documentation Decision Register and every later DDR artifact located in the project files. Missing identifiers are explicitly noted rather than reconstructed.

# Original Documentation Decision Register

| **DDR ID** | **Decision** | **Status** | **Rationale** |
|----|----|----|----|
| DDR-0001 | Adopt stable document IDs | Frozen | Enables cross-reference and lifecycle tracking. |
| DDR-0002 | Architecture Bible is canonical rationale source | Frozen | Avoids duplicated rationale. |
| DDR-0003 | Machine-readable ISA is canonical encoding source | Frozen | Prevents assembler/RTL/doc drift. |
| DDR-0004 | Separate RTL, simulator, FPGA and ASIC documents | Frozen | Different audiences and lifecycle. |
| DDR-0005 | Split inside-chip, system-context and signal-interface documents | Frozen | Separates logical/physical core, SoC integration and board-facing interfaces. |
| DDR-0006 | Maintain document outline database | Frozen | Tracks internal structure and completion. |
| DDR-0007 | Maintain requirements traceability database | Frozen | Links needs to ADRs, specs and tests. |
| DDR-0008 | Maintain topic index | Accepted | Supports cross-document navigation by subject. |

# Later Documentation Decision Records

| **DDR ID** | **Record title** | **Current status** | **Repository file** | **Supersession / notes** |
|----|----|----|----|----|
| DDR-0046 | Aurora Documentation Decision Register — Addendum | Locked/Accepted | documentation-records/AUR-PM-008_DDR_Addendum_0046_Instruction_Bytecodes.docx | Standalone documentation decision preserved. |
| DDR-0047 | DDR-0047 — Document MODE and Two-Dimensional Stream Configuration | Locked/Accepted | documentation-records/DDR-0047_MODE_and_2D_Stream_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0048 | DDR-0048 — Document Privilege, Wait/Halt, and Context Transfer Instructions | LOCKED | documentation-records/DDR-0048_Privilege_Wait_Halt_and_Context_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0049 | DDR-0049 — Document Extension and Bounds-Fault Semantics | LOCKED | documentation-records/DDR-0049_Extension_and_Bounds_Fault_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0050 | DDR-0050 — Hardware Loop Documentation and Terminology | LOCKED | documentation-records/DDR-0050_Hardware_Loop_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0051 | DDR-0051 — Pinned Stream Documentation | LOCKED | documentation-records/DDR-0051_Pinned_Stream_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0052 | DDR-0052 — Complex Multiply Mode Documentation | LOCKED | documentation-records/DDR-0052_Complex_Multiply_Mode_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0053 | DDR-0053 — COMPLEX16 Overflow Documentation Revision | LOCKED | documentation-records/DDR-0053_COMPLEX16_Overflow_Documentation_Revision.docx | Standalone documentation decision preserved. |
| DDR-0054 | DDR-0054 — Multiply Mode-Bit Documentation | LOCKED | documentation-records/DDR-0054_Multiply_Mode_Bit_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0055 | DDR-0055 — Rounding and Saturation Documentation | LOCKED | documentation-records/DDR-0055_Rounding_and_Saturation_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0056 | DDR-0056 — COMPLEX8 Documentation | LOCKED | documentation-records/DDR-0056_COMPLEX8_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0057 | DDR-0057 — CONJ Instruction Documentation | LOCKED | documentation-records/DDR-0057_CONJ_Instruction_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0058 | DDR-0058 — DMA and Reduction/Stream Documentation | LOCKED | documentation-records/DDR-0058_DMA_and_Separation_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0059 | DDR-0059 — ZR, Compare Aliases, and Packed Predicate Documentation | LOCKED | documentation-records/DDR-0059_ZR_Compare_and_Predicate_Documentation.docx | Standalone documentation decision preserved. |
| DDR-0060 | DDR-0060 — Explicit Stream Access Documentation | Partially superseded | documentation-records/DDR-0060_Explicit_Stream_Access_Documentation.docx | Superseded by DDR-0061 where it claimed only POP/PUSH/PEEK could access streams; pure MOV/CMOV documentation remains valid. |
| DDR-0061 | DDR-0061 — Corrected Stream-Access Documentation Rule | LOCKED | documentation-records/DDR-0061_Corrected_Stream_Access_Documentation_Rule.docx | Standalone documentation decision preserved. |
| DDR-0062 | DDR-0062 — Prefetch and Hardware-Loop Window Documentation | LOCKED | documentation-records/DDR-0062_Prefetch_and_Hardware_Loop_Window_Documentation.docx | Standalone documentation decision preserved. |

Missing-number note: DDR-0009 through DDR-0045 were not found in the available artifacts and are not invented in this consolidation.
