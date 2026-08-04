Status: LOCKED\
Architecture baseline: Aurora v1.2k\
Date: August 2, 2026

# Decision

- Aurora multiply behavior is controlled by two independent sticky MODE bits: MUL_WIDE and MUL_COMPLEX.

- MUL_WIDE selects narrow versus widened destination treatment for ordinary real multiplication.

- MUL_COMPLEX selects ordinary real/packed interpretation versus COMPLEX16 cross-product interpretation.

- MAC and MAS remain explicit opcodes. There is no accumulation mode bit.

- MUL_WIDE=0 and MUL_COMPLEX=0: ordinary narrow real/packed multiply; destination receives the architecturally selected low-width result and normal multiply overflow/status rules apply.

- MUL_WIDE=1 and MUL_COMPLEX=0: ordinary widened real/packed multiply; every product lane is written at double input width using the existing aligned register-pair rules.

- MUL_WIDE=0 and MUL_COMPLEX=1: COMPLEX16 MUL; sources are \[imag:16\|real:16\], destination is one aligned 64-bit pair containing real32 and imag32, with sticky COVR/COVI overflow status.

- MUL_WIDE=1 and MUL_COMPLEX=1 is reserved/illegal for MUL in the v1.2k baseline because exact complex components require 33 bits and the previously considered four-register result was rejected.

- In COMPLEX16 mode, explicit MAC/MAS always inject the exact 33-bit real and imaginary product components into A0 and A1 before accumulation, independent of MUL_WIDE.

- The reserved complex-wide MUL combination may be assigned by a future profile only through a new architecture decision.

- MODECLR restores MUL_WIDE=0 and MUL_COMPLEX=0 along with the other scalar defaults.

# Mode Matrix

| MUL_COMPLEX | MUL_WIDE | MUL behavior | Destination | Status |
|----|----|----|----|----|
| 0 | 0 | ordinary narrow real/packed multiply | normal-width destination | normal multiply status |
| 0 | 1 | ordinary widened real/packed multiply | double-width pair/lane layout | exact product |
| 1 | 0 | COMPLEX16 packed multiply | Rd=real32, Rd+1=imag32 | sticky COVR/COVI |
| 1 | 1 | reserved for MUL | none | illegal-instruction/mode fault |

# Rationale

Separating result width from operand interpretation keeps the multiply family regular and avoids an accumulation mode that would duplicate the explicit MAC/MAS opcodes. Reserving complex-wide MUL preserves the uniform 32-bit register architecture and the compact two-register complex result already selected.
