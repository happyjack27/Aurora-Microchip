This roadmap supersedes earlier planning and orders the remaining documents by dependency rather than by convenience. Earlier documents are assumed complete or in progress.

# Phase A – RTL Definition (highest dependency)

| ID | Document | Purpose |
|----|----|----|
| AUR-RTL-002 | RTL Module Specifications | One specification per hardware block (fetch, decode, issue window, register file, lanes, LSU, streams, multiplier, reduction tree, divider, commit, interrupt, memory fabric, debug). |
| AUR-ARCH-009 | Performance Modeling Guide | Analytical throughput, IPC, bandwidth, latency and area models. |

# Phase B – Physical Implementation

| ID | Document | Purpose |
|----|----|----|
| AUR-ASIC-001 | ASIC Planning & Physical Design Guide | Floorplanning, SRAM macros, clocks, power, synthesis assumptions. |
| AUR-ASIC-002 | Timing Closure & Synthesis Guide | Constraints, critical paths, optimization strategy. |

# Phase C – Software Infrastructure

| ID | Document | Purpose |
|----|----|----|
| AUR-SDK-001 | SDK & Runtime Specification | CRT, startup, HAL, DSP library, intrinsics, linker scripts. |
| AUR-SIM-002 | Simulator Internal Design | Implementation architecture of functional and cycle-accurate simulators. |

# Phase D – Verification Expansion

| ID | Document | Purpose |
|----|----|----|
| AUR-VER-004 | Formal Verification Plan | Properties, proofs, coverage. |
| AUR-FPGA-002 | FPGA Demonstration Applications | Reference applications and validation demos. |

# Phase E – Productization

| ID | Document | Purpose |
|----|----|----|
| AUR-PROD-001 | Aurora Product Family Specification | Aurora-L, M and P feature matrices. |
| AUR-MIG-001 | Migration Guides | ARM Cortex-M, RISC-V, dsPIC, TI DSP migration. |
| AUR-SALES-001 | Sales & Product Guide | Customer-facing positioning and application guidance. |

# Dependency Graph

Architecture → RTL Module Specs → Performance Model → ASIC Planning → SDK & Simulator → Verification Expansion → Product Family → Migration Guides → Sales Guide

# Automatic Execution Plan

- Complete all AUR-RTL-002 module specifications before detailed RTL coding.

- Update the Architecture Bible, ADRs and Requirements DB whenever an architectural change occurs.

- Treat the machine-readable ISA database as the canonical encoding source.

- Keep verification and simulator synchronized with RTL module specifications.
