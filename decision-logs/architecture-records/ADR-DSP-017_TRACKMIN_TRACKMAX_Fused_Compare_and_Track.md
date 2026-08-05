Status: PROPOSED — OPEN DECISION, NOT LOCKED\
Architecture baseline: Aurora v1.2s\
Date: August 4, 2026

# Decision

**None yet.** This ADR exists to formally track an open question, not to record a settled choice.

Under consideration: a fused `TRACKMIN`/`TRACKMAX` "compare-and-track" instruction that would
update a running best value *and* a paired index/tag register in one instruction, replacing the
current `CMP` + `CMOV.cond` + `CMOV.cond` three-instruction idiom (four including the `POPMETA`
or `MOV` that supplies the candidate) used by argmin/argmax stream kernels — see the worked
examples in ADR-ISA-021 and the Prefetch/Eight-Word-Loop addendum.

# Alternatives Under Consideration

1. **Do nothing (status quo).** Keep `POPMETA` + `CMP` + `CMOV.LT` (value) + `CMOV.LT` (index) as
   the standard argmin/argmax idiom. No new opcode, no new hardware. Costs one extra loop-word per
   iteration versus a fused form.
2. **Add fused `TRACKMIN`/`TRACKMAX Rbest, Rbestidx, Rnew, Rnewidx`.** One instruction performs the
   compare and both conditional updates. Saves 2 of the loop body's scarce eight words per kernel,
   at the cost of a new opcode, a wider register-operand encoding (needs 4 register fields, larger
   than any current base-word format), and dedicated execution hardware.
3. **Something narrower** (e.g. fuse only the two `CMOV`s, or only value+flag without a paired
   index) — not yet explored.

# Why This Isn't Decided

- No opcode space, bit layout, or execution-resource cost has been designed for option 2 — a
  4-register-operand instruction does not fit Aurora's 16-bit base word without a mandatory EXT
  word, which changes its cost/benefit relative to the status-quo sequence.
- The benefit is workload-dependent (only matters for kernels near the eight-word loop-capacity
  limit) and has not been benchmarked against representative code.
- Recorded as "Reserved / benchmark" in `RECENT_DECISIONS_SNAPSHOT.md` and as provisional entry
  `LATE-DSP-TRACK` in `ARCHITECTURE_DECISION_LOG_CURRENT.md` prior to this ADR; this document
  promotes that entry to a numbered ADR without resolving it, so it isn't lost track of.

# Next Steps Before This Can Be Locked

1. Benchmark representative argmin/argmax/track kernels with and without a fused instruction to
   quantify the actual cycle/loop-word savings.
2. If justified, design a concrete encoding (likely requiring a mandatory EXT word for the 4th
   register operand) and reconcile it against free opcode space.
3. Decide whether `TRACKMIN`/`TRACKMAX` making `POPMETA`'s specific use case less necessary changes
   the calculus on `POPMETA` itself (it does not — `POPMETA` is already locked/allocated via
   ADR-STREAM-009 and serves other stream-consume use cases beyond just this idiom).

# Related ADRs

- ADR-STREAM-009 — POPMETA Opcode Allocation (the current status-quo building block this would
  partially replace for the argmin/argmax use case specifically).
- ADR-ISA-021 — Contextual ZR, Unified Compare, and Packed Predicate Flags (defines the current
  `SUB ZR` / `CMOV` based argmin/argmax pattern this proposal targets).
- ADR-FE-006 — Two-Entry Prefetch Buffer and Eight-Word Hardware Loop (the loop-body-size
  constraint that makes fusion valuable in the first place).
