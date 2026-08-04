**Aurora Instruction Set Reference**

Phase 1 Baseline, Revision 1.0

# 1. Encoding model

Every base instruction is 16 bits. Bits 15:12 select one of sixteen primary families. R0-R15 use direct four-bit fields. Selected instructions consume one 16-bit extension word. A prefix and its consumer form one precise restartable instruction group.

| **Primary** | **Family**             | **Default format**             |
|-------------|------------------------|--------------------------------|
| 0           | System/control         | class\[11:8\], function\[7:0\] |
| 1           | Move/immediate         | Rd\[11:8\], imm8\[7:0\]        |
| 2           | Load                   | Rd, Rb, mode/offset            |
| 3           | Store                  | Rs, Rb, mode/offset            |
| 4           | Scalar arithmetic      | Rd, Ra, Rb / subfn             |
| 5           | Logic/compare/bit      | Rd, Ra, Rb / subfn             |
| 6           | Shift/rotate           | Rd, Rs, subfn/amount           |
| 7           | Scalar multiply/divide | Rd/pair, Ra, Rb / subfn        |
| 8           | Packed/SIMD            | Rd/pair, Ra, Rb / subfn        |
| 9           | Pack/unpack/convert    | Rd, Rs, subfn                  |
| A           | Reduction              | Rd/pair, Rs/Ra, subfn          |
| B           | Stream/stack/DMA       | class, operands/function       |
| C           | Conditional branch     | cond\[11:8\], disp8\[7:0\]     |
| D           | Jump/call/return       | class\[11:8\], operand\[7:0\]  |
| E           | Extended DSP           | Rd/pair, operands/subfn        |
| F           | Prefix/extensions      | class\[11:8\], payload\[7:0\]  |

# 2. Exact primary and sub-opcode allocation

## 0x0 System/control

| **Code/subfunction** | **Mnemonic** | **Normative meaning** |
|----|----|----|
| 00 | NOP | No operation |
| 01 | WAIT | Wait for interrupt/event |
| 02 | HALT | Halt until reset or permitted wake |
| 03 | EI | Enable maskable interrupts |
| 04 | DI | Disable maskable interrupts |
| 05 | SYNC | Order selected scalar/stream/DMA accesses |
| 06 | ISYNC | Synchronize instruction fetch |
| 07 | BREAK | Debug breakpoint |
| 08 | CLRQ | Clear sticky Q |
| 09 | RPSR | Read PSR to Rd encoded in extension |
| 0A | WPSR | Write permitted PSR fields from Rs |
| 0B | TRAP | Software exception; vector in extension |
| 0C | RETI | Return from interrupt |
| 0D | SVC | Supervisor call |
| 0E | FENCEIO | Strong device-ordering fence |
| 0F-FF | RES | Reserved |

## 0x1 Move/immediate

| **Code/subfunction** | **Mnemonic** | **Normative meaning** |
|----|----|----|
| Rd:imm8 | MOVI8 | Sign-extended 8-bit immediate |
| sub0 | MOV | Rd \<- Rs |
| sub1 | MOVU8 | Zero-extended imm8 |
| sub2 | LUI16 | Load upper 16 via extension |
| sub3 | MOV16 | Load 16-bit immediate via extension |
| sub4 | MOV32 | Load 32-bit immediate via two extension words |
| sub5 | CMOVcc | Conditional move; condition in extension |
| sub6-F | RES | Reserved |

## 0x2 Load

| **Code/subfunction** | **Mnemonic** | **Normative meaning**          |
|----------------------|--------------|--------------------------------|
| 0                    | LDBU         | Unsigned byte load             |
| 1                    | LDBS         | Signed byte load               |
| 2                    | LDHU         | Unsigned halfword load         |
| 3                    | LDHS         | Signed halfword load           |
| 4                    | LDW          | 32-bit word load               |
| 5                    | LDD          | 64-bit pair load               |
| 6                    | LDW.POST     | Word load, post-increment base |
| 7                    | LDW.PRE      | Pre-decrement base, word load  |
| 8                    | LDX          | Indexed/extended load          |
| 9-F                  | RES          | Reserved                       |

## 0x3 Store

| **Code/subfunction** | **Mnemonic** | **Normative meaning**           |
|----------------------|--------------|---------------------------------|
| 0                    | STB          | Byte store                      |
| 1                    | STH          | Halfword store                  |
| 2                    | STW          | 32-bit word store               |
| 3                    | STD          | 64-bit pair store               |
| 4                    | STW.POST     | Word store, post-increment base |
| 5                    | STW.PRE      | Pre-decrement base, word store  |
| 6                    | STX          | Indexed/extended store          |
| 7-F                  | RES          | Reserved                        |

## 0x4 Scalar arithmetic

| **Code/subfunction** | **Mnemonic** | **Normative meaning** |
|----|----|----|
| 0 | ADD | Rd=Ra+Rb |
| 1 | ADDS | ADD and update NZCV |
| 2 | ADC | Add with carry |
| 3 | ADCS | ADC and update NZCV |
| 4 | SUB | Rd=Ra-Rb |
| 5 | SUBS | SUB and update NZCV |
| 6 | SBC | Subtract with borrow/no-borrow convention |
| 7 | SBCS | SBC and update NZCV |
| 8 | MIN | Signed min |
| 9 | MAX | Signed max |
| A | UMIN | Unsigned min |
| B | UMAX | Unsigned max |
| C | ABS | Scalar absolute value |
| D | NEG | Two's-complement negate |
| E | ADDI4 | Signed short immediate add |
| F | SUBI4 | Signed short immediate subtract |

## 0x5 Logic/compare/bit

| **Code/subfunction** | **Mnemonic** | **Normative meaning** |
|----|----|----|
| 0 | AND | Bitwise AND |
| 1 | OR | Bitwise OR |
| 2 | XOR | Bitwise XOR |
| 3 | BIC | Ra AND NOT Rb |
| 4 | NOT | Bitwise complement |
| 5 | CMP | Ra-Rb; flags only |
| 6 | CMPI4 | Compare signed short immediate |
| 7 | TST | Ra AND Rb; flags only |
| 8 | CLZ | Count leading zeros |
| 9 | CTZ | Count trailing zeros |
| A | POPCNT | Population count |
| B | BITREV | Reverse 32 bits |
| C | BEXT | Bit-field extract; extension defines field |
| D | BINS | Bit-field insert; extension defines field |
| E-F | RES | Reserved |

## 0x6 Shift/rotate

| **Code/subfunction** | **Mnemonic** | **Normative meaning**               |
|----------------------|--------------|-------------------------------------|
| 0                    | LSL.I        | Logical left, immediate             |
| 1                    | LSR.I        | Logical right, immediate            |
| 2                    | ASR.I        | Arithmetic right, immediate         |
| 3                    | LSRR.I       | Rounded logical right, immediate    |
| 4                    | ASRR.I       | Rounded arithmetic right, immediate |
| 5                    | ROL.I        | Rotate left, immediate              |
| 6                    | ROR.I        | Rotate right, immediate             |
| 7                    | RCL.I        | Rotate through carry left           |
| 8                    | RCR.I        | Rotate through carry right          |
| 9                    | LSL.R        | Register shift amount               |
| A                    | LSR.R        | Register shift amount               |
| B                    | ASR.R        | Register shift amount               |
| C                    | ROR.R        | Register rotate amount              |
| D-F                  | RES          | Reserved                            |

## 0x7 Scalar multiply/divide

| **Code/subfunction** | **Mnemonic** | **Normative meaning**               |
|----------------------|--------------|-------------------------------------|
| 0                    | MULLO        | Low 32 bits unsigned/signed-neutral |
| 1                    | MULH         | High 32 bits signed                 |
| 2                    | UMULH        | High 32 bits unsigned               |
| 3                    | MUL64        | Signed 32x32 -\> 64 pair            |
| 4                    | UMUL64       | Unsigned 32x32 -\> 64 pair          |
| 5                    | DIV          | Signed quotient                     |
| 6                    | UDIV         | Unsigned quotient                   |
| 7                    | DIVREM       | Signed quotient/remainder pair      |
| 8                    | UDIVREM      | Unsigned quotient/remainder pair    |
| 9-F                  | RES          | Reserved                            |

## 0x8 Packed/SIMD

| **Code/subfunction** | **Mnemonic** | **Normative meaning** |
|----|----|----|
| 0 | PADD16 | 2x16 wrapping add |
| 1 | PSUB16 | 2x16 wrapping subtract |
| 2 | PADD8 | 4x8 wrapping add |
| 3 | PSUB8 | 4x8 wrapping subtract |
| 4 | QADD16 | 2x16 signed saturating add |
| 5 | QSUB16 | 2x16 signed saturating subtract |
| 6 | QADD8 | 4x8 signed saturating add |
| 7 | QSUB8 | 4x8 signed saturating subtract |
| 8 | PMIN16 | 2x16 signed min |
| 9 | PMAX16 | 2x16 signed max |
| A | PMIN8 | 4x8 signed min |
| B | PMAX8 | 4x8 signed max |
| C | PABSD16 | 2x16 absolute difference |
| D | PABSD8 | 4x8 absolute difference |
| E | PCMP16 | 2x16 comparison mask; condition extension |
| F | PCMP8 | 4x8 comparison mask; condition extension |

## 0x9 Pack/unpack/convert

| **Code/subfunction** | **Mnemonic** | **Normative meaning**             |
|----------------------|--------------|-----------------------------------|
| 0                    | PACK16       | Truncate two 32-bit lanes to 2x16 |
| 1                    | PACK8        | Truncate four 16-bit lanes to 4x8 |
| 2                    | QPACK16      | Signed saturating 32-\>16         |
| 3                    | QPACKU16     | Unsigned saturating 32-\>16       |
| 4                    | QPACK8       | Signed saturating 16-\>8          |
| 5                    | QPACKU8      | Unsigned saturating 16-\>8        |
| 6                    | UNPACK16L    | Widen low 16 lane                 |
| 7                    | UNPACK16H    | Widen high 16 lane                |
| 8                    | UNPACK8L     | Widen low two 8-bit lanes         |
| 9                    | UNPACK8H     | Widen high two 8-bit lanes        |
| A                    | ZIP16        | Interleave 16-bit lanes           |
| B                    | UNZIP16      | Deinterleave 16-bit lanes         |
| C                    | ZIP8         | Interleave 8-bit lanes            |
| D                    | UNZIP8       | Deinterleave 8-bit lanes          |
| E-F                  | RES          | Reserved                          |

## 0xA Horizontal/reduction

| **Code/subfunction** | **Mnemonic** | **Normative meaning**                    |
|----------------------|--------------|------------------------------------------|
| 0                    | HADD16       | Sum 2x16 to 32-bit scalar                |
| 1                    | HADD8        | Sum 4x8 to 32-bit scalar                 |
| 2                    | HMIN16       | Horizontal signed min                    |
| 3                    | HMAX16       | Horizontal signed max                    |
| 4                    | HMIN8        | Horizontal signed min                    |
| 5                    | HMAX8        | Horizontal signed max                    |
| 6                    | HADDW16      | Sum two widened 32-bit lanes -\> 64 pair |
| 7                    | HADDW8       | Sum four widened 16-bit lanes -\> 32     |
| 8                    | SAD16        | Sum 2x16 absolute differences            |
| 9                    | SAD8         | Sum 4x8 absolute differences             |
| A                    | HOR          | Horizontal OR                            |
| B                    | HXOR         | Horizontal XOR                           |
| C                    | HAND         | Horizontal AND                           |
| D-F                  | RES          | Reserved                                 |

## 0xB Stream/stack/DMA

| **Code/subfunction** | **Mnemonic** | **Normative meaning** |
|----|----|----|
| 00 | STRCFG0 | Configure R0 stream from descriptor registers |
| 01 | STRCFG4 | Configure R4 stream |
| 02 | STREN0 | Enable R0 stream |
| 03 | STREN4 | Enable R4 stream |
| 04 | STRDIS0 | Disable R0 stream |
| 05 | STRDIS4 | Disable R4 stream |
| 06 | STRSYNC | Synchronize selected streams |
| 07 | STRFLUSH | Flush selected stream writes |
| 08 | LIFOON | Couple R0/R4 LIFO |
| 09 | LIFOOFF | Decouple after synchronization |
| 0A | PUSH | Push one register on R13 stack |
| 0B | POP | Pop one register from R13 stack |
| 0C | PUSHM | Push register mask in extension |
| 0D | POPM | Pop register mask in extension |
| 10 | DMACFG | Configure DMA channel |
| 11 | DMASTART | Start DMA channel |
| 12 | DMASTOP | Stop DMA channel |
| 13 | DMASYNC | Synchronize DMA channel |
| 14-FF | RES | Reserved |

## 0xC Conditional branch

| **Code/subfunction** | **Mnemonic** | **Normative meaning**       |
|----------------------|--------------|-----------------------------|
| 0                    | AL           | Always                      |
| 1                    | EQ           | Z=1                         |
| 2                    | NE           | Z=0                         |
| 3                    | CS/HS        | C=1                         |
| 4                    | CC/LO        | C=0                         |
| 5                    | MI           | N=1                         |
| 6                    | PL           | N=0                         |
| 7                    | VS           | V=1                         |
| 8                    | VC           | V=0                         |
| 9                    | HI           | C=1 and Z=0                 |
| A                    | LS           | C=0 or Z=1                  |
| B                    | GE           | N=V                         |
| C                    | LT           | N!=V                        |
| D                    | GT           | Z=0 and N=V                 |
| E                    | LE           | Z=1 or N!=V                 |
| F                    | NV           | Never/reserved for patching |

## 0xD Jump/call/return

| **Code/subfunction** | **Mnemonic** | **Normative meaning**           |
|----------------------|--------------|---------------------------------|
| 0                    | JREL         | Signed relative jump; extension |
| 1                    | JREG         | Jump register                   |
| 2                    | CALLREL      | Relative call; extension        |
| 3                    | CALLREG      | Call register                   |
| 4                    | RET          | PC \<- R14                      |
| 5                    | RETI         | Return from interrupt           |
| 6                    | TAIL         | Tail-call register              |
| 7                    | SWITCH       | Indexed jump-table assist       |
| 8-F                  | RES          | Reserved                        |

## 0xE Extended DSP/arithmetic

| **Code/subfunction** | **Mnemonic** | **Normative meaning**                    |
|----------------------|--------------|------------------------------------------|
| 0                    | PMUL16       | 2x16 widening signed multiply -\> pair   |
| 1                    | PUMUL16      | 2x16 widening unsigned multiply -\> pair |
| 2                    | PMUL8        | 4x8 widening signed multiply -\> pair    |
| 3                    | PUMUL8       | 4x8 widening unsigned multiply -\> pair  |
| 4                    | PMAC16       | 2x16 widening MAC                        |
| 5                    | PMSUB16      | 2x16 widening multiply-subtract          |
| 6                    | PMAC8        | 4x8 widening MAC                         |
| 7                    | PMSUB8       | 4x8 widening multiply-subtract           |
| 8                    | DOT16        | 2x16 dot product -\> 64 pair             |
| 9                    | DOT8         | 4x8 dot product -\> 32                   |
| A                    | PSHL16       | Packed 2x16 shift                        |
| B                    | PSHL8        | Packed 4x8 shift                         |
| C                    | PRSHR16      | Packed rounded right shift               |
| D                    | PRSHR8       | Packed rounded right shift               |
| E-F                  | RES          | Reserved                                 |

## 0xF Prefix/extensions

| **Code/subfunction** | **Mnemonic** | **Normative meaning** |
|----|----|----|
| 0 | IMMHI | High immediate payload for next instruction |
| 1 | IMM32 | Begins 32-bit immediate group |
| 2 | DISP16 | 16-bit displacement for next memory/control instruction |
| 3 | REGMASK | Register mask for PUSHM/POPM |
| 4 | COND | Condition selector for CMOV/PCMP |
| 5 | STREAMX | Extended stream configuration payload |
| 6 | DMAX | Extended DMA payload |
| 7 | SYSX | Extended privileged/system payload |
| 8-F | RES | Reserved |

# 3. Normative execution rules

- All scalar arithmetic is modulo 2^32 unless an explicit saturating operation is selected.

- All packed wrapping operations wrap independently within each lane.

- Saturating operations clamp each lane and set sticky Q if any lane clamps.

- 64-bit destinations name an even register; the following odd register is implied. Odd pair bases trap.

- Loads, stores, streams, multiply, divide, and reductions may be scoreboarded and complete after the nominal pipeline stage.

- Instructions retire in program order. Faulting instructions do not partially update registers, PSR, stream state, or memory.

- Branches use signed displacement in 16-bit instruction units relative to the following instruction.

- R0 and R4 behave as ordinary registers when their stream mode is disabled.

- When stream mode is enabled, an architectural read or write consumes or produces one configured 8-, 16-, or 32-bit element and advances only on successful completion.

- No baseline 4-bit stream or packed lane format exists.

# 4. Baseline timing classes

| **Class** | **Latency** | **Initiation interval** | **Notes** |
|----|----|----|----|
| Scalar ALU/logic/shift | 1 | 1 | Forwarding may remove adjacent dependency stall |
| Packed ALU/pack/narrow | 1 | 1 | Q updates retire in order |
| Load hit in closely coupled SRAM | 2 | 1 per bank | Longer on bank conflict or wait-state memory |
| Store enqueue | 1 | 1 per bank | Visibility ordered by store/stream rules |
| Packed multiply/MAC | 2 | 1 | Shared compressor resource |
| Scalar multiply | 4 | 2 | Shared compressor resource |
| Reduction/SAD/dot | 2 | 1 | Shared compressor resource |
| Divide | \<=34 | non-pipelined | Scoreboarded iterative divider |
| Branch | resolved EX/MEM | \- | Mispredict penalty implementation profile: 2 cycles |
