# Cycle Boundaries

- Fetch→Decode: one pipeline transfer.

- Decode→Issue after pairing.

- Execution writes completion records.

- Retirement commits oldest completed instructions.

# Flush Rules

- Flush invalidates fetch, decode window, younger completions.

- Committed state is never rolled back.

# Memory Timing

- Ready/valid handshake.

- Outstanding requests tracked by age tags.
