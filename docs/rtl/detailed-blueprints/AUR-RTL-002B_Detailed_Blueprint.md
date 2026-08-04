# Architectural Responsibility

The Decode & Issue Window implements the architectural behavior defined by the ISA and microarchitecture specifications.

# Primary Functions

- 16-bit decode

- extension-word merge

- 4-entry window

- oldest-first pairing

- resource arbitration

- window compaction

# Pipeline Placement

Identify stage ownership, input/output latching, forwarding boundaries, and stall behavior.

# State Elements

Enumerate every flip-flop, RAM, counter, queue, and valid bit owned by this module.

# Interfaces

Specify every signal with width, direction, timing, reset value, and protocol.

# Microarchitecture Notes

- Decoded instruction

- resource mask

- operand IDs

- age

- pair eligibility

# RTL Guidance

Provide synthesizable SystemVerilog pseudocode, parameterization rules, assertions, and clock-gating opportunities.

# Verification Matrix

| Feature              | Directed | Random/Formal |
|----------------------|----------|---------------|
| 16-bit decode        | Required | Required      |
| extension-word merge | Required | Required      |
| 4-entry window       | Required | Required      |
| oldest-first pairing | Required | Required      |
| resource arbitration | Required | Required      |
| window compaction    | Required | Required      |

# Open Items

Fill with concrete signal definitions and RTL as implementation proceeds.
