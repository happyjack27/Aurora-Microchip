# Aurora v1.2 Compiler, Toolchain and Static Scheduling Specification

This document defines the expected behavior of the compiler, assembler, linker, scheduler, simulator, and debugger for Aurora v1.2.

## Compiler backend

LLVM/GCC backend, ABI lowering, instruction selection, register allocation, paired-64 support.

## Register allocation

Exploit L8/L16 upper-lane storage, prefer aligned register pairs, model R13 as conditional LR/GPR, preserve R14/R15.

## Instruction scheduling

Compiler performs primary scheduling. Hardware four-entry pairing window performs only local pairing repair. Model resource usage rather than fixed issue slots.

## Dual issue

Emit independent instruction streams; favor shuffle/layout ops as pairing candidates; alternate accumulator use when profitable.

## Streams

Recognize streaming loops, configure Q0/Q1, generate circular addressing and consume/peek controls.

## DSP intrinsics

Expose DOT, REDUCE, SAD, PACK, UNPACK, ZIP, UNZIP, MAC, MAS through intrinsics.

## Assembler

Accept pseudo-ops, paired registers, extension words, and machine-readable ISA database as source of truth.

## Linker

Support ITCM/DTCM placement, vector placement, boot ROM sections, profile-aware memory maps.

## Simulator

Cycle-accurate mode and functional mode generated from ISA database.

## Debugger

Show accumulators, stream state, pairing window, scoreboard, and pipeline state.

## Verification

Assembler, simulator, RTL, and documentation generated from the same ISA database.
