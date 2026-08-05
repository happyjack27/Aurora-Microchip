/*
 * Aurora scheduler reference implementation.
 * Policy: priority first, then EDF or optional latest-safe-start.
 * This is an executable-design sketch, not production RTOS code.
 *
 * Data structure: one unsorted intrusive ready list per effective_priority
 * (256 levels, matching the uint8_t priority field), plus a 256-bit
 * occupancy bitmap so the highest occupied priority is found with a
 * handful of word tests and a clz, not a scan over every task.
 *
 * Insertion never sorts the bucket - it is O(1): splice onto the list,
 * and only bother comparing against the bucket's cached min_hint. Most
 * arrivals are neither the new bucket minimum nor in the currently
 * running priority level, so most of the time there is nothing further
 * to do. The true minimum of a bucket is only ever reconstructed lazily,
 * on demand, in aurora_sched_peek_best - and only for the one bucket that
 * is actually the highest occupied priority at that moment, since that's
 * the only bucket whose minimum the scheduler ever needs to read.
 *
 * Task lifecycle against this structure:
 *   BLOCKED  - unlinked, not in any bucket.
 *   READY    - linked into head[effective_priority], order unspecified.
 *   RUNNING  - unlinked; held solely as the caller's "current" pointer.
 * A context switch away from `current` must re-enqueue it as READY.
 *
 * aurora_sched_wake() is the entry point for a task becoming READY: it
 * enqueues, then immediately re-runs the same priority/urgency decision
 * used everywhere else, so a newly ready task that outranks `current`
 * (higher priority, or same priority once its deadline rule fires)
 * preempts right away instead of waiting for an unrelated event.
 *
 * Dependency inheritance: a task blocked on another task's resource
 * (aurora_sched_task_block_on) contributes its effective priority/urgency
 * to the owner's via recompute_inherited, propagating up the blocking
 * chain. This is the standard priority/deadline-inheritance protection
 * against priority inversion, described in code/programs/scheduler/README.md.
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

    /* Intrusive linkage into the scheduler's per-priority ready list. */
    struct task *rq_next;
    struct task *rq_prev;
    bool rq_linked;

    /* Dependency/inheritance linkage. blocked_on is the task-owned resource
     * this task is waiting on (NULL if none). waiters_head lists the tasks
     * blocked on *this* task; waiter_next/prev link a task into whichever
     * owner's waiters_head it currently belongs to. */
    struct task *blocked_on;
    struct task *waiters_head;
    struct task *waiter_next;
    struct task *waiter_prev;
} task_t;

#define AURORA_SCHED_PRIORITY_LEVELS 256
#define AURORA_SCHED_BITMAP_WORDS (AURORA_SCHED_PRIORITY_LEVELS / 64)

typedef struct {
    task_t *head[AURORA_SCHED_PRIORITY_LEVELS]; /* unsorted; O(1) insert/remove */
    task_t *min_hint[AURORA_SCHED_PRIORITY_LEVELS]; /* cached true min, or NULL if unknown */
    uint64_t occupied[AURORA_SCHED_BITMAP_WORDS]; /* one bit per nonempty level */
    uint64_t next_ready_sequence;
    scheduler_mode_t mode; /* fixed per scheduler: urgency comparisons depend on it */
} aurora_scheduler_t;

static uint64_t urgency_key(const task_t *t, scheduler_mode_t mode) {
    return mode == SCHED_LATEST_SAFE_START
        ? t->effective_latest_safe_start
        : t->effective_finish_deadline;
}

static bool urgency_less(const task_t *a, const task_t *b, scheduler_mode_t mode) {
    uint64_t ak = urgency_key(a, mode);
    uint64_t bk = urgency_key(b, mode);
    if (ak != bk) return ak < bk;
    return a->ready_sequence < b->ready_sequence;
}

static inline unsigned clz64(uint64_t x) {
#if defined(__GNUC__) || defined(__clang__)
    return (unsigned)__builtin_clzll(x);
#else
    unsigned n = 0;
    while (!(x & (1ULL << 63))) { x <<= 1; ++n; }
    return n;
#endif
}

static inline void bitmap_set(aurora_scheduler_t *s, uint8_t p) {
    s->occupied[p >> 6] |= (1ULL << (p & 63));
}

static inline void bitmap_clear(aurora_scheduler_t *s, uint8_t p) {
    s->occupied[p >> 6] &= ~(1ULL << (p & 63));
}

/* Highest occupied priority level, or -1 if every bucket is empty. */
static int highest_occupied_priority(const aurora_scheduler_t *s) {
    for (int w = AURORA_SCHED_BITMAP_WORDS - 1; w >= 0; --w) {
        uint64_t word = s->occupied[w];
        if (word) {
            unsigned bit_in_word = 63u - clz64(word);
            return w * 64 + (int)bit_in_word;
        }
    }
    return -1;
}

/* Unconditional O(1) splice onto head[t->effective_priority], plus an O(1)
 * min_hint update: replace it if the hint is already known and t beats it,
 * or if the bucket was empty and t is trivially the only candidate. If the
 * hint is currently unknown (NULL, bucket dirty), leave it unknown - t may
 * or may not be the true min and finding out would require the very scan
 * this design avoids on the insert path. */
static void insert_lazy(aurora_scheduler_t *s, task_t *t) {
    uint8_t p = t->effective_priority;
    task_t *old_head = s->head[p];

    t->rq_next = old_head;
    t->rq_prev = NULL;
    if (old_head) old_head->rq_prev = t;
    s->head[p] = t;
    t->rq_linked = true;

    task_t *hint = s->min_hint[p];
    if (old_head == NULL)
        s->min_hint[p] = t;
    else if (hint != NULL && urgency_less(t, hint, s->mode))
        s->min_hint[p] = t;

    bitmap_set(s, p);
}

void aurora_sched_init(aurora_scheduler_t *s, scheduler_mode_t mode) {
    for (int i = 0; i < AURORA_SCHED_PRIORITY_LEVELS; ++i) {
        s->head[i] = NULL;
        s->min_hint[i] = NULL;
    }
    for (int i = 0; i < AURORA_SCHED_BITMAP_WORDS; ++i)
        s->occupied[i] = 0;
    s->next_ready_sequence = 0;
    s->mode = mode;
}

/* Admit a previously blocked/new task as READY. O(1), see insert_lazy. */
void aurora_sched_task_ready(aurora_scheduler_t *s, task_t *t) {
    t->state = TASK_READY;
    t->ready_sequence = s->next_ready_sequence++;
    insert_lazy(s, t);
}

/* Remove a task from its ready bucket (blocking, or leaving to run). O(1):
 * splicing is always O(1), and dropping the cached min just marks it
 * unknown rather than paying to find the next-best candidate now. */
void aurora_sched_dequeue(aurora_scheduler_t *s, task_t *t) {
    if (!t->rq_linked) return;

    uint8_t p = t->effective_priority;
    if (t->rq_prev) t->rq_prev->rq_next = t->rq_next; else s->head[p] = t->rq_next;
    if (t->rq_next) t->rq_next->rq_prev = t->rq_prev;

    t->rq_next = NULL;
    t->rq_prev = NULL;
    t->rq_linked = false;

    if (s->head[p] == NULL) {
        bitmap_clear(s, p);
        s->min_hint[p] = NULL;
    } else if (s->min_hint[p] == t) {
        s->min_hint[p] = NULL;
    }
}

void aurora_sched_task_block(aurora_scheduler_t *s, task_t *t) {
    aurora_sched_dequeue(s, t);
    t->state = TASK_BLOCKED;
}

/* A task's own (non-inherited) latest-safe-start, per the formula in
 * code/programs/scheduler/README.md. */
static uint64_t own_latest_safe_start(const task_t *t) {
    return t->finish_deadline - t->estimated_remaining;
}

/* Recompute owner's effective priority/urgency as the best of its own
 * nominal values and every task directly blocked on it (dependents already
 * reflect their own inheritance, so this naturally covers transitive
 * chains one link at a time), reposition owner in the ready structure if
 * linked, and propagate to whatever owner is itself blocked on. O(w) in
 * owner's direct waiter count; a no-op past the first unchanged link. */
static void recompute_inherited(aurora_scheduler_t *s, task_t *owner) {
    uint8_t priority = owner->base_priority;
    uint64_t deadline = owner->finish_deadline;
    uint64_t lss = own_latest_safe_start(owner);
    uint64_t key = (s->mode == SCHED_LATEST_SAFE_START) ? lss : deadline;
    uint64_t seq = owner->ready_sequence;

    for (task_t *w = owner->waiters_head; w != NULL; w = w->waiter_next) {
        uint64_t wk = urgency_key(w, s->mode);
        bool better = w->effective_priority > priority ||
            (w->effective_priority == priority &&
             (wk < key || (wk == key && w->ready_sequence < seq)));
        if (better) {
            priority = w->effective_priority;
            deadline = w->effective_finish_deadline;
            lss = w->effective_latest_safe_start;
            key = wk;
            seq = w->ready_sequence;
        }
    }

    if (priority == owner->effective_priority &&
        deadline == owner->effective_finish_deadline &&
        lss == owner->effective_latest_safe_start)
        return;

    bool was_linked = owner->rq_linked;
    if (was_linked) aurora_sched_dequeue(s, owner);

    owner->effective_priority = priority;
    owner->effective_finish_deadline = deadline;
    owner->effective_latest_safe_start = lss;

    if (was_linked) insert_lazy(s, owner);

    if (owner->blocked_on != NULL)
        recompute_inherited(s, owner->blocked_on);
}

/* Block t on owner (e.g. a lock/resource owner) instead of an unspecified
 * wait: unlinks t from the ready structure, registers it as one of
 * owner's dependents, and lets owner inherit t's urgency if t is more
 * urgent than owner's own nominal priority/deadline. */
void aurora_sched_task_block_on(aurora_scheduler_t *s, task_t *t, task_t *owner) {
    aurora_sched_dequeue(s, t);
    t->state = TASK_BLOCKED;
    t->blocked_on = owner;

    t->waiter_next = owner->waiters_head;
    t->waiter_prev = NULL;
    if (owner->waiters_head) owner->waiters_head->waiter_prev = t;
    owner->waiters_head = t;

    recompute_inherited(s, owner);
}

/* Release t from whatever task it was blocked on (its dependency is
 * satisfied); owner's inheritance is recomputed without t's contribution.
 * Caller still must admit t as READY separately (aurora_sched_wake). */
void aurora_sched_task_unblock(aurora_scheduler_t *s, task_t *t) {
    task_t *owner = t->blocked_on;
    if (owner == NULL) return;

    if (t->waiter_prev) t->waiter_prev->waiter_next = t->waiter_next;
    else owner->waiters_head = t->waiter_next;
    if (t->waiter_next) t->waiter_next->waiter_prev = t->waiter_prev;

    t->waiter_next = NULL;
    t->waiter_prev = NULL;
    t->blocked_on = NULL;

    recompute_inherited(s, owner);
}

/* Priority-inheritance / base-priority change. Moves the task to the new
 * bucket if it is currently ready; a no-op reposition otherwise. O(1). */
void aurora_sched_reprioritize(aurora_scheduler_t *s, task_t *t, uint8_t new_priority) {
    bool was_linked = t->rq_linked;
    if (was_linked) aurora_sched_dequeue(s, t);
    t->effective_priority = new_priority;
    if (was_linked) insert_lazy(s, t);
}

/* Deadline/latest-safe-start recompute without a priority or bucket change.
 * O(1): urgency_key reads the task's fields directly, so an existing hint
 * only needs invalidating if t itself was the hint (its key may have
 * gotten worse) or updating if t now beats a still-valid hint. */
void aurora_sched_update_urgency(aurora_scheduler_t *s, task_t *t) {
    if (!t->rq_linked) return;

    uint8_t p = t->effective_priority;
    if (s->min_hint[p] == t)
        s->min_hint[p] = NULL;
    else if (s->min_hint[p] != NULL && urgency_less(t, s->min_hint[p], s->mode))
        s->min_hint[p] = t;
}

/* Best READY candidate: highest occupied priority, earliest urgency.
 * O(1) whenever that bucket's min_hint is already known. Otherwise O(k)
 * in that one bucket's size to rebuild the hint - paid lazily, only when
 * the top-priority bucket's cached minimum was actually invalidated.
 *
 * This fallback is a flat linear reduction, not a tree walk, on purpose:
 * on Aurora hardware the equivalent scan over a contiguous urgency-key
 * array is exactly the documented argmin idiom (LOOPR + POPMETA/CMP/
 * CMOV.LT value+index, or HMIN/HMAX where the layout allows it) - a
 * branch-free hardware-loop replay with no pointer-chasing. A tree/heap
 * here would trade that away for an O(log k) bound this workload's
 * expected small per-priority occupancy doesn't need. Getting the actual
 * speedup on real hardware requires the bucket contents to be a
 * contiguous/strided array rather than a pointer-linked list; this
 * portable C sketch keeps the list for unbounded, waste-free capacity. */
task_t *aurora_sched_peek_best(aurora_scheduler_t *s) {
    int p = highest_occupied_priority(s);
    if (p < 0) return NULL;

    task_t *hint = s->min_hint[p];
    if (hint != NULL) return hint;

    task_t *best = NULL;
    for (task_t *c = s->head[p]; c != NULL; c = c->rq_next) {
        if (best == NULL || urgency_less(c, best, s->mode))
            best = c;
    }
    s->min_hint[p] = best;
    return best;
}

task_t *aurora_select_task(aurora_scheduler_t *s, task_t *current, uint64_t now) {
    task_t *best = aurora_sched_peek_best(s);

    if (best == NULL) return current;
    if (current == NULL) return best;

    if (best->effective_priority > current->effective_priority)
        return best;

    if (best->effective_priority < current->effective_priority)
        return current;

    /* Hard same-priority deadline protection. */
    if (s->mode == SCHED_LATEST_SAFE_START &&
        now >= best->effective_latest_safe_start)
        return best;

    /* Stickiness/minimum quantum while the challenger still has margin. */
    if (now < current->min_run_until)
        return current;

    return best;
}

/* Admit t as READY and immediately re-run the priority/urgency decision
 * against the currently running task, instead of leaving t to sit in the
 * ready structure until some unrelated event calls aurora_select_task.
 * Returns the task that should run now: t itself if it outranks current
 * (higher priority, or same priority once the deadline rule fires),
 * otherwise current. */
task_t *aurora_sched_wake(aurora_scheduler_t *s, task_t *t, task_t *current, uint64_t now) {
    aurora_sched_task_ready(s, t);
    return aurora_select_task(s, current, now);
}
