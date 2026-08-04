Status: LOCKED\
Date: August 3, 2026

- The Architecture Bible, memory-system specification, stream-engine specification, SoC integration guide, programmer guide, system-register map, RTL block catalog, and master index shall identify DMA as a required baseline near-memory subsystem.

- Documentation shall keep packed reduction semantics separate from stream traversal and DMA transfer semantics.

- The DMA chapter shall define the two-channel baseline, 1D/2D descriptors, arbitration, events, faults, fences, and double-buffer workflow.

- The pinned-stream chapter shall state that DMA-modified backing memory requires explicit invalidation or reconfiguration before pinned reuse.

- Timing and block diagrams shall show DMA as a local-memory-fabric master alongside IF, LSU, Q0, and Q1.

- AUR-ARCH-005 v1.2o becomes the canonical working Instruction Reference after appending the architectural interaction notes.
