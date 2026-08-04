Status: LOCKED\
Architecture baseline: Aurora v1.2p\
Date: August 3, 2026

# Locked Decisions

- Aurora defines ZR as a contextual zero/discard operand encoding rather than as a seventeenth register or a permanently dedicated GPR.

- In instruction fields where direct PC access is architecturally prohibited, register code 0xF is interpreted as ZR rather than R15.

- Reading ZR yields 0x00000000. Writing ZR discards the result while preserving the instruction's defined flag and exception effects.

- R15 remains the architectural PC in control-flow and other formats that explicitly permit or require PC access.

- The register map remains unchanged: R15=PC, R14=SP, R13=LR, and R12=optional FP or ordinary GPR.

- R14 and R15 remain hard special-purpose registers. R12 and R13 remain soft or conventionally special-purpose and are not sacrificed for zero storage.

- Aurora does not allocate a separate packed-compare opcode family.

- CMP is an assembler alias for SUB ZR, Ra, Rb. TST is an assembler alias for AND ZR, Ra, Rb.

- In scalar mode, compare/test aliases update the ordinary scalar condition flags.

- In packed 8-bit or packed 16-bit mode, the same SUB/AND-to-ZR encodings perform lane-wise operations and update one predicate flag per active packed lane.

- Packed predicate flags are non-sticky current-result state, replaced by the next packed flag-producing operation.

- For 4x8 mode, predicate bits P0-P3 correspond to lanes 0-3. For 2x16 mode, P0-P1 are active and the remaining predicate bits are cleared.

- For aligned wide packed forms, the predicate state expands to eight bits for 8x8 or four bits for 4x16. The implementation stores the complete current lane predicate mask in the DSP predicate-status register.

- The ordinary conditional-move instruction uses scalar condition flags in scalar mode and performs lane-wise conditional movement using the current predicate flags in packed mode.

- No separate packed conditional-move or masked-move opcode is allocated.

- A packed conditional move selects the source lane when the selected predicate condition is true and otherwise preserves the corresponding destination lane.

- Predicate inversion is selected by the ordinary condition field, so the same conditional-move encoding supports move-if-true and move-if-false.

- Flag-producing packed comparisons and packed conditional moves remain ordinary register operations; they are conceptually separate from stream traversal.

- A stream argmin/argmax kernel may consume packed values from Q0/Q1, compare them against packed running candidates through SUB ZR, and update packed values or indices through the ordinary conditional-move instruction inside a hardware loop.

- ZR is not permitted as a register-pair member or pair base.

- ZR as a load destination is prohibited. ZR as a store-data operand is permitted and stores zero. ZR as a base operand is format-specific and is not enabled in the baseline memory formats unless separately documented.

# Register Classification

| Register | Locked role | Classification |
|----|----|----|
| R15 | Program counter | Hard special-purpose; its code becomes ZR only in formats where PC is prohibited |
| R14 | Stack pointer | Hard special-purpose |
| R13 | Link register | Soft special-purpose; reusable when the return address is not live |
| R12 | Optional frame pointer / GPR | Soft convention; fully usable as a GPR when no frame pointer is required |

# Examples

CMP R2, R3 ; alias: SUB ZR, R2, R3\
TST R4, R5 ; alias: AND ZR, R4, R5\
SUB R6, ZR, R7 ; negate R7\
ADD R8, R9, ZR ; copy R9\
ST32 ZR, \[R10\] ; store zero\
\
MODE \#PACKED8\
CMP R4, R5 ; sets P0-P3 lane predicates\
CMOV.GT R4, R5 ; per lane: if predicate true, R4 lane \<- R5 lane

# Rationale

This restores the useful zero-register behavior without reducing Aurora's already constrained visible register set. Using the same arithmetic and logic instructions for scalar and packed comparisons avoids opcode duplication. Reusing the ordinary conditional-move encoding in packed mode provides branchless lane updates that fit short hardware loops without allocating a packed-only masked-move opcode.
