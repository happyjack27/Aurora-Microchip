**AUR-RTL-002I Memory Fabric**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Arbitrate instruction fetch, LSU, Q0/Q1, DMA, TCM, banked SRAM, MMIO, and external-memory transactions with deterministic ordering and bounded service.

# 2. Masters and Slaves

| Type    | Interfaces                                                |
|---------|-----------------------------------------------------------|
| Masters | IF, LSU, Q0, Q1, DMA channels, debug                      |
| Slaves  | ITCM, DTCM, SRAM bank 0/1, MMIO, external SRAM/flash/DRAM |

# 3. Request Bundle

| Field     | Width  | Meaning                   |
|-----------|--------|---------------------------|
| valid     | 1      | Request valid             |
| master_id | enum   | Origin                    |
| address   | 32     | Byte address              |
| write     | 1      | Write/read                |
| wdata     | 64 max | Write payload             |
| wstrb     | 8 max  | Byte strobes              |
| size      | 3      | Transfer width            |
| device    | 1      | Strong-order attribute    |
| age       | tag    | Retirement/completion tag |

# 4. Arbitration Policy

- TCM requests use dedicated paths where implemented.

- CPU retirement-critical requests have bounded priority.

- Stream refill may receive deterministic reservation slots.

- DMA receives remaining burst opportunities but cannot starve CPU/streams.

- MMIO is non-bursting and strongly ordered.

- Arbitration policy is fixed or privileged-configured and must be documented.

# 5. SRAM Banking

- Bank selection uses native 16-bit word interleaving.

- Two independent banks permit concurrent accesses when addresses select different banks.

- Same-bank conflicts serialize deterministically.

- Instruction fetch and data access may proceed concurrently if mapped to different banks or dedicated TCM.

# 6. Response Rules

- Responses return master ID, age tag, data, ready and fault.

- Responses may complete out of order only if the requesting master supports tags.

- MMIO responses preserve issue order.

- External ready/acknowledge wait states are absorbed without changing architectural order.

# 7. Assertions

- Every accepted request receives exactly one response or documented cancellation.

- No master is starved beyond configured bound.

- MMIO order equals request order.

- Same-bank collisions never corrupt data.

- Fault response does not include stale data as valid.
