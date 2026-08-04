Status: LOCKED\
Architecture baseline: Aurora v1.2h\
Date: August 2, 2026

# Decision

- Q0 and Q1 support a pinned circular read mode for small resident patterns.

- Pinned mode retains a complete circular working set in the existing 128-bit stream staging buffer and replays it locally without further memory reads.

- The pinned working set may contain 1 through 4 elements at 32-bit width, or any 8-bit/16-bit element count whose total storage does not exceed 128 bits.

- Pinned mode is read-only in the baseline architecture. Pinned write streams are illegal.

- Pinned mode requires circular mode. Enabling PIN while circular mode is disabled raises a precise QCFG fault.

- The default phase advances only after a successful consuming stream read or pop.

- Pipeline stalls, scoreboard delays, faults, interrupts, debug halt, and unsuccessful accesses do not advance the pinned phase.

- QPEEK observes the current element without advancing it.

- QSTEP Qn explicitly advances the current pinned circular phase by one element without transferring data.

- QSTEP uses opcode key 0xB8 and is legal only for a valid pinned circular stream. Otherwise it raises a precise STREAM_STATE fault.

- Aurora does not provide raw per-CPU-clock pinned-stream rotation in the baseline architecture.

- Timer-, peripheral-, sample-clock-, or DMA-event-driven phase advancement is reserved as an optional SoC integration feature and is not architectural in the baseline core.

- QCFG gains a PIN field. The assembler alias QSETPIN Qn, \#ON/#OFF encodes as QCFG.

- Entering pinned mode fills the complete working set before the first architectural consume completes; the implementation may prefill speculatively, but no partial pinned set is visible.

- Reconfiguring address, width, circular extent, count, stride, or PIN clears pinned validity and requires refill.

- Explicit stream invalidate, context restore, reset, or a relevant coherence invalidation clears pinned validity.

- Full CTXSAVE/CTXRESTORE preserves pinned configuration, phase, validity, and resident staging contents when STREAM_CONFIG and STREAM_STAGING are selected.

- Pinned mode does not suppress alignment, access-permission, or physical-memory faults during initial fill.

# Rationale

Pinned mode turns the existing stream staging buffer into a deterministic tiny resident circular store for repeated coefficients and short patterns. Advancing on successful consumption preserves precise in-order behavior through stalls and interrupts. Explicit QSTEP covers deliberate phase changes without coupling semantics to the raw CPU clock.

# Rejected Alternative

Automatic advancement every CPU clock was rejected because stalls, clock-frequency changes, debug stops, and interrupts would make the visible stream phase depend on microarchitectural timing rather than architectural consumption.
