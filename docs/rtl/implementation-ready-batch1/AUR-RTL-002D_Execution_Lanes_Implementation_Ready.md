**AUR-RTL-002D Symmetric Execution Lanes**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Execute ordinary scalar, packed, low-lane, shift, compare, move and layout operations in either of two symmetric lanes.

# 2. Lane Capabilities

| Class | Operations |
|----|----|
| Scalar ALU | ADD/SUB/AND/OR/XOR/MIN/MAX/CMP |
| Packed ALU | 4x8 and 2x16 lane-isolated operations |
| Low-lane | L8/L16 read-modify-write |
| Shift/rotate | Scalar and packed; paired-64 dispatched to multi-cycle helper |
| Layout | MOV, BSWAP, WSWAP, PACK, UNPACK, ZIP, UNZIP, SHUFFLE |
| Control assist | Branch compare and target assist |

# 3. Ports

| Signal          | Dir | Width   | Meaning                                  |
|-----------------|-----|---------|------------------------------------------|
| op_i            | in  | decoded | Operation and mode                       |
| src_a_i/src_b_i | in  | 32 each | Operands                                 |
| old_dst_i       | in  | 32      | Merge source for L8/L16                  |
| carry_i         | in  | 1       | Carry/borrow input                       |
| result_o        | out | 32      | Result                                   |
| flags_o         | out | ZNVC    | Flags                                    |
| branch_taken_o  | out | 1       | Condition result                         |
| shared_req_o    | out | bundle  | Request to multiplier/LSU/reduction/etc. |

# 4. Packed Arithmetic

- Packed modes suppress carries between lanes.

- Signedness is instruction/subfunction controlled.

- Horizontal reductions do not execute in general lanes; they dispatch to reduction cluster.

- L8/L16 modify only low lane and preserve upper storage.

# 5. Lane Symmetry

Either lane accepts any ordinary operation. Shared-resource dispatch is lane-independent. Lane numbering has no architectural meaning.

# 6. Timing Targets

| Operation         | Latency  | Initiation |
|-------------------|----------|------------|
| ALU/logic/compare | 1        | 1          |
| Packed ALU        | 1        | 1          |
| Layout/shuffle    | 1        | 1          |
| Scalar shift      | 1 target | 1          |
| L8/L16 merge      | 1        | 1          |

# 7. Assertions

- Same opcode and operands produce identical result in either lane.

- Packed carries never cross lane boundaries.

- Layout operations ignore lane mask.

- L8/L16 preserve upper bits exactly.

- Shared request includes complete age/destination metadata.
