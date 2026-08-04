# Instruction Prefetch

The front end fetches 32 bits per cycle and contains two 32-bit prefetch entries. Together these entries retain four adjacent 16-bit instruction words.

# Captured Hardware-Loop Window

A captured hardware loop may contain up to eight contiguous 16-bit instruction words:\
\
words 0-3: decoded replay buffer\
words 4-7: pinned raw prefetch entries\
\
Words 4-7 pass through the normal decoder on every replay but do not require instruction-memory or I-cache access.

# Instruction Boundaries

- Extension words count toward the eight-word limit.

- Replay begins only at a base instruction.

- The final captured word must complete an instruction.

- The assembler diagnoses any loop whose extension sequence crosses the eight-word boundary.

# Loop Completion and Replay

- A body that uses all eight words terminates implicitly at capacity.

- A shorter body uses the established loop-end marker or encoded body-length mechanism.

- The loop sequencer decrements the count and selects the captured start without branch prediction.

- No instruction pair may span the iteration wrap.

- Normal dual-issue pairing is allowed across the word-3/word-4 storage boundary.

# Fallback

Bodies longer than eight words are not captured in the local replay window. They execute through the ordinary fetch path while retaining the architecture's loop-count and backward-loop control behavior.

# Example: Six-Instruction Argmax Loop

LOOPR Rcount\
POPMETA R4:R5, Q0, ORD\
ABS R4, R4\
CMP Rbest, R4\
CMOV.LT Rbest, R4\
CMOV.LT Rbestidx, R5\
REDUCE.ADD A0, R4, ACC\
; six one-word instructions occupy six of eight loop words
