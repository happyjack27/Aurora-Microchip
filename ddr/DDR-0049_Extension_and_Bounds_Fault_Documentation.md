Status: LOCKED\
Date: August 2, 2026

# Decision

The Instruction Reference, Assembly Programmer's Guide, Programmer's Model, system-register specification, stream-engine specification, stack/ABI specification, machine-readable ISA table, and simulator/RTL documentation shall incorporate ZEXT8, SEXT8, ZEXT16, SEXT16, stack bounds, and non-circular stream end-fault behavior.

- Instruction entries must state that extension operations are unary, single-cycle pass-through candidates.

- Stack documentation must define STKLOW, STKHIGH, enable semantics, downward growth, and no-state-change on fault.

- Stream documentation must distinguish STOP, STATUS/IRQ, and FAULT end behaviors.

- Circular mode must be explicitly documented as suppressing terminal-count bounds faults while still allowing alignment or memory-access faults.

- Fault tables must add STACK_BOUNDS and STREAM_BOUNDS causes and identify the recorded candidate address.

- The v1.2f Instruction Reference supersedes v1.2e.
