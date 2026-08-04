**Aurora v1.2 — Instruction Pipeline Event Sequences**

*AUR-ARCH-009 | Microarchitecture Reference*

---

# Overview

This document describes the sequence of microarchitectural events each Aurora v1.2 instruction class passes through from fetch to retirement. Each row shows the chain of units visited, using arrow notation (`->`), along with the shared execution resource contended and a verbal description of what happens at each stage.

The four pipeline stages are:

| Stage | Name | Primary Work |
|---|---|---|
| 1 | **IF** | Fetch 1–2 16-bit words; assemble EXT word; prefetch |
| 2 | **ID/RR** (DW) | Decode; 4-entry pairing window; hazard/scoreboard checks; register read |
| 3 | **EX/MEM** | Execute / address generation / branch resolve / memory launch |
| 4 | **WB/RET** | Writeback; completion commit; in-order architectural retirement |

## Unit Abbreviations

| Abbreviation | Unit |
|---|---|
| IF | Instruction Fetch |
| DW | Decode Window (4-entry pairing window) |
| RF | Register File |
| SB | Scoreboard |
| ALU | Scalar ALU |
| SHF | Barrel Shifter |
| MUL | Multiplier / Compressor Cluster |
| DIV | Divider |
| AGU | Address Generation Unit |
| LSU | Load/Store Unit |
| BRU | Branch Resolution Unit |
| RED | Reduction Tree |
| STR | Stream Engine (Q0/Q1) |
| MR | Mode Register |
| SYS | System / Privilege Unit |
| WB | Writeback |
| RET | Retire |

## Slot and Resource Model

Both issue lanes are **symmetric**: any instruction may issue from either lane when dependencies and resources permit. Pairing legality is determined by data dependencies, ordering rules, and physical resource availability — not by a fixed slot assignment. The **Shared Resource** column identifies what functional unit is contended; two instructions may pair only if they target different shared resources and carry no data dependency between them.

---

# Instruction Pipeline Event Sequences

| Instruction(s) | Shared Resource | Pipeline Chain | Notes |
|---|---|---|---|
| ADD, SUB, AND, OR, XOR, CMP, MIN, MAX | ALU | IF -> DW -> RF -> ALU -> WB -> RET | No scoreboard mark; 1-cycle; flags (Z/N/C/V) produced; EX→ID bypass available |
| ADDI, SUBI, ANDI, ORI, XORI, CMPI | ALU | IF -> DW -> RF -> ALU -> WB -> RET | Immediate replaces Rb; otherwise identical to register ALU path |
| MOV, ZEXT8, SEXT8, ZEXT16, SEXT16 | ALU | IF -> DW -> RF -> ALU -> WB -> RET | Preferred pass-through candidates in pairing window |
| PACK, UNPACK, ZIP, UNZIP, BSWAP, WSWAP, SHUFFLE | ALU | IF -> DW -> RF -> ALU -> WB -> RET | Register-layout; preferred pairing candidates; ignore lane mask and stream interception |
| LSL, LSR, ASR, ROL, ROR | ALU / SHF | IF -> DW -> RF -> SB(mark) -> SHF -> SHF -> WB -> SB(clear) -> RET | 2-cycle; Rd marked busy at issue; PAIRED64 mode may require additional cycle |
| DIVSTEP | ALU / SHF | IF -> DW -> RF -> ALU -> WB -> RET | Single radix step; reuses ALU/shifter; no scoreboard mark; 1-cycle |
| MUL, MULH, MAC, MAS | MUL | IF -> DW -> RF -> SB(mark) -> MUL -> MUL -> MUL -> WB -> SB(clear) -> RET | 3-cycle pipelined; dst/accumulator marked busy; II=1 (new op may launch each cycle) |
| DIV | DIV | IF -> DW -> RF -> SB(mark) -> DIV(×8..32) -> WB -> SB(clear) -> RET | Non-pipelined; DIV resource locked for full duration; II = latency |
| REDUCE.ADD, REDUCE.AND, REDUCE.OR, REDUCE.XOR, REDUCE.MIN, REDUCE.MAX, REDUCE.ABSMAX, REDUCE.COUNT | RED (shared with MUL) | IF -> DW -> RF -> SB(mark A0/A1) -> RED -> WB(A0/A1) -> SB(clear) -> RET | 2-cycle; lane mask applied; fold path merges with accumulator using operator rule |
| DOT, SAD | MUL + RED | IF -> DW -> RF -> SB(mark A0/A1) -> MUL -> MUL -> RED -> WB(A0/A1) -> SB(clear) -> RET | 3-cycle; lane-wise multiply then compress into accumulator |
| LD | LSU | IF -> DW -> RF -> SB(mark Rd) -> AGU -> LSU -> MEM -> WB -> SB(clear) -> RET | Rd busy until data returns; alignment/access fault possible; external targets insert wait states |
| POP, POPM | LSU | IF -> DW -> RF -> SB(mark Rd) -> AGU(R14) -> LSU -> MEM -> WB -> SB(clear) -> RET | Uses R14 as stack pointer; POPM iterates over register mask |
| ST | LSU | IF -> DW -> RF -> AGU -> LSU -> RET | No Rd; store-order barrier; becomes externally visible only at in-order retirement |
| PUSH, PUSHM | LSU | IF -> DW -> RF -> AGU(R14) -> LSU -> RET | Uses R14 as stack pointer; PUSHM iterates; ordered-memory barrier |
| B.EQ, B.NE, B.LT, B.GE, B.LTU, B.GEU, B.MI, B.PL | BRU | IF -> DW -> RF(flags) -> BRU -> [flush+redirect \| fall-through] -> RET | Flags must not be SB-busy; backward=predict-taken, forward=predict-not-taken; misprediction flushes DW + prefetch |
| CALL | BRU | IF -> DW -> BRU -> WB(R13=PC+len) -> RET | R13 written with return address; direct target predicted taken; refill penalty on redirect |
| JMP | BRU | IF -> DW -> BRU -> RET | PC redirected; no register write; refill penalty on taken |
| RET | BRU | IF -> DW -> RF(R13) -> BRU -> RET | Reads R13 as target; indirect — refill penalty always applies |
| JMPR | BRU | IF -> DW -> RF(Rsrc) -> BRU -> RET | Reads arbitrary register as target; indirect — refill penalty always applies |
| QMASK, QPEEK, QDUP, QREPL | STR | IF -> DW -> SB(Q-check) -> STR -> WB -> SB(clear) -> RET | 1-cycle; stream ordering enforced; Q-state SB conflict stalls issue |
| QPUSH, QPOP, QCFG, QCIRC | STR | IF -> DW -> RF -> SB(Q-check) -> STR -> WB -> SB(clear) -> RET | 2-cycle; QPOP writes Rd; QPUSH reads Rs; QCFG/QCIRC update stream config registers |
| QSTEP | STR | IF -> DW -> SB(Q-check) -> STR -> RET | Advances pinned-stream phase; no data transfer; stream config fault possible |
| LOOPSET, LOOPEND | AGU | IF -> DW -> RF -> AGU(loop-ctr) -> [redirect if ctr≠0] -> RET | Control barrier; younger instructions held until retire; LOOPEND redirects PC if counter ≠ 0 |
| AGUCFG, STRIDE | AGU | IF -> DW -> RF -> AGU(cfg) -> RET | Writes AGU configuration registers; no control barrier |
| MODE | MR | IF -> DW -> MR -> RET | Writes ARITH_MODE bits (SCALAR32/PACKED/LOW/PAIRED); all subsequent mode-sensitive ops observe new mode |
| MRS | SYS | IF -> DW -> SYS -> WB(Rd) -> RET | Privileged; reads system register into GPR; privilege_fault if not privileged |
| MSR | SYS | IF -> DW -> RF -> SYS -> RET | Privileged; writes GPR to system register; privilege_fault if not privileged |
| EI, DI | SYS | IF -> DW -> SYS -> RET | Enable/disable interrupts; serializing — older instructions retire first |
| IRET | SYS | IF -> DW -> SYS -> WB(PSR+PC) -> RET | Restores saved PSR and PC; serializing; privilege_fault if not privileged |
| ASCALL, TIMERLOAD, TIMERVEC, TIMERCTL | SYS | IF -> DW -> RF -> SYS -> RET | Privileged system/timer ops; serializing |
| RDCYCLE | SYS | IF -> DW -> SYS -> WB(Rd) -> RET | Non-privileged cycle counter read |
| WFI, WFE | SYS | IF -> DW -> SYS -> [idle] -> RET | Serializing; core idles until interrupt (WFI) or architectural event (WFE) |
| HALT | SYS | IF -> DW -> SYS -> [core stopped] | Privileged; core stops until allowed wake, debug, or reset |
| CTXSAVE | SYS + LSU | IF -> DW -> RF -> SYS -> AGU -> LSU(×4) -> RET | Serializing; iterates register mask to memory via stream-style path; alignment/access fault possible |
| CTXRESTORE | SYS + LSU | IF -> DW -> RF -> SYS -> AGU -> LSU(×4) -> WB(PSR+PC last) -> RET | PSR and PC committed architecturally last; serializing; younger instructions blocked |
| EXT | (prefix — no resource) | IF(attach) -> DW -> [merged with base instruction] | Transparent prefix; no standalone SB entry; EXT+base fetched and decoded as one unit |
| CUSTOM | implementation-defined | IF -> DW -> [impl-defined] | Raises illegal_instruction if unimplemented |

---

*Cross-references: AUR-ARCH-007 (Microarchitecture), AUR-ARCH-008 (Core Floorplan), Aurora_Architecture_v1_2_Pipeline_and_Microarchitecture_Specification.md*
