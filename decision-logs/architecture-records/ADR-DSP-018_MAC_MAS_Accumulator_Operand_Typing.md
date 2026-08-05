Status: LOCKED (operand typing and accumulator-selector encoding)\
Architecture baseline: Aurora v1.2s\
Date: August 4, 2026 (amended August 4, 2026 - accumulator-selector encoding resolved)

# Decision

- `MAC` and `MAS` are redefined as:

  ```
  MAC accumulator, Ra, Rb    ; accumulator <- accumulator + Ra*Rb
  MAS accumulator, Ra, Rb    ; accumulator <- accumulator - Ra*Rb
  ```

  The first operand's *type* is corrected from a bare GPR write destination (`dst`) to an
  **accumulator selector**. Both instructions' `semantics` text (`A = A + Ra*Rb` / `A = A -
  Ra*Rb`) already only ever referenced the implicit accumulator `A` — `dst` was never actually
  used by the documented behavior, so this closes a real operand-typing/semantics mismatch, not
  just a cosmetic rename.

- The instruction still has three explicit assembly operands; only operand 0's declared type
  changes (`gpr_destination` → `accumulator`).

- For complex-multiply mode, `A0`/`A1` may operate as the real/imaginary accumulator pair
  according to the existing rules in ADR-DSP-011/012/013/014/015/016 — this ADR does not alter
  that behavior.

# Amendment (August 4, 2026): Accumulator-Selector Bit Resolved

The bit-mapping deferred below at initial locking is now resolved:

- `RRR_OR_ACC`'s `subop` field only ever takes values 0-5 (`MUL`/`MULH`/`MAC`/`MAS`/`DIVSTEP`/`DIV`),
  which fit entirely in 3 bits. Bit 11 (the subop nibble's MSB) was therefore always `0` and unused
  by every mnemonic sharing that format — a genuinely spare bit, not an invented one.
- `MAC`/`MAS` are moved to a new, dedicated format, `RRR_ACC` (in `aurora_v1_2_encoding.json`):
  `primary[15:12]`, `acc_sel[11:11]` (`0`=A0, `1`=A1), `subop[10:8]` (unchanged numbering: `2`=MAC,
  `3`=MAS), `Ra[7:4]`, `Rb[3:0]`. Unlike `MUL`/`MULH`/`DIVSTEP`/`DIV` (2-address, `Rd`=`Ra`), `Ra`
  and `Rb` are two fully independent register operands — `MAC`/`MAS` never had a real destination
  register to begin with, so there was no 2-address constraint to preserve.
- This is purely additive/reinterpretive: every pre-existing `RRR_OR_ACC` encoding (`MUL`, `MULH`,
  `DIVSTEP`, `DIV`, and `MAC`/`MAS` at their old implicit `acc_sel=0`/A0 encoding) is bit-for-bit
  unchanged. Only the previously-unused bit 11 gains meaning, and only for `MAC`/`MAS`.
- Canonical DB: `MAC`/`MAS` `format` changed `RRR_OR_ACC` → `RRR_ACC`; `operand_spec_confidence`
  raised `inferred` → `documented` (the gap this ADR previously flagged is closed).
- Encoder: new `_encode_RRR_ACC(instr, fmt, ra, rb, accumulator="A0"|"A1")` handler in
  `aurora_encode.py`. Self-tests: `MAC A0,R2,R3` → `0x3223`, `MAC A1,R2,R3` → `0x3A23`,
  `MAS A1,R2,R3` → `0x3B23`; `decode(0x3A23)` round-trips to `MAC` with `acc_sel=1`.
- `OPEN_QUESTIONS_CURRENT.md` item 8's remaining sub-question (accumulator-selector bit mapping)
  is now closed; no further follow-up is pending for this ADR.

# Explicitly NOT Decided Here (original text, superseded by the amendment above)

- **The bit-level mapping from an encoded accumulator-selector value to A0 vs. A1 is not
  specified by this ADR.** `MAC`/`MAS` keep the same physical bit field position they already had
  (bits `11:8`, the shared `RRR`-shaped word's `Rd_Ra` slot — this position itself is documented,
  confirmed by the worked `DIVSTEP` hex example that shares the same base format). What that
  field's *value* means for accumulator selection (e.g. whether only bit 0 is significant, whether
  legal encodings are restricted to specific values, or whether accumulator selection instead
  comes from elsewhere such as a MODE-register bit) is genuinely unresolved.
- No prior docx source itemizes this mapping, and per the reconciliation proposal that prompted
  this ADR, encoding details must not be silently invented where source material is insufficient.
  The canonical DB marks `MAC`/`MAS`'s `operand_spec_confidence` as `inferred` (not `documented`)
  specifically to flag this gap, with a note pointing back here.

# Rationale

Leaving `dst` as a plain GPR operand was actively misleading: nothing in the accumulate/subtract
semantics ever produced a GPR write, so any assembler or simulator built naively off the operand
list would invent a nonexistent register writeback. Correcting the operand *type* now (while
explicitly not inventing the missing bit-mapping) prevents that class of bug without overreaching
into an encoding decision this ADR isn't equipped to make correctly.

# Consequences

- `isa/database/aurora_v1_2_isa.{json,yaml}` and both CSV mirrors: `MAC`/`MAS` operand 0 renamed
  `dst` → `accumulator`; format changed `RRR_OR_ACC` → `RRR_ACC`; `operand_spec_confidence` set to
  `documented` (raised from `inferred` per the amendment above); `encoding_spec_confidence` and
  `semantic_spec_confidence` remain `documented`.
- `isa/database/aurora_v1_2_encoding.json`: `RRR_OR_ACC`'s `subop` field narrowed from `[11,8]` to
  `[10,8]` (bit-identical in practice, since values 0-5 never used bit 11); new `RRR_ACC` format
  added for `MAC`/`MAS` with a dedicated `acc_sel` field at bit 11.
- `isa/database/aurora_encode.py`: new `_encode_RRR_ACC` handler; self-tests added (see amendment).
- `OPEN_QUESTIONS_CURRENT.md` item 8 (MAC/MAS operand ambiguity) is fully closed — both the
  operand-typing question and the accumulator-selector encoding question are resolved.

# Related ADRs

- ADR-DSP-011 through ADR-DSP-016 — complex-multiply / accumulator mode rules this does not alter.
- ADR-ISA-022 — LOOPR and AGU retirement (companion decision from the same reconciliation pass).
