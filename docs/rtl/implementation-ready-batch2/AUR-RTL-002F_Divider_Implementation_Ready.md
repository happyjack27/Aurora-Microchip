**AUR-RTL-002F Divider**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Implement integer division using an iterative radix-step engine, supporting signed/unsigned scalar operation and paired-64 assistance without a full single-cycle divider.

# 2. State

| Field           | Meaning                    |
|-----------------|----------------------------|
| busy            | Operation active           |
| signed          | Signed or unsigned         |
| dividend        | Working dividend/remainder |
| divisor         | Normalized divisor         |
| quotient        | Partial quotient           |
| step            | Iteration counter          |
| age/destination | Completion metadata        |
| fault           | Divide-by-zero/overflow    |

# 3. Algorithm

- Baseline may use radix-2 or radix-4 restoring/non-restoring division.

- DIVSTEP exposes one architectural step for software-assisted forms.

- Full DIV runs internally until quotient/remainder complete.

- Signed division converts operands to magnitude and restores signs at completion.

# 4. Interruptibility

- Divider should provide checkpoint/abort between iterations.

- If canceled for precise interrupt, the whole instruction restarts.

- Maximum non-abortable interval should be one iteration.

- One outstanding divide is sufficient for v1.2.

# 5. Assertions

- quotient \* divisor + remainder equals dividend for valid operations.

- Remainder magnitude is less than divisor magnitude.

- Divide-by-zero produces precise fault and no destination write.

- Canceled divide produces no architectural result.

- Signed overflow case is explicitly defined.
