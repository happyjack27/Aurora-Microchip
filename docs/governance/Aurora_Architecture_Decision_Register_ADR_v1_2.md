This register assigns a permanent Architecture Decision Record (ADR) identifier to every major architectural choice. Other documents should reference ADR IDs instead of repeating rationale.

# ADR Lifecycle

- Proposed

- Accepted

- Frozen

- Superseded

- Deprecated

# ADR Index

| ADR ID | Decision | Status | Primary Document | Notes |
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

# Referencing Rules

- All architecture documents should cite ADR IDs when discussing rationale.

- Implementation documents should reference ADRs instead of duplicating design justification.

- Superseded ADRs remain in the register for historical traceability.

- Each ADR should eventually expand into its own section in the Architecture Bible.

# Long-Term Goal

Expand each ADR into a full Architecture Decision Record containing: Problem, Alternatives, Decision, Tradeoffs, Consequences, Related ADRs, Affected Documents, and Revision History.
