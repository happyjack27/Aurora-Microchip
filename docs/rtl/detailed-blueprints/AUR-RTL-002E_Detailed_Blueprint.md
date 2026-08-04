# Architectural Responsibility

The Multiplier & Reduction Cluster implements the architectural behavior defined by the ISA and microarchitecture specifications.

# Primary Functions

- Radix multiplier

- shared compressor tree

- MAC

- DOT

- SAD

- AND/OR/XOR reductions

# Pipeline Placement

Identify stage ownership, input/output latching, forwarding boundaries, and stall behavior.

# State Elements

Enumerate every flip-flop, RAM, counter, queue, and valid bit owned by this module.

# Interfaces

Specify every signal with width, direction, timing, reset value, and protocol.

# Microarchitecture Notes

- One shared reduction resource

- 40-bit accumulators

# RTL Guidance

Provide synthesizable SystemVerilog pseudocode, parameterization rules, assertions, and clock-gating opportunities.

# Verification Matrix

| Feature                | Directed | Random/Formal |
|------------------------|----------|---------------|
| Radix multiplier       | Required | Required      |
| shared compressor tree | Required | Required      |
| MAC                    | Required | Required      |
| DOT                    | Required | Required      |
| SAD                    | Required | Required      |
| AND/OR/XOR reductions  | Required | Required      |

# Open Items

Fill with concrete signal definitions and RTL as implementation proceeds.
