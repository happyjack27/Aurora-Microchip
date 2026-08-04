Status: LOCKED\
Architecture baseline: Aurora v1.2o\
Date: August 3, 2026

# Locked Decisions

- Aurora keeps packed reduction instructions and stream traversal conceptually and architecturally separate.

- Packed reductions operate only on scalar or packed values presented through registers or stream-register reads; they do not autonomously walk memory.

- The stream engines remain responsible for address generation, 1D/2D traversal, circular and pinned behavior, staging, element width, and successful-consume advancement.

- DMA is a required near-memory subsystem in the baseline Aurora SoC profile, not an optional future concept.

- The baseline DMA contains two channels: one real-time/high-priority channel and one background/general channel.

- Each DMA channel supports source and destination addresses, 8/16/32-bit element width, inner count, outer count, signed source stride, signed destination stride, source row adjustment, destination row adjustment, enable, priority, completion, half-transfer, and error status.

- DMA can transfer among peripherals/external memory and the two local DTCM/SRAM banks, subject to the SoC memory map and protection rules.

- DMA is a direct master of the local-memory fabric and does not route data through the GPR file, LSU writeback path, or execution lanes.

- The local-memory arbiter explicitly handles instruction fetch/refill, LSU, Q0, Q1, and DMA requests.

- Arbitration is weighted or deadline-aware rather than permanently fixed-priority; real-time stream service may receive urgent preference, while DMA receives guaranteed progress and cannot starve.

- DMA completion, half-transfer, and fault conditions can generate an interrupt and/or architectural event; WFE may wake on enabled DMA events.

- DMA faults include alignment, bounds/protection, bus/target error, and descriptor/configuration error.

- FENCE and FENCE.IO provide the ordering primitives needed before starting DMA and before consuming DMA-produced data.

- DMA supports ping-pong/double-buffer operation through half-transfer/completion events and software-controlled buffer exchange.

- DMA writes do not automatically update pinned stream staging contents. Software must invalidate or reconfigure a pinned stream before consuming memory modified by DMA.

- Optional hardware snoop-based pinned-stream invalidation may exist in a future SoC profile, but is not required in the baseline.

- The DMA addition requires a memory-fabric master port, arbitration, event/interrupt wiring, DMA control/status registers, and optional small transfer FIFOs; it does not require changes to the GPR width, register-file port count, execution-lane arithmetic, or ABI.

- DMA architectural configuration is supervisor-only unless an implementation exposes restricted user descriptors through a protection mechanism.

# Conceptual Layering

Packed reduction: compare/sum/min/max/arg/count within values already delivered to the core.\
Stream engine: select and stage the next values using deterministic address-generation state.\
DMA engine: move blocks between peripherals/external memory and near memory independently of instruction issue.

# Required Hardware Delta

| Block | Required change | Unchanged |
|----|----|----|
| Local memory fabric | Add DMA master request/response path and fairness/deadline arbitration | Two-bank interleaved SRAM organization |
| Interrupt/event fabric | Add per-channel completion, half-transfer, and error sources | Existing vectored priority model |
| System register space | Add DMA channel descriptors and status | GPR/ABI layout |
| Pinned streams | Add software-visible invalidation/coherence rule | 128-bit staging structure |
| Execution core | Add ordering/documented synchronization points | ALUs, multiplier, scoreboard fundamentals |

# Rationale

This division keeps each mechanism regular: reductions compute, streams traverse, and DMA transports. A two-channel 2D-capable DMA materially improves audio, imaging, sensing, motor-control, and communications workloads while requiring only localized memory-fabric and control-plane additions.
