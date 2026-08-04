Status: LOCKED\
Architecture baseline: Aurora v1.2m\
Date: August 2, 2026

# Decision

- Aurora restores COMPLEX8 as a first-class packed complex multiply mode.

- COMPLEX8 is selected through the existing sticky MUL_COMPLEX interpretation state together with 8-bit packed element width.

- Each 32-bit source contains two signed complex values packed as \[imag1:8 \| real1:8 \| imag0:8 \| real0:8\].

- For each complex lane k, the exact internal components are Real_k = Ar_k\*Br_k - Ai_k\*Bi_k and Imag_k = Ar_k\*Bi_k + Ai_k\*Br_k.

- Each exact COMPLEX8 component may require 17 signed bits.

- Narrow COMPLEX8 MUL writes one aligned 64-bit destination pair containing \[imag1:16 \| real1:16 \| imag0:16 \| real0:16\].

- Each 17-bit exact component is reduced to its low 16 bits; sticky COVR and COVI indicate real or imaginary overflow in any packed lane.

- The implementation may retain a non-architectural per-lane overflow mask for debug, trace, or optional profile use.

- CONJ_A and CONJ_B modifiers apply independently to both packed complex lanes.

- COMPLEX8 MAC and MAS perform horizontal two-lane complex reduction into A0 and A1: A0 accumulates Real_0 + Real_1 and A1 accumulates Imag_0 + Imag_1.

- The exact widened products and sums are injected into the existing shared compressor/reduction network before accumulation.

- Independent per-lane complex accumulators are not added in the baseline architecture.

- COMPLEX8 uses the same overflow, trap-disable-by-default, and sticky status philosophy as COMPLEX16.

- COMPLEX32 remains deferred.

# Packed Layout

Source register:\
\[31:24\] imag1\
\[23:16\] real1\
\[15:8\] imag0\
\[7:0\] real0\
\
Destination pair:\
\[63:48\] imag1_result16\
\[47:32\] real1_result16\
\[31:16\] imag0_result16\
\[15:0\] real0_result16

# Rationale

Aurora already contains packed 8-bit multiplication, horizontal reduction, sign routing, sticky complex overflow, and COMPLEX16 cross-product control. COMPLEX8 therefore regularizes the mode system at modest incremental cost and directly benefits low-precision communications, SDR, correlation, beamforming, and packed FFT kernels.
