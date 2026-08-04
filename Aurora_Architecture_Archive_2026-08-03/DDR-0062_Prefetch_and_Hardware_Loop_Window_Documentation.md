Status: LOCKED\
Date: August 3, 2026

- AUR-ARCH-005 shall define the prefetch buffer as two 32-bit entries, separate from the four-word decoded loop replay buffer.

- The hardware-loop chapter shall define an eight-word captured window and distinguish words from architectural instructions.

- All loop examples and assembler diagnostics shall count extension words against the eight-word capacity.

- The compiler and assembler shall reject captured loops that end on an incomplete instruction boundary.

- The scheduler shall model the first four loop words as decoded replay and words five through eight as pinned raw words requiring normal decode.

- The RTL, simulator, verification plan, and power model shall cover pairing across the storage boundary and prohibit pairing across the iteration wrap.

- AUR-ARCH-005 v1.2s supersedes v1.2r as the canonical working Instruction Reference.
