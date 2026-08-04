**AUR-RTL-002K Interrupt & Timer Unit**

*Implementation-Ready RTL Blueprint v1.2*

# 1. Purpose

Implement sixteen fixed-priority interrupt levels, source routing, pending/active state, precise retirement-boundary recognition, one coarse countdown timer, and one coarse free-running counter.

# 2. Interrupt State

| Field       | Meaning                                |
|-------------|----------------------------------------|
| pending     | Pending source/vector bits             |
| enable      | Source enable mask                     |
| route       | Source to vector/priority mapping      |
| threshold   | Current minimum accepted priority      |
| active      | Current nesting stack or active vector |
| vector_base | Base of active vector table            |

# 3. Priority Rule

- Lower vector number denotes higher architectural priority.

- Equal-priority sources use deterministic fixed subpriority or configured round-robin if profile permits.

- Task scheduling policy such as EDF remains software.

- Nested interrupts are allowed only when new priority exceeds current threshold.

# 4. Timer State

| Register     | Meaning                         |
|--------------|---------------------------------|
| CYCLE_COUNT  | 32-bit coarse monotonic counter |
| TIMER_COUNT  | 32-bit one-shot countdown       |
| TIMER_VECTOR | Vector to pend on expiration    |
| TIMER_CTRL   | Enable, hold, clear, prescale   |

# 5. Timer Semantics

- Timer tick may represent 2^P core cycles.

- Countdown decrements on timer ticks, not necessarily every core cycle.

- Expiration posts the programmed vector with fixed documented latency.

- Software multiplexes all OS deadlines onto the one countdown timer.

- Counter implementation may be ripple/segmented/serial because it is off the critical path.

# 6. Assertions

- Highest-priority enabled pending vector is selected.

- Timer expiration posts exactly one pending event per load.

- Disabled timer never decrements or fires.

- Interrupt entry only begins at a legal retirement boundary.

- Vector-base alignment is enforced.
