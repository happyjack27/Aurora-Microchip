# Aurora Code

Top-level container for all software/hardware-description code related to
the Aurora chip, as distinct from the specification/documentation trees
(`docs/`, `adr/`, `ddr/`, `decision-logs/`, `isa/`).

- [hardware](hardware) — chip-definition source (RTL/VHDL). Empty for now;
  see [docs/rtl](../docs/rtl) for the current documentation-only material.
- [programs](programs) — reference implementations of software that runs on
  the chip (e.g. the [scheduler](programs/scheduler)).
- [toolchain](toolchain) — compiler/assembler tooling for writing code for
  the chip. Empty for now; see [isa/database](../isa/database) for the
  machine-readable ISA and encoding helper scripts.
