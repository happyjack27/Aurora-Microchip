Status: LOCKED\
Architecture baseline: Aurora v1.2q\
Date: August 3, 2026

# Locked Decisions

- Q0 and Q1 are stream-engine entities and are not ordinary GPR source or destination operands.

- All stream data transfer is explicit through POP, PUSH, and PEEK instructions.

- POP Rd, Qn consumes exactly one stream element and advances stream address, count, ordinal, and staging state only after successful completion.

- PEEK Rd, Qn reads the current staged element without consuming it and without changing address, count, ordinal, phase, or staging pointers.

- PUSH Qn, Rs produces exactly one stream element and advances stream state only after successful completion.

- MOV is strictly a GPR-to-GPR operation. MOV may not read from or write to Q0/Q1 and may not access stream system state.

- CMOV is strictly a GPR-to-GPR conditional copy. Its only conditional architectural effect is whether its GPR destination is replaced.

- CMOV may not POP, PUSH, PEEK, access memory, access MMIO, read or write stream system registers, update stream addresses, or modify stream counts or ordinals.

- The true and false paths of CMOV therefore have identical memory, stream, address-generation, and exception side effects.

- In packed mode, CMOV remains lane-wise under the current predicate flags, but it still operates only on GPR lanes already read into the execution pipeline.

- Conditional execution must never determine whether a stream advances. Stream progression is controlled only by explicit POP/PUSH operations that retire successfully.

- Stream configuration and stream position metadata are architectural system-register state, accessed through the existing low-operand-count system-register transfer instructions.

- Each stream exposes ADDR_NEXT, ADDR_LAST, ORD_NEXT, and ORD_LAST system registers.

- ORD_NEXT and ORD_LAST are zero-based linear logical-element ordinals. They advance only on successful consuming or producing operations as defined by stream direction.

- For packed stream transfers, ORD_LAST identifies the first scalar lane in the transferred packed group; a scalar lane ordinal is ORD_LAST plus its lane number.

- Stalls, PEEK operations, faults, flushed instructions, interrupts before retirement, and debug halt do not advance stream address or ordinal state.

- A combined POP-with-metadata instruction is not part of the v1.2q baseline. It remains a future encoding candidate if benchmarks show that a separate POP plus system-register read prevents important kernels from fitting the four-instruction hardware-loop buffer.

- R13 remains an optional link register rather than a permanently reserved register. The compiler may allocate R13 as a GPR in leaf functions or whenever the return address is saved or dead.

# Canonical Stream Operations

| Operation | Data movement | Advances stream? | Permitted side effects |
|----|----|----|----|
| POP Rd, Qn | Stream to GPR | Yes, after successful retirement | Consume, address/count/ordinal update |
| PEEK Rd, Qn | Stream to GPR | No | GPR write only |
| PUSH Qn, Rs | GPR to stream | Yes, after successful retirement | Produce, address/count/ordinal update |
| MOV Rd, Rs | GPR to GPR | No | GPR write only |
| CMOV.cond Rd, Rs | Conditional GPR to GPR | No | Conditional GPR write only |

# Rationale

Explicit stream operations make every address-changing action visible in assembly and deterministic under stalls, predication, faults, interrupts, and debugging. Keeping MOV and CMOV pure prevents a condition result from changing which stream elements later instructions observe. Metadata remains system state rather than being disguised as GPR operands.
