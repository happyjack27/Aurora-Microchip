Status: LOCKED\
Date: August 2, 2026

- AUR-ARCH-005 shall document ROUND and SAT as sticky MODE bits and list the exact instruction classes they affect.

- The manual shall state that ordinary scalar shifts do not obey ROUND and ordinary arithmetic does not obey SAT.

- All affected instruction entries shall specify operation ordering: shift/narrow, round-to-nearest-even, then saturation clamp.

- Timing tables shall allow an implementation-defined additional cycle when ROUND or SAT is active.

- AUR-ARCH-006 shall include Q15/Q31 audio, packed sample conversion, and accumulator-extraction examples.

- The DSP status register documentation shall define SAT_OCCURRED and its explicit clear mechanism.

- AUR-ARCH-005 v1.2l supersedes v1.2k as the canonical working Instruction Reference.
