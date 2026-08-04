Status: LOCKED\
Date: August 2, 2026

- AUR-ARCH-005 shall document COMPLEX16 MODE semantics, packed source layout, exact 33-bit component equations, four-register destination layout, conjugation modifiers, timing, and scoreboard behavior.

- AUR-ARCH-006 shall include complex multiply, complex MAC, conjugate dot-product, and FFT-oriented examples.

- The multiply/reduction hardware specification shall document cross-product routing and sign injection into the shared compressor tree.

- The ABI/compiler documentation shall require an aligned four-register destination group for widened COMPLEX16 MUL results.

- The machine-readable architecture data shall record COMPLEX16 as a MODE variant rather than separate CMUL/CMAC mnemonics.

- AUR-ARCH-005 v1.2i supersedes v1.2h as the canonical working Instruction Reference.
