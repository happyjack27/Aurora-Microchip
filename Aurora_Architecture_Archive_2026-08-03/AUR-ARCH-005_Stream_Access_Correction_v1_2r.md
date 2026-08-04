This section supersedes the v1.2q statement that POP, PUSH, and PEEK are the only stream-access instructions.

# Three Instruction Categories

| Category | Examples | Stream behavior | Rule |
|----|----|----|----|
| Stream-capable computation | ADD, SUB, packed ALU, MUL, MAC/MAS, REDUCE, DOT, SAD | Implicit consume/produce when Q0/Q1 is selected | Side effect is part of the computation |
| Standalone stream transfer | POP, PUSH, PEEK | Explicit consume, produce, or non-consuming read | Used when no fused computation is desired |
| Pure register/control | MOV, CMOV, branches, unrelated system operations | Never accesses stream data | Predicate outcome cannot change stream progression |

# Reduction Formats

One-source reductions accept one GPR or supported stream source and write A0 or A1. Two-source reductions accept the combinations defined by their encoding, with Q0/Q1 paired consumption prioritized. The selected accumulator is read implicitly only when ACC=1; INIT=1 replaces the accumulator with the current reduction result.

Examples:\
REDUCE.ADD A0, Q0, ACC\
REDUCE.XOR A1, Q1, INIT\
DOT A0, Q0, Q1, ACC\
SAD A1, R4, Q0, ACC ; only if the mixed form is defined by the final encoding

# Atomicity

- A stream source advances once only when the instruction successfully retires.

- A stream destination advances once only when the produced result successfully retires.

- Two stream sources advance together or not at all.

- A consume-plus-produce instruction updates both participating streams and its architectural result atomically.

- Faults, flushes, and interrupted unretired instructions leave all participating streams unchanged.

# MOV and CMOV

MOV and CMOV accept only GPR values. Packed CMOV performs lane-wise selection using packed predicate flags, but it cannot name Q0/Q1. Therefore both predicate outcomes have identical stream and address side effects: none.

# Reserved POPMETA Form

POPMETA Rd:Rd+1, Qn, meta remains a reserved encoding concept. If allocated later, Rd:Rd+1 is an aligned pair: Rd receives popped data and Rd+1 receives selected metadata such as ORD_LAST or ADDR_LAST.
