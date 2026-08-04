**AURORA**

**Shared Compressor Arithmetic Engine**

*Phase 2 Microarchitecture Workbook — Version 2.0 (Frozen Baseline)*

# Decision Summary

The remaining implementation choices are now frozen for the baseline core. These choices favor predictable layout, modest area, and timing isolation of the scalar multiply path.

| **Decision** | **Frozen choice** | **Reason** |
|----|----|----|
| **Compressor scheduling** | Dadda tree using mostly 3:2 compressors | Fewer compressors and lower switching than Wallace while retaining controlled depth; better fit for low-cost DSP baseline. |
| **4:2 compressors** | Use only in the densest central columns when they remove a full reduction level | Avoids wholesale custom-cell dependence while preserving timing where it matters. |
| **Alternate-row injection** | Four reserved late-entry rows after the first native partial-product reduction level | Keeps reduction/SAD muxing off the Booth-to-first-compressor critical path and supports up to four packed/reduction operands. |
| **Final adder** | 64-bit segmented carry-select adder, four 16-bit segments | Lower delay than ripple, less routing and area than a full prefix tree, and natural 32-bit upper-half gating. |
| **Scalar multiply partition** | Booth recode + first Dadda level; remaining Dadda levels; carry-select add/format | Meets the four-cycle architectural latency without forcing large input muxes into the critical first stage. |
| **Packed/reduction partition** | Prepare/inject rows; Dadda compression; carry-select add/format | Supports two-cycle latency and one-cycle initiation for independent packed operations. |
| **Tag queue** | Two-entry completion tag queue | Sufficient for the baseline scalar II=2 and packed II=1 while avoiding a reservation station. |

# Frozen Datapath

Multiplier mode: Booth generator -\> native first Dadda level -\> shared Dadda core -\> four-segment carry-select adder -\> formatter/writeback.

Reduction mode: packed ALU / absolute-difference / accumulator rows -\> four late injection rows -\> shared Dadda core -\> same carry-select adder -\> formatter/writeback.

The alternate rows enter after the first native multiplier reduction level. They therefore do not add a mux level to the scalar multiply front end. In reduction modes, the Booth generator and unused early compressor columns are operand-isolated.

# Concrete Row-Injection Rules

- Four 64-bit-aligned alternate input rows are provided.

- For HADD.8 and SAD.8, each widened lane occupies one row; unused upper bits are zero.

- For HADD.16, two rows carry the widened lanes and two rows are zero.

- For packed MAC/MSUB, product rows use the native product path and accumulator/correction values use alternate rows.

- For dot products, widened products are compressed directly; no intermediate product-pair writeback is required.

- Only the columns needed by the selected operation toggle; sign extension is generated locally at injection.

# Latency and Resource Contract

| **Operation** | **Latency** | **Initiation interval** | **Resource** |
|----|----|----|----|
| 32×32 scalar multiply | 4 cycles | 2 cycles | Shared compressor engine |
| 2×16 / 4×8 packed multiply | 2 cycles | 1 cycle | Shared compressor engine |
| PMAC / PMSUB | 2 cycles | 1 cycle | Shared compressor engine |
| DOT / HADD / SAD | 2 cycles | 1 cycle | Shared compressor engine |
| HMIN / HMAX | 1 cycle | 1 cycle | Comparator tree; separate |

# Timing-Risk Controls

- No full-width selection mux precedes the Booth generator.

- The late-row muxes are local to four reserved compressor inputs.

- The final adder is physically segmented into four 16-bit regions with carry-select between regions.

- The upper 32 bits are isolated for operations producing only a 32-bit result.

- Packed lane boundaries are hard-wired with carry blocking before widening/reduction.

- If synthesis misses timing, the first permitted change is retiming between the Dadda core and final adder; changing ISA latency requires architecture review.

# Architecture Review Result

PASS — The selected organization reuses the compressor tree broadly, avoids a multiply-front-end timing penalty, keeps control regular, and is consistent with Aurora’s low-cost DSP-first product niche. The remaining work is RTL proof, not architectural choice.

**AURORA**

**Shared Compressor Arithmetic Engine**

Phase 2 Microarchitecture Workbook — Version 1.0

*Status: Baseline microarchitecture proposal for RTL implementation and synthesis validation*

| **Design objective** | **Baseline decision** |
|----|----|
| Primary role | One common multi-operand arithmetic engine for multiply, MAC/MSUB, dot product, HADD, SAD, and widened accumulation. |
| Cost strategy | Share compressor rows and the final carry-propagate adder while preserving a simple, timing-friendly injection network. |
| Execution slot | Slot B; scoreboarded and variable latency. |
| Native formats | 32-bit scalar, 2×16-bit packed, 4×8-bit packed, 64-bit register-pair results. |
| Non-goals | Horizontal min/max, division, arbitrary permutation, and general out-of-order scheduling. |

# 1. Executive Summary

The shared compressor arithmetic engine is one of Aurora’s defining implementation choices. Instead of building a multiplier, a separate horizontal-adder tree, a separate SAD tree, and dedicated MAC accumulation hardware, Aurora treats carry-save compression as a common pattern. Several producers inject aligned operand rows into one compressor network, which reduces them to two vectors before a shared final carry-propagate adder produces the architectural result.

This approach is intended to improve useful arithmetic per transistor. It gives the DSP-oriented operations a common datapath, simplifies scoreboarding, and leaves higher-performance implementations free to pipeline or duplicate selected front ends without changing the ISA.

## 1.1 Locked architectural uses

- Scalar signed and unsigned 32×32 multiplication, including low, high, and full 64-bit results.

- Packed 2×16 and 4×8 widening multiplication.

- Packed multiply-accumulate and multiply-subtract.

- Packed dot-product accumulation.

- Horizontal add and widened horizontal reduction.

- Sum of absolute differences (SAD).

- Multiword partial-product accumulation used by 64-bit software arithmetic.

## 1.2 Operations kept outside the engine

- Horizontal minimum and maximum, which use comparator/select trees.

- Division, which uses an iterative divider.

- Ordinary one-cycle packed add/subtract and logic, handled by the packed ALU.

- Lane permutation, PACK/UNPACK, and narrowing, handled by their own routing datapath.

# 2. Functional Organization

32-bit scalar operands ── Booth/partial-product generator ─┐\
2×16 / 4×8 products ─────────────────────────────────────────┤\
MAC/MSUB accumulator rows ───────────────────────────────────┤\
Packed lanes for HADD ───────────────┐ │\
Absolute differences for SAD ────────┼─ row align/injection ─┼─ compressor tree ── CPA ── format/writeback\
64-bit software partial products ────┘ │\
Zero/sign/correction rows ───────────────────────────────────┘

The engine is organized into producer front ends, a selective row-injection network, a carry-save compressor core, a shared final adder, and a result formatter. The multiplier’s native partial-product rows enter directly. Non-multiply operations inject only the rows they need; they do not pass through the partial-product generator.

# 3. External Interface

| **Signal group** | **Contents** | **Behavior** |
|----|----|----|
| Issue request | operation class, signedness, lane mode, source registers, destination register/pair, flag controls | Accepted when req_valid and req_ready are both asserted. |
| Operands | up to three 32-bit register operands plus optional 64-bit accumulator pair | Read in ID/RR or captured into an issue register. |
| Completion | result data, destination tag, exception status, Q/NZCV updates | Returned to the scoreboard/writeback network with a completion tag. |
| Backpressure | req_ready and completion-ready | Prevents overrun when the engine or writeback port is occupied. |
| Kill/flush | precise pipeline flush tag | Cancels unretired work when architecturally permitted; older precise operations complete or are replayed. |

# 4. Operating Modes

| **Mode** | **Function** | **Row source** | **Result** | **Latency** | **Initiation** |
|----|----|----|----|----|----|
| MUL32 | 32×32 → low/high/full 64 | partial products | 32 or 64 | 4 cycles | 2 cycles |
| PMUL16 | 2 independent 16×16 → 2×32 | packed products | 64 | 2 cycles | 1 cycle |
| PMUL8 | 4 independent 8×8 → 4×16 | packed products | 64 | 2 cycles | 1 cycle |
| PMAC/PMSUB | widened products ± accumulator lanes | products + accumulator rows | 64 | 2 cycles | 1 cycle |
| DOT16 | two 16×16 products reduced | products | 64 scalar | 2–3 cycles | 1 cycle |
| DOT8 | four 8×8 products reduced | products | 32 scalar | 2 cycles | 1 cycle |
| HADD16 | two 16-bit lanes reduced | packed ALU/register rows | 32 scalar | 2 cycles | 1 cycle |
| HADD8 | four 8-bit lanes reduced | packed ALU/register rows | 32 scalar | 2 cycles | 1 cycle |
| HADD.W16 | two 32-bit widened lanes reduced | register-pair rows | 64 scalar | 2 cycles | 1 cycle |
| SAD16 | two \|a-b\| lanes reduced | absolute-difference rows | 32 scalar | 2 cycles | 1 cycle |
| SAD8 | four \|a-b\| lanes reduced | absolute-difference rows | 32 scalar | 2 cycles | 1 cycle |

Latency values are the baseline timing contract for the initial implementation profile. A faster implementation may shorten them, but software-visible semantics and scoreboard dependencies remain unchanged.

# 5. Datapath Design

## 5.1 Partial-product generation

The baseline scalar multiplier should use radix-4 modified Booth recoding. A 32-bit multiplier then produces approximately seventeen signed partial-product rows including correction handling. Packed modes partition the generator so the 16-bit and 8-bit lanes do not exchange carries or sign extension.

- Scalar mode: one 32×32 signed or unsigned multiplication.

- 2×16 mode: two independent Booth-recoded 16×16 multiplications.

- 4×8 mode: four independent 8×8 multiplications; simple array generation is also acceptable if smaller.

- Lane boundaries insert zeros/correction terms so no carry crosses between packed products before widening.

## 5.2 Selective row injection

Non-multiply reductions should not place a mux in front of every multiplier partial-product bit. Instead, the compressor tree reserves a small number of aligned row-entry points. A mode-dependent injection network selects packed lanes, absolute differences, accumulator values, or software partial products into those rows.

| **Injected source** | **Maximum rows** | **Alignment/extension** |
|----|----|----|
| MAC/MSUB accumulator | 2 | Lane-aligned; subtraction uses complement plus correction row. |
| HADD16 | 2 | Zero- or sign-extended 16-bit lanes into scalar 32-bit positions. |
| HADD8 / SAD8 | 4 | Four zero-extended 8- or 9-bit values aligned as independent rows. |
| HADD.W16 | 2 | Two 32-bit values aligned into a 64-bit reduction. |
| 64-bit software accumulation | 2–4 | Caller-selected 32-bit partial products shifted by 0 or 32 bits. |

## 5.3 Compressor topology

The recommended baseline is a Wallace/Dadda-style tree built from 3:2 compressors, with selective 4:2 compressors only where they materially reduce depth. The implementation target is to reduce all active rows to two carry-save vectors without carry propagation through the tree.

- Use Dadda scheduling if area and regular placement dominate.

- Use Wallace-style early compression if timing dominates after synthesis.

- Keep lane-mode gating local so inactive columns do not toggle unnecessarily.

- Do not force one exact compressor topology into the ISA specification; this workbook defines the baseline RTL target.

## 5.4 Final carry-propagate adder

One shared 64-bit final adder converts the two compressor outputs into the architectural result. A 32-bit operation uses the low portion and may clock-gate the upper half. The baseline choice should be a segmented carry-select or prefix-assisted adder if synthesis shows a ripple adder would dominate timing.

| **Candidate** | **Area** | **Delay** | **Recommendation** |
|----|----|----|----|
| Ripple carry | Lowest | Highest | Use only if target clock is modest and synthesis confirms margin. |
| Carry select, segmented | Moderate | Moderate | Preferred baseline for low-cost timing balance. |
| Prefix adder | Highest | Lowest | Optional higher-performance implementation. |

# 6. SAD and Reduction Front End

SAD reuses the packed subtractor and absolute-value logic before injecting values into the compressor tree. The multiplier partial-product generator is bypassed. For unsigned lanes, absolute difference can be formed with compare/select around a subtractor; for signed lanes, the architecture should specify whether SAD is defined on signed magnitudes or raw lane values. The baseline recommendation is unsigned SAD for image and signal matching, with signed absolute difference retained as a separate packed ALU operation.

SAD.8 Rd, Ra, Rb\
d0 = abs_u8(a0 - b0)\
d1 = abs_u8(a1 - b1)\
d2 = abs_u8(a2 - b2)\
d3 = abs_u8(a3 - b3)\
Rd = d0 + d1 + d2 + d3

## 6.1 Why SAD belongs in the shared engine

- The subtract/absolute front end already exists for packed absolute difference.

- The compressor tree already performs the required four-input sum.

- Only row routing, mode control, and result formatting are added.

- It avoids materializing an intermediate packed absolute-difference register.

# 7. Scheduling, Scoreboarding, and Resource Conflicts

The compressor engine is a single baseline Slot B resource. MUL, PMUL, PMAC, PMSUB, DOT, HADD, and SAD therefore contend for it. The scoreboard tracks destination availability and the engine’s initiation interval.

| **Hazard** | **Required action** |
|----|----|
| Read after pending engine result | Stall the consuming instruction until completion forwarding or writeback. |
| Write to busy destination/pair | Stall to preserve precise in-order architectural state. |
| Two compressor operations adjacent | Issue according to initiation interval; hold the younger instruction if the engine is not ready. |
| Independent Slot A instruction | May continue while compressor operation is outstanding if retirement and resource rules permit. |
| Branch consuming pending flags | Stall until the older flag-producing operation retires. |
| Exception in older memory operation | Suppress visibility of younger compressor result until precise ordering is established. |

## 7.1 Recommended implementation queue

Use one issue register plus a small completion tag rather than a general reservation station. Scalar multiply may occupy internal stages for four cycles, while packed/reduction modes use the shorter path. A two-entry destination-tag queue is sufficient for the baseline initiation intervals, subject to RTL simulation.

# 8. Timing and Pipeline Partition

Cycle N : issue capture / Booth recode or reduction-row preparation\
Cycle N+1 : compressor stage(s)\
Cycle N+2 : final CPA / result formatting for packed and reduction modes\
Cycle N+3..N+4 : additional scalar-multiply compression/CPA stages as required\
Completion : scoreboard wakeup, forwarding, then in-order retirement

The nominal four-stage core pipeline does not constrain the engine to one EX/MEM cycle. The engine is a decoupled multi-cycle unit. The preferred partition keeps the row-selection mux out of the scalar multiply’s most timing-sensitive Booth-to-compressor path.

# 9. Area, Gate Cost, and Power Expectations

Exact gate counts require a target process and synthesis. The values below are planning ranges, not verified silicon measurements. They are intended to compare alternatives and set expectations for Phase 2 RTL work.

| **Block** | **Planning estimate** | **Notes** |
|----|----|----|
| 32×32 Booth generation + compressor core | 8k–18k NAND2-equivalent gates | Strongly process/library dependent; largest block. |
| 64-bit final adder | 0.8k–2.5k gates | Ripple at low end; carry-select/prefix at high end. |
| Selective row-injection muxing | 0.4k–1.5k gates | Depends on row count and physical placement. |
| Packed abs-difference front end | 0.3k–1.0k gates | May reuse packed subtractor/comparator hardware. |
| Mode/control/result formatting | 0.3k–1.0k gates | Decode, sign extension, lane gating, destination tags. |
| Separate HADD + SAD trees avoided | ~0.8k–3k gates saved | Indicative; depends on standalone alternative. |

## 9.1 Power controls

- Clock-gate Booth recoding and unused compressor columns in HADD/SAD modes.

- Gate inactive packed lanes in 2×16 and 4×8 modes.

- Gate the upper 32 bits of the final adder for narrow scalar results.

- Avoid toggling multiplier partial-product rows when alternate reduction rows are active.

- Use operand isolation before wide muxes rather than relying only on downstream clock gating.

# 10. Architecture Review Gate

| **Criterion** | **Status** | **Assessment** |
|----|----|----|
| Workload value | PASS | FIR, convolution, matrix, FFT, SAD/image matching, PCA/ICA primitives, 64-bit arithmetic. |
| Instruction savings | PASS | Fuses intermediate product/abs-difference materialization and reduction. |
| Compiler usability | PASS | Operations map cleanly to intrinsics and recognized reduction patterns. |
| Silicon reuse | PASS | Reuses the dominant compressor network and final adder. |
| Critical-path risk | CONDITIONAL | Must verify mux placement and scalar multiply path after synthesis. |
| Power impact | CONDITIONAL | Requires operand isolation and lane/column gating. |
| Opcode cost | PASS | Uses existing multiply/reduction families; SAD consumes a justified sub-opcode. |
| Determinism | PASS | Fixed operation semantics and documented baseline latencies. |
| Verification complexity | CONDITIONAL | Many signedness/lane/correction combinations require formal properties. |
| Product differentiation | PASS | Common compressor engine is a coherent low-cost DSP implementation story. |

# 11. Verification Plan

## 11.1 Directed test classes

- Zero, one, all-ones, minimum signed, maximum signed, and alternating-bit operands.

- Every signed/unsigned scalar multiply form, including high-half correctness.

- Every packed lane boundary with no cross-lane carry contamination.

- MAC/MSUB carry and correction-row corner cases.

- SAD equality, maximum difference, and mixed-lane patterns.

- Horizontal reductions at maximum positive and negative lane values.

- Odd destination-pair encoding traps.

- Scoreboard stalls, forwarding, flush, exception, and interrupt boundaries.

## 11.2 Formal properties

- For every accepted operation, result equals a mathematical reference model at completion.

- Packed modes never propagate carry or sign between lanes before the defined widening/reduction step.

- A killed or fault-suppressed operation cannot update architectural state.

- Destination tags and result data remain paired under all stalls and backpressure.

- No two operations claim the shared final adder in the same cycle unless the implementation explicitly supports it.

- Sticky Q and optional NZCV updates occur only for the retiring tagged instruction.

## 11.3 Benchmark kernels

| **Kernel** | **Engine operations to measure** | **Primary metric** |
|----|----|----|
| FIR 16-bit | PMAC16, occasional HADD.W16 | cycles/tap and accumulator utilization |
| 4×8 image convolution | PMAC8, rounded shift, saturating narrow | pixels/cycle |
| Block matching | SAD8/SAD16 | bytes compared per cycle |
| Matrix multiply | PMAC16 or DOT16 | MACs/cycle and scoreboard stalls |
| FFT butterfly | PMUL16, add/sub, rounded shift | cycles/butterfly |
| PCA covariance | PMAC/DOT and 64-bit accumulation | cycles/sample-dimension |

# 12. Recommended RTL Decomposition

| **Module** | **Responsibility** |
|----|----|
| aurora_comp_issue | Decode normalized engine command, capture operands, assign destination tag. |
| aurora_booth_gen | Scalar and packed partial-product generation with signedness correction. |
| aurora_absdiff | Packed unsigned absolute-difference generation for SAD and PABSDIFF. |
| aurora_row_inject | Align/extend accumulator, reduction, SAD, and software partial-product rows. |
| aurora_csa_tree | Parameterized compressor network reducing active rows to sum/carry vectors. |
| aurora_final_adder | Shared 64-bit carry-propagate adder with 32-bit gating option. |
| aurora_comp_format | Lane/result formatting, high/low selection, Q/NZCV generation. |
| aurora_comp_ctrl | Pipeline valid bits, initiation control, flush, completion, and error handling. |

# 13. Locked Decisions and Phase 2 Open Items

## 13.1 Locked

- The compressor network is a common arithmetic resource, not multiply-only.

- The final 64-bit adder is shared by multiply and reduction modes.

- SAD is implemented as abs-difference rows plus compressor reduction.

- HMIN/HMAX remain comparator-tree operations outside the compressor engine.

- All compressor modes are Slot B operations and contend for one baseline resource.

- The ISA permits higher-performance implementations to pipeline or duplicate internal resources without semantic changes.

## 13.2 Must be resolved by RTL/synthesis

- Dadda versus Wallace compressor scheduling for the target library.

- Exact number and placement of alternate row-injection points.

- Ripple, carry-select, or prefix final-adder choice.

- Whether scalar multiply meets four-cycle latency at the target clock.

- Whether the packed path can sustain one result per cycle with the shared final adder.

- Whether a two-entry destination-tag queue is sufficient under realistic stalls.

- Gate and power estimates after synthesis in at least one FPGA and one representative ASIC library.

# 14. Block Acceptance Criteria

1.  Cycle-accurate RTL matches the ISA reference model for all directed and randomized arithmetic tests.

2.  Formal checks prove packed-lane isolation, precise kill behavior, and destination-tag integrity.

3.  The baseline target latencies and initiation intervals are achieved or the architecture documents are revised through review.

4.  Synthesis shows the shared design is smaller or more energy efficient than separate multiplier and reduction blocks at comparable throughput.

5.  The scalar multiply critical path is not materially degraded by alternate row-injection muxing.

6.  FIR, SAD, matrix, FFT, and PCA-oriented traces demonstrate useful Slot B utilization without pathological scoreboard stalls.

7.  The architecture review checklist is re-run using measured RTL results before the block is marked Phase 2 frozen.
