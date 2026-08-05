> **STATUS: Superseded — pending regeneration** (per DDR-0063, 2026-08-04). This revision predates
> ADR-ISA-020, ADR-FE-006, ADR-STREAM-009, ADR-ISA-022, and ADR-DSP-018, and its `0xC` opcode-class
> table below (`LOOP.SET`/`LOOP.END`/`AGU.*`/`CIRC.*`/`ALIGN`/`LEA.S`/`BOUND`) directly conflicts
> with those locked decisions (which instead define `0xC0`=`LOOP`, `0xC1`=`NOP`, `0xC2`=`LOOPR`,
> `0xC3`-`0xC9` reserved). Per the documentation authority order adopted in DDR-0063, a document's
> prior `Frozen` status does not override a newer locked ADR — **the canonical
> `isa/database/aurora_v1_2_isa.json` (and its YAML/CSV mirrors) is authoritative for opcode
> assignments until this document is regenerated.** See `docs/governance/AUR-PM-004_Document_Status.csv`.

**Canonical Encoding Draft 1 - August 2026**

This specification converts the v1.2 programmer model and ABI into a concrete 16-bit base instruction map. It preserves compact code density, mode-based packed arithmetic, two-wide issue, stream controls, paired-64 emulation, and extension-word escape space.

# 1. Encoding Principles

- Every base instruction is exactly 16 bits. Optional extension words immediately follow the base word.

- Bits 15:12 form the primary opcode. The remaining 12 bits are interpreted by the selected format.

- R0-R15 use 4-bit register fields in ordinary scalar formats.

- Packed-8, packed-16, low-lane L8/L16, and paired-64 behavior is selected by PSR mode state rather than separate arithmetic opcode families.

- Instructions whose semantics must ignore packed or stream state carry a fixed decoder classification; they do not consume additional instruction bits.

- Extension words are used for long immediates, long branches, absolute addresses, privileged subfunctions, and future expansion.

- Undefined encodings trap as Illegal Instruction; they are not treated as NOPs.

# 2. Common Bit Numbering

> 15 12 11 0\
> +----------------------------+----------------------------+\
> \| primary opcode \| format payload \|\
> +----------------------------+----------------------------+

Register fields name the visible architectural register unless a format explicitly compresses an even pair base. R14 and R15 retain SP and PC semantics in every mode.

# 3. Base Instruction Formats

| Format | Bit layout | Use |
|----|----|----|
| RRR | op\[15:12\] \| rd\[11:8\] \| ra\[7:4\] \| rb\[3:0\] | Three-register ALU, compare, packed arithmetic, selected DSP operations. |
| RRI4 | op \| rd \| ra \| imm4 | Small signed/unsigned immediate arithmetic and shifts. |
| RR-SUB | op \| rd \| ra \| subop\[3:0\] | Unary operations, moves, byte/word rearrangement. |
| MEM4 | op \| rd/rs \| base \| off4 | Compact load/store with scaled or signed 4-bit offset. |
| BR8 | op \| cond\[11:8\] \| disp8\[7:0\] | Conditional PC-relative branch. |
| SYS12 | op \| system payload\[11:0\] | Control, mode, stream, interrupt, and extension escape. |
| PAIR | op \| pd\[11:9\] \| pa\[8:6\] \| pb/fn\[5:0\] | Compressed even-pair fields in paired-64 forms. |

# 4. Primary Opcode Map

| Opcode | Class | Purpose |
|----|----|----|
| 0x0 | ALU-R | RRR integer/packed add, sub, logic, compare-class operations |
| 0x1 | ALU-I | RRI4 immediate arithmetic, logic, and small constants |
| 0x2 | SHIFT | Immediate/register shifts, rotates, pair shifts in paired-64 mode |
| 0x3 | MUL/DIV | Multiply-step, multiply, MAC/MAS family, divide-step/divide |
| 0x4 | DSP-RED | DOT, SAD, REDUCE and accumulator fold/overwrite operations |
| 0x5 | PACK/SHUF | PACK, UNPACK, ZIP, UNZIP, BSWAP, WSWAP, byte shuffle |
| 0x6 | LOAD | Loads, including mode-dependent pair loads |
| 0x7 | STORE | Stores, including mode-dependent pair stores |
| 0x8 | BRANCH | Conditional PC-relative branches |
| 0x9 | CALL/JUMP | CALL, indirect jump, RET, long control transfers |
| 0xA | STACK | PUSH, POP, stack adjustment, compact save/restore |
| 0xB | STREAM | Q0/Q1 data, peek, push, pop, duplicate, replace, mask |
| 0xC | LOOP/AGU | Low-overhead loop, circular-address and address-generation control |
| 0xD | SYSTEM | PSR/mode, timer, interrupt, ASC, barriers, privileged control |
| 0xE | EXT | Extension-word escape and extended immediate/address forms |
| 0xF | CUSTOM/RES | Implementation profile, future ISA, and custom acceleration escape |

# 5. ALU Register Class - Primary 0x0

Format: RRR. Function is selected by the low nibble where the destination and first source are in the upper fields. The mode state determines scalar-32, packed-16, packed-8, L16, or L8 behavior.

| fn  | Mnemonic | Semantics                                 | Flags   |
|-----|----------|-------------------------------------------|---------|
| 0   | ADD      | rd = ra + rb                              | Z N C V |
| 1   | SUB      | rd = ra - rb                              | Z N C V |
| 2   | AND      | rd = ra & rb                              | Z N     |
| 3   | OR       | rd = ra \| rb                             | Z N     |
| 4   | XOR      | rd = ra ^ rb                              | Z N     |
| 5   | ANDN     | rd = ra & ~rb                             | Z N     |
| 6   | MIN.S    | signed lane/scalar min                    | Z N     |
| 7   | MAX.S    | signed lane/scalar max                    | Z N     |
| 8   | MIN.U    | unsigned lane/scalar min                  | Z N     |
| 9   | MAX.U    | unsigned lane/scalar max                  | Z N     |
| A   | CMP      | flags from ra-rb; rd field reserved/alias | Z N C V |
| B   | ADC      | rd = ra + rb + C                          | Z N C V |
| C   | SBC      | rd = ra - rb - !C                         | Z N C V |
| D   | MOV.M    | mode-sensitive move/merge form            | Z N     |
| E   | ABS      | absolute value by active lane             | Z N V   |
| F   | NEG      | two's-complement negate                   | Z N C V |

L8/L16 forms are two-address in-place when a preserved upper lane is required: rd is both old destination and source A. The assembler rejects a distinct ra unless an expansion sequence is selected.

# 6. Immediate ALU Class - Primary 0x1

| subop | Mnemonic | Immediate interpretation                     |
|-------|----------|----------------------------------------------|
| 0     | ADDI     | signed imm4                                  |
| 1     | SUBI     | signed imm4                                  |
| 2     | ANDI     | zero-extended imm4                           |
| 3     | ORI      | zero-extended imm4                           |
| 4     | XORI     | zero-extended imm4                           |
| 5     | CMPI     | signed imm4                                  |
| 6     | MOVI     | zero-extended imm4                           |
| 7     | MOVNI    | bitwise-not of imm4                          |
| 8     | ADDI.U   | unsigned imm4                                |
| 9     | BSET     | set selected low bit                         |
| A     | BCLR     | clear selected low bit                       |
| B     | BTST     | test selected low bit                        |
| C     | MINI     | signed immediate min                         |
| D     | MAXI     | signed immediate max                         |
| E     | EXTI     | consume following 16-bit immediate extension |
| F     | LEA4     | small address calculation                    |

# 7. Shift and Rotate Class - Primary 0x2

| fn  | Mnemonic | Behavior                        |
|-----|----------|---------------------------------|
| 0   | LSL.I    | logical left, imm4              |
| 1   | LSR.I    | logical right, imm4             |
| 2   | ASR.I    | arithmetic right, imm4          |
| 3   | ROL.I    | rotate left, imm4               |
| 4   | ROR.I    | rotate right, imm4              |
| 5   | LSL.R    | count from rb                   |
| 6   | LSR.R    | count from rb                   |
| 7   | ASR.R    | count from rb                   |
| 8   | ROL.R    | count from rb                   |
| 9   | ROR.R    | count from rb                   |
| A   | CLZ      | count leading zeros             |
| B   | CTZ      | count trailing zeros            |
| C   | POPCNT   | population count                |
| D   | BITREV   | bit reverse within active width |
| E   | ASHR.RND | rounded arithmetic shift right  |
| F   | reserved | future funnel/normalize form    |

In paired-64 mode, even-pair operands use compressed pair fields. SP and PC may be selected as zero-extended 64-bit sources in source-capable pair formats. Pair destinations are limited to R0:R1 through R12:R13, with R12:R13 legal only when LR is not live. Pair shift latency is implementation-defined but bounded and scoreboarded.

# 8. Multiply and Divide Class - Primary 0x3

| fn  | Mnemonic | Behavior                                         |
|-----|----------|--------------------------------------------------|
| 0   | MUL.LO   | low product by active lane/scalar width          |
| 1   | MUL.WIDE | full-width product to pair or internal wide path |
| 2   | MULH.S   | signed high half                                 |
| 3   | MULH.U   | unsigned high half                               |
| 4   | MAC      | multiply-add into selected accumulator           |
| 5   | MAS      | multiply-subtract from selected accumulator      |
| 6   | MULSTEP  | radix-4 iterative multiplication step            |
| 7   | DIVSTEP  | iterative division step                          |
| 8   | DIV.S    | signed divide, multi-cycle                       |
| 9   | DIV.U    | unsigned divide, multi-cycle                     |
| A   | REM.S    | signed remainder                                 |
| B   | REM.U    | unsigned remainder                               |
| C-F | reserved | future complex/dual-multiply profile             |

No scaled-divide opcode is allocated. Fixed-point scaling is performed explicitly with accumulator or pair shifts.

# 9. DSP Reduction Class - Primary 0x4

DSP-RED uses a compact accumulator-select bit, overwrite/fold bit, stream-consume override, and operation selector. Exact field layout:

> 15 12 11 10 9 8 5 4 0\
> +----+--+--+--+----------+------------+\
> \|4hex\|A \|F \|C \| srcsel \| redop \|\
> +----+--+--+--+----------+------------+\
> A: 0=A0, 1=A1 F: 0=overwrite, 1=fold C: stream consume override

| redop | Operation | Overwrite/fold semantics                     |
|-------|-----------|----------------------------------------------|
| 00    | ADD       | sum lanes; fold uses addition                |
| 01    | DOT       | sum lane products; fold uses addition        |
| 02    | SAD       | sum absolute differences; fold uses addition |
| 03    | AND       | bitwise AND reduction; fold uses AND         |
| 04    | OR        | bitwise OR reduction; fold uses OR           |
| 05    | XOR       | bitwise XOR reduction; fold uses XOR         |
| 06    | MIN.S     | signed minimum; fold uses min                |
| 07    | MAX.S     | signed maximum; fold uses max                |
| 08    | MIN.U     | unsigned minimum; fold uses min              |
| 09    | MAX.U     | unsigned maximum; fold uses max              |
| 0A    | ABSMAX    | maximum absolute lane value                  |
| 0B    | COUNT     | count true lanes; fold uses addition         |
| 0C-1F | reserved  | future reduction operators                   |

Source selection names register pairs or Q0/Q1 stream groups according to the mode and operation. Logical reductions zero-extend their scalar result into the selected 40-bit accumulator. Signed arithmetic reductions sign-extend as defined by active mode.

# 10. Pack, Shuffle, and Layout Class - Primary 0x5

| fn | Mnemonic | Behavior |
|----|----|----|
| 0 | MOV | full 32-bit register move; ignores L8/L16 and stream interception |
| 1 | BSWAP | reverse four bytes |
| 2 | WSWAP | swap high and low 16-bit words |
| 3 | ZIP8 | interleave byte lanes |
| 4 | UNZIP8 | deinterleave byte lanes |
| 5 | ZIP16 | interleave halfwords |
| 6 | UNZIP16 | deinterleave halfwords |
| 7 | PACK8 | pack selected low bytes |
| 8 | PACK16 | pack selected low halfwords |
| 9 | UNPACK8.S | sign-extend selected bytes |
| A | UNPACK8.U | zero-extend selected bytes |
| B | UNPACK16.S | sign-extend selected halfwords |
| C | UNPACK16.U | zero-extend selected halfwords |
| D | SHUF4 | small immediate byte permutation |
| E | MERGE | masked lane merge |
| F | reserved | future cross-pair permutation |

These operations are register-only and ignore stream consumption and low-lane arithmetic masking. They are strong candidates for the four-entry pairing window pass-through policy.

# 11. Load and Store Classes - Primaries 0x6 and 0x7

> 15 12 11 8 7 4 3 0\
> +----+-------+------+------ +\
> \| op \| rd/rs \| base \| off4 \|\
> +----+-------+------+-------+

| Active interpretation | Assembler mnemonic | Transfer |
|----|----|----|
| mode scalar-32 | LD.W / ST.W | 32-bit word, off4 scaled by 4 |
| packed-16 or L16 | LD.H / ST.H | 16-bit transfer, off4 scaled by 2 |
| packed-8 or L8 | LD.B / ST.B | 8-bit transfer, byte offset |
| paired-64 | LD.P / ST.P | atomic two-word transfer, even pair destination/source |
| extension form | LDX/STX | following word provides larger signed offset or absolute address |

- Loads are potentially faulting and therefore are conservative ordering points in the four-entry pairing window.

- Stores remain in program order and do not bypass older memory operations in the v1.2 baseline.

- MMIO regions are strongly ordered regardless of ordinary-memory rules.

- Pair loads/stores place the low word at the lower address and high word at address +4.

- Unaligned behavior is profile-defined; portable code uses natural alignment.

# 12. Branch Class - Primary 0x8

| cond | Mnemonic | Condition               |
|------|----------|-------------------------|
| 0    | AL       | always                  |
| 1    | EQ       | Z=1                     |
| 2    | NE       | Z=0                     |
| 3    | LT       | N xor V                 |
| 4    | GE       | not LT                  |
| 5    | LE       | Z or LT                 |
| 6    | GT       | not Z and GE            |
| 7    | CS/HS    | C=1                     |
| 8    | CC/LO    | C=0                     |
| 9    | MI       | N=1                     |
| A    | PL       | N=0                     |
| B    | VS       | V=1                     |
| C    | VC       | V=0                     |
| D    | Q0E      | Q0 end/empty condition  |
| E    | Q1E      | Q1 end/empty condition  |
| F    | reserved | future predicate source |

disp8 is a signed halfword displacement relative to the next base instruction. Backward branches are predicted taken; forward branches are predicted not taken. Extension opcode 0xE supplies long displacement forms.

# 13. Call and Jump Class - Primary 0x9

| subop | Mnemonic | Semantics                               |
|-------|----------|-----------------------------------------|
| 0     | CALL8    | short PC-relative call; writes R13      |
| 1     | CALLR    | register-indirect call; writes R13      |
| 2     | JMP8     | short unconditional PC-relative jump    |
| 3     | JMPR     | register-indirect jump                  |
| 4     | RET      | jump to R13                             |
| 5     | RET.POP  | restore LR from stack and return        |
| 6     | TAILR    | indirect tail call without changing R13 |
| 7     | TAIL8    | short PC-relative tail call             |
| 8     | CALLX    | extension-word long call                |
| 9     | JMPX     | extension-word long jump                |
| A-F   | reserved | future call gates / capability profiles |

# 14. Stack Class - Primary 0xA

| subop | Mnemonic | Semantics                                          |
|-------|----------|----------------------------------------------------|
| 0     | PUSH     | push one 32-bit register                           |
| 1     | POP      | pop one 32-bit register                            |
| 2     | PUSH.P   | push one 64-bit pair                               |
| 3     | POP.P    | pop one 64-bit pair                                |
| 4     | ADJSP-   | allocate small frame                               |
| 5     | ADJSP+   | release small frame                                |
| 6     | SAVE     | compact register-mask save using extension word    |
| 7     | RESTORE  | compact register-mask restore using extension word |
| 8     | ENTER    | save LR/FP and allocate frame                      |
| 9     | LEAVE    | release frame and restore LR/FP                    |
| A     | PUSHS    | push selected special state                        |
| B     | POPS     | restore selected special state                     |
| C-F   | reserved | future stack cache operations                      |

R14 is the implicit 32-bit stack pointer. Stack operations remain valid in every arithmetic mode and ignore stream interception.

# 15. Stream Class - Primary 0xB

| subop | Mnemonic | Semantics                                          |
|-------|----------|----------------------------------------------------|
| 0     | QMASK    | set two-bit Q0/Q1 interception mask                |
| 1     | QPEEK    | read current element without advancing             |
| 2     | QPOP     | consume current element                            |
| 3     | QPUSH    | produce one element                                |
| 4     | QDUP     | duplicate valid local/LIFO top                     |
| 5     | QREPL    | replace top/head without occupancy change          |
| 6     | QCFG     | configure width/stride/count using extension state |
| 7     | QADDR    | read/write current address                         |
| 8     | QCOUNT   | read/write remaining count                         |
| 9     | QSYNC    | synchronize DMA/buffer state                       |
| A     | QCIRC    | configure power-of-two circular region             |
| B     | QSTAT    | read status/end flags                              |
| C     | QCLR     | clear/reset selected stream engine                 |
| D-F   | reserved | future scatter/gather or multi-stream profile      |

Q0 is associated with R0 or R0:R1; Q1 with R4 or R4:R5. Register-only instructions naming those registers never consume a stream element. Stream consumption and production remain ordered independently for Q0 and Q1.

# 16. Loop and AGU Class - Primary 0xC

| subop | Mnemonic | Semantics                                             |
|-------|----------|-------------------------------------------------------|
| 0     | LOOP.SET | set loop start/end/count                              |
| 1     | LOOP.END | decrement/test and branch to loop start               |
| 2     | AGU.ADD  | address add with signed stride                        |
| 3     | AGU.POST | post-update address                                   |
| 4     | AGU.PRE  | pre-update address                                    |
| 5     | CIRC.ADD | power-of-two wrapped address update                   |
| 6     | CIRC.SUB | wrapped decrement                                     |
| 7     | ALIGN    | align address to selected power of two                |
| 8     | LEA.S    | scaled address calculation                            |
| 9     | BOUND    | bounds check / optional trap                          |
| A-F   | reserved | future bit-reversed addressing and profile extensions |

# 17. System Class - Primary 0xD

| payload | Mnemonic          | Semantics                                      |
|---------|-------------------|------------------------------------------------|
| 000     | MRS               | read PSR or selected special register          |
| 001     | MSR               | write permitted PSR or special field           |
| 002     | MODE              | set scalar/packed/L8/L16/paired-64 mode        |
| 003     | FENCE             | memory/stream ordering barrier                 |
| 004     | EI                | enable interrupts                              |
| 005     | DI                | disable interrupts                             |
| 006     | IRET              | return from interrupt/exception                |
| 007     | SVC               | enter ASC service by immediate number          |
| 008     | WFI               | wait for interrupt                             |
| 009     | TIMER.LOAD        | atomically load countdown and vector control   |
| 00A     | TIMER.CTL         | enable/disable/ack timer                       |
| 00B     | TIME.READ         | read 32-bit free-running coarse counter        |
| 00C     | VBASE             | read/write interrupt vector base               |
| 00D     | DMA.CTL           | privileged DMA control escape                  |
| 00E     | BREAK             | debug breakpoint                               |
| 00F     | NOP               | architectural no-operation                     |
| 010-FFF | reserved/extended | system subfunction or extension-word operation |

The countdown timer uses coarse implementation-defined ticks and posts a selected interrupt when it reaches zero. The free-running counter is a separate 32-bit special register. Both may be prescaled; software or ASC translates requested time into ticks.

# 18. Extension Escape - Primary 0xE

| ext kind | Name     | Meaning                                           |
|----------|----------|---------------------------------------------------|
| 0        | IMM16    | following word is a 16-bit immediate              |
| 1        | IMM32    | following two words form a 32-bit immediate       |
| 2        | BR16     | following word is signed long branch displacement |
| 3        | CALL16   | following word is signed long call displacement   |
| 4        | ABS32    | following two words form absolute 32-bit address  |
| 5        | MEM16    | following word is signed memory offset            |
| 6        | SYSX     | following word extends system subfunction         |
| 7        | SHUFX    | following word supplies shuffle mask              |
| 8        | REGMASK  | following word supplies save/restore mask         |
| 9        | QCFGX    | following words supply stream configuration       |
| A        | LOOPX    | following words supply loop configuration         |
| B-F      | reserved | future ISA extension                              |

An extension escape and its payload words form one architectural instruction for PC advancement, CALL link generation, exception restart, and debugger single-step behavior.

# 19. Custom and Reserved Escape - Primary 0xF

- 0xF encodings are not assigned to ordinary software in the base profile.

- An implementation may expose documented custom accelerators only through a discoverable profile identifier.

- Base-profile software encountering unsupported 0xF encodings receives Illegal Instruction.

- Toolchains must not emit custom forms unless the selected target profile explicitly enables them.

# 20. PSR Mode-State Encoding Requirement

The exact PSR bit positions remain part of the privileged-register layout, but the mode field must encode at least the following six states:

| mode | Meaning                    |
|------|----------------------------|
| 000  | Scalar-32                  |
| 001  | Packed-16                  |
| 010  | Packed-8                   |
| 011  | L16 low-lane arithmetic    |
| 100  | L8 low-lane arithmetic     |
| 101  | Paired-64 scalar emulation |
| 110  | Reserved                   |
| 111  | Reserved                   |

This three-bit field leaves two encodings for future fractional, complex, or profile-specific modes. Instruction classes marked register-layout or transport ignore L8/L16 masking. Stream interception is controlled separately by QMASK and per-instruction consume/local classification.

# 21. Four-Entry Pairing Metadata

Each decoded instruction receives static metadata used by the four-entry dynamic pairing window:

| Metadata | Purpose |
|----|----|
| slot eligibility | A, B, or either |
| source mask | whole-register source dependencies |
| destination mask | whole-register destination dependencies |
| flags read/write | condition-code hazards |
| A0/A1 access | read, write, fold, overwrite |
| Q0/Q1 access | local, peek, consume, produce, configure |
| memory class | none, load, store, MMIO, barrier |
| fault class | non-faulting, potentially faulting, privileged |
| resource mask | ALU, shifter, multiplier cluster, reduction tree, AGU, memory port |

Unary register-only operations in primary 0x5 are preferred pass-through candidates. The oldest unissued instruction anchors issue; one compatible younger instruction may issue with it. Unissued entries compact in original order and the front end refills one or two positions.

# 22. Reserved-Space Policy

- Reserved primary and subfunction encodings remain illegal until assigned by a later architecture version.

- New operations should first consume reserved subfunctions within the most closely related primary class.

- Primary 0xE is preferred for operations needing extra operands or immediates.

- Primary 0xF is reserved for optional implementation profiles and should not fragment the base ABI.

- No v1.2 encoding is repurposed based solely on microarchitectural implementation convenience.

# 23. Encoding Review Checklist

| Review item                                       | Status        |
|---------------------------------------------------|---------------|
| All 16 primary opcode values assigned or reserved | PASS          |
| Core ALU and mode-based packed operations encoded | PASS          |
| DOT/SAD/REDUCE overwrite and fold encoded         | PASS          |
| Stream queue operations encoded                   | PASS          |
| Pair load/store and pair shifts represented       | PASS          |
| SP/PC zero-extended paired sources preserved      | PASS          |
| CALL/RET and R13 LR semantics represented         | PASS          |
| Timer and free-running counter access represented | PASS          |
| Long immediates and addresses have extension path | PASS          |
| Exact RTL bit slices for every subformat          | NEXT DETAIL   |
| Assembler grammar and canonical aliases           | NEXT DETAIL   |
| Per-instruction timing table                      | NEXT DOCUMENT |

# 24. Next Documentation Dependency

With the opcode map fixed at the class and subfunction level, the next document should be the Complete Instruction Reference and Timing Table. It will define exact operands, pseudocode, flags, exceptions, issue slot, latency, initiation interval, mode legality, and examples for every assigned encoding.
