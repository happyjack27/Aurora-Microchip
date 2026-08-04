Status: LOCKED\
Architecture baseline: Aurora v1.2n\
Date: August 2, 2026

# Decision

- Aurora adds a unary CONJ instruction for standalone complex conjugation.

- CONJ reuses the existing packed negate/subtract-from-zero datapath; no dedicated complex arithmetic unit is added.

- CONJ operates according to the active packed element width.

- In COMPLEX16 form, the source layout is \[imaginary:16 \| real:16\]; the real lane passes unchanged and the imaginary lane is negated.

- In COMPLEX8 form, the source layout is \[imag1:8 \| real1:8 \| imag0:8 \| real0:8\]; both imaginary lanes are negated and both real lanes pass unchanged.

- CONJ is a one-source, one-destination instruction and does not require MUL_COMPLEX to be active.

- CONJ does not alter the sticky CONJ_A or CONJ_B multiply modifiers.

- Negating the most-negative signed lane wraps in ordinary two's-complement form and sets the corresponding packed overflow status.

- ROUND and SAT mode bits do not affect CONJ.

- CONJ is expected to execute in one ordinary ALU/packed-negate cycle and may issue in either symmetric execution lane, subject to normal destination and resource hazards.

# Semantics

COMPLEX16:\
Rd\[15:0\] = Rs\[15:0\]\
Rd\[31:16\] = -signed(Rs\[31:16\])\
\
COMPLEX8:\
Rd\[7:0\] = Rs\[7:0\]\
Rd\[15:8\] = -signed(Rs\[15:8\])\
Rd\[23:16\] = Rs\[23:16\]\
Rd\[31:24\] = -signed(Rs\[31:24\])

# Rationale

Complex conjugation is only a selective packed negation. Making it an explicit unary instruction is clearer than broadening sticky conjugation modifiers to unrelated operations, while adding very little circuitry because Aurora already supports packed subtraction and negation.
