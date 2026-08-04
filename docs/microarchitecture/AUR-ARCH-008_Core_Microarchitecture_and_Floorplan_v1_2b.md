**Aurora Core Microarchitecture & Floorplan Specification**

*AUR-ARCH-008 \| Inside the Chip*

# 1. Core Inventory

| Block | Approx. area % | Role |
|----|----|----|
| Front end | 8 | Fetch, prefetch, branch prediction, decode |
| Issue window & scoreboard | 10 | 4-entry pairing, hazards, completion tracking |
| Register file | 9 | 16 x 32, two read ports, writeback arbitration |
| Two general execution lanes | 15 | Scalar/packed ALU, shifts, layout |
| Multiply/reduction cluster | 18 | Radix multiplier, compressor/reduction tree, MAC/DOT/SAD |
| DIVSTEP assist/control | 1 | One-step control and muxing; reuses lane ALU/shifter |
| Stream engines Q0/Q1 | 10 | 128-bit staging each, circular addressing |
| LSU and AGU | 8 | Load/store launch and address generation |
| Interrupt/ASC/control | 5 | Priority control, timers, privileged entry |
| Core memory fabric | 8 | TCM/SRAM/MMIO/DMA arbitration |
| Debug/trace/misc. | 8 | Debug state and implementation overhead |

# 2. Connectivity

Fetch -\> decode/window -\> register read -\> either issue lane -\> shared specialized resources -\> completion/commit -\> memory fabric.

# 3. Physical Guidance

- Place register file centrally between issue lanes.

- Place multiplier/reduction cluster close to both lanes and accumulators.

- Place Q0/Q1 near LSU and DTCM/SRAM interfaces.

- Place ITCM near front end and DTCM near LSU/streams.

- Keep issue-window dependency comparators physically compact.

- Area percentages are planning estimates, not synthesis results.

# 4. Critical Paths

- Window dependency select

- Register-file read to ALU

- Reduction-tree final stage

- Memory-bank arbitration

- Completion-to-forwarding path
