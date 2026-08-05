Status: LOCKED\
Architecture baseline: Aurora v1.2s\
Date: August 4, 2026

# Decision

- `AGUCFG` (0xC2) and `STRIDE` (0xC3) are **retired** and removed entirely from the canonical
  instruction database. Neither was ever backed by an ADR; both were stub-quality placeholders
  (`format: LOOP_AGU`, literal `args` operand, no bit diagram, identical boilerplate semantics
  text) left over from an early, never-adopted general-purpose AGU class.

- The older, fuller AGU class documented in `docs/isa/AUR-ARCH-004_ISA_Opcode_Map_v1_2.md`
  (`LOOP.SET`/`LOOP.END`/`AGU.ADD`/`AGU.POST`/`AGU.PRE`/`CIRC.ADD`/`CIRC.SUB`/`ALIGN`/`LEA.S`/
  `BOUND`) is **not** resurrected as part of the baseline ISA. Its functionality substantially
  overlaps existing facilities: ordinary `ADD`/shift/mask/`LD`/`ST`, `Q0`/`Q1` stream stride and
  circular-address generation (`QCFG`/`QCIRC`), stream configuration registers, stack/memory
  bounds checking (ADR-ISA-019), and system-control mechanisms.

- The opcode slot vacated by `AGUCFG` (0xC2) is reallocated to **`LOOPR Rs`** — a new instruction
  making the register-supplied hardware-loop count (informally used as `LOOPR` in several worked
  examples, e.g. the argmin/argmax kernels in ADR-ISA-021 and the Prefetch/Eight-Word-Loop
  addendum) a real, encoded instruction rather than undefined example pseudocode.

- `LOOPR Rs` repeats the next NOP-terminated instruction body `Rs` times (unsigned, must be
  nonzero — a zero count is illegal / must be checked by software beforehand). It uses the exact
  same hardware-loop machinery, restrictions, and eight-word capture window as immediate `LOOP`
  (ADR-ISA-020, ADR-FE-006): up to eight captured 16-bit words including extension words, no
  nesting, no pairing across the iteration wrap, precise-interrupt and context-save/restore state
  preservation, and the same prohibited-instruction list in the loop body.

- Encoding: format `LOOP_REG`. Base word: `primary[15:12]=0xC`, `subop[11:8]=2`, `Rs[7:4]`,
  `reserved[3:0]` must be 0.

- `0xC3`-`0xC9` remain reserved (no DB entries). Unused opcode space is left unallocated rather
  than filled solely because an older draft once listed possible operations there.

# Rationale

Immediate-only loop counts (`LOOP #count`, 8-bit, max 256) cannot express runtime-sized trip
counts — arrays, DMA blocks, stream buffers, audio frames, image rows, and packet lengths whose
size is not known until execution. `LOOPR` closes that gap using the same low-overhead mechanism
already validated for `LOOP`, at the cost of one opcode instead of inventing a wider immediate
encoding or a separate counted-branch idiom.

Retiring `AGUCFG`/`STRIDE` instead of resurrecting the older 8-op AGU class keeps the opcode map
honest: no instruction should exist in the canonical DB without either a ratified bit diagram or
an ADR backing it. Reintroducing that whole class was judged unnecessary scope for this baseline
given the overlap with existing addressing mechanisms; if a genuine gap is found later (e.g. a
scaled load-effective-address operation), it should go through its own proposal rather than be
grandfathered in from a stale draft.

# Consequences

- `isa/database/aurora_v1_2_isa.{json,yaml}` and both CSV mirrors: `AGUCFG`/`STRIDE` removed;
  `LOOPR` added at `0xC2`. Total canonical instruction count: 97 (post ADR-STREAM-009) − 2 (retired)
  + 1 (`LOOPR`) = 96.
- `isa/database/aurora_v1_2_encoding.json`: the `LOOP_AGU` format is removed; a new `LOOP_REG`
  format is added.
- `isa/database/aurora_encode.py`: gained `_encode_LOOP_REG`; self-tests confirm `LOOPR R3` →
  `0xC230`, and confirm the four retired mnemonics no longer encode (raise `AuroraEncodingError`).
- `OPEN_QUESTIONS_CURRENT.md` items 2 and 7 (AGUCFG/STRIDE fate, LOOPR identification) are closed
  by this ADR.
- Opcode-space map (`docs/isa/aurora_v1_2_opcode_space_map.png`) regenerated to reflect 0xC0=LOOP,
  0xC1=NOP, 0xC2=LOOPR, 0xC3-0xC9 reserved.

# Related ADRs

- ADR-ISA-020 — NOP-Terminated Hardware Loop (the base mechanism `LOOPR` reuses).
- ADR-FE-006 — Two-Entry Prefetch Buffer and Eight-Word Hardware Loop (the capture-window rules
  `LOOPR` inherits unchanged).
- ADR-STREAM-009 — POPMETA Opcode Allocation (the sibling opcode-allocation decision made the same
  day, motivated by the same class of argmin/argmax kernel).
