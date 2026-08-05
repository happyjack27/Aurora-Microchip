**Draft 1 - August 2026**

This specification defines the canonical 32-bit physical address layout, required and optional memory regions, privileged system registers, interrupt-controller window, DMA window, TCM profiles, memory attributes, and ordering rules for Aurora v1.2 implementations.

# 1. Architectural Principles

- Aurora uses a unified 32-bit byte-addressed physical address space.

- ITCM, DTCM, SRAM, ROM, MMIO and external memory are separate targets on the internal memory fabric.

- TCM is an implementation-profile feature; the baseline ISA does not require every Aurora device to include it.

- Memory-mapped I/O is strongly ordered, non-cacheable and non-executable.

- The v1.2 baseline does not require L1 or L2 caches.

- ASC ROM and reset services must not depend on external memory.

- DMA and stream engines use the same physical address map as the CPU, subject to protection and arbitration.

# 2. Canonical Physical Address Map

| Start | End | Size | Region | Required | Attributes | Notes |
|----|----|----|----|----|----|----|
| 0x0000_0000 | 0x0000_FFFF | 64 KiB | Boot/ASC ROM | Yes | RX, privileged write-protected | Reset entry, ASC services, recovery, immutable vectors. |
| 0x0001_0000 | 0x0001_FFFF | 64 KiB | ITCM Window | Profile-dependent | RX or RWX by profile | Deterministic instruction memory; absent regions fault or alias implementation memory only if profile says so. |
| 0x0002_0000 | 0x0002_FFFF | 64 KiB | DTCM Window | Profile-dependent | RW, executable optional | Deterministic data memory, DMA-accessible. |
| 0x0003_0000 | 0x0003_FFFF | 64 KiB | Vector/Protected RAM Window | Recommended | RW, privileged configuration | Relocatable active vector table, interrupt stacks, ASC scratch. |
| 0x0010_0000 | 0x0FFF_FFFF | 255 MiB | On-chip SRAM / implementation RAM | Yes, size varies | RWX by MPU policy | Banked SRAM, shared CPU/stream/DMA access. |
| 0x1000_0000 | 0x1FFF_FFFF | 256 MiB | Peripheral MMIO | Yes | Device, strongly ordered, non-executable | Timers, interrupt controller, DMA, serial, GPIO and platform peripherals. |
| 0x2000_0000 | 0x2FFF_FFFF | 256 MiB | External SRAM/PSRAM | Optional | RWX by MPU policy | Ready/acknowledge external-memory controller. |
| 0x3000_0000 | 0x3FFF_FFFF | 256 MiB | External Flash / XIP | Optional | RX, writes through controller | Bootable code and constants. |
| 0x4000_0000 | 0x7FFF_FFFF | 1 GiB | External DRAM / high-capacity memory | Optional | RWX by MPU policy | High-end profile; DMA and stream engines may access. |
| 0x8000_0000 | 0xEFFF_FFFF | 1.75 GiB | Platform / implementation-defined | No | Profile-defined | Accelerators, additional memory windows, SoC integration. |
| 0xF000_0000 | 0xFFFF_FFFF | 256 MiB | System control and debug | Yes | Privileged, device, non-executable | Core-local registers, debug, trace, MPU and implementation ID. |

# 3. Reset, ASC and Interrupt Vectors

After reset, instruction fetch begins in Boot/ASC ROM. The immutable reset vector and recovery entry remain available even if external flash or SRAM is unavailable.

- Reset entry is at 0x0000_0000.

- The immutable ROM vector table occupies the beginning of Boot/ASC ROM.

- VECTOR_BASE selects the active vector table after startup.

- The active vector table should normally reside in ITCM or protected on-chip RAM for deterministic entry.

- Each vector entry contains a 32-bit handler address or an implementation-approved compact branch stub.

- Sixteen architectural priority levels remain fixed-priority in hardware; multiple sources may route to each level.

# 4. TCM and SRAM Profiles

| Profile | TCM | General SRAM | DMA | Intended use |
|----|----|----|----|----|
| Aurora-L | No dedicated TCM required | Banked on-chip SRAM | Simple DMA optional | MCU-oriented control plus occasional DSP |
| Aurora-M | 32-64 KiB ITCM + 32-64 KiB DTCM | Moderate banked SRAM | DMA standard | Target low/mid fixed-point DSP + MCU consolidation |
| Aurora-P | 64-256 KiB ITCM + 64-256 KiB DTCM | Larger SRAM and external DRAM | Multi-channel DMA standard | Sustained streaming and higher throughput |

The fixed ITCM and DTCM windows provide software portability. An implementation advertises actual size through ARCH_VERSION/feature discovery. Access beyond implemented capacity faults rather than silently wrapping. Aurora-L software may place all code and data in general SRAM or flash.

# 5. Memory Attributes and Ordering

- Normal memory may permit instruction fetch, speculative prefetch and burst access according to profile.

- Device/MMIO memory is strongly ordered. Loads and stores do not reorder across MMIO accesses.

- Stores remain architecturally ordered in v1.2.

- The four-entry pairing window may move non-faulting register operations around memory instructions only when precise state is preserved.

- Loads do not pass older stores unless a future profile explicitly adds address-disambiguation support.

- Instruction writes to executable memory require an explicit synchronization operation before execution.

- DMA completion does not imply CPU visibility until required memory barriers and ownership rules are satisfied.

# 6. Core-Local Privileged Registers

| Address | Register | Access | Purpose |
|----|----|----|----|
| 0xF000_0000 | CORE_ID | RO | Implementation and profile identifier |
| 0xF000_0004 | ARCH_VERSION | RO | Architectural version and feature bitmap |
| 0xF000_0010 | PSR | RW privileged fields | Flags, mode, interrupt state, DSP sticky status |
| 0xF000_0014 | VECTOR_BASE | RW privileged | Aligned base address of active vector table |
| 0xF000_0018 | EXC_CAUSE | RO | Current or most recent exception cause |
| 0xF000_001C | EXC_ADDR | RO | Faulting address or restart PC |
| 0xF000_0020 | CYCLE_COUNT | RO | 32-bit free-running coarse monotonic timer |
| 0xF000_0024 | TIMER_COUNT | RW privileged | Single 32-bit coarse countdown timer |
| 0xF000_0028 | TIMER_VECTOR | RW privileged | Interrupt vector pended when timer expires |
| 0xF000_002C | TIMER_CTRL | RW privileged | Enable, hold, pending-clear, tick prescale |
| 0xF000_0030 | STREAM_MASK | RW | One-cycle Q0/Q1 enable mask |
| 0xF000_0060 | DMA_GLOBAL_CTRL | RW privileged | Global DMA enable, fault and arbitration policy |

# 7. Countdown Timer and Monotonic Counter

Aurora exposes one 32-bit free-running coarse counter and one 32-bit OS-scheduled countdown timer. The countdown represents only the next scheduled event; privileged software multiplexes all logical timers in a software priority queue.

- CYCLE_COUNT increments in coarse timer ticks and wraps modulo 2^32.

- TIMER_COUNT decrements in the same or an implementation-advertised coarse tick domain.

- A timer tick may represent 2^P CPU cycles; software or ASC translates requested delays.

- TIMER_VECTOR selects the interrupt vector pended at expiration.

- Expiration-to-pending latency is fixed and documented for each implementation.

- The counter implementation may be ripple, segmented, serial or otherwise low-cost and must remain off the CPU critical path.

- The baseline timer is one-shot. Privileged software reloads it for periodic scheduling.

# 8. Interrupt Controller MMIO

| Address | Register | Access | Purpose |
|----|----|----|----|
| 0x1000_0000 | INT_PENDING | RO/W1C | Pending interrupt-source bitmap or bank selector |
| 0x1000_0004 | INT_ENABLE | RW | Interrupt enable bitmap or bank selector |
| 0x1000_0008 | INT_ACTIVE | RO | Currently active source/vector |
| 0x1000_000C | INT_EOI | WO | End-of-interrupt acknowledgement |
| 0x1000_0010 | INT_THRESHOLD | RW privileged | Current minimum accepted priority |
| 0x1000_0040-0x1000_007C | INT_ROUTE\[n\] | RW privileged | Source-to-vector and subpriority routing |

Routing entries bind a physical source to one of sixteen architectural vectors/priority levels and may also define a deterministic fixed subpriority. EDF or other task scheduling remains software policy.

# 9. DMA MMIO

| Address | Register | Access | Purpose |
|----|----|----|----|
| 0x1001_0000 | DMA_CTRL | RW | Global DMA control |
| 0x1001_0010 + n\*0x40 | DMA_SRC\[n\] | RW | Channel source address |
| 0x1001_0014 + n\*0x40 | DMA_DST\[n\] | RW | Channel destination address |
| 0x1001_0018 + n\*0x40 | DMA_COUNT\[n\] | RW | Transfer count |
| 0x1001_001C + n\*0x40 | DMA_STRIDE\[n\] | RW | Source/destination stride |
| 0x1001_0020 + n\*0x40 | DMA_CFG\[n\] | RW | Width, burst, circular, interrupt, trigger |
| 0x1001_0024 + n\*0x40 | DMA_STATUS\[n\] | RO/W1C | Busy, complete and fault state |

The number of channels is implementation-defined. Channel zero should exist in DSP-oriented profiles. DMA may transfer among TCM, on-chip SRAM, peripherals and external memory. Writes to ITCM require instruction synchronization before execution.

# 10. Stream and TCM Interaction

- Q0 and Q1 use ordinary physical addresses; no separate stream-only address space exists.

- DTCM and banked SRAM are preferred low-latency stream sources and sinks.

- DMA may double-buffer stream regions while the core operates on the alternate buffer.

- Circular addressing may be used in TCM, SRAM or external memory when alignment and region-size rules are met.

- The system fabric arbitrates CPU, stream and DMA requests deterministically according to profile.

# 11. External Memory Interface

External-memory targets use a ready/acknowledge request-response interface. Slow devices may insert wait states without changing ISA semantics.

- Address, read/write data, byte enables, valid, ready and fault/error are the minimum logical signals.

- External SRAM, PSRAM, NOR flash, QSPI/OSPI flash and DRAM controllers may be attached.

- Aurora-L need not implement external DRAM.

- MMIO and external-memory controllers are fabric slaves; general SRAM is not physically placed in front of them.

# 12. Protection and Privilege

- Boot/ASC ROM is executable and privileged-write-protected.

- System-control and debug regions are privileged.

- User mode may access permitted normal memory and selected peripheral windows.

- The MPU defines execute, read, write, device and privilege attributes.

- ASC may emulate optional unaligned accesses or unsupported operations, but normal fast-path protection checks remain hardware.

# 13. Discovery and Portability

Software must discover profile features rather than infer them from product names. CORE_ID and ARCH_VERSION report TCM sizes, SRAM banks, DMA channels, external-memory support, timer prescale and optional features.

- The canonical windows remain fixed even when a region is absent.

- Absent optional regions raise a precise access fault.

- Boot firmware publishes a platform descriptor for board-specific peripherals and clocks.

- The architecture manual defines addresses; the SoC manual defines peripheral-specific blocks inside MMIO.

# 14. Freeze Checklist

PASS - 32-bit unified physical address space defined.

PASS - Boot/ASC ROM and reset vector fixed.

PASS - Optional ITCM/DTCM windows defined.

PASS - On-chip SRAM, MMIO and external-memory windows defined.

PASS - Core-local system-register window defined.

PASS - Single countdown timer and coarse monotonic counter defined.

PASS - Interrupt-controller and DMA base windows defined.

PASS - Ordering, protection and discovery rules defined.
