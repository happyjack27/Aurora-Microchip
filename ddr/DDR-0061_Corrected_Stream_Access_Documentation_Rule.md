Status: LOCKED\
Date: August 3, 2026

- AUR-ARCH-005 shall state the canonical distinction: stream-capable computation accesses Q0/Q1 implicitly; POP/PUSH/PEEK are standalone explicit transfers; MOV/CMOV never access streams.

- All wording claiming POP/PUSH/PEEK are the only stream-access instructions shall be marked superseded and removed from future consolidated editions.

- Every stream-capable instruction entry shall specify which source and destination positions may select Q0/Q1 and whether the action is consume, produce, or peek.

- Reduction-format documentation shall retain local/stream source selection and INIT/ACC behavior.

- Atomic retirement rules shall cover one-stream, two-stream, and consume-plus-produce instructions.

- Assembler, simulator, RTL, compiler, scheduler, scoreboard, and verification documents shall use this exact distinction.

- MOV/CMOV tests shall verify that no stream side effects occur on either predicate path.

- AUR-ARCH-005 v1.2r supersedes v1.2q as the canonical working Instruction Reference.
