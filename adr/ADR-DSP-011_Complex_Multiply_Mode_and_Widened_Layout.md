Status: LOCKED\
Architecture baseline: Aurora v1.2i\
Date: August 2, 2026

# Locked Decisions

- All Aurora multiply operations produce mathematically widened results; complex mode does not introduce truncating multiply semantics.

- Complex multiplication is selected through sticky arithmetic MODE state and does not allocate separate CMUL or CMAC opcodes.

- The baseline complex mode is COMPLEX16, operating on one signed complex value packed into each 32-bit source register.

- For COMPLEX16, bits \[15:0\] contain the real component and bits \[31:16\] contain the imaginary component.

- Given A = Ar + jAi and B = Br + jBi, multiply-family operations compute Real = Ar\*Br - Ai\*Bi and Imag = Ar\*Bi + Ai\*Br.

- Each component is an exact signed 33-bit mathematical result because it combines two signed 16x16 products.

- The real result is sign-extended into one aligned 64-bit destination register pair; the imaginary result is sign-extended into the next aligned 64-bit destination pair.

- Complex widened outputs are not word-interleaved. Each real or imaginary component remains contiguous in its own normal aligned register pair.

- Ordinary packed 2x16 multiplication remains lane-wise: each signed 16x16 product widens independently to 32 bits, and the two 32-bit lane products occupy one aligned 64-bit destination pair.

- Complex MAC and MAS use A0 as the real accumulator and A1 as the imaginary accumulator.

- A0 and A1 receive the signed cross-products through the existing multiplier/compressor network with mode-controlled routing and signs.

- COMPLEX16 mode may include CONJ_A and CONJ_B modifier bits. Conjugation negates the selected source's imaginary component before product routing.

- Complex mode affects MUL, MAC, MAS, and complex-capable DOT/reduction forms only. ADD, SUB, logic, compare, load/store, and ordinary packed operations retain their normal semantics.

- Complex 32-bit multiplication is not part of the v1.2i baseline because each exact component can require 65 signed bits, exceeding one 64-bit register pair. It remains a future profile decision.

- The scoreboard treats the four-register widened complex destination as two aligned register-pair writes and reserves both pairs until completion.

# Result Layout

Sources:\
Rs = \[ Ai:16 \| Ar:16 \]\
Rt = \[ Bi:16 \| Br:16 \]\
\
Destination beginning at aligned even register Rd:\
Rd:Rd+1 = sign_extend_64(Ar\*Br - Ai\*Bi)\
Rd+2:Rd+3 = sign_extend_64(Ar\*Bi + Ai\*Br)

# Rationale

This layout conforms to Aurora's existing packed-multiply rule: every output lane or component widens independently and is stored contiguously in ordinary aligned register-pair containers. Avoiding interleaving preserves carry, shift, scoreboard, forwarding, compiler, and debugger simplicity.
