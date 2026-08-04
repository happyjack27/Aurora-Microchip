**Aurora Design Journal and Architecture Review Checklist**

Phase 1, Revision 1.0

# Architecture review checklist - mandatory gate

1\. What representative workloads benefit, and how frequently?

2\. How many dynamic instructions, cycles, memory transactions, or bytes are saved?

3\. Can the compiler synthesize the behavior efficiently from existing operations?

4\. What is the estimated gate, SRAM, routing, and verification cost?

5\. Does the feature add a mux or fan-out on a likely critical path?

6\. Can it reuse the scalar ALU, packed ALU, compressor tree, shifter, stream engine, or DMA?

7\. Does it consume scarce opcode space or reduce operand/immediate range?

8\. Does it complicate dual issue, scoreboarding, precise exceptions, ABI, context switching, or debugging?

9\. Is timing deterministic and understandable?

10\. Does it require specialty external parts or increase board cost?

11\. Is it baseline-worthy, optional extension material, or better left to software?

12\. What benchmark, trace, or synthesis evidence is required before approval?

13\. Have the overview, specification, ISA reference, tests, and toolchain contract been updated?

# Key Phase 1 decisions and rationale

| **Decision** | **Rationale** |
|----|----|
| DSP-first, MCU-capable | A plain MCU is difficult to differentiate. DSP-oriented data movement and packed arithmetic create a credible niche while retaining control capability. |
| 16-bit instructions, 32-bit data | Preserves code density and dual-fetch grouping without restricting native computation. |
| R0/R4 streams | Makes regular access implicit and provides two independently buffered operands for DSP kernels. |
| No 4-bit lanes or streams | Avoids awkward packing/state complexity and low-value opcode pressure. |
| Banked commodity SRAM | Captures most dual-port bandwidth using standard low-cost memories. |
| Four-stage pipeline plus scoreboard | Keeps the front end simple while allowing memory and arithmetic to outlive pipeline stages. |
| Shared compressor tree | Reuses a common high-value structure for multiply, MAC/MSUB, dot, HADD, and SAD. |
| No branch-buffer split | Fetch complexity and bandwidth waste did not justify a balanced-branch feature. |
| Explicit saturation and rounding | Avoids hidden numeric modes and preserves exact instruction meaning. |
| No dedicated PCA/ICA/FFT opcodes | General linear-algebra and reduction primitives are broader and easier to compile. |
| Exact reserved opcode policy | Prevents accidental ISA drift and leaves controlled room for future extensions. |

# Change control after Phase 1

- Any semantic change to an allocated instruction requires a major architecture revision.

- Using a reserved encoding requires the full review checklist, validation kernels, and toolchain updates.

- Latency improvements that preserve baseline timing contracts are implementation revisions, not ISA revisions.

- Changes to ABI, exception frames, stream context, or memory ordering require explicit compatibility review.

- Every accepted decision must be reflected in the living overview, architecture specification, ISA reference, tests, and journal.
