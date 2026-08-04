**AUR-RTL-002H Stream Engines Q0/Q1**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Implement two independent stream engines over R0 and R4, each with address, stride, width, count, circular addressing, consume/peek behavior, and a 128-bit staging buffer.

# 2. Per-Stream State

| Field      | Width     | Meaning                           |
|------------|-----------|-----------------------------------|
| enabled    | 1         | Stream interception active        |
| address    | 32        | Current byte address              |
| stride     | 32 signed | Byte stride after consume/produce |
| width      | 2         | 8/16/32-bit element               |
| count      | 32        | Remaining elements                |
| limit/base | 32 each   | Circular buffer parameters        |
| direction  | 1         | Read or write stream              |
| head/tail  | index     | Staging-buffer pointers           |
| fill       | 3         | Number of valid 32-bit lanes      |
| end_mode   | enum      | Stop, wrap, signal, predicate     |

# 3. Ports

| Signal             | Dir | Width  | Meaning                          |
|--------------------|-----|--------|----------------------------------|
| req_valid_i        | in  | 1      | Stream operation request         |
| stream_sel_i       | in  | 1      | Q0/Q1                            |
| op_i               | in  | enum   | peek/pop/push/dup/replace/config |
| consume_override_i | in  | 1      | Consume vs local register access |
| src_data_i         | in  | 64 max | Produced value                   |
| result_o           | out | 64 max | Consumed/peeked value            |
| result_valid_o     | out | 1      | Result ready                     |
| mem_req_o          | out | bundle | Refill/spill request             |
| mem_rsp_i          | in  | bundle | Memory response                  |
| state_busy_o       | out | 2      | Q0/Q1 busy                       |

# 4. Buffer Behavior

- Each engine has a 128-bit staging buffer organized as four 32-bit lanes.

- 8-bit and 16-bit elements pack within lanes; lane extraction is width-aware.

- Coupled LIFO mode may combine Q0 and Q1 into one 256-bit logical stack.

- Peek returns the next element without advancing address/count.

- Simultaneous pop and push replacement may update the top element without changing depth.

# 5. Circular Addressing

Circular mode requires aligned power-of-two regions in the baseline. The next address masks selected low carry bits while preserving the aligned base.

next = base \| ((address - base + stride) & (size - 1))

# 6. Ordering and Hazards

- Consumption remains ordered independently for Q0 and Q1.

- Register-only MOV/PACK/UNPACK/SHUFFLE operations do not consume stream elements.

- Configuration changes serialize later operations on the affected stream.

- A stream fault must not partially advance architectural address/count state.

- Q0 and Q1 may refill concurrently when memory-fabric capacity permits.

# 7. Assertions

- Peek never changes address, count, or fill.

- Consume advances exactly once per committed operation.

- Circular address always remains inside configured region.

- Buffer fill remains between zero and four lanes.

- Faulting transfers leave stream state restartable.
