This document is the master index for all Aurora documentation. It tracks completion status, document purpose, dependencies, and recommended creation order.

# Phase 0 – Vision & Product Definition

| Document | Status | Purpose |
|----|----|----|
| Executive Summary | Complete | Project vision and overview. |
| Market Positioning | Complete | Target market, intended applications, competitive niche. |
| Architecture Bible | In Progress | Canonical design rationale and decision log. |

# Phase 1 – Architectural Specification

| Document | Status | Purpose |
|----|----|----|
| Programmer's Model | Complete | Registers, modes, accumulators, streams. |
| ABI Specification | Complete | Calling convention and binary interface. |
| Instruction Formats & Opcode Map | Complete | Encoding and opcode allocation. |
| Instruction Reference | Complete | Semantics, timing, flags, examples. |
| Machine-readable ISA Database | Complete | JSON/YAML source of truth. |

# Phase 2 – Microarchitecture

| Document | Status | Purpose |
|----|----|----|
| Memory Map & Privileged Registers | Complete | Address map and system registers. |
| Pipeline & Microarchitecture | Complete | Pipeline, hazards, pairing, scoreboard. |
| Compiler & Toolchain Spec | Complete | Compiler, assembler, linker, debugger. |
| Programmer's Guide | Complete | Optimization and coding guidance. |

# Phase 3 – Verification

| Document | Status | Purpose |
|----|----|----|
| Validation & Benchmark Suite | Not Started | ISA, DSP, MCU, compiler and regression tests. |
| RTL Architecture Specification | Not Started | Module hierarchy and interfaces. |
| Cycle-Accurate Simulator Spec | Not Started | Timing model and simulator. |
| Verification Plan | Not Started | Coverage, random testing, formal goals. |

# Phase 4 – Silicon

| Document                        | Status      | Purpose                     |
|---------------------------------|-------------|-----------------------------|
| Area / Timing / Power Estimates | Not Started | Implementation projections. |
| FPGA Bring-up Guide             | Not Started | Prototype validation.       |
| Silicon Bring-up Guide          | Not Started | Post-silicon validation.    |

# Phase 5 – Productization

| Document                      | Status      | Purpose                        |
|-------------------------------|-------------|--------------------------------|
| Aurora-L / M / P Family Guide | Not Started | Implementation profiles.       |
| Migration Guides              | Not Started | ARM, RISC-V, dsPIC, TI DSP.    |
| Sales & Product Guide         | Not Started | Customer-facing documentation. |

# Recommended Next Work Order

1.  1\. Validation & Benchmark Suite

2.  2\. RTL Architecture Specification

3.  3\. Cycle-Accurate Simulator Specification

4.  4\. Verification Plan

5.  5\. Silicon Area/Timing/Power Estimates

6.  6\. Aurora Product Family Guide

7.  7\. Migration Guides

8.  8\. Sales & Product Guide

# Document Relationships

Architecture Bible -\> Programmer's Model -\> ABI -\> ISA -\> Microarchitecture -\> Compiler -\> Programmer's Guide -\> RTL -\> Simulator -\> Verification -\> Product Guides.

# Completion Summary

Architecture definition is largely complete. Remaining work focuses on implementation, verification, benchmarking, silicon planning, and product collateral.
