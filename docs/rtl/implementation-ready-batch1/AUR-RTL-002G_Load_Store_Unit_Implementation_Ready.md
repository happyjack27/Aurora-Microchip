**AUR-RTL-002G Load/Store Unit**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Generate effective addresses, enforce alignment and protection, launch ordered memory transactions, and return scalar or paired data through the scoreboard/completion system.

# 2. Ports

| Signal                 | Dir | Width            | Meaning                    |
|------------------------|-----|------------------|----------------------------|
| req_valid_i            | in  | 1                | Memory request             |
| req_load_i/req_store_i | in  | 1 each           | Operation type             |
| base_i                 | in  | 32               | Base address               |
| offset_i               | in  | signed immediate | Offset                     |
| store_data_i           | in  | 64 max           | Store data or pair         |
| width_i                | in  | 2                | 8/16/32/64                 |
| device_i               | in  | 1                | MMIO/strongly ordered      |
| mem_valid_o            | out | 1                | Fabric request             |
| mem_ready_i            | in  | 1                | Fabric response            |
| mem_addr_o             | out | 32               | Effective address          |
| mem_wdata_o            | out | 64 max           | Write data                 |
| mem_rdata_i            | in  | 64 max           | Read data                  |
| fault_o                | out | enum             | Alignment/access/bus fault |
| complete_o             | out | bundle           | Age-tagged completion      |

# 3. Address Generation

effective_address = (base + sign_extend(offset)) mod 2^32

- SP/PC sources are ordinary 32-bit addresses.

- Paired-64 data width does not create a 64-bit address space.

- Pair loads/stores require 8-byte alignment in portable ABI code.

- Unaligned support is profile-defined; baseline may trap to ASC.

# 4. Memory Classes

| Class | Ordering | Speculation |
|----|----|----|
| TCM/SRAM normal | Stores ordered; loads conservative | No load-over-store disambiguation baseline |
| External normal | Same architectural order; may wait | Outstanding request scoreboarded |
| MMIO/device | Strongly ordered | Never speculative |
| Instruction synchronization | Explicit barrier after executable writes | Required |

# 5. Bank Selection

- General SRAM interleaves at native 16-bit word granularity.

- LSU presents address and byte strobes; fabric selects bank.

- Bank conflicts stall or serialize deterministically.

- DMA and streams arbitrate through the fabric; CPU retirement-critical traffic has bounded service.

# 6. Store Commit Rule

A store may not become externally visible until it reaches its architectural retirement point. MMIO writes are never canceled after acceptance.

# 7. Assertions

- No duplicate store after interrupt or branch recovery.

- MMIO order matches program order.

- Pair load becomes visible atomically.

- Faulting load/store produces no partial architectural destination update.

- Byte strobes match width and address.
