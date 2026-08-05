Status: LOCKED — SUPERSEDES THE "RESERVED, NOT ALLOCATED" CLAUSE OF ADR-STREAM-008\
Architecture baseline: Aurora v1.2s\
Date: August 4, 2026

# Decision

- `POPMETA Rd:Rd+1, Qn, meta` is allocated a real opcode: primary `0xB` (STREAM), subop `9` (`0xB9`), format `STREAM_POPMETA`.

- `Rd:Rd+1` is an aligned register pair. `Rd` receives the popped stream value; `Rd+1` receives the selected metadata word.

- `meta` selects which metadata is returned: `ORD` (the popped element's ordinal, equivalent to reading `Qn.ORD_LAST` immediately after) or `ADDR` (the popped element's address, equivalent to `Qn.ADDR_LAST`).

- Base-word encoding: bits 15:12 = `1011` (primary 0xB), bits 11:8 = `1001` (subop 9), bits 7:4 = `Rd`, bit 3 = `Qn` (0 = Q0, 1 = Q1), bit 2 = `meta` (0 = ORD, 1 = ADDR), bits 1:0 = reserved (must be 0).

- `POPMETA` consumes exactly one stream element from `Qn`, identical to standalone `POP` in every atomicity and fault-behavior respect defined by ADR-STREAM-008 (DDR/ADR-STREAM-007 correction v1.2r): stream and register-pair state update together on successful retirement only, or not at all on fault.

- This closes the encoding gap explicitly left open by ADR-STREAM-008 (*"POPMETA... remains reserved, not allocated. If later adopted, it uses an aligned register-pair destination..."*) — the concept there is unchanged; only the opcode/bit-layout is new.

# Rationale

`POPMETA` exists to remove the extra bookkeeping instruction that argmin/argmax-style stream kernels otherwise need to track an element's index or address alongside its value inside a tight hardware-loop body (see the "Six-Instruction Argmax Loop" example in the Prefetch/Eight-Word-Loop addendum, and the packed argmin/argmax note in ADR-ISA-021). Since the hardware-loop body is capped at eight 16-bit words, folding "pop value" and "read last ordinal/address" into one instruction meaningfully shortens loop bodies that would otherwise not fit.

`0xB9` was chosen because it was the next free STREAM subop immediately following `QSTEP` (`0xB8`); subops `0xBA`-`0xBF` remain free for the other documented-but-unimplemented stream ops (`QADDR`, `QCOUNT`, `QSYNC`, `QSTAT`, `QCLR`, `QON`/`QOFF` — see `OPEN_QUESTIONS_CURRENT.md` item 4).

# Consequences

- `isa/database/aurora_v1_2_isa.{json,yaml}` and both `instruction_table.csv` mirrors now include `POPMETA` as a 97th instruction.
- `isa/database/aurora_v1_2_encoding.json` gains a `STREAM_POPMETA` format entry; `isa/database/aurora_encode.py` gains a matching encoder, self-tested against `POPMETA R4:R5, Q0, ORD` → `0xB940`.
- Bit positions above are a fresh allocation (no prior docx bit-diagram existed for POPMETA), so treat them as this ADR's normative definition going forward, not as extracted from an older source.

# Related ADRs

- ADR-STREAM-008 — Implicit Stream Access for Stream-Capable Computation (defines the POPMETA concept this ADR allocates real bits for).
- ADR-ISA-021 — Contextual ZR, Unified Compare, and Packed Predicate Flags (the argmin/argmax kernel pattern POPMETA serves).
- ADR-FE-006 — Two-Entry Prefetch Buffer and Eight-Word Hardware Loop (the loop-body-size constraint motivating this instruction).

# Amendment (August 4, 2026): meta operand removed, ORD_NEXT/ORD_LAST retired

- `Qn.ORD_NEXT` and `Qn.ORD_LAST` are retired as system registers (see ADR-STREAM-007/008 amendments) — they duplicated index tracking already available from `Qn.COUNT` for ordinary loop control, and were otherwise only consumed by POPMETA's `ORD` option.
- `POPMETA Rd:Rd+1, Qn` drops the `meta` operand entirely. `Rd` still receives the popped value; `Rd+1` now unconditionally receives the popped element's address (`Qn.ADDR_LAST` after the pop) — the old `ADDR` option, not `ORD`.
- Encoding: bit 2 (formerly `meta`) is folded into `reserved`, which is now bits [2:0], must be 0. The physical word for the surviving form is unchanged: `POPMETA R4:R5, Q0` still encodes to `0xB940`.
- The "Six-Instruction Argmax Loop" example (AUR-ARCH-005 v1.2s addendum) is updated: the register formerly named `Rbestidx` (best element's ordinal) is renamed `Rbestaddr` (best element's address), since POPMETA no longer exposes an ordinal. Kernels that need an index rather than an address must compute it from the address (`(addr - stream_base) / element_size`) in software; no ADR currently defines a dedicated ordinal-recovery instruction.
