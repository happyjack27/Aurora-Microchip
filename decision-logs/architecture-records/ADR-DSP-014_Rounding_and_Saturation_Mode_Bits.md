Status: LOCKED\
Architecture baseline: Aurora v1.2l\
Date: August 2, 2026

# Locked Decisions

- Aurora adds two independent sticky DSP mode bits: ROUND and SAT.

- ROUND applies only to explicit DSP operations that discard low-order bits: narrowing shifts, pack/narrow operations, and accumulator-to-register extraction.

- SAT applies only to explicit conversions into a smaller destination width: pack/narrow operations and accumulator-to-register extraction.

- Ordinary ADD, SUB, LSL, LSR, ASR, ROR, MOV, and other scalar operations remain mode-independent and retain exact modulo or bit-shift semantics.

- When ROUND and SAT are both enabled, rounding is performed first and saturation is applied to the rounded value.

- The baseline rounding rule is signed round-to-nearest-even using guard, round/sticky, and retained-LSB information.

- Unsigned narrowing uses the corresponding unsigned round-to-nearest-even rule.

- Saturation clamps to the signed or unsigned destination range selected by the narrowing/packing operation.

- At least one saturation event sets the existing sticky DSP saturation status bit SAT_OCCURRED; packed implementations may retain a non-architectural lane mask for debug or trace.

- Rounding alone does not set SAT_OCCURRED. Implementations may expose a separate inexact/rounded-away status only in an optional profile.

- ROUND and SAT do not generate interrupts by default. A privileged optional DSP trap-enable may convert saturation into a precise exception, but it is disabled after reset.

- An implementation may require one additional execution cycle when ROUND or SAT is active. This latency is architecturally permitted and must be reported in the implementation timing profile.

- The added cycle, when present, is scoreboarded; dependent consumers wait normally and no software-visible partial result occurs.

- The fast ordinary scalar ALU and basic shifter critical paths are not required to contain rounding or saturation logic.

- MODECLR clears ROUND and SAT along with the other sticky arithmetic mode bits.

# Affected Operation Classes

| Operation class | ROUND | SAT | Notes |
|----|----|----|----|
| Ordinary scalar ALU and shifts | No | No | Always exact modulo/bit semantics |
| DSP narrowing right shift | Optional | No | Discards low-order bits but retains destination width |
| NARROW / PACK8 / PACK16 | Optional | Optional | Round first, then clamp |
| Accumulator extraction / ACCMOV | Optional | Optional | Wide accumulator to smaller GPR/packed destination |

# Rationale

Rounding and saturation are most valuable at precision-reduction boundaries. Limiting the mode bits to explicit narrowing, packing, and accumulator extraction avoids burdening Aurora's fast scalar ALUs while allowing fused fixed-point conversions. Permitting one extra cycle keeps timing closure and area under implementation control.
