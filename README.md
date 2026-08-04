# Aurora Repository Seed — 2026-08-03

This archive is intended to be unpacked directly into a Git repository.

## Most important starting points

- `docs/canonical/AUR-ARCH-005_Aurora_Instruction_Reference_Full_v1_2s.docx`
- `docs/canonical/RECENT_DECISIONS_SNAPSHOT.md`
- `isa/database/aurora_v1_2_isa.yaml`
- `isa/database/aurora_v1_2_isa.json`
- `isa/database/aurora_v1_2_instruction_table.csv`
- `docs/abi/Aurora_Architecture_v1_2_ABI_Specification.docx`
- `docs/governance/Aurora_Architecture_Decision_Register_ADR_v1_2.docx`
- `scheduler/README.md`
- `scheduler/aurora_scheduler_reference.c`

## Important warning

The latest full reference is cumulative, but some late-session decisions are newer than portions of the older machine-readable ISA database. Treat `RECENT_DECISIONS_SNAPSHOT.md` and the latest ADRs as superseding older conflicting text until the database and consolidated specification are regenerated.

## Suggested first repository tasks

1. Commit this archive unchanged as an import baseline.
2. Create a canonical machine-readable architecture database revision.
3. Reconcile all ADRs against the instruction table.
4. Regenerate opcode maps, reference manual, assembler constants, and RTL decode tables.
5. Add CI validation for register-map, opcode, stream-side-effect, and loop-window invariants.

## Decision logs — start here

- `ARCHITECTURE_DECISION_LOG_CURRENT.md`
- `DOCUMENTATION_DECISION_LOG_CURRENT.md`
- Word versions with the same names are at the repository root.
- Original and individual decision records are under `decision-logs/`.
