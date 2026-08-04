**Aurora v1.2 Cycle-Accurate Simulator Specification**

*AUR-SIM-001 \| Canonical Draft 1*

# 1. Simulator Modes

- Functional mode: architectural correctness without cycle timing

- Cycle-accurate mode: pipeline, window, scoreboard, memory and interrupt timing

- Trace-replay mode: deterministic reproduction of failures

# 2. State Model

- GPRs, PSR, A0/A1, Q0/Q1, PC/SP/LR

- Four-entry issue window and per-entry status

- Scoreboard and outstanding completion records

- Memory map, TCM/SRAM timing, MMIO and DMA state

- Interrupt pending/active state and countdown timer

# 3. Per-Cycle Order

1.  Apply external events and memory responses

2.  Retire oldest completed instructions

3.  Recognize precise interrupts

4.  Advance multi-cycle units

5.  Execute/launch selected issue pair

6.  Select and compact issue window

7.  Fetch and decode new words

# 4. Trace Format

- Cycle number, PC, decoded instruction, issue lane, resource mask

- Register/flag/accumulator writes

- Memory requests/responses and stream consumption

- Window contents, scoreboard stalls and branch recovery

- Interrupt and exception events

# 5. Validation

The simulator must consume the canonical ISA JSON and compare against directed tests, random programs, and RTL traces.
