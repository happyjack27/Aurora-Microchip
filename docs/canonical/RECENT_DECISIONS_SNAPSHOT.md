# Recent Locked / Reserved Decisions Snapshot

This file captures late-session decisions that may not yet be fully merged into the canonical DOCX.

## Locked

- R15 = PC, R14 = SP, R13 = optional LR/GPR, R12 = optional FP/GPR.
- Contextual ZR uses register code 0xF only in formats where PC is prohibited.
- CMP/TST are aliases using ZR as a discarded destination.
- Packed comparisons update per-lane predicate state; ordinary CMOV becomes lane-wise in packed mode.
- MOV and CMOV never consume or produce stream data.
- Stream-capable arithmetic, packed, multiply, MAC/MAS, and reduction instructions implicitly consume/produce when Q0/Q1 is selected.
- POP/PUSH/PEEK remain standalone explicit stream transfers.
- POPMETA is locked as an aligned register-pair destination concept: value plus address (meta selector removed, ORD option retired 2026-08-04 along with Qn.ORD_NEXT/ORD_LAST).
- Two 32-bit prefetch entries plus four decoded words form an eight-16-bit-word captured loop window.
- Short backward relative branches may replay from the resident eight-word window.
- Resident replay assumes compiler-enforced single-entry regions; hardware performs no interior-entry detection.
- Explicit hardware loops remain valuable because they remove decrement/test/branch overhead and final-exit misprediction.
- DMA is a required near-memory subsystem; reductions, stream traversal, and DMA remain conceptually distinct.

## Reserved / benchmark candidates

- TRACKMIN / TRACKMAX fused compare-and-track pair operation.
- Comparison-count reduction (REDCNT) remains a candidate and is not locked.
