**AUR-RTL-002A Fetch & Branch Predictor**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Fetch up to two adjacent 16-bit words per cycle, assemble extension-word sequences, predict simple control flow, and redirect fetch on branch, exception, or interrupt recovery.

# 2. Ports

| Signal             | Dir | Width   | Meaning                             |
|--------------------|-----|---------|-------------------------------------|
| clk_i              | in  | 1       | Core clock                          |
| rst_i              | in  | 1       | Synchronous reset                   |
| redirect_valid_i   | in  | 1       | Branch/exception/interrupt redirect |
| redirect_pc_i      | in  | 32      | Redirect target                     |
| fetch_addr_o       | out | 32      | Instruction memory address          |
| fetch_req_o        | out | 1       | Fetch request valid                 |
| fetch_ready_i      | in  | 1       | Instruction memory accepts request  |
| fetch_data_i       | in  | 32      | Two adjacent 16-bit words           |
| fetch_data_valid_i | in  | 1       | Returned fetch data valid           |
| fetch_fault_i      | in  | 1       | Instruction access fault            |
| decode_ready_i     | in  | 1       | Decode window can accept words      |
| word0_o/word1_o    | out | 16 each | Fetched words                       |
| pc0_o/pc1_o        | out | 32 each | Associated PCs                      |
| valid_o            | out | 2       | Word valid bits                     |

# 3. Predictor

- Backward conditional branches are predicted taken.

- Forward conditional branches are predicted not taken.

- Unconditional direct branches are predicted taken when target formation is available.

- No branch target buffer is required in the v1.2 baseline.

- Prediction state is combinational from decoded direction and immediate sign; no history table is required.

# 4. Prefetch Buffer

- Single predicted path only.

- Minimum capacity: four 16-bit words beyond the current decode demand.

- Redirect invalidates all prefetched words younger than redirect point.

- Extension words remain associated with their base PC and are never independently retired.

# 5. Fetch State Machine

IDLE:\
if decode_ready: issue fetch at fetch_pc\
WAIT:\
if redirect: cancel/kill response if possible; set fetch_pc = redirect_pc\
elif response_valid:\
enqueue returned words\
fetch_pc += number_of_valid_words \* 2\
DELIVER:\
present up to two adjacent words to decode

# 6. Assertions

- PCs increase by two bytes for adjacent 16-bit words.

- Redirected wrong-path words never reach decode as valid.

- Extension words retain original fetch order.

- Instruction faults report the address of the failing fetch.

- At most two words are delivered per cycle.
