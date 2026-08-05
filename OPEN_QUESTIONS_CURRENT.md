# Aurora v1.2 — Open Questions for Architecture Review

Compiled 2026-08-04. These are unresolved conflicts, gaps, and design questions surfaced
while reconciling the canonical machine-readable ISA database (`isa/database/`) against the
full documentation set. None of these block current tooling (validator/encoder/opcode map
all run clean today), but each needs a human decision before it can be called settled.

---

## 1. Opcode `0xC0`/`0xC1` — LOOPSET/LOOPEND vs LOOP/NOP — ✅ RESOLVED 2026-08-04

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
- **Resolved:** `0xC0`/`0xC1` renamed to `LOOP`(format `LOOP_IMM8`, `#count` operand, 1-4 instruction
  body, `LOOP_FORMAT` exception)/`NOP` in `isa/database/aurora_v1_2_isa.{json,yaml}` and both CSV
  mirrors. `aurora_v1_2_encoding.json`'s conflict note updated to reflect resolution; `LOOP_IMM8`
  format status is now `normative`. Encoder gained `_encode_LOOP_IMM8` with passing self-tests
  (`LOOP #16` → `0xC00F`, `NOP` → `0xC100`). `AGUCFG`/`STRIDE` (0xC2/0xC3) deliberately left
  untouched — see #2 below, still open.

## 2. Opcode `0xC2`/`0xC3` — ✅ RESOLVED 2026-08-04 — AGUCFG/STRIDE retired, LOOPR allocated at 0xC2

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
- **Resolved** via [ADR-ISA-022](decision-logs/architecture-records/ADR-ISA-022_LOOPR_Register_Count_Hardware_Loop_and_AGU_Retirement.md)
  (locked): `AGUCFG`/`STRIDE` are retired and removed entirely from the canonical DB (option a); the
  older 8-op AUR-ARCH-004 AGU class is explicitly **not** resurrected (option b rejected) since its
  functionality substantially overlaps `ADD`/shift/`LD`/`ST`/`QCFG`/`QCIRC`/bounds-checking. The
  vacated `0xC2` slot is reallocated to a new instruction, `LOOPR Rs` (format `LOOP_REG`) — see #7
  below. `0xC3`-`0xC9` remain reserved. DB/encoding.json/encoder all updated; self-tests confirm
  `AGUCFG`/`STRIDE` (and `LOOPSET`/`LOOPEND`) no longer encode.

## 3. Document precedence conflict — ✅ RESOLVED 2026-08-04 — AUR-ARCH-004 superseded

- [docs/governance/AUR-PM-004_Document_Status.csv](docs/governance/AUR-PM-004_Document_Status.csv)
  and the Master Index both list **AUR-ARCH-004 (ISA & Opcode Map) as `Frozen`**, and
  [ADR-0017](docs/governance/Aurora_Architecture_Decision_Register_ADR_v1_2.md) names it the
  frozen **"source of truth"** that generates the machine-readable tools/docs.
- Meanwhile **AUR-ARCH-005 (Instruction Reference)** — where the actual LOOP/NOP hardware-loop
  decision, QSTEP, stream-access rules, etc. all live — is only status `Draft`.
- In practice, AUR-ARCH-004 is stale: it predates ADR-ISA-020/ADR-FE-006 and was never updated to
  match. So the nominally-authoritative "Frozen" doc contradicts the actual current locked design.
- **Resolved** via [DDR-0063](decision-logs/documentation-records/DDR-0063_ISA_Reconciliation_Confidence_Metadata_and_AUR-ARCH-004_Supersession.md)
  (locked): adopted an explicit authority order (ADRs > canonical machine-readable DB > canonical
  specs > generated references > historical/exploratory docs) — a document's `Frozen` status no
  longer implies precedence over a newer locked ADR. `AUR-ARCH-004`'s status in
  [docs/governance/AUR-PM-004_Document_Status.csv](docs/governance/AUR-PM-004_Document_Status.csv)
  was changed to `Superseded — pending regeneration`, and a status banner was added to the top of
  the document itself. Full prose/table regeneration of AUR-ARCH-004 is scoped as separate
  follow-up work (not fabricated as part of this pass) — the canonical `isa/database/` JSON/YAML/CSV
  remain authoritative for opcode assignments in the interim.

## 4. Stream instruction gap (`0xB`) — ✅ RESOLVED 2026-08-04 — exposed as system registers, not new opcodes

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

`0xB9`-`0xBF` (7 opcodes) were free in the canonical map (0xB9 has since been given to `POPMETA`,
see #5). Also note: AUR-ARCH-004's subop numbering for the ops it does share with the DB (e.g.
`QCIRC` at subop `A` vs the DB's subop `7`) **does not match** the canonical DB either.
- **Resolved** via [DDR-0063](decision-logs/documentation-records/DDR-0063_ISA_Reconciliation_Confidence_Metadata_and_AUR-ARCH-004_Supersession.md):
  none of these six are adopted as standalone opcodes. `QADDR`/`QCOUNT`/`QSTAT` state is exposed
  through the existing system-register access mechanism (`Q0.ADDR_NEXT`/`ADDR_LAST`/`COUNT`/
  `STATUS`, and the `Q1.*` equivalents — `ORD_NEXT`/`ORD_LAST` were retired 2026-08-04, see ADR-STREAM-007/008/009 amendments) instead of new opcodes. `QON`/`QOFF`/
  `QCLR` behavior is expressed through `QCFG`/writable stream-control registers. `QSYNC` is
  **rejected** outright as a stream opcode — DMA synchronization uses DMA status/completion/error
  events, interrupts, `WFE`, and explicit buffer-ownership protocols, keeping stream traversal and
  DMA transport separate. No canonical DB opcode changes were needed for this item; the numbering
  mismatch noted above is moot since these ops are not being encoded as opcodes at all.

## 5. `POPMETA` — ✅ RESOLVED 2026-08-04 — opcode allocated

- [ADR-STREAM-008](decision-logs/architecture-records/ADR-STREAM-008_Implicit_Stream_Access_for_Computation.md)
  and [RECENT_DECISIONS_SNAPSHOT.md](docs/canonical/RECENT_DECISIONS_SNAPSHOT.md) agree: `POPMETA
  Rd:Rd+1, Qn, meta` — an aligned register-pair destination that atomically returns a popped
  stream value plus metadata (`ORD`/ordinal-index or `ADDR`) — is locked *as a concept* but
  explicitly "reserved, not allocated." Zero opcode bits assigned; absent from the canonical DB.
- Origin/use case: argmin/argmax stream kernels (e.g. finding the index of the lowest value in an
  array) inside a hardware loop, avoiding a separate index-increment instruction per element. See
  the worked example in [docs/isa/AUR-ARCH-005_Prefetch_and_8_Word_Loop_Addendum_v1_2s.md](docs/isa/AUR-ARCH-005_Prefetch_and_8_Word_Loop_Addendum_v1_2s.md).
- **Resolved:** allocated `0xB9` (format `STREAM_POPMETA`, new), per
  [ADR-STREAM-009](decision-logs/architecture-records/ADR-STREAM-009_POPMETA_Opcode_Allocation.md)
  (locked). Base word: `Rd[7:4]`, `Qn[3]`, `meta[2]` (`0`=ORD, `1`=ADDR), `reserved[1:0]`=0.
  Added to the canonical DB (97 instructions at the time; net count is 96 today after `AGUCFG`/
  `STRIDE` retirement per #2 below) and to `aurora_v1_2_encoding.json`; encoder gained
  `_encode_STREAM_POPMETA`, self-tested (`POPMETA R4:R5, Q0, ORD` → `0xB940`). This did **not**
  wait on #6 (TRACKMIN/TRACKMAX) — the two are independent; TRACKMIN/TRACKMAX remains its own
  open question regardless of POPMETA now having bits.

## 6. `TRACKMIN`/`TRACKMAX` — competing idea to `POPMETA`, formally tracked as open 2026-08-04

- [ARCHITECTURE_DECISION_LOG_CURRENT.md](decision-logs/ARCHITECTURE_DECISION_LOG_CURRENT.md#L55):
  a fused compare-and-track instruction was proposed to replace the whole
  `POPMETA + CMP + two CMOVs` argmin/argmax sequence with one instruction. Status: **"Reserved /
  benchmark"** — explicitly not baseline, not decided either way.
- **Now has a formal ADR** (deliberately kept open, NOT locked):
  [ADR-DSP-017](decision-logs/architecture-records/ADR-DSP-017_TRACKMIN_TRACKMAX_Fused_Compare_and_Track.md),
  status `PROPOSED — OPEN, NOT LOCKED`. It records the alternatives (status quo / fused instruction /
  narrower fusion) and what's needed before a decision can be made (benchmarking, a concrete
  encoding — a 4-register-operand instruction needs a mandatory EXT word).
- **Question for review (unchanged):** is a fused `TRACKMIN`/`TRACKMAX` worth the opcode/hardware
  cost over the 4-instruction `POPMETA`-based sequence? No longer blocks #5 — POPMETA has its own
  opcode now regardless of how this is decided.

## 7. `LOOPR` — ✅ RESOLVED 2026-08-04 — formally defined and allocated at 0xC2

- Several worked examples (argmax loop, etc.) use `LOOPR Rcount` (register-supplied loop count).
- The only *locked* loop instruction is `LOOP #count` — an 8-bit **immediate** count-minus-one
  (ADR-ISA-020). No ADR/DDR defines a register-count variant.
- **Found exactly two usages, both in argmin/argmax stream kernels, both structurally identical:**
  1. ADR-ISA-021's "Hardware-Loop Use" example:
     ```
     LOOPR Rcount
     MOV Rnew, Q0
     CMP Rbest, Rnew
     CMOV.LT Rbest, Rnew
     CMOV.LT Rindex, Rnewindex
     ```
  2. The "Six-Instruction Argmax Loop" in the v1.2s Prefetch/Eight-Word-Loop addendum:
     ```
     LOOPR Rcount
     POPMETA R4:R5, Q0, ORD
     ABS R4, R4
     CMP Rbest, R4
     CMOV.LT Rbest, R4
     CMOV.LT Rbestidx, R5
     REDUCE.ADD A0, R4, ACC
     ```
  In both, `LOOPR` opens a hardware-loop body exactly where `LOOP` would, but with the trip count
  read from a **register** rather than a compile-time `#count` immediate — needed because these are
  argmin/argmax kernels over runtime-determined array lengths, which `LOOP`'s fixed 8-bit immediate
  (max 256, and only known at assemble time) cannot express.
- **Assessment:** `LOOPR` reads as a genuinely-intended register-count sibling to `LOOP`, not a
  typo/shorthand — both examples use it purposefully in otherwise precise, ADR-quality pseudocode,
  and the motivating need (variable-length array loops) is real and distinct from anything `LOOP`
  covers. However it has **zero** ADR/DDR coverage, zero opcode allocation, and zero encoding —
  it is currently pure vapor.
- **Resolved:** allocated at `0xC2` (format `LOOP_REG`: `Rs[7:4]`, `reserved[3:0]`=0) per
  [ADR-ISA-022](decision-logs/architecture-records/ADR-ISA-022_LOOPR_Register_Count_Hardware_Loop_and_AGU_Retirement.md)
  (locked) — the same ADR that retired `AGUCFG`/`STRIDE` and vacated the slot. `LOOPR Rs` repeats
  the next NOP-terminated body `Rs` times (unsigned, nonzero), reusing `LOOP`/`NOP`'s exact
  hardware-loop machinery and eight-word capture window. Added to the canonical DB, `encoding.json`,
  and the encoder (`_encode_LOOP_REG`); self-test confirms `LOOPR R3` → `0xC230`.

## 8. `MAC`/`MAS` — ✅ RESOLVED 2026-08-04 — operand typing and accumulator-selector encoding

- Canonical DB lists `operands: [dst, Ra, Rb]` (3 operands) for both, but their `semantics` strings
  (`A = A + Ra*Rb`, `A = A - Ra*Rb`) never reference `dst` at all — only the implicit accumulator
  `A`. This suggests `dst` may not be a real GPR write target the way `ADD Rd,Ra,Rb`'s `Rd` is; it
  could be vestigial or an accumulator-select bit that was never renamed.
- **Not changed** in the recent operand-count pass — left at `operand_count: 3` matching existing
  DB data, since this is a real semantic question, not a mechanical bug like the `RET` fix was.
- **Resolved** via [ADR-DSP-018](decision-logs/architecture-records/ADR-DSP-018_MAC_MAS_Accumulator_Operand_Typing.md)
  (locked): operand 0 renamed `dst` → `accumulator` in the canonical DB, matching the semantics
  that never referenced a GPR write. The accumulator-selector bit mapping, initially left
  deliberately undecided, was resolved the same day once a genuinely spare bit was identified:
  `RRR_OR_ACC`'s `subop` field only ever uses values 0-5 (fits in 3 bits), so bit 11 was always
  unused/reserved across `MUL`/`MULH`/`MAC`/`MAS`/`DIVSTEP`/`DIV`. `MAC`/`MAS` now use a dedicated
  format, `RRR_ACC` (`acc_sel[11]`: `0`=A0, `1`=A1; `subop[10:8]` unchanged; `Ra[7:4]`/`Rb[3:0]` as
  two independent registers, not a 2-address `Rd`=`Ra` pair like their `RRR_OR_ACC` siblings). This
  is purely additive — every pre-existing encoding is bit-for-bit unchanged, only the previously-dead
  bit 11 now carries meaning. `operand_spec_confidence` raised back to `documented`.
  `encoding_spec_confidence`/`semantic_spec_confidence` remain `documented`. Encoder gained
  `_encode_RRR_ACC`; self-tests confirm `MAC A0,R2,R3`→`0x3223`, `MAC A1,R2,R3`→`0x3A23`,
  `MAS A1,R2,R3`→`0x3B23`.

## 9. Operand-count/immediate-bits confidence tiers — ✅ SUPERSEDED 2026-08-04 by formal confidence metadata

The informal tiers below were superseded by explicit per-instruction
`operand_spec_confidence`/`encoding_spec_confidence`/`semantic_spec_confidence`/`sources`/`notes`
fields added to the canonical DB per [DDR-0063](decision-logs/documentation-records/DDR-0063_ISA_Reconciliation_Confidence_Metadata_and_AUR-ARCH-004_Supersession.md)
(locked), generated mechanically by `isa/database/apply_proposal_fix_issues_1.py` from each
format's `encoding.json` status, then hand-corrected for `MAC`/`MAS` (see #8). Historical tiers,
for reference:
- **docx-confirmed:** `QPEEK`, `QPUSH`, `QCFG`, `QSTEP`, `ZEXT*/SEXT*` family, `MODE`, `WFI`/`WFE`/`HALT`,
  the `RRR`/`DIVSTEP` worked hex examples.
- **inferred by physical-encoding-constraint reasoning or analogy:** most remaining `STREAM` ops,
  all `SYSTEM` "args" ops.
- **genuinely undocumented (`null`):** was `LOOPSET`/`LOOPEND`/`AGUCFG`/`STRIDE` — moot now that
  `LOOPSET`/`LOOPEND` were renamed `LOOP`/`NOP` (#1) and `AGUCFG`/`STRIDE` were retired (#2).

---

## Already resolved (for reference, not open)

- `RET`'s `operands` field was a copy-paste bug (`["target/reg"]` from `CALL`/`JMP`/`JMPR`) — fixed
  to `[]` since `RET` takes no operand (`PC = R13`, implicit).
- `ZEXT8/SEXT8/ZEXT16/SEXT16` flags corrected to `[Z, N]` (were empty).
- `WFI`/`WFE` corrected from privileged to User/Supervisor-accessible + `serializing` attribute.
- `QSTEP` (0xB8) was entirely missing from the canonical DB — added.
- `packages/original/CONTENT_CLASSIFICATION.md` redundant/superseded attributions were corrected
  after byte-diff verification (no content loss found).
