Status: LOCKED\
Architecture baseline: Aurora v1.2f\
Date: August 2, 2026

# Decisions

- CLZ, CTZ, and POPCNT are confirmed as existing Aurora instructions and shall not be added as new ISA work.

- Aurora adds four unary extension instructions: ZEXT8, SEXT8, ZEXT16, and SEXT16.

- The extension instructions are register-only pass-through operations suitable for either symmetric issue lane.

- Extension results are available on the ordinary forwarding network and do not consume the multiply/reduction, LSU, stream, or DIVSTEP resources.

- Aurora defines programmable stack bounds using supervisor system registers STKLOW and STKHIGH plus a stack-bounds enable bit.

- The architectural stack grows downward. PUSH/PUSHM validate the candidate decremented address before writing; POP/POPM validate the current address before reading and the resulting incremented SP before committing.

- A stack access outside the enabled \[STKLOW, STKHIGH) interval raises a precise synchronous STACK_BOUNDS fault.

- The failing stack operation performs no memory transfer, register write, or SP update.

- Each stream retains configurable end behavior. Non-circular mode adds STREAM_END_FAULT as an end behavior.

- A non-circular stream operation attempted with no remaining element, row, or legal terminal address raises a precise synchronous STREAM_BOUNDS fault when STREAM_END_FAULT is selected.

- Circular streams wrap according to their circular configuration and do not raise an end-of-stream bounds fault solely because the inner or outer count reaches its reload point.

- A failing stream operation does not consume or produce data and does not update address, count, row state, staging-buffer pointers, or destination registers.

- Stream memory protection/alignment faults remain distinct from STREAM_BOUNDS.

- The fault address register records the candidate stack or stream address; the fault information register records the stream number or stack operation and access width.

# Rationale

Zero/sign extension is common in embedded protocol, sensor, and packed-data code and can be implemented almost entirely as wiring. Precise bounds faults make the stack and stream mechanisms safer without requiring paging. Keeping circular streams exempt from terminal-count faults preserves their intended indefinite ring-buffer behavior.

# Rejected Alternatives

- Asynchronous end-of-stream interrupt as the only mechanism: rejected because the faulting instruction needs precise restart semantics.

- Always faulting when a stream count reaches zero: rejected because normal finite streams may use stop/status/interrupt end behavior instead.

- Inferring stack bounds from mapped memory: rejected because explicit bounds provide deterministic and inexpensive checks.

- Automatic recovery or silent saturation of SP/stream addresses: rejected because it hides software defects.
