Status: LOCKED\
Date: August 2, 2026

# Decision

AUR-ARCH-005 Instruction Reference, AUR-ARCH-006 Assembly Language Programmer's Guide, the Architecture Bible, Programmer's Model, system-register specification, RTL module specifications, and machine-readable ISA database shall document the two-level privilege model and the IRET, WFI, WFE, HALT, CTXSAVE, and CTXRESTORE instructions.

# Required Documentation Rules

- Use IRET as the canonical mnemonic; IRT may be accepted as an assembler alias.

- Describe WFI and WFE wake conditions separately.

- Mark HALT, CTXSAVE, and CTXRESTORE as privileged and serializing.

- State that context transfers defer maskable interrupts but retain them as pending.

- State that CTXSAVE/CTXRESTORE reuse the stream-style memory path without modifying Q0/Q1 architectural state.

- Include context-mask groups and atomic restore ordering.

- Update opcode tables and bytecode diagrams with system sub-opcodes 0xDB through 0xDF.

- Record v1.2e as the first documentation baseline containing these locked decisions.
