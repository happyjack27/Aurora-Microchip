**Aurora Documentation Decision Register**

*AUR-PM-008 \| DDR v1.2*

Documentation Decision Records govern why the document set is organized the way it is.

| DDR ID | Decision | Status | Rationale |
|----|----|----|----|
| DDR-0001 | Adopt stable document IDs | Frozen | Enables cross-reference and lifecycle tracking. |
| DDR-0002 | Architecture Bible is canonical rationale source | Frozen | Avoids duplicated rationale. |
| DDR-0003 | Machine-readable ISA is canonical encoding source | Frozen | Prevents assembler/RTL/doc drift. |
| DDR-0004 | Separate RTL, simulator, FPGA and ASIC documents | Frozen | Different audiences and lifecycle. |
| DDR-0005 | Split inside-chip, system-context and signal-interface documents | Frozen | Separates logical/physical core, SoC integration and board-facing interfaces. |
| DDR-0006 | Maintain document outline database | Frozen | Tracks internal structure and completion. |
| DDR-0007 | Maintain requirements traceability database | Frozen | Links needs to ADRs, specs and tests. |
| DDR-0008 | Maintain topic index | Accepted | Supports cross-document navigation by subject. |
