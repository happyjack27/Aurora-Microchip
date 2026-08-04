Canonical cross-module signal database.

| Signal          | Source       | Destination     | Width  | Protocol    |
|-----------------|--------------|-----------------|--------|-------------|
| fetch_bundle    | Fetch        | Decode          | struct | ready/valid |
| issue_bundle0/1 | Issue Window | Execution Lanes | struct | ready/valid |
| wb_bundle       | Execution    | Regfile         | struct | completion  |
| mem_req         | LSU          | Memory Fabric   | struct | req/rsp     |
| stream_req      | Q0/Q1        | Memory Fabric   | struct | req/rsp     |
| commit_rec      | Execution    | Retirement      | struct | completion  |
| irq_pending     | Interrupt    | Retirement      | 16     | level       |
