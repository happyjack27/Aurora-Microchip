**AUR-RTL-002L Debug & Trace**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Provide nonintrusive architectural debug, breakpoints, single-step, trace visibility, and performance-observation hooks without changing normal execution semantics.

# 2. Debug Features

- Halt/resume at retirement boundary.

- Single-step one architectural instruction or retirement group.

- Instruction-address breakpoints.

- Optional data watchpoints.

- Read/write GPR, PSR, accumulators, streams and system registers while halted.

- Optional trace of issue, completion, retirement, memory and interrupts.

# 3. Trace Record

| Field        | Meaning                              |
|--------------|--------------------------------------|
| cycle        | Coarse or exact cycle count          |
| pc           | Instruction PC                       |
| opcode       | Decoded instruction                  |
| issue lanes  | Which instructions issued            |
| stall reason | Dependency/resource/memory           |
| writes       | Architectural destinations           |
| memory       | Address/data/type                    |
| event        | Branch, fault, interrupt, DMA/stream |

# 4. Intrusiveness Rules

- Disabled debug logic must not affect architectural timing except documented synthesis impact.

- Trace overflow may drop records but must not stall the core unless explicitly configured.

- Halting waits for precise boundary; externally visible stores are not duplicated.

- Debug writes to PC/PSR invalidate prefetched and decoded state.

# 5. Assertions

- Single-step retires the requested number of architectural instructions.

- Breakpoint halts before executing the matching instruction unless configured after-execute.

- Trace records preserve retirement order.

- Debug access while running cannot corrupt register file arbitration.

- Resume restarts from architecturally visible PC.
