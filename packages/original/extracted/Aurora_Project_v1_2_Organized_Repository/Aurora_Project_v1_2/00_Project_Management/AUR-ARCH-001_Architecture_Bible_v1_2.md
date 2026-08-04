Purpose: This document is the long-term engineering record for Aurora. Every major architectural decision is captured with its motivation, alternatives, tradeoffs, chosen solution, consequences, and future expansion path. It is intended to prevent design drift and preserve architectural intent.

# 1. Product Mission

## Problem

Determine where Aurora competes.

## Alternatives Considered

- High-end DSP

- General-purpose CPU

- Traditional MCU

- MCU + DSP consolidation

## Decision

Target MCU + low-to-mid-range fixed-point DSP consolidation.

## Why This Was Chosen

Most embedded systems needing meaningful DSP today combine a control processor with a DSP. Integrating both reduces board complexity while preserving deterministic behavior.

## Consequences

- Lower BOM

- Lower latency

- Lower power

- Simpler software stack

## Future Expansion

Scale memory and peripherals across Aurora-L/M/P while keeping one ISA.

# 2. ISA Width

## Problem

Balance code density and decoding simplicity.

## Alternatives Considered

- 16-bit fixed

- 32-bit fixed

- Variable length

## Decision

16-bit base ISA with extension words.

## Why This Was Chosen

Excellent embedded code density without forcing all instructions to carry large immediates.

## Consequences

- Small flash footprint

- Simple decoder

- Occasional extension-word cost

## Future Expansion

Additional extension formats can be added without changing the base ISA.

# 3. Register File

## Problem

Provide enough registers while minimizing area.

## Alternatives Considered

- 8 GPR

- 16 GPR

- 32 GPR

- Separate address/data files

## Decision

16 unified 32-bit GPRs.

## Why This Was Chosen

Compiler-friendly and simpler than classic DSP split register files.

## Consequences

- Good C performance

- Lower hardware complexity

- Unified programming model

## Future Expansion

Future profiles may add implementation-private shadow registers, but architectural count remains 16.

# 4. 64-bit Support

## Problem

Support 64-bit arithmetic without doubling hardware.

## Alternatives Considered

- Native 64-bit core

- Dedicated 64-bit register bank

- Paired-register emulation

## Decision

Paired even/odd registers emulate 64-bit values.

## Why This Was Chosen

64-bit operations are relatively uncommon in the target market; spending cycles is preferable to spending silicon.

## Consequences

- Higher latency

- Small area

- Compiler manages pairs

## Future Expansion

Selective paired instructions may be added where cost-effective.

# 5. Pipeline Philosophy

## Problem

Increase throughput without high OoO complexity.

## Alternatives Considered

- Single issue

- Out-of-order

- Wide VLIW

- Dual issue with local lookahead

## Decision

Four-stage in-order pipeline with a four-entry dynamic pairing window.

## Why This Was Chosen

Most ILP can be exposed by the compiler; hardware only repairs nearby missed opportunities.

## Consequences

- Predictable timing

- Small hardware

- Good dual-issue utilization

## Future Expansion

Window depth can grow in future cores without ISA changes.

# 6. DSP Features

## Problem

Deliver strong fixed-point performance.

## Alternatives Considered

- Conventional ALU only

- Dedicated vector engine

- Streams + packed SIMD + accumulators

## Decision

Two 40-bit accumulators, stream engines, packed modes, reductions, circular addressing.

## Why This Was Chosen

These features provide high sustained DSP throughput with modest hardware.

## Consequences

- Excellent FIR/IIR support

- Good AI preprocessing

- Low power

## Future Expansion

Additional reduction operators or stream profiles remain ISA-compatible.

# 7. Memory System

## Problem

Provide deterministic bandwidth.

## Alternatives Considered

- Mandatory caches

- TCM only

- Optional ITCM/DTCM + banked SRAM + DMA

## Decision

Optional TCM with unified address map.

## Why This Was Chosen

Many MCU-oriented products do not need TCM, while DSP-oriented products benefit greatly.

## Consequences

- Flexible product scaling

- Deterministic hot code/data

## Future Expansion

Future implementations may add caches transparently.

# 8. Compiler Philosophy

## Problem

Divide optimization work between software and hardware.

## Alternatives Considered

- Hardware scheduling

- Compiler scheduling

- Hybrid

## Decision

Compiler performs primary scheduling; hardware performs local pairing repair.

## Why This Was Chosen

Compiler has global visibility while hardware only needs inexpensive local logic.

## Consequences

- Simpler silicon

- Strong LLVM/GCC backend importance

## Future Expansion

PGO and auto-vectorization can further improve results.

# 9. Guiding Principles

## Problem

Establish enduring engineering rules.

## Alternatives Considered

## Decision

Adopt a stable set of design principles.

## Why This Was Chosen

## Consequences

- Prefer deterministic behavior over speculative peak performance.

- Spend silicon on throughput, not speculation.

- Reuse hardware aggressively.

- Keep software portability a first-class objective.

- Optimize for whole-system cost, not benchmark leadership.

- Allow scalable implementation profiles without ISA fragmentation.

## Future Expansion

These principles should be consulted before any future architectural change.

# Open Questions for Future Versions

- Whether a second LSU launch path is justified by synthesis results.

- Whether paired-64 shift/rotate should gain additional helper instructions.

- Whether optional cache profiles provide worthwhile system benefits.

- Whether future AI-oriented packed integer operations merit standardization.

# Architecture Freeze

The programmer's model, ABI, ISA, pipeline philosophy, memory map, compiler model, interrupt model, and product positioning are considered frozen for Aurora v1.2. Subsequent revisions should preserve backward compatibility whenever practical.
