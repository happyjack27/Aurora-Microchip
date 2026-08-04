# Aurora Scheduler Design Snapshot

Current scheduler:\
- Interrupt priority first.\
- Highest effective task priority.\
- EDF within priority initially.\
- Planned evolution to latest-safe-start = finish deadline - estimated remaining execution.\
- Sticky scheduling + minimum execution quantum.\
- Immediate preemption when same-priority task reaches latest-safe-start.\
- Dependency inheritance: highest blocked priority, then earliest urgency within that priority.\
- Scheduler only considers READY tasks.
