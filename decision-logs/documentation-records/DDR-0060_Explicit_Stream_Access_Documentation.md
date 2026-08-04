Status: LOCKED\
Date: August 3, 2026

- AUR-ARCH-005 shall define POP, PUSH, and PEEK as the only baseline stream-data access instructions.

- All examples that treat Q0/Q1 as ordinary MOV or CMOV operands shall be removed or corrected.

- MOV and CMOV instruction entries shall explicitly prohibit stream, memory, MMIO, and system-register side effects.

- The stream chapter shall document ADDR_NEXT, ADDR_LAST, ORD_NEXT, and ORD_LAST as system registers accessed through system-register transfer instructions.

- The simulator and RTL shall advance stream state only when an explicit POP or PUSH successfully retires.

- The compiler backend shall not fold stream consumption into MOV, CMOV, or predicated operations.

- The ABI documentation shall describe R13 as an optional LR whose liveness is determined by call analysis.

- AUR-ARCH-005 v1.2q supersedes v1.2p as the canonical working Instruction Reference.
