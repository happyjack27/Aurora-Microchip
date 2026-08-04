Status: LOCKED\
Architecture baseline: Aurora v1.2s\
Date: August 3, 2026

# Locked Decisions

- Aurora has a 32-bit instruction fetch width and two 32-bit prefetch entries.

- The prefetch buffer therefore retains four adjacent 16-bit instruction words.

- The existing decoded loop replay buffer retains four decoded 16-bit instruction words.

- The hardware-loop capture window is eight contiguous 16-bit instruction words: four decoded words plus four pinned raw prefetch words.

- The eight-word limit is measured in 16-bit instruction words, not architectural instruction count.

- Extension words consume loop-window entries and must remain attached to their base instructions.

- A captured loop may begin only on a base-instruction boundary and may end only after a complete instruction.

- Loops of one through four words replay entirely from the decoded loop buffer.

- Loops of five through eight words replay the first four words from decoded storage and the remaining words from pinned prefetch storage through the normal decoder.

- The loop sequencer supplies loop start, loop end or length, remaining count, and replay position. Repeated iterations require no normal branch prediction or instruction-memory refetch.

- The two prefetch entries remain pinned for the lifetime of the captured loop and are not overwritten by ordinary prefetch traffic.

- A full eight-word body terminates implicitly at capacity. Shorter bodies continue to use the existing explicit loop-end marker or encoded length rule.

- No dual issue is permitted across the iteration wrap in the baseline implementation.

- Pairing within the eight-word body, including across the decoded/prefetch storage boundary, is permitted when normal legality rules allow it.

- Loops longer than eight words retain zero-overhead loop redirection when possible but execute from the ordinary instruction-fetch path rather than the captured replay window.

- Interrupt architectural state includes loop start, loop end or word length, remaining count, active flag, and replay position. Captured instruction contents are reconstructable microarchitectural state.

- This larger loop window reduces pressure to add specialized fused instructions solely to fit five- through eight-word kernels.

# Front-End Organization

Instruction memory / I-cache\
\|\
2 x 32-bit prefetch entries (4 raw words)\
\|\
decode / dual-issue formation\
\|\
4-word decoded loop replay buffer\
\|\
scoreboard and execution

# Loop Capacity Examples

| Body composition | Words used | Architectural instructions | Captured? |
|----|----|----|----|
| 8 one-word instructions | 8 | 8 | Yes |
| 6 one-word instructions + 1 extended instruction | 8 | 7 | Yes |
| 4 one-word instructions + 2 extended instructions | 8 | 6 | Yes |
| 8-word body ending with an incomplete extended instruction | 8 | Invalid | No |
| 9 one-word instructions | 9 | 9 | No; ordinary fetch fallback |

# Rationale

Two 32-bit prefetch entries provide useful fetch elasticity for dual issue and extension words at very low storage cost. Pinning these existing entries during loop replay expands the captured loop from four to eight words without adding a separate loop cache. The four-word decoded path remains the lowest-energy fast path, while five- through eight-word loops gain local replay with no instruction-memory access.
