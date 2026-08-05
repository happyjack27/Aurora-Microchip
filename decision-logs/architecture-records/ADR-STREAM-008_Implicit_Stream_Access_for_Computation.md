Status: LOCKED — SUPERSEDES CONFLICTING PORTIONS OF ADR-STREAM-007\
Architecture baseline: Aurora v1.2r\
Date: August 3, 2026

# Canonical Rule

Stream access is implicit when a stream-capable arithmetic, packed, multiply, MAC/MAS, or reduction instruction selects Q0 or Q1 as an operand or destination. Standalone POP, PUSH, and PEEK remain explicit stream-transfer instructions. MOV and CMOV are pure GPR operations and never consume, produce, peek, or otherwise access stream state.

# Locked Decisions

- Q0 and Q1 are architectural stream operands available only to instruction classes whose definitions explicitly mark them stream-capable.

- For a stream-capable instruction, naming Qn as a source implicitly consumes exactly one logical stream transfer from Qn.

- For a stream-capable instruction, naming Qn as a destination implicitly produces exactly one logical stream transfer to Qn.

- Stream consume/produce is part of the arithmetic or reduction instruction itself; no preceding POP or following PUSH is required.

- Standalone POP, PUSH, and PEEK remain available for cases that need an explicit transfer without a simultaneous arithmetic or reduction operation.

- MOV is GPR-to-GPR only. MOV cannot name Q0/Q1 and cannot access stream metadata.

- CMOV is GPR-to-GPR only. CMOV cannot name Q0/Q1, and its true and false paths have identical stream, memory, MMIO, address, count, ordinal, and exception side effects.

- Packed lane-wise CMOV consumes only existing predicate state and GPR values; it never conditionally advances a stream.

- Arithmetic and DSP formats are biased toward stream sources and accumulator destinations. Encoding priority is consume/reduce first, GPR-result forms second, and stream-producing forms where useful and affordable.

- One-source reductions may select one GPR or one stream source and write only A0 or A1.

- Two-source reductions such as DOT, SAD, and comparison-count may select supported GPR/stream source combinations; paired Q0/Q1 consumption receives highest stream-form priority.

- The A0/A1 accumulator is an explicit destination selector and an implicit source only when the reduction's ACC bit is set. INIT replaces/initializes the selected accumulator.

- A stream-capable instruction that names two stream sources consumes both atomically: either both transfers and the arithmetic result retire, or neither stream advances.

- A stream-capable instruction with a stream destination produces only after successful completion. On fault, no stream source, stream destination, GPR, accumulator, predicate, address, count, or ordinal state is partially updated.

- PEEK never advances stream state. It remains the only standalone non-consuming stream-data transfer.

- ADDR_NEXT, ADDR_LAST, ORD_NEXT, and ORD_LAST remain system registers accessed through system-register transfer instructions.

- POPMETA Rd:Rd+1, Qn, meta remains reserved, not allocated. If later adopted, it uses an aligned register-pair destination and atomically returns popped data plus selected metadata.

- The statement in ADR-STREAM-007 that all stream transfer is only through POP/PUSH/PEEK is withdrawn and must not be repeated.

- R13 remains an optional link register. Compiler call analysis may allocate R13 as a GPR in leaf functions or whenever the return address is saved or dead.

# Examples

ADD R4, Q0, R5 ; implicitly consume Q0, write R4\
ADD Q1, Q0, R5 ; implicitly consume Q0 and produce Q1\
REDUCE.ADD A0, Q0, ACC ; implicitly consume Q0 and accumulate into A0\
DOT A1, Q0, Q1, ACC ; atomically consume Q0 and Q1\
POP R4, Q0 ; explicit standalone consume\
PEEK R5, Q0 ; explicit non-consuming read\
PUSH Q1, R6 ; explicit standalone produce\
\
MOV R4, Q0 ; illegal\
CMOV.GT R4, Q0 ; illegal\

# Amendment (August 4, 2026): ORD_NEXT/ORD_LAST retired, POPMETA narrowed

`ORD_NEXT` and `ORD_LAST` are withdrawn; only `ADDR_NEXT` and `ADDR_LAST` remain as stream position system registers. `POPMETA Rd:Rd+1, Qn, meta` (allocated by ADR-STREAM-009) no longer takes a `meta` operand — it always returns the popped element's address in `Rd+1`. See the ADR-STREAM-009 amendment for the encoding change.
CMOV.GT Q1, R4 ; illegal

# Rationale

Aurora is stream-first. Folding stream transfers into computation removes redundant data-movement instructions and lets short hardware loops perform consume/compute/reduce efficiently. Keeping MOV and CMOV pure prevents data-dependent stream alignment and preserves deterministic side effects.
