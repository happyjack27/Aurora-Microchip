**AUR-RTL-002J Commit & Retirement**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Retire up to two instructions per cycle in program order, commit architectural results, preserve precise exceptions, and coordinate flush, branch recovery, and interrupt boundaries.

# 2. Completion Record

| Field            | Meaning                                  |
|------------------|------------------------------------------|
| valid            | Record exists                            |
| age/PC           | Program-order identity                   |
| destination mask | Registers/flags/accumulator/stream state |
| result           | Data or pointer to unit result           |
| fault            | Exception type and address               |
| store_commit     | Pending externally visible store         |
| branch_result    | Resolved target and prediction status    |
| complete         | Execution finished                       |

# 3. Retirement Algorithm

candidate0 = oldest architectural instruction\
candidate1 = next-oldest instruction\
if candidate0.complete and no older fault:\
commit candidate0\
if candidate1.complete and no conflict with commit resources:\
commit candidate1\
if candidate0.fault:\
commit no younger instruction\
save precise PC/PSR\
flush younger work

# 4. Store Rule

- Stores become externally visible only when their instruction reaches retirement.

- MMIO writes are accepted only when they can no longer be squashed.

- Once accepted, a visible store is never replayed after interrupt or branch recovery.

# 5. Interrupt Boundary

- Interrupt recognition occurs after completing the current retirement group.

- Older non-abortable operations must finish or reach restartable state.

- Younger window entries and noncommitted completions are flushed.

- Hardware saves at least PC and PSR before vectoring.

# 6. Assertions

- Architectural retirement order matches program order.

- No younger instruction retires after an older fault.

- At most two instructions retire per cycle.

- Squashed instruction results never update architectural state.

- Every committed store corresponds to exactly one retired store instruction.
