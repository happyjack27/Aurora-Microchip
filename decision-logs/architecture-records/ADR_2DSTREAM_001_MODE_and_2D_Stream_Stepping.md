# Status

Accepted — Aurora Architecture v1.2c.

# Decision

Add the nonprivileged MODE \#mode instruction. Extend each stream engine with outer_adjust and outer_count state so Q0/Q1 can generate nested two-dimensional patterns. QCFG configures all stream fields; readable QSET\* mnemonics are assembler aliases.

# Rationale

MODE was part of the architectural concept but absent from the encoded instruction inventory. Two-dimensional stepping covers images, matrices, line buffers, tiled sensors, and strided records without software address-update instructions. Storing outer_adjust directly avoids multiplication hardware.

# Consequences

Each stream adds two 32-bit configuration values plus remaining/reload state. Row-boundary control adds a small compare/reload/add path. Stream configuration is a state barrier for later operations on that stream.

# Compatibility

One-dimensional streams use OUTER_COUNT=1 and OUTER_ADJUST=0. Existing QCFG bytecode 0xB6 is retained and clarified. MODE uses previously unassigned key 0xDA.
