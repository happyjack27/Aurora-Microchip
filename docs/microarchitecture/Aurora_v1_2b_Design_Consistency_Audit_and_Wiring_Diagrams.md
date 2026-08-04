**Aurora Architecture v1.2b\
Design Consistency Audit and Wiring Diagrams**

*Canonical correction package — August 2026*

# 1. Audit Conclusion

The major Aurora design choices remain coherent: 16 compact 32-bit registers, 16-bit base instructions, two symmetric issue lanes, a four-entry oldest-anchored pairing window, in-order retirement, no register renaming or general reorder buffer, two 40-bit accumulators, two stream engines, optional ITCM/DTCM, and DIVSTEP-based software/runtime division.

# 2. Inconsistencies Found and Corrected

| Issue | Finding | Resolution |
|----|----|----|
| Fixed Slot A / Slot B wording | ABI, instruction reference, and microarchitecture retained older asymmetric scheduling language. | Replaced with symmetric-lane terminology and explicit shared-resource constraints. |
| Standalone divider | Instruction timing, microarchitecture, and floorplan still described or budgeted a dedicated divider. | Replaced with a small DIVSTEP assist reusing lane ALU/shifter/compare resources. |
| Divider area allocation | Floorplan allocated 4% of core logic to a divider. | Reduced DIVSTEP assist to 1%; returned 3% to debug/trace/miscellaneous implementation allowance. |
| Stale source files | Older RTL module documents named AUR-RTL-002F Divider remain in historical folders. | Marked superseded by AUR-RTL-002F DIVSTEP Assist v1.2a; they should remain only as historical artifacts. |

# 3. Confirmed Canonical Design Choices

- R13 is the link register and conditionally allocatable GPR; R14 is SP; R15 is PC.

- R14 and R15 remain 32-bit and may only be zero-extended paired-64 sources.

- Writable 64-bit pairs are R0:R1 through R12:R13, with R12:R13 conditional on LR liveness.

- A0 and A1 are 40-bit accumulators, with low 32-bit views associated with R8 and R10.

- Q0 overlays R0/R1 and Q1 overlays R4/R5; register-only layout operations do not consume streams.

- Both issue lanes accept ordinary operations; specialized units are shared resources.

- DIVSTEP is the hardware primitive; full divide/remainder is compiler/runtime/ASC software.

- TCM is optional by product profile; the baseline has no mandatory L1/L2 cache.

- Architectural retirement is in order and exceptions/interrupts are precise.

- One coarse countdown timer is software-multiplexed for OS deadlines.

# 4. Internal Core Wiring and Layout

<img src="media/image1.png" style="width:7in;height:4.2947in" />

This is a logical floorplan, not a transistor-level or place-and-route drawing. The central register file, adjacent symmetric lanes, nearby multiply/reduction cluster, and streams close to the data-memory fabric minimize the most important data paths.

# 5. External SoC and Board Context

<img src="media/image2.png" style="width:7in;height:4.2947in" />

Aurora presents a unified physical address space. On-chip memories and peripherals are fabric targets; external flash, SRAM, or DRAM connect through ready/acknowledge controllers. DMA and streams use the same physical map and can double-buffer data without a separate stream address space.

# 6. Remaining Consistency Work

- Regenerate the complete instruction/timing table from the machine-readable ISA database so no fixed slot letters remain.

- Remove or archive superseded divider documents from active repository indexes.

- Replace the initial shallow marketing feature matrix with evidence-backed comparisons after synthesis and benchmark results.

- Consolidate duplicated architecture databases into one canonical repository location.

- Add document revision headers identifying v1.2b corrections and superseded sources.

# 7. Corrected Canonical Documents in This Package

- AUR-ARCH-003_ABI_Specification_v1_2b.docx

- AUR-ARCH-005_Instruction_Reference_v1_2b.docx

- AUR-ARCH-007_Microarchitecture_v1_2b.docx

- AUR-ARCH-008_Core_Microarchitecture_and_Floorplan_v1_2b.docx
