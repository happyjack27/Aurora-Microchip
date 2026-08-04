**Canonical ABI Draft 1 — August 2026**

This document defines the software-visible calling convention, register usage, stack layout, function entry and return rules, data layout, interrupt frames, paired-64 behavior, accumulator and stream preservation, and toolchain obligations for Aurora Architecture v1.2.

# 1. ABI Scope and Design Goals

- Support efficient C and systems programming while preserving Aurora’s compact 16-bit instruction format.

- Keep common leaf functions inexpensive and permit aggressive compiler scheduling and dual issue.

- Allow DSP kernels to use streams, packed modes, and accumulators without imposing their save cost on ordinary MCU code.

- Keep 64-bit data support practical through register pairs and efficient spills without turning Aurora into a native 64-bit architecture.

- Provide deterministic interrupt and exception behavior suitable for real-time systems.

- Define one stable baseline ABI that can span low-cost MCU-oriented and DSP-oriented Aurora implementations.

# 2. Canonical Register Roles

| Register | Primary ABI role | Call volatility | Paired-64 role | Notes |
|----|----|----|----|----|
| R0-R3 | Arguments and return values | Caller-saved | R0:R1, R2:R3 | R0/R4 may also be stream bases when enabled. |
| R4-R7 | Caller temporaries / additional arguments | Caller-saved | R4:R5, R6:R7 | R4 is Q1 stream base when enabled. |
| R8 | A0-backed general register | Caller-saved | Low half of R8:R9 | Writes define the visible low 32 bits of accumulator A0. |
| R9 | General temporary | Caller-saved | High half of R8:R9 | Independent GPR outside paired live ranges. |
| R10 | A1-backed general register | Callee-saved | Low half of R10:R11 | Writes define the visible low 32 bits of accumulator A1. |
| R11 | General callee-saved register | Callee-saved | High half of R10:R11 | Pairs naturally with R10. |
| R12 | Frame pointer or general callee-saved register | Callee-saved | Low half of R12:R13 | Frame pointer is optional. |
| R13 | Link register, conditionally allocatable | Special / caller-clobbered by CALL | High half of R12:R13 | May be used as GPR only when return address is dead or saved. |
| R14 | Stack pointer | Preserved | Zero-extended source only | Always 32-bit; never a paired destination. |
| R15 | Program counter | Control state | Zero-extended source only | Always 32-bit; never a paired destination. |

Normative rule: R13 receives the return address on CALL. A function may allocate R13 as an ordinary register only after proving that its incoming return address is not needed, or after saving that address to another register or the stack. A leaf function normally still requires R13 for RET.

# 3. Calling Convention

## 3.1 Scalar arguments

The first four 32-bit argument words are passed in R0-R3. Additional argument words are placed on the caller’s stack in ascending address order. Values smaller than 32 bits occupy one register or stack word.

- Unsigned 8-bit and 16-bit arguments are zero-extended to 32 bits.

- Signed 8-bit and 16-bit arguments are sign-extended to 32 bits.

- Pointers are 32-bit unsigned addresses.

- Structures of 1, 2, or 4 bytes may be passed as an integer word.

- Larger structures are passed by reference unless the language ABI explicitly decomposes them.

## 3.2 64-bit and paired arguments

A 64-bit argument uses an aligned even/odd register pair. The low 32 bits occupy the even register and the high 32 bits occupy the following odd register. Register assignment skips to the next even register when necessary.

| Argument type | Preferred location | Fallback |
|----|----|----|
| First 64-bit argument | R0:R1 | 8-byte-aligned stack slot |
| Second 64-bit argument | R2:R3 | 8-byte-aligned stack slot |
| Later 64-bit argument | R4:R5 or R6:R7 when available | 8-byte-aligned stack slot |

## 3.3 Return values

- 8-, 16-, and 32-bit integer or pointer results return in R0.

- 64-bit integer results return in R0:R1.

- A second scalar result may return in R1 when an intrinsic or language convention specifies it.

- Small aggregates of up to 64 bits may return in R0:R1.

- Larger aggregates use a hidden result pointer passed in R0; user arguments then begin at R1.

- DOT/REDUCE accumulator results are not ABI return locations by default; they must be extracted to R0 or R0:R1.

# 4. Caller-Saved and Callee-Saved State

Baseline integer convention:

| Class | Registers/state | Responsibility |
|----|----|----|
| Caller-saved | R0-R9, condition codes | Caller preserves live values across a call. |
| Callee-saved | R10-R12 | Callee restores values before return if modified. |
| Link/control | R13 LR, R14 SP, R15 PC | CALL writes R13; callee preserves stack discipline; PC is control state. |
| Optional DSP state | A0/A1 guard bits, Q0/Q1 state, packed/low-lane mode | Saved only by functions that alter state classified as nonvolatile by their ABI attribute. |

R8 and R10 are visible 32-bit views of A0 and A1. Ordinary calls treat R8 as caller-saved and R10 as callee-saved. The hidden accumulator guard bits are caller-saved unless a function is explicitly declared DSP-state-preserving.

# 5. Stack Model

- The stack grows toward lower addresses.

- R14 contains the address of the current stack top.

- The stack is 8-byte aligned at every public function-call boundary.

- A 16-byte alignment may be requested by functions using wide local buffers or implementation-specific accelerators.

- All stack addresses and frame sizes are 32-bit.

- A paired load/store transfers low word at the lower address and high word at address +4.

## 5.1 Call frame

A typical non-leaf frame is organized as follows:

| Higher addresses | Contents                            | Owner         |
|------------------|-------------------------------------|---------------|
|                  | Incoming stack arguments            | Caller        |
|                  | Optional alignment padding          | Caller/callee |
|                  | Saved LR (R13), if required         | Callee        |
|                  | Saved callee-saved registers        | Callee        |
|                  | Local variables and spills          | Callee        |
| Lower addresses  | Outgoing argument area, if reserved | Callee        |

## 5.2 Frame pointer

R12 may serve as a frame pointer when dynamic stack allocation, debugging, exception unwinding, or large frames make a stable base useful. Otherwise the compiler should omit the frame pointer and use R12 as a callee-saved general register.

# 6. Function Entry, Calls, and Returns

## 6.1 CALL

CALL writes the address of the instruction following the complete call encoding into R13, then transfers control to the target. The caller assumes R13 is overwritten.

## 6.2 Leaf functions

A leaf function may return directly through R13 without touching the stack. It may use R13 as a temporary only if it first preserves the return address elsewhere and restores it before RET.

## 6.3 Non-leaf functions

A function that performs another CALL must preserve its incoming R13 before the nested call. The normal method is to push R13 in the prologue and restore it in the epilogue. A compiler may instead move it to a dead callee-saved register when profitable.

## 6.4 Conditional R12:R13 pair

R12:R13 is a legal paired-64 operand only while the LR value is not live in R13. The compiler must model the pair as aliasing both R12 and R13. Allocating the pair therefore requires either a dead LR or an explicit LR save. Calls are barriers that redefine R13.

# 7. Data Representation and Alignment

| Type | Size | Natural alignment | Representation |
|----|----|----|----|
| char / uint8 | 1 | 1 | 8-bit two's-complement or unsigned |
| short / uint16 | 2 | 2 | 16-bit little-endian |
| int / long / pointer | 4 | 4 | 32-bit little-endian |
| long long | 8 | 8 | Low word at lower address |
| float | 4 | 4 | Software-defined or optional profile |
| double | 8 | 8 | Software-defined or optional profile |

Aurora is little-endian. Unaligned scalar accesses may trap, be emulated by ASC, or be supported by an implementation profile. Portable ABI-conforming code must use natural alignment.

# 8. Packed, Low-Lane, and 64-bit Modes

## 8.1 Mode state across calls

The baseline ABI requires public functions to enter and return in normal scalar-32 mode unless their symbol is marked with a compatible mode-specific calling convention. Packed-8, packed-16, L8, L16, and paired-64 states are caller-saved.

## 8.2 Low-lane modes

- L8 updates bits 7:0 and preserves bits 31:8.

- L16 updates bits 15:0 and preserves bits 31:16.

- MOV, BSWAP, WSWAP, PACK, UNPACK, ZIP, and UNZIP remain full-register operations.

- The scoreboard remains whole-register granular.

## 8.3 Paired-64 mode

- Writable pairs are R0:R1, R2:R3, R4:R5, R6:R7, R8:R9, R10:R11, and conditionally R12:R13.

- R14/SP and R15/PC remain 32-bit but may be used as zero-extended 64-bit source operands.

- SP and PC are never paired destinations.

- Pair operations may be multi-cycle and scoreboarded.

- No extra 64-bit-only architectural scratch registers are required in v1.2.

# 9. Stream and Accumulator ABI

## 9.1 Stream state

Q0 and Q1 stream engines are caller-saved by default. A normal function may assume no live stream state survives a call unless both caller and callee use a stream-preserving ABI attribute.

- Register-only operations do not consume stream elements.

- A public function must restore the global stream-enable mask to its incoming value if it changes it.

- Q0 uses R0 or R0:R1; Q1 uses R4 or R4:R5.

- Interrupt handlers must not consume application stream state unless they save and restore it.

## 9.2 Accumulators

A0 and A1 are 40-bit signed accumulators backed by R8 and R10. Their visible low 32-bit register portions follow the integer volatility rules; hidden guard bits are caller-saved by default.

- A0 is intended as the primary caller-temporary accumulator.

- A1 may be used as a longer-lived accumulator, but a callee using A1 must preserve R10 and any required hidden guard state under a DSP-preserving ABI.

- General-purpose functions should extract accumulator results before calling unrelated code.

- DOT, SAD, and all REDUCE operations support overwrite and operator-specific fold forms.

# 10. Interrupt and Exception ABI

Hardware performs a short deterministic privileged entry. The minimum architectural interrupt frame contains the interrupted PC and PSR. The active vector may transfer directly to a handler or through ASC.

| Frame component | Required | Notes |
|----|----|----|
| Interrupted PC | Yes | Exact restart or return address. |
| PSR | Yes | Flags, mode, interrupt state, DSP sticky state. |
| R13/LR | When handler may call | Saved before nested CALL. |
| R0-R12 | As used | Handler preserves any register it modifies unless designated scratch. |
| A0/A1 hidden state | If modified | May be lazily saved using dirty state. |
| Q0/Q1 state | If modified | Must preserve pointers, counts, masks, and buffered elements. |

The default fast-interrupt convention reserves R0-R3 and flags as handler scratch. A full C interrupt handler or RTOS entry routine saves additional live state according to its generated prologue.

# 11. Variadic Functions and Language Interoperability

- Variadic arguments use the same register assignment as fixed arguments.

- The caller provides a register-save area when required by the language runtime so va_list can traverse register and stack arguments uniformly.

- Mode-specific or stream-preserving functions must not be called through an untyped function pointer.

- C, C++, Rust, and assembly interfaces must agree on data alignment, register volatility, and mode state.

# 12. Toolchain Requirements

- The compiler must model issue-slot eligibility, four-entry dynamic pairing, resource conflicts, and exact instruction latency.

- R13 must be represented as both LR and a conditionally allocatable GPR with correct call clobbering.

- R12:R13 allocation must alias the LR and be prohibited while the incoming return address is live.

- The allocator should prefer pair-aligned registers for 64-bit values and use atomic pair loads/stores for spills.

- The scheduler should alternate A0/A1 when useful, place independent operations near each other for either symmetric issue lane, and model contention for shared LSU, multiply/reduction, stream, branch, and writeback resources. Simple shuffles remain strong pairing candidates.

- The compiler may use L8/L16 upper-lane storage, but whole-register hazards must be respected.

- Public symbols must carry attributes for stream-preserving, DSP-state-preserving, interrupt, privileged, and paired-mode conventions.

# 13. Canonical Prologue and Epilogue Examples

## 13.1 Simple leaf function

ADD R0, R1\
RET R13

## 13.2 Non-leaf function

PUSH R13 ; preserve incoming return address\
PUSH R10 ; preserve callee-saved register if used\
...\
CALL helper\
...\
POP R10\
POP R13\
RET R13

## 13.3 Function using R12:R13 as a 64-bit temporary

PUSH R13 ; LR no longer live in R13\
; R12:R13 may now be allocated as a pair\
LD.P R12, \[R14, \#offset\]\
...\
POP R13 ; restore LR before return\
RET R13

# 14. Open Encoding Dependencies

The ABI is architecturally defined, but the following encoding details must be resolved in the subsequent ISA-reference phase:

- Exact encodings for pair load/store, mode changes, and special-register reads.

- Exact compact prologue/epilogue encodings for PUSH/POP register lists.

- Whether RET is a dedicated opcode or an alias for a branch through R13.

- Exact PSR fields for packed, low-lane, paired-64, stream-mask, and dirty-state controls.

- The interrupt-frame hardware minimum and any implementation-profile extensions.

# 15. ABI Freeze Checklist

| Review item                                   | Status     |
|-----------------------------------------------|------------|
| Register roles internally consistent          | PASS       |
| R13 LR and conditional GPR use defined        | PASS       |
| R14 SP and R15 PC remain 32-bit               | PASS       |
| 64-bit pair argument and return rules defined | PASS       |
| Stack growth and alignment defined            | PASS       |
| Caller/callee volatility defined              | PASS       |
| Streams and accumulators covered              | PASS       |
| Interrupt-frame policy defined                | PASS       |
| Exact instruction encodings complete          | NEXT PHASE |
