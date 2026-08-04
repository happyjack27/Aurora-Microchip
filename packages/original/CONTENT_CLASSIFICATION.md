# packages/original — Content Classification

This folder used to hold 11 vendor delivery-snapshot `.zip` files. They were extracted and
their `.docx` files converted to Markdown under `extracted/` on 2026-08-04, then the `.zip`
files were deleted (recoverable from git history). Every extracted file was compared against
the rest of the repository to determine whether it was already present. Results below.

## Redundant — byte-identical to a file already in the repo (verified by content diff)

| Extracted file (under `extracted/<package>/`) | Package | Identical to |
|---|---|---|
| `ADR-MEM-009_Required_Near_Memory_DMA_and_Separation` | Aurora_DMA_and_Reduction_Separation_Update_v1_2o | [adr/ADR-MEM-009_Required_Near_Memory_DMA_and_Separation.md](../../adr/ADR-MEM-009_Required_Near_Memory_DMA_and_Separation.md) |
| `DDR-0058_DMA_and_Separation_Documentation` | Aurora_DMA_and_Reduction_Separation_Update_v1_2o | [ddr/DDR-0058_DMA_and_Separation_Documentation.md](../../ddr/DDR-0058_DMA_and_Separation_Documentation.md) |
| `ADR-STREAM-008_Implicit_Stream_Access_for_Computation` | Aurora_Implicit_Stream_Arithmetic_Rule_v1_2r | [adr/ADR-STREAM-008_Implicit_Stream_Access_for_Computation.md](../../adr/ADR-STREAM-008_Implicit_Stream_Access_for_Computation.md) |
| `DDR-0061_Corrected_Stream_Access_Documentation_Rule` | Aurora_Implicit_Stream_Arithmetic_Rule_v1_2r | [ddr/DDR-0061_Corrected_Stream_Access_Documentation_Rule.md](../../ddr/DDR-0061_Corrected_Stream_Access_Documentation_Rule.md) |
| `AUR-ARCH-005_Aurora_Instruction_Reference_Full_v1_2s` | Aurora_Prefetch_and_8_Word_Loop_Update_v1_2s | [docs/canonical/AUR-ARCH-005_Aurora_Instruction_Reference_Full_v1_2s.md](../../docs/canonical/AUR-ARCH-005_Aurora_Instruction_Reference_Full_v1_2s.md) |
| `DDR-0062_Prefetch_and_Hardware_Loop_Window_Documentation` | Aurora_Prefetch_and_8_Word_Loop_Update_v1_2s | [ddr/DDR-0062_Prefetch_and_Hardware_Loop_Window_Documentation.md](../../ddr/DDR-0062_Prefetch_and_Hardware_Loop_Window_Documentation.md) |
| `ADR-FE-006_Two_Entry_Prefetch_and_Eight_Word_Loop` | Aurora_Prefetch_and_8_Word_Loop_Update_v1_2s | [adr/ADR-FE-006_Two_Entry_Prefetch_and_Eight_Word_Loop.md](../../adr/ADR-FE-006_Two_Entry_Prefetch_and_Eight_Word_Loop.md) |
| `Aurora_Architecture_v1_2_ABI_Specification` | Aurora_v1_2_ISA_Encoding_and_ABI_Package | [docs/abi/Aurora_Architecture_v1_2_ABI_Specification.md](../../docs/abi/Aurora_Architecture_v1_2_ABI_Specification.md) |
| `Aurora_Architecture_v1_2_ABI_Specification` | Aurora_v1_2_Instruction_Reference_Package | same as above |
| `AUR-PM-002_ADR_Register_v1_2` | Aurora_Project_v1_2_Organized_Repository | [decision-logs/source-registers/Aurora_Architecture_Decision_Register_ADR_v1_2.md](../../decision-logs/source-registers/Aurora_Architecture_Decision_Register_ADR_v1_2.md) |
| `AUR-PM-003_Expanded_ADR_Set_v1_2` | Aurora_Project_v1_2_Organized_Repository | [decision-logs/source-registers/Aurora_Expanded_ADR_Set_v1_2.md](../../decision-logs/source-registers/Aurora_Expanded_ADR_Set_v1_2.md) |
| `AUR-PM-001_Documentation_Master_Index_v1_2` | Aurora_Project_v1_2_Organized_Repository | [docs/governance/Aurora_Documentation_Master_Index_v1_2.md](../../docs/governance/Aurora_Documentation_Master_Index_v1_2.md) |

No action taken — left in `extracted/` only.

## Superseded — differs from a newer revision already in the repo

| Extracted file | Package | Superseded by |
|---|---|---|
| `AUR-ARCH-005_Aurora_Instruction_Reference_Full_v1_2o` | Aurora_DMA_and_Reduction_Separation_Update_v1_2o | `docs/canonical/AUR-ARCH-005_..._Full_v1_2s.md` (final) |
| `AUR-ARCH-005_Aurora_Instruction_Reference_Full_v1_2r` | Aurora_Implicit_Stream_Arithmetic_Rule_v1_2r | same, `v1_2s` (final) |
| `AUR-ARCH-005_Instruction_Reference_v1_2` (no letter) | Aurora_Project_v1_2_Organized_Repository | same, `v1_2s` (final) |
| `AUR-ARCH-003_ABI_Specification_v1_2` | Aurora_Project_v1_2_Organized_Repository | [docs/abi/AUR-ARCH-003_ABI_Specification_v1_2b.md](../../docs/abi/AUR-ARCH-003_ABI_Specification_v1_2b.md) (confirmed content differs) |
| `AUR-ARCH-007_Microarchitecture_v1_2a` | Aurora_Project_v1_2_Organized_Repository | [docs/microarchitecture/AUR-ARCH-007_Microarchitecture_v1_2b.md](../../docs/microarchitecture/AUR-ARCH-007_Microarchitecture_v1_2b.md) |

No action taken — left in `extracted/` only, as historical drafts.

## New — not found anywhere else in the repo; copied to their proper home

| Extracted file | Package | Copied to |
|---|---|---|
| `AUR-ARCH-010_Machine_Readable_Architecture_Database_Expanded` + `aurora_architecture_v1_2.json`, `aurora_arch_pkg.sv`, `aurora_arch_v1_2.h`, `aurora_arch_constants.py`, `validate_architecture_database.py`, `aurora_architecture_schema_v1_0.json`, `aurora_memory_regions.csv`, `aurora_requirements.csv`, `aurora_resources.csv`, `SHA256SUMS.json` | Aurora_Architecture_Database_v1_2_Expanded | `docs/architecture/machine-readable-database/` |
| `AUR-ARCH-006_Aurora_Assembly_Language_Programmers_Guide_v1_0`, `AUR-ARCH-006_Index_Update` | Aurora_Assembly_Guide_Batch | `docs/software/` |
| `AUR-ARCH-005_DMA_Interaction_Addendum_v1_2o`, `aurora_v1_2o_dma_registers.csv` | Aurora_DMA_and_Reduction_Separation_Update_v1_2o | `docs/memory-stream-dma/` |
| `AUR-PM-001_Master_Document_Index_Update_v1_2o` | Aurora_DMA_and_Reduction_Separation_Update_v1_2o | `docs/governance/` |
| `AUR-ARCH-005_Stream_Access_Correction_v1_2r` | Aurora_Implicit_Stream_Arithmetic_Rule_v1_2r | `docs/memory-stream-dma/` |
| `AUR-PM-001_Master_Document_Index_Update_v1_2r` | Aurora_Implicit_Stream_Arithmetic_Rule_v1_2r | `docs/governance/` |
| `Aurora_Architecture_Overview_Phase1_Complete`, `Aurora_Architecture_Specification_Phase1_Complete`, `Aurora_Design_Journal_and_Review_Checklist_Phase1`, `Aurora_Phase1_Validation_and_Freeze_Report` | Aurora_Phase1_Complete_Package | `docs/architecture/` |
| `Aurora_ISA_Reference_Phase1` | Aurora_Phase1_Complete_Package | `docs/isa/` |
| `AUR-ARCH-005_Prefetch_and_8_Word_Loop_Addendum_v1_2s` | Aurora_Prefetch_and_8_Word_Loop_Update_v1_2s | `docs/isa/` |
| `AUR-PM-001_Master_Document_Index_Update_v1_2s` | Aurora_Prefetch_and_8_Word_Loop_Update_v1_2s | `docs/governance/` |
| `AUR-ARCH-001_Architecture_Bible_v1_2` | Aurora_Project_v1_2_Organized_Repository | `docs/architecture/` |
| `AUR-PM-004_Document_Status.csv` | Aurora_Project_v1_2_Organized_Repository | `docs/governance/` |
| `AUR-ARCH-004_ISA_Opcode_Map_v1_2` | Aurora_Project_v1_2_Organized_Repository | `docs/isa/` |
| `AUR-ARCH-006_Memory_Map_v1_2` | Aurora_Project_v1_2_Organized_Repository | `docs/architecture/` |
| `AUR-TOOL-001_Compiler_Toolchain_v1_2` | Aurora_Project_v1_2_Organized_Repository | `docs/software/` |
| `AUR-RTL-001_RTL_Architecture_v1_2` (docx+pdf) | Aurora_Project_v1_2_Organized_Repository | `docs/rtl/` |
| `AUR-SIM-001_Cycle_Accurate_Simulator_v1_2` (docx+pdf) | Aurora_Project_v1_2_Organized_Repository | `docs/simulator/` (new folder) |
| `AUR-VER-001_Validation_and_Benchmark_Suite_v1_2` (docx+pdf) | Aurora_Project_v1_2_Organized_Repository | `docs/verification/` (new folder) |
| `AUR-GUIDE-001_Programmers_Guide_v1_2` | Aurora_Project_v1_2_Organized_Repository | `docs/software/` |
| `AUR-REF-001_Aurora_Quick_Reference_Card` | Aurora_Quick_Reference_Batch | `docs/isa/` |
| `Master_Document_Index_Update_with_Reference` | Aurora_Quick_Reference_Batch | `docs/governance/` |
| `Aurora_Architecture_v1_2_Complete_Instruction_Reference_and_Timing` (docx+pdf), `Aurora_Architecture_v1_2_Instruction_Formats_and_Opcode_Map` | Aurora_v1_2_Instruction_Reference_Package | `docs/isa/` |
| `Aurora_Architecture_v1_2_Pipeline_and_Microarchitecture_Specification`, `aurora_v1_2_microarchitecture.json`, `aurora_v1_2_pipeline_timing.csv` | Aurora_v1_2_Pipeline_and_Microarchitecture_Package | `docs/microarchitecture/` |

`.md` files were copied to the destination folder directly; their original `.docx`/`.pdf` were
copied into a `docx-originals/` subfolder there, matching the convention used for the rest of
the repo's docx-to-md conversion. `extracted/` is left intact as the full original snapshot.
