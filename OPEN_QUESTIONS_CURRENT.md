# Aurora v1.2 — Open Questions for Architecture Review

Compiled 2026-08-04. These are unresolved conflicts, gaps, and design questions surfaced
while reconciling the canonical machine-readable ISA database (`isa/database/`) against the
full documentation set. None of these block current tooling (validator/encoder/opcode map
all run clean today), but each needs a human decision before it can be called settled.

---

## 1. Opcode `0xC0`/`0xC1` — LOOPSET/LOOPEND vs LOOP/NOP (mostly resolved, DB not updated)

- **Canonical DB today** (`isa/database/aurora_v1_2_isa.json`): `LOOPSET`(0xC0)/`LOOPEND`(0xC1)/
  `AGUCFG`(0xC2)/`STRIDE`(0xC3), format `LOOP_AGU`. All four have identical placeholder
  descriptions ("... low-overhead loop or address-generation control"), literal `args` as their
  operand list, and no bit-diagram anywhere. This is stub-quality data, not a real spec.
- **Locked decision that supersedes half of it**: [ADR-ISA-020](decision-logs/architecture-records/ADR-ISA-020_NOP_Terminated_Hardware_Loop.md)
  + [DDR-0050](decision-logs/documentation-records/DDR-0050_Hardware_Loop_Documentation.md) —
  `LOOP #count` (0xC0) repeats the next 1-4 instructions; the first ordinary `NOP` (0xC1)
  terminates the body. States outright: *"The earlier provisional LOOPSET/LOOPEND pair is
  superseded... No separate LOOPEND instruction remains."* DDR-0050 explicitly directs
  *"The machine-readable ISA table shall rename opcode keys 0xC0 and 0xC1 accordingly"* —
  **this rename was never applied to the DB.**
- **Refined further** by [ADR-FE-006](adr/ADR-FE-006_Two_Entry_Prefetch_and_Eight_Word_Loop.md) +
  [DDR-0062](ddr/DDR-0062_Prefetch_and_Hardware_Loop_Window_Documentation.md): the capture window
  is 8 contiguous 16-bit words (4 decoded + 4 pinned prefetch), still using the same `LOOP`/`NOP`
  encoding.
- **Action needed:** mechanical DB fix — rename `0xC0`→`LOOP` (format `LOOP_IMM8`, `#count` operand)
  and `0xC1`→`NOP`, per the locked ADR. Low-risk, no open design question, just needs doing.

## 2. Opcode `0xC2`/`0xC3` — AGUCFG/STRIDE (genuinely unresolved, no ADR)

- Neither ADR-ISA-020 nor DDR-0050 says anything about `0xC2`/`0xC3` — only `0xC0`/`0xC1` are
  addressed. No ADR/DDR anywhere mentions `AGUCFG` or `STRIDE` by name.
- A **different, older, much more detailed** address-generation design exists in the frozen
  [docs/isa/AUR-ARCH-004_ISA_Opcode_Map_v1_2.md](docs/isa/AUR-ARCH-004_ISA_Opcode_Map_v1_2.md)
  ("Loop and AGU Class - Primary 0xC", subops 0-9):

  | subop | Mnemonic | Role |
  |---|---|---|
  | 0 | `LOOP.SET` | set loop start/end/count |
  | 1 | `LOOP.END` | decrement/test **and branch** to loop start (conflicts with NOP-terminated design) |
  | 2 | `AGU.ADD` | address add with signed stride |
  | 3 | `AGU.POST` | post-update address |
  | 4 | `AGU.PRE` | pre-update address |
  | 5 | `CIRC.ADD` | power-of-two wrapped address update |
  | 6 | `CIRC.SUB` | wrapped decrement |
  | 7 | `ALIGN` | align address to power of two |
  | 8 | `LEA.S` | scaled address calculation (load-effective-address) |
  | 9 | `BOUND` | bounds check / optional trap |

  This is likely where `AGUCFG`/`STRIDE` originated as an abbreviated stand-in, before the detail
  got lost. None of `AGU.ADD/AGU.POST/AGU.PRE/CIRC.ADD/CIRC.SUB/ALIGN/LEA.S/BOUND` were ever
  carried into the canonical machine-readable DB — they exist only as prose in this one doc.
- **Question for review:** do we (a) formally retire `AGUCFG`/`STRIDE` the same way `LOOPSET`/
  `LOOPEND` was retired, (b) resurrect the fuller 8-op AGU class from AUR-ARCH-004 at `0xC2`-`0xC9`,
  or (c) drop general-purpose AGU entirely and rely on existing `LD`/`ST`/stream addressing? No
  decision has been made either way.

## 3. Document precedence conflict — AUR-ARCH-004 (Frozen) vs AUR-ARCH-005 (Draft)

- [docs/governance/AUR-PM-004_Document_Status.csv](docs/governance/AUR-PM-004_Document_Status.csv)
  and the Master Index both list **AUR-ARCH-004 (ISA & Opcode Map) as `Frozen`**, and
  [ADR-0017](docs/governance/Aurora_Architecture_Decision_Register_ADR_v1_2.md) names it the
  frozen **"source of truth"** that generates the machine-readable tools/docs.
- Meanwhile **AUR-ARCH-005 (Instruction Reference)** — where the actual LOOP/NOP hardware-loop
  decision, QSTEP, stream-access rules, etc. all live — is only status `Draft`.
- In practice, AUR-ARCH-004 is stale: it predates ADR-ISA-020/ADR-FE-006 and was never updated to
  match. So the nominally-authoritative "Frozen" doc contradicts the actual current locked design.
- **Question for review:** either re-open AUR-ARCH-004 for a real update pass, or formally
  demote/re-badge it so its "Frozen" status stops implying it overrides newer AUR-ARCH-005 content.

## 4. Stream instruction gap (`0xB`) — several documented ops never implemented

Canonical DB encodes only 9 of the `0xB` STREAM ops (subops `0`-`8`: `QMASK`, `QPEEK`, `QPUSH`,
`QPOP`, `QDUP`, `QREPL`, `QCFG`, `QCIRC`, `QSTEP`). AUR-ARCH-004 additionally documents:

| Mnemonic | Role | In canonical DB? |
|---|---|---|
| `QADDR` | direct read/write of current address | missing |
| `QCOUNT` | direct read/write of remaining count | missing |
| `QSYNC` | synchronize DMA/buffer state | missing |
| `QSTAT` | read status/end flags | missing |
| `QCLR` | clear/reset selected stream engine | missing |
| `QON`/`QOFF` | enable/disable stream engine | missing |

`0xB9`-`0xBF` (7 opcodes) are currently free in the canonical map — enough room for all of the
above. Also note: AUR-ARCH-004's subop numbering for the ops it does share with the DB (e.g.
`QCIRC` at subop `A` vs the DB's subop `7`) **does not match** the canonical DB either.
**Question for review:** adopt these six ops for real (and fix the numbering mismatch), or
confirm they were intentionally dropped.

## 5. `POPMETA` — locked as a concept, never allocated real opcode bits

- [ADR-STREAM-008](decision-logs/architecture-records/ADR-STREAM-008_Implicit_Stream_Access_for_Computation.md)
  and [RECENT_DECISIONS_SNAPSHOT.md](docs/canonical/RECENT_DECISIONS_SNAPSHOT.md) agree: `POPMETA
  Rd:Rd+1, Qn, meta` — an aligned register-pair destination that atomically returns a popped
  stream value plus metadata (`ORD`/ordinal-index or `ADDR`) — is locked *as a concept* but
  explicitly "reserved, not allocated." Zero opcode bits assigned; absent from the canonical DB.
- Origin/use case: argmin/argmax stream kernels (e.g. finding the index of the lowest value in an
  array) inside a hardware loop, avoiding a separate index-increment instruction per element. See
  the worked example in [docs/isa/AUR-ARCH-005_Prefetch_and_8_Word_Loop_Addendum_v1_2s.md](docs/isa/AUR-ARCH-005_Prefetch_and_8_Word_Loop_Addendum_v1_2s.md).
- **Question for review:** allocate real opcode bits for `POPMETA` (candidate: unused `0xB9`-`0xBF`
  space), contingent on question #6 below.

## 6. `TRACKMIN`/`TRACKMAX` — competing idea to `POPMETA`, not decided

- [ARCHITECTURE_DECISION_LOG_CURRENT.md](decision-logs/ARCHITECTURE_DECISION_LOG_CURRENT.md#L55):
  a fused compare-and-track instruction was proposed to replace the whole
  `POPMETA + CMP + two CMOVs` argmin/argmax sequence with one instruction. Status: **"Reserved /
  benchmark"** — explicitly not baseline, not decided either way.
- **Question for review:** is a fused `TRACKMIN`/`TRACKMAX` worth the opcode/hardware cost over the
  4-instruction `POPMETA`-based sequence? This decision should probably come before #5 is finalized,
  since choosing `TRACKMIN`/`TRACKMAX` could make dedicating opcode space to `POPMETA` unnecessary.

## 7. `LOOPR` — appears only in illustrative examples, never formally defined

- Several worked examples (argmax loop, etc.) use `LOOPR Rcount` (register-supplied loop count).
- The only *locked* loop instruction is `LOOP #count` — an 8-bit **immediate** count-minus-one
  (ADR-ISA-020). No ADR/DDR defines a register-count variant.
- **Question for review:** is `LOOPR` a real intended second form (needs its own ADR + opcode), or
  just informal shorthand in example pseudocode that should be corrected to `LOOP #count` semantics?

## 8. `MAC`/`MAS` — operand ambiguity around `dst`

- Canonical DB lists `operands: [dst, Ra, Rb]` (3 operands) for both, but their `semantics` strings
  (`A = A + Ra*Rb`, `A = A - Ra*Rb`) never reference `dst` at all — only the implicit accumulator
  `A`. This suggests `dst` may not be a real GPR write target the way `ADD Rd,Ra,Rb`'s `Rd` is; it
  could be vestigial or an accumulator-select bit that was never renamed.
- **Not changed** in the recent operand-count pass — left at `operand_count: 3` matching existing
  DB data, since this is a real semantic question, not a mechanical bug like the `RET` fix was.
- **Question for review:** does `MAC`/`MAS` actually write a 3rd GPR destination, or should `dst`
  be removed/renamed to reflect accumulator-only semantics?

## 9. Operand-count/immediate-bits confidence tiers (informational, not a conflict)

The recently-added `operand_count`/`immediate_bits` columns are graded by confidence:
- **docx-confirmed:** `QPEEK`, `QPUSH`, `QCFG`, `QSTEP`, `ZEXT*/SEXT*` family, `MODE`, `WFI`/`WFE`/`HALT`,
  the `RRR`/`DIVSTEP` worked hex examples.
- **inferred by physical-encoding-constraint reasoning or analogy:** most remaining `STREAM` ops,
  all `SYSTEM` "args" ops.
- **genuinely undocumented (`null`):** `LOOPSET`/`LOOPEND`/`AGUCFG`/`STRIDE` (ties directly into #1/#2
  above — once those opcodes are settled, these can finally get real values).

---

## Already resolved (for reference, not open)

- `RET`'s `operands` field was a copy-paste bug (`["target/reg"]` from `CALL`/`JMP`/`JMPR`) — fixed
  to `[]` since `RET` takes no operand (`PC = R13`, implicit).
- `ZEXT8/SEXT8/ZEXT16/SEXT16` flags corrected to `[Z, N]` (were empty).
- `WFI`/`WFE` corrected from privileged to User/Supervisor-accessible + `serializing` attribute.
- `QSTEP` (0xB8) was entirely missing from the canonical DB — added.
- `packages/original/CONTENT_CLASSIFICATION.md` redundant/superseded attributions were corrected
  after byte-diff verification (no content loss found).
