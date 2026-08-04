/*
 * Aurora scheduler reference pseudocode.
 * Policy: priority first, then EDF or optional latest-safe-start.
 * This is an executable-design sketch, not production RTOS code.
 */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef enum {
    TASK_BLOCKED = 0,
    TASK_READY   = 1,
    TASK_RUNNING = 2
} task_state_t;

typedef enum {
    SCHED_EDF = 0,
    SCHED_LATEST_SAFE_START = 1
} scheduler_mode_t;

typedef struct task {
    uint32_t id;
    task_state_t state;

    uint8_t base_priority;
    uint8_t effective_priority;

    uint64_t finish_deadline;
    uint64_t estimated_remaining;
    uint64_t effective_finish_deadline;
    uint64_t effective_latest_safe_start;

    uint64_t min_run_until;
    uint64_t ready_sequence;
} task_t;

static uint64_t urgency_key(const task_t *t, scheduler_mode_t mode) {
    return mode == SCHED_LATEST_SAFE_START
        ? t->effective_latest_safe_start
        : t->effective_finish_deadline;
}

static bool lexically_better(const task_t *a, const task_t *b,
                             scheduler_mode_t mode) {
    if (b == NULL) return true;
    if (a->effective_priority != b->effective_priority)
        return a->effective_priority > b->effective_priority;

    uint64_t au = urgency_key(a, mode);
    uint64_t bu = urgency_key(b, mode);
    if (au != bu) return au < bu;

    return a->ready_sequence < b->ready_sequence;
}

task_t *aurora_select_task(task_t *tasks, size_t count,
                           task_t *current, uint64_t now,
                           scheduler_mode_t mode) {
    task_t *best = NULL;

    for (size_t i = 0; i < count; ++i) {
        task_t *t = &tasks[i];
        if (t->state != TASK_READY && t != current)
            continue;
        if (lexically_better(t, best, mode))
            best = t;
    }

    if (best == NULL || current == NULL)
        return best;

    if (best->effective_priority > current->effective_priority)
        return best;

    if (best->effective_priority < current->effective_priority)
        return current;

    /* Hard same-priority deadline protection. */
    if (mode == SCHED_LATEST_SAFE_START &&
        now >= best->effective_latest_safe_start)
        return best;

    /* Stickiness/minimum quantum while the challenger still has margin. */
    if (now < current->min_run_until)
        return current;

    return best;
}
