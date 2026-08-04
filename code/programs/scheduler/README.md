# Aurora Scheduler Design

## Scheduling key

The scheduler considers only READY tasks.

1. Highest effective priority, descending.
2. Within that priority, earliest urgency timestamp, ascending.
3. Current-task stickiness while no peer is at its latest-safe-start.
4. Stable queue order / task ID.

The initial urgency timestamp is the absolute finish deadline (priority + EDF).

Optional expansion:

    latest_safe_start = finish_deadline - estimated_remaining_execution

At a scheduling instant, ordering by earliest latest-safe-start is equivalent to least laxity.

## Mandatory preemption

A higher effective priority task preempts immediately.

Within the same effective priority, a READY task preempts immediately when:

    now >= effective_latest_safe_start

This overrides stickiness, hysteresis, and the minimum execution quantum.

## Dependency inheritance

A task that owns or produces a resource required by blocked tasks inherits a lexicographic urgency key:

1. Highest effective priority among blocked dependents.
2. Earliest deadline/latest-safe-start among blocked dependents at that priority.

Inheritance propagates through dependency chains and is removed when the dependency disappears.

## Stickiness and minimum run quantum

Before a peer reaches its latest-safe-start, the current task may continue to reduce context-switch churn. Reevaluate on:

- task creation, termination, block, wake, yield, or fault;
- dependency changes;
- deadline or execution-estimate updates;
- minimum-quantum expiration;
- scheduler timer events.

Interrupts remain separate and preempt immediately according to hardware interrupt priority.
