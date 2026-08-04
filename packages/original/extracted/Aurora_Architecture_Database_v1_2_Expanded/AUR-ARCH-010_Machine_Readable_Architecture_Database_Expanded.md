**Aurora v1.2 Machine-Readable Architecture Database**

*AUR-ARCH-010 \| Expanded Canonical Specification*

# 1. Purpose

Define one authoritative data model for architecture facts shared by documentation, assembler, compiler, simulator, RTL, verification, and product profiles.

# 2. Canonical Domains

- Core architecture and pipeline

- Registers and paired-64 rules

- Modes and lane behavior

- Execution resources and capacities

- Streams and accumulators

- Timers and interrupts

- Memory regions and exceptions

- RTL interface bundles

- Requirements and verification links

- Aurora-L/M/P profile overrides

# 3. Generated Artifacts

| Artifact | Use |
|----|----|
| aurora_architecture_v1_2.json | Canonical architecture database |
| aurora_architecture_schema_v1_0.json | Structural validation schema |
| aurora_arch_pkg.sv | Shared SystemVerilog modes, exceptions and bundles |
| aurora_arch_v1_2.h | C constants for SDK/tooling |
| aurora_arch_constants.py | Simulator/reference-model constants |
| CSV exports | Resources, memory map and requirements |
| validate_architecture_database.py | Project invariant checks |

# 4. Architectural Invariants Enforced

- Exactly sixteen architectural GPRs.

- Two-wide issue with a four-entry lookahead window.

- In-order retirement with no register renaming or general ROB.

- Seven aligned writable register pairs; SP and PC are source-only in paired-64 mode.

- Two stream engines and two 40-bit accumulators.

- One coarse OS-managed countdown timer.

- No dedicated full divider resource; division uses DIVSTEP.

- MMIO remains strongly ordered.

# 5. Traceability

| Requirement | Statement | Database Domain | Verification |
|----|----|----|----|
| REQ-0001 | Architectural retirement shall be in order. | architecture/resources/interfaces | commit_order_property |
| REQ-0002 | Either issue lane may execute ordinary ALU-class instructions. | architecture/resources/interfaces | lane_symmetry_test |
| REQ-0003 | DIV shall not require a dedicated full divider. | architecture/resources/interfaces | divstep_only_decode_property |
| REQ-0004 | Stream consumption shall remain ordered per stream. | architecture/resources/interfaces | stream_order_property |
| REQ-0005 | MMIO transactions shall remain strongly ordered. | architecture/resources/interfaces | mmio_order_property |

# 6. Governance

- Encoding changes originate in the ISA database and propagate here.

- Architecture changes require an ADR before database modification.

- Documentation-structure changes require a DDR.

- Generated files must not be hand-edited.

- CI must run schema and invariant validation before accepting changes.
