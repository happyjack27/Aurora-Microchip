# Architectural Responsibility

The Load/Store Unit implements the architectural behavior defined by the ISA and microarchitecture specifications.

# Primary Functions

- Address generation

- bank selection

- MMIO

- ITCM/DTCM

- alignment

# Pipeline Placement

Identify stage ownership, input/output latching, forwarding boundaries, and stall behavior.

# State Elements

Enumerate every flip-flop, RAM, counter, queue, and valid bit owned by this module.

# Interfaces

Specify every signal with width, direction, timing, reset value, and protocol.

# Microarchitecture Notes

- One launch/cycle baseline

- DMA interaction

# RTL Guidance

Provide synthesizable SystemVerilog pseudocode, parameterization rules, assertions, and clock-gating opportunities.

# Verification Matrix

| Feature            | Directed | Random/Formal |
|--------------------|----------|---------------|
| Address generation | Required | Required      |
| bank selection     | Required | Required      |
| MMIO               | Required | Required      |
| ITCM/DTCM          | Required | Required      |
| alignment          | Required | Required      |

# Open Items

Fill with concrete signal definitions and RTL as implementation proceeds.
