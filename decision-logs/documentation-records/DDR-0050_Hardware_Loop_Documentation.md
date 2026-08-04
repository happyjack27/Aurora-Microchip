Status: LOCKED\
Date: August 2, 2026

# Decision

- All canonical documents shall use LOOP and NOP, not LOOPSET, LOOPEND, or NOP.LEND.

- Instruction Reference entries shall include bytecodes, count-minus-one encoding, legal body rules, LOOP_FORMAT faults, interrupt resumption, and context-transfer behavior.

- The Assembly Programmer's Guide shall show one-instruction and short multi-instruction examples.

- The pipeline and front-end documents shall identify a four-entry loop buffer or equivalent reuse of the prefetch/decode storage.

- The machine-readable ISA table shall rename opcode keys 0xC0 and 0xC1 accordingly.

- The Master Documentation Index shall identify AUR-ARCH-005 v1.2g as the canonical working Instruction Reference.
