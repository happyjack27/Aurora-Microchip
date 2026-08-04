**Aurora Documentation Decision Register — Addendum**

*DDR-0046 • Encoded bytecodes in the Instruction Reference*

# Decision

The canonical AUR-ARCH-005 Instruction Reference shall display programmer-visible bytecodes, including the 16-bit base format, primary opcode map, subopcode keys, binary keys, operand-format diagrams, complete encoded instruction inventory, and little-endian byte examples.

# Rationale

A reader evaluating or programming Aurora needs to see the actual machine representation, not only mnemonics and semantics. Keeping bytecodes in the Instruction Reference also makes the document useful to assembler, simulator, compiler, and RTL readers.

# Governance

- The machine-readable ISA database is the source of truth for opcode values.

- Any opcode reassignment requires an ADR and regeneration of the reference.

- DIV remains a pseudo-operation; DIVSTEP is the encoded primitive.

- The Master Documentation Index identifies v1.1 as the current presentable bytecode edition.
