**AUR-RTL-002E Multiplier & Reduction Cluster**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Implement scalar/packed multiplication, MAC/MAS, DOT, SAD and generalized reductions using a shared Dadda-style compressor infrastructure and two 40-bit accumulators.

# 2. Internal Blocks

| Block | Role |
|----|----|
| Partial-product generator | Scalar/packed signed or unsigned products |
| Radix-4 step logic | Multi-cycle wide multiplication support |
| Compressor tree | 3:2 default; selective 4:2 only when synthesis wins |
| Late injection points | Four 64-bit-aligned injection points for MAC/DOT/SAD/reduce |
| Final adder | Produces scalar/packed result |
| Accumulator merge | A0/A1 overwrite/fold behavior |

# 3. Supported Operations

- MUL/MULH scalar and paired support

- Packed 4x8 and 2x16 multiply

- MAC and MAS

- DOT and SAD

- REDUCE.ADD/AND/OR/XOR/MIN/MAX/ABSMAX/COUNT

- Overwrite or operator-specific fold into A0/A1

# 4. Ports

| Signal         | Dir | Width          | Meaning                          |
|----------------|-----|----------------|----------------------------------|
| req_valid_i    | in  | 1              | Launch request                   |
| req_op_i       | in  | enum           | Operation                        |
| req_mode_i     | in  | 3              | Packed/scalar mode               |
| src0_i/src1_i  | in  | 64 max logical | Operands or pair bundle          |
| acc_sel_i      | in  | 1              | A0/A1                            |
| fold_i         | in  | 1              | Overwrite vs fold                |
| consume_i      | in  | 2              | Stream consume override metadata |
| result_valid_o | out | 1              | Completion                       |
| result_o       | out | 64/40          | Result/accumulator value         |
| fault_o        | out | 1              | Illegal mode/operation           |

# 5. Pipeline

| Stage       | Work                                                       |
|-------------|------------------------------------------------------------|
| M0          | Decode mode, sign, lane widths; generate partial products  |
| M1          | Initial Dadda compression                                  |
| M2          | Late injections, final compression and add                 |
| M3 optional | Accumulator merge / paired writeback where timing requires |

# 6. Resource Rules

- One reduction-class launch per cycle baseline.

- Multiplier initiation interval target is one where no conflicting reduction launch exists.

- DOT/SAD and REDUCE share final reduction resources.

- A0 and A1 are independently scoreboarded; two dependent folds to same accumulator cannot overlap illegally.

# 7. Assertions

- Reduction result equals mathematical lane operation with specified widening.

- Fold uses operator-specific identity and combination.

- Accumulator never loses guard bits except through explicit extraction/shift semantics.

- Stream consume occurs exactly once per committed launch.

- Illegal packed mode combinations fault precisely.
