**AUR-RTL-002F DIVSTEP Assist & Division Runtime Interface**

*Corrected Implementation-Ready RTL Blueprint v1.2a*

# 1. Architectural Decision

Aurora v1.2 does not implement a large dedicated integer divider. Division is provided by the architectural DIVSTEP primitive, which reuses the existing execution-lane ALU, shifter, compare/subtract, carry/borrow, and register-pair datapaths. Full divide and remainder operations are synthesized by the compiler/runtime or implemented through an ASC helper.

# 2. Purpose of This Module

Provide the small amount of control and operand-routing logic needed to execute one divide iteration. This block is an assist unit, not a standalone quotient/remainder engine.

# 3. Explicit Non-Goals

- No dedicated 32-bit or 64-bit quotient/remainder datapath.

- No wide normalization tree.

- No multi-stage divide pipeline.

- No separate divider forwarding network.

- No requirement to keep an entire divide operation internally outstanding.

- No extra architectural divider state beyond normal registers, flags, and optional loop state.

# 4. Reused Hardware

| Existing resource | DIVSTEP use |
|----|----|
| General execution lane ALU | Conditional subtract/add of divisor from partial remainder |
| Shifter/rotate path | Shift combined remainder/quotient state by one or two bits |
| Compare/carry logic | Select quotient bit(s) and next remainder |
| Register pairs | Hold dividend, quotient, and partial remainder state |
| Flags/condition logic | Expose carry/borrow/sign decisions |
| Low-overhead loop support | Repeat the fixed number of DIVSTEP iterations |

# 5. Architectural Operation

A DIVSTEP instruction transforms software-visible divide state by one bounded iteration. The exact register convention is defined by the ISA reference and runtime ABI.

conceptual unsigned radix-2 step:\
\
combined = (remainder : quotient) \<\< 1\
trial = combined.remainder - divisor\
\
if trial \>= 0:\
remainder = trial\
quotient\[0\] = 1\
else:\
remainder = combined.remainder\
quotient\[0\] = 0

A radix-4 implementation may generate two quotient bits per instruction if synthesis shows the small additional selection logic is worthwhile. The ISA semantics must remain deterministic and profile-visible.

# 6. Suggested Ports

| Signal       | Dir | Width        | Meaning                               |
|--------------|-----|--------------|---------------------------------------|
| req_valid_i  | in  | 1            | DIVSTEP request                       |
| req_signed_i | in  | 1            | Signed/unsigned step mode             |
| req_radix_i  | in  | 1 or profile | Radix-2 or radix-4 internal choice    |
| state_hi_i   | in  | 32           | Partial remainder/high state          |
| state_lo_i   | in  | 32           | Quotient/dividend low state           |
| divisor_i    | in  | 32           | Divisor                               |
| result_hi_o  | out | 32           | Updated partial remainder             |
| result_lo_o  | out | 32           | Updated quotient/dividend state       |
| step_flags_o | out | small        | Quotient bit(s), borrow/sign metadata |
| complete_o   | out | 1            | One step completed                    |
| illegal_o    | out | 1            | Illegal mode or register form         |

# 7. Compiler and Runtime Expansion

- C integer division and remainder lower to a runtime helper or an inline DIVSTEP loop.

- The compiler may choose inline expansion for constant or hot divisors.

- The ASC runtime provides canonical signed and unsigned 32-bit helpers.

- Paired-64 division is a software routine using paired shifts, subtracts, and DIVSTEP-compatible control.

- A DIV mnemonic may remain as an assembler pseudo-instruction only.

# 8. Exceptional Cases

| Case | Handling |
|----|----|
| Divide by zero | Detected before the step loop by compiler/runtime or minimal setup logic; precise fault or language-defined helper result |
| Signed MIN / -1 overflow | Detected by signed helper setup; precise architectural behavior |
| Interrupt during sequence | Each DIVSTEP is independently retired; interruption occurs between steps |
| Fault/restart | No hidden multi-cycle divide state exists, so restart is ordinary instruction restart |

# 9. Timing and Area Targets

| Property | Target |
|----|----|
| DIVSTEP latency | 1 cycle preferred; 2 cycles acceptable if routed through shared shift/subtract path |
| Initiation interval | 1 |
| Dedicated state | Minimal or none beyond request/result registers |
| Area objective | Small control/mux increment relative to one general execution lane |
| Power objective | Clock-gated except during DIVSTEP |

# 10. Pairing and Scheduling

- DIVSTEP may issue in either symmetric execution lane.

- It consumes ALU, shifter, compare, and flag resources for that cycle.

- It may pair with an independent instruction only when the second lane and shared register-file/writeback resources are available.

- A sequence of DIVSTEP instructions is compiler-scheduled like any other dependent loop.

- The four-entry issue window may pair independent loop bookkeeping or address work around the sequence.

# 11. Assertions

- One DIVSTEP changes only its specified destination state and flags.

- No hidden divide state remains after retirement.

- Canceled or flushed DIVSTEP produces no architectural write.

- Unsigned step result matches the specified subtract/shift recurrence.

- Signed helper sequences produce the language-defined quotient and remainder.

- A DIV pseudo-instruction never reaches RTL as a distinct hardware opcode.

# 12. Verification Plan

| Test class              | Method                                         |
|-------------------------|------------------------------------------------|
| Single-step recurrence  | Exhaustive reduced-width model + random 32-bit |
| Full unsigned divide    | Runtime loop vs mathematical reference         |
| Full signed divide      | All sign combinations and corner cases         |
| Divide by zero          | Directed precise-fault tests                   |
| Interrupt between steps | Directed retirement-boundary injection         |
| Dual-issue interaction  | Constrained-random resource conflict tests     |

# 13. Superseded Wording

This document supersedes earlier AUR-RTL-002F text describing a self-contained iterative divider with internal quotient, divisor, remainder, and iteration state. Those structures are not part of the Aurora v1.2 baseline.
