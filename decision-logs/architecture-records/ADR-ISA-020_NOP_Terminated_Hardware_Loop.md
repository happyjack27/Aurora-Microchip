Status: LOCKED\
Architecture baseline: Aurora v1.2g\
Date: August 2, 2026

# Decision

- Aurora provides one active zero-overhead hardware loop using LOOP \#count.

- LOOP uses opcode key 0xC0. The low eight instruction bits encode count-minus-one, supporting 1 through 256 iterations.

- The first ordinary NOP encountered while a hardware loop is active terminates the loop body; no separate LOOPEND or NOP.LEND instruction exists.

- NOP uses opcode key 0xC1. Outside an active hardware loop it has no architectural effect.

- The loop body begins with the instruction immediately following LOOP and excludes the terminating NOP.

- The loop body contains one through four 16-bit instructions, matching the baseline small loop-buffer capacity.

- Only one hardware loop may be active. LOOP inside an active hardware loop is illegal; hardware nesting is not supported.

- Branches, calls, returns, IRET, ASC/system-service entry, WFI, WFE, HALT, CTXSAVE, CTXRESTORE, fences, and other serializing or control-transfer instructions are prohibited in the body.

- Ordinary ALU, shift, packed, multiply/reduction, DIVSTEP, load/store, and stream instructions are permitted subject to normal hazards and resource availability.

- The first pass fetches and decodes the body into the loop buffer. Later iterations replay the buffered operations without instruction-memory access, branch prediction, or a software counter instruction.

- At retirement of the terminating NOP, the hidden remaining count is decremented. If iterations remain, execution restarts at the first buffered operation; otherwise execution continues after NOP.

- Count denotes total body executions. LOOP \#1 executes the body once and does not replay it.

- The loop is precisely interruptible between retired instructions. Interrupt entry snapshots active-loop state; IRET restores it.

- The CONTROL context group used by CTXSAVE/CTXRESTORE includes loop-active, remaining-count, body length, replay position, and buffered-loop identity/state required for exact resumption.

- A synchronous exception in the body preserves precise state. The faulting instruction may be restarted, and the remaining loop count is not decremented until the terminating NOP retires.

- If no terminating NOP is decoded within four body instructions, or a prohibited instruction is encountered, a precise LOOP_FORMAT exception occurs before the offending instruction issues.

# Rationale

A NOP terminator avoids encoding body length in LOOP and allows one compact instruction to describe bodies of different sizes. Reusing the ordinary NOP avoids a special loop-end mnemonic while preserving a clear hardware marker. The four-instruction limit matches Aurora's small-window philosophy and targets DIVSTEP, CORDIC, CRC, short MAC, and iterative fixed-point kernels.

# Superseded Encoding

The earlier provisional LOOPSET/LOOPEND pair is superseded. Opcode 0xC0 is renamed LOOP and opcode 0xC1 is renamed NOP. No separate LOOPEND instruction remains.
