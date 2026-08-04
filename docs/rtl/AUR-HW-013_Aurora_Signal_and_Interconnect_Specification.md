This document is the canonical specification for inter-block interfaces within the Aurora processor. Every major datapath and control interface should eventually be described here. The entries below establish the canonical interface inventory.

| Interface ID | Source | Destination | Typical Width | Timing | Handshake | Purpose |
|----|----|----|----|----|----|----|
| IFETCH_BUS | HW-FE-001 Instruction Fetch | HW-FE-003 Prefetch Buffer | TBD | Registered unless noted | Ready/valid or dedicated control | Instruction words, fetch control |
| PREFETCH_TO_DECODE | HW-FE-003 Prefetch Buffer | HW-FE-004 Decoder | TBD | Registered unless noted | Ready/valid or dedicated control | Decoded instruction stream |
| DECODE_TO_WINDOW | HW-FE-004 Decoder | HW-ISS-001 Issue Window | TBD | Registered unless noted | Ready/valid or dedicated control | Decoded operations and metadata |
| WINDOW_TO_SCOREBOARD | HW-ISS-001 Issue Window | HW-ISS-002 Scoreboard | TBD | Registered unless noted | Ready/valid or dedicated control | Hazard queries |
| WINDOW_TO_LANES | HW-ISS-001 Issue Window | HW-EXE-001 Execution Lanes | TBD | Registered unless noted | Ready/valid or dedicated control | Issued operations |
| REG_READ | HW-REG-001 Register File | HW-EXE-001 Execution Lanes | TBD | Registered unless noted | Ready/valid or dedicated control | Operand buses |
| IMM_PATH | HW-FE-004 Decoder | HW-EXE-001 Execution Lanes | TBD | Registered unless noted | Ready/valid or dedicated control | Immediate values |
| BYPASS_NET | HW-EXE-001 / HW-RET-001 | HW-REG-002 Operand Routing | TBD | Registered unless noted | Ready/valid or dedicated control | Forwarding network |
| MUL_REQ | HW-EXE-001 | HW-EXE-002 Shared Arithmetic | TBD | Registered unless noted | Ready/valid or dedicated control | Multiply/MAC/DOT requests |
| DIVSTEP_REQ | HW-EXE-001 | HW-EXE-003 DIVSTEP Assist | TBD | Registered unless noted | Ready/valid or dedicated control | DIVSTEP requests |
| LSU_REQ | HW-EXE-001 | HW-MEM-001 LSU | TBD | Registered unless noted | Ready/valid or dedicated control | Load/store operations |
| STREAM_REQ | HW-EXE-001 | HW-MEM-002/003 Streams | TBD | Registered unless noted | Ready/valid or dedicated control | Stream operations |
| MEM_FABRIC | HW-MEM-001 LSU | HW-MEM-004 Memory Fabric | TBD | Registered unless noted | Ready/valid or dedicated control | Memory transactions |
| DMA_FABRIC | DMA | HW-MEM-004 Memory Fabric | TBD | Registered unless noted | Ready/valid or dedicated control | DMA transfers |
| WRITEBACK | HW-RET-001 Retirement | HW-REG-001 Register File | TBD | Registered unless noted | Ready/valid or dedicated control | Register writes |
| FLAG_UPDATE | HW-RET-001 Retirement | PSR | TBD | Registered unless noted | Ready/valid or dedicated control | Flag writes |
| INTERRUPT | HW-CTL-001 Interrupt Controller | HW-RET-001 Retirement | TBD | Registered unless noted | Ready/valid or dedicated control | Precise interrupt requests |
| DEBUG | HW-DBG-001 Debug | Multiple | TBD | Registered unless noted | Ready/valid or dedicated control | Halt, step, trace |

# Interconnect Categories

- Instruction path

- Operand path

- Immediate path

- Forwarding/bypass network

- Shared arithmetic request/response

- Load/store path

- Stream path

- Memory fabric

- Writeback buses

- Interrupt and exception network

- Debug and trace network

- Clock/reset distribution (documented separately in physical design)

# Future Expansion

Each interface will ultimately specify signal names, widths, reset values, timing, pipeline stage, arbitration rules, and corresponding RTL modules.
