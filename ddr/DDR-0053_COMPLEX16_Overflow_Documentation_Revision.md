Status: LOCKED\
Date: August 2, 2026

- AUR-ARCH-005 shall replace the v1.2i four-register COMPLEX16 MUL result with one aligned 64-bit pair containing 32-bit real and imaginary results.

- The Instruction Reference shall document COVR, COVI, aggregate COV, sticky-clear behavior, and optional trap enable.

- AUR-ARCH-006 shall recommend MAC/MAS into A0/A1 when exact complex product accumulation is required.

- The ABI/compiler documentation shall treat COMPLEX16 MUL as a two-register result and no longer reserve four destination registers.

- The multiply/reduction hardware documentation shall retain exact 33-bit internal component generation before truncation and overflow detection.

- AUR-ARCH-005 v1.2j supersedes v1.2i.
