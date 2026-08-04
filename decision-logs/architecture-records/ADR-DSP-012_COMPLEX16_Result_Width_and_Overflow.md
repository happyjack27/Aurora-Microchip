Status: LOCKED\
Architecture baseline: Aurora v1.2j\
Date: August 2, 2026

# Decision

- Aurora retains a uniform 32-bit general-purpose register width. No 33-bit GPR format or special extra result bit is added.

- COMPLEX16 MUL accepts packed signed sources \[imaginary:16 \| real:16\].

- The exact mathematical real and imaginary components may each require 33 signed bits.

- COMPLEX16 MUL writes one aligned 64-bit destination pair: Rd receives the low 32 bits of the real component and Rd+1 receives the low 32 bits of the imaginary component.

- If either exact component is outside the signed 32-bit range, the corresponding sticky DSP overflow status is set.

- The architecture provides separate sticky real and imaginary overflow indications, COVR and COVI, plus an aggregate COV condition defined as COVR OR COVI.

- Overflow does not trap or interrupt by default.

- An implementation may provide a privileged trap-enable control that converts newly detected complex overflow into a precise DSP-overflow exception, but this is optional and disabled after reset.

- COMPLEX16 MAC and MAS accumulate the exact widened real and imaginary components into A0 and A1 respectively, preserving the full product range subject to the existing accumulator-width and overflow rules.

- COMPLEX16 MUL therefore uses compact packed results, while MAC/MAS provide the exact accumulation path for precision-sensitive DSP kernels.

- The prior v1.2i four-register exact-result layout is superseded.

# Result Layout

Sources:\
Rs = \[ Ai:16 \| Ar:16 \]\
Rt = \[ Bi:16 \| Br:16 \]\
\
Exact internal values:\
Real33 = Ar\*Br - Ai\*Bi\
Imag33 = Ar\*Bi + Ai\*Br\
\
Architectural MUL result:\
Rd = Real33\[31:0\]\
Rd+1 = Imag33\[31:0\]\
COVR = sticky(COVR OR !fits_signed32(Real33))\
COVI = sticky(COVI OR !fits_signed32(Imag33))

# Rationale

Changing the register file, forwarding network, scoreboard, ABI, debugger state, and context format for a single extra complex-result bit would be disproportionate. Sticky overflow reporting preserves visibility of lost range, while A0/A1 retain an exact accumulation path for the workloads where that precision matters.
