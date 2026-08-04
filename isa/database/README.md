# Aurora v1.2 Machine-Readable ISA Database

This package is the canonical machine-readable source for the Aurora v1.2 ISA draft.

## Files

- `aurora_v1_2_isa.json` — canonical database
- `aurora_v1_2_isa.yaml` — human-friendly equivalent
- `aurora_v1_2_instruction_table.csv` — flat reference table
- `aurora_v1_2_opcodes.vh` — generated Verilog primary-opcode constants
- `aurora_v1_2_opcodes.h` — generated C primary-opcode constants
- `generate_aurora_tables.py` — validator/generator entry point

## Current coverage

- 16 primary opcode classes
- arithmetic modes and register roles
- paired-64 legality
- issue-window metadata
- instruction semantics
- latency and initiation interval
- flags, exceptions, and scheduling attributes

## Validation

Run:

```bash
python generate_aurora_tables.py
```

Generated: 2026-08-02
