Status: LOCKED\
Date: August 4, 2026

# Decision

## 1. Documentation authority order (adopted)

When documents disagree, the following precedence applies, highest first:

1. Accepted Architecture Decision Records (ADRs)
2. The current canonical machine-readable architecture database (`isa/database/aurora_v1_2_isa.json`
   and its YAML/CSV mirrors)
3. Current canonical architecture and instruction specifications (e.g. `AUR-ARCH-005` and its
   addenda)
4. Generated instruction references, opcode maps, diagrams, and summaries
5. Historical, superseded, or exploratory documents

A document's `Frozen` status does **not** override a newer Accepted/Locked ADR. This codifies in
writing what ADR-0017 ("machine-readable ISA as source of truth") already implied, and resolves
`OPEN_QUESTIONS_CURRENT.md` item 3.

## 2. AUR-ARCH-004 marked superseded pending regeneration

`docs/isa/AUR-ARCH-004_ISA_Opcode_Map_v1_2.md` predates ADR-ISA-020, ADR-FE-006, ADR-STREAM-009,
ADR-ISA-022, and ADR-DSP-018, and its `0xC` opcode-class table (`LOOP.SET`/`LOOP.END`/`AGU.*`/
`CIRC.*`/`ALIGN`/`LEA.S`/`BOUND`) directly conflicts with those locked decisions. Its
`docs/governance/AUR-PM-004_Document_Status.csv` status is changed from `Frozen` to:

```
Superseded — pending regeneration
```

Per the authority order above, the canonical `isa/database/` JSON/YAML/CSV are authoritative for
opcode assignments in the interim, regardless of AUR-ARCH-004's stale content.

**Scope note:** this DDR marks the status change and records what must change on regeneration
(below); it does not itself perform a full rewrite of AUR-ARCH-004's prose/tables — that
regeneration is tracked as follow-up work, not fabricated here, consistent with the reconciliation
proposal's instruction not to invent content beyond what sources support.

Required corrections for the eventual regenerated AUR-ARCH-004 revision:
- `0xC` class: `LOOP`(0)/`NOP`(1)/`LOOPR`(2), `0xC3`-`0xC9` reserved — replacing the old
  `LOOP.SET`/`LOOP.END`/`AGU.*`/`CIRC.*`/`ALIGN`/`LEA.S`/`BOUND` table.
- `0xB` class: add `POPMETA` at `0xB9`.
- `MAC`/`MAS` operand 0 relabeled `accumulator` (not a GPR destination).
- Any stream-management entries for `QADDR`/`QCOUNT`/`QSYNC`/`QSTAT`/`QCLR`/`QON`/`QOFF` should be
  described as system-register access (see item 3 below), not standalone opcodes.

## 3. Legacy stream-management operations exposed as system registers, not new opcodes

`QADDR`, `QCOUNT`, `QSTAT` state is exposed through the existing system-register access mechanism
(`MRS`/`MSR`) rather than new stream opcodes: `Q0.ADDR_NEXT`, `Q0.ADDR_LAST`, `Q0.COUNT`,
`Q0.STATUS` (and the `Q1.*` equivalents). Stream enable/disable/reset
(`QON`/`QOFF`/`QCLR`) is expressed through `QCFG` or writable stream-control registers instead of
dedicated opcodes. `QSYNC` is **rejected** as a stream opcode — DMA synchronization uses DMA
status/completion/error events, interrupts, `WFE`, and explicit buffer-ownership protocols,
keeping stream traversal/computation and DMA transport separate. This resolves
`OPEN_QUESTIONS_CURRENT.md` item 4 without allocating `0xBA`-`0xBF`.

*(No canonical DB changes were made for this item — it is a documentation/design decision that
these six operations are deliberately NOT added as opcodes; item 4 in `OPEN_QUESTIONS_CURRENT.md`
is closed with "will not implement as opcodes", not with new instructions.)*

**Amendment (August 4, 2026):** `Q0.ORD_NEXT`/`Q0.ORD_LAST` (and the `Q1.*` equivalents) were
subsequently retired as system registers — see the ADR-STREAM-007/008/009 amendments. Only
`ADDR_NEXT`/`ADDR_LAST`/`COUNT`/`STATUS` remain per stream.

## 4. Machine-readable ISA confidence/provenance metadata

Every instruction in `isa/database/aurora_v1_2_isa.{json,yaml}` and both CSV mirrors gained:

- `operand_spec_confidence`, `encoding_spec_confidence`, `semantic_spec_confidence` — each one of
  `documented` (stated directly in accepted documentation), `inferred` (derived from encoding
  constraints/analogy, not explicitly documented), or `unresolved` (not sufficiently specified;
  the `operands` or `semantics` field is still placeholder text).
- `sources` — list of contributing ADRs/DDRs/AUR-ARCH-* documents.
- `notes` — free-text caveats (e.g. `MAC`/`MAS`'s accumulator-selector bit-mapping gap, see
  ADR-DSP-018).

Generated mechanically by `isa/database/apply_proposal_fix_issues_1.py` from each instruction's
`format`'s status in `aurora_v1_2_encoding.json`, plus a placeholder-text pattern match, then
hand-corrected for `MAC`/`MAS` (see ADR-DSP-018) where the mechanical derivation over-stated
confidence. This resolves `OPEN_QUESTIONS_CURRENT.md` item 9.

# Consequences

- `docs/governance/AUR-PM-004_Document_Status.csv`: `AUR-ARCH-004` status changed.
- `docs/isa/AUR-ARCH-004_ISA_Opcode_Map_v1_2.md`: superseded banner added at the top.
- `isa/database/` JSON/YAML/CSV: confidence/provenance columns added to every instruction (see
  ADR-ISA-022, ADR-STREAM-009, ADR-DSP-018 for the specific opcode-level decisions these fields
  describe).
- `OPEN_QUESTIONS_CURRENT.md`: items 2, 3, 4, 7, 8, 9 updated/closed.

# Related ADRs / DDRs

- ADR-0017 — Machine-readable ISA as source of truth (the precedence principle this DDR codifies
  explicitly).
- ADR-ISA-020, ADR-FE-006, ADR-STREAM-009, ADR-ISA-022, ADR-DSP-018 — the specific decisions
  AUR-ARCH-004's regeneration must reconcile against.
- DDR-0050, DDR-0062 — prior hardware-loop documentation decisions this DDR is consistent with.
