# Architectural Responsibility

The Register File & Scoreboard implements the architectural behavior defined by the ISA and microarchitecture specifications.

# Primary Functions

- 16x32 GPR

- paired aliases

- L8/L16 preservation

- forwarding

- busy bits

# Pipeline Placement

Identify stage ownership, input/output latching, forwarding boundaries, and stall behavior.

# State Elements

Enumerate every flip-flop, RAM, counter, queue, and valid bit owned by this module.

# Interfaces

Specify every signal with width, direction, timing, reset value, and protocol.

# Microarchitecture Notes

- 2R/2W baseline

- whole-register hazards

- pair write atomicity

# RTL Guidance

Provide synthesizable SystemVerilog pseudocode, parameterization rules, assertions, and clock-gating opportunities.

# Verification Matrix

| Feature             | Directed | Random/Formal |
|---------------------|----------|---------------|
| 16x32 GPR           | Required | Required      |
| paired aliases      | Required | Required      |
| L8/L16 preservation | Required | Required      |
| forwarding          | Required | Required      |
| busy bits           | Required | Required      |

# Open Items

Fill with concrete signal definitions and RTL as implementation proceeds.
