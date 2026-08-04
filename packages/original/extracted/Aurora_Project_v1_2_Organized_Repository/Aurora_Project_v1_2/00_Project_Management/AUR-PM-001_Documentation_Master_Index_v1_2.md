This document is the authoritative index for every architecture, implementation, verification, and product document in the Aurora project.

# Document Lifecycle

Status values:\
• Planned\
• Draft\
• Review\
• Frozen\
• Superseded\
• Archived

# Document Metadata Standard

| ID | Title | Version | Status | Owner | Dependencies | Last Updated |
|----|----|----|----|----|----|----|
| AUR-ARCH-001 | Architecture Bible | 1.2 | Draft | Architecture | — | 2026-08 |
| AUR-ARCH-002 | Programmer's Model | 1.2 | Frozen | Architecture | 001 | 2026-08 |
| AUR-ARCH-003 | ABI Specification | 1.2 | Frozen | Architecture | 002 | 2026-08 |
| AUR-ARCH-004 | ISA & Opcode Map | 1.2 | Frozen | Architecture | 003 | 2026-08 |
| AUR-ARCH-005 | Instruction Reference | 1.2 | Draft | Architecture | 004 | 2026-08 |
| AUR-ARCH-006 | Memory Map | 1.2 | Draft | Architecture | 002 | 2026-08 |
| AUR-ARCH-007 | Pipeline & Microarchitecture | 1.2a | Draft | Architecture | 004,006 | 2026-08 |
| AUR-TOOL-001 | Compiler & Toolchain | 1.2 | Draft | Toolchain | 003,004,007 | 2026-08 |
| AUR-GUIDE-001 | Programmer's Guide | 1.2 | Draft | Toolchain | 001,005,007 | 2026-08 |
| AUR-VER-001 | Validation & Benchmark Suite | — | Planned | Verification | 005,007 | — |
| AUR-RTL-001 | RTL Architecture | — | Planned | Hardware | 007 | — |
| AUR-SIM-001 | Cycle Accurate Simulator | — | Planned | Simulation | 004,007 | — |
| AUR-VER-002 | Verification Plan | — | Planned | Verification | 001,007,RTL | — |
| AUR-PROD-001 | Aurora Product Family | — | Planned | Marketing | 001 | — |
| AUR-SALES-001 | Sales Guide | — | Planned | Marketing | PROD-001 | — |

# Dependency Flow

Architecture Bible → Programmer's Model → ABI → ISA → Memory Map & Pipeline → Compiler/Toolchain → Programmer's Guide → RTL → Simulator → Verification → Product Guides

# Governance Rules

- Every architectural change must update the Architecture Bible first.

- Frozen documents require an approved revision to change.

- Implementation documents must not contradict frozen architectural documents.

- The machine-readable ISA database is the single source of truth for encodings.

- Every document must reference related document IDs.

- Every release should include a document status review.
