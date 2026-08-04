Status: LOCKED\
Architecture baseline: Aurora v1.2e\
Date: August 2, 2026

# Decision

- Aurora has exactly two architectural privilege modes: User and Supervisor.

- The current privilege level is represented by one PSR privilege bit.

- Reset, interrupt entry, exception entry, and ASC/system-service entry enter Supervisor mode.

- IRET remains the canonical interrupt/exception return instruction and atomically restores the saved PC, PSR, previous privilege mode, and previous interrupt-enable state.

- WFI (wait for interrupt), WFE (wait for event), and HALT are architectural instructions.

- WFI waits until an enabled interrupt becomes serviceable. It may be used from User mode unless disabled by a supervisor control bit.

- WFE waits for an implementation-defined architectural event, including interrupt, DMA/peripheral event, or explicit event signal. It may be used from User mode unless disabled by a supervisor control bit.

- HALT is privileged and stops instruction execution until reset, debug resume, or an implementation-defined wake condition permitted by system control.

- Aurora adds privileged CTXSAVE and CTXRESTORE instructions.

- CTXSAVE/CTXRESTORE launch a small context sequencer that reuses the stream-style transfer path and the local DTCM/SRAM interface without consuming or overwriting architectural Q0/Q1 state.

- The context transfer supports masks for volatile GPRs, full GPR state, PC/PSR, A0/A1, Q0/Q1 configuration, and optionally Q0/Q1 staging contents.

- Context transfer begins at a precise retirement boundary, blocks normal issue, and is non-interruptible until its atomic completion boundary.

- Maskable interrupts that arrive during a context transfer remain pending and are serviced afterward; they are not lost.

- Reset and a true NMI/reset-class watchdog may abort the sequence according to implementation policy.

- CTXRESTORE restores PSR and resume PC last, so partially restored state is never architecturally visible.

- Aurora does not adopt four x86-style privilege rings and does not require paging or page faults in the baseline architecture.

# Rationale

Two privilege levels cover the realistic embedded RTOS split between kernel/handler code and application code. The wait instructions improve power efficiency and event-driven firmware. A thin context sequencer provides nearly the bandwidth of a dedicated context engine while preserving Aurora's shared-hardware philosophy and avoiding the self-clobbering problem that would occur if Q0/Q1 were used directly to save their own state.

# Context Transfer Timing Model

The transfer engine targets up to two 32-bit architectural words per cycle when the register-file ports and local memory banks permit. A basic 16-word GPR/PC/PSR context therefore has an approximate lower bound of eight transfer cycles plus launch and completion overhead. Exact timing is implementation-defined but bounded and reported by the implementation profile.

# Rejected Alternatives

- Four privilege rings: rejected as complexity without useful embedded software demand.

- Using Q0/Q1 directly for every context switch: rejected because an interrupted task may already own live stream state.

- A wholly separate high-bandwidth context engine: rejected as unnecessary duplication.

- Automatically turning R0-R4 into a stack window: rejected because it complicates the ABI, forwarding, and scoreboarding.
