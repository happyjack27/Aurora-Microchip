# Architectural Separation

| Mechanism | Primary role | Consumes instructions? | Walks memory autonomously? |
|----|----|----|----|
| Packed reduction | Compute over register/packed operands | Yes | No |
| Q0/Q1 stream | Address generation, staging, circular/pinned traversal | Triggered by stream-register operations | Prefetch/refill only within configured stream |
| DMA | Independent block transport | Only for setup/control | Yes |

# Baseline DMA Channels

- Channel 0: real-time/high-priority streaming transfer.

- Channel 1: background/general transfer.

- Both channels support 8/16/32-bit elements, 1D and 2D addressing, signed strides, row adjustments, inner/outer counts, half-transfer, completion, and error events.

# Near-Memory Connection

External/peripheral fabric -\> DMA channels -\> local-memory arbiter -\> DTCM/SRAM bank 0 and bank 1 -\> LSU and Q0/Q1 consumers.

# Synchronization Rules

- Complete core writes and issue FENCE/FENCE.IO as required before enabling a DMA read of those locations.

- Wait for DMA completion status/event, then issue the required fence before core or stream consumption of DMA-written data.

- Invalidate or reconfigure pinned streams whose backing memory was modified by DMA.

- DMA events may wake WFE and may also be routed to configured interrupt vectors.

# DMA Fault Model

| Fault | Meaning | Architectural response |
|----|----|----|
| DMA_ALIGN | Element/address alignment violation | Channel stops; error event/interrupt |
| DMA_BOUNDS | Protection or configured-region violation | Channel stops; fault address/status recorded |
| DMA_BUS | External/local target error | Channel stops; bus status recorded |
| DMA_CFG | Invalid descriptor or unsupported mode | Transfer does not start or stops precisely |

# No Core Datapath Redesign

The DMA block adds memory-fabric ports, arbitration, descriptor state, address adders/counters, small optional FIFOs, and event wiring. It does not change the architectural register file, arithmetic lanes, multiply modes, or calling convention.
