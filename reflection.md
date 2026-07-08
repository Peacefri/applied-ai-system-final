# PawPal+ Project Reflection

## 1. System Design
Three core actions: delivering a daily schedule and why that daily schedule works. Whenever you have free time , it is the best time for a pet's high priority needs. Log the habits and learn from those habits. 
Object 1 : Pet (attributes): Name, Type of pet,current health status and energy level
(methods): energyLevelupdate(), setSpecies(input) ,getNeeds()

Object 2 : UserScheduler (attributes) : OwnerName, PetID, BusyTimeBlocks, FreeTimeBlocks, DayPlan, PlanReasoning. 
(methods): calculateFreeTime() ,generateDailySchedule(taskList) , generateReasoning() 

Object 3 : LoggerBasedHabits(attributes) : CompletedLogs, MissedTasks, UserPatterns 
(methods): logActivity(task, status) ,analyzeHabits() 
Object 4 : Task (attributes): TaskID, Name, Priority (High/Med/Low), Duration (Minutes), IsCompleted. 
(methods): editTask(name, priority, duration) ,markComplete() 


**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
Initial UML design used four core classes: Pet, UserScheduler, LoggerBasedHabits, and Task.

Pet holds pet state like name, species, health status, and energy, and provides methods to update energy, set species, and derive care needs.

UserScheduler manages owner scheduling data, including busy/free time blocks, a daily plan, and reasoning logic for generating schedules.

LoggerBasedHabits tracks completed logs, missed tasks, and user patterns, with methods to log activities and analyze habits.

Task represents scheduled actions with id, name, priority, duration, and completion status, plus methods to edit the task and mark it complete

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler weighs four constraints, applied in a strict order by
`generateDailySchedule` (the sort key is `(startTime is None, startTime,
priority.rank, durationMinutes)`):

1. **Completion status** — before anything else, `retrieveTasks()` pulls only
   *incomplete* tasks (via `Pet.getNeeds`). A finished task is never planned, so
   the day plan only ever contains work that still needs doing.
2. **Fixed time** — tasks with a `startTime` are placed first, in chronological
   order. A real appointment (Feed at 08:00, Vet at 14:00) has a fixed slot the
   owner can't move, so honoring the clock comes before any preference of ours.
3. **Priority** — among tasks *without* a fixed time, High beats Med beats Low
   (encoded as `Priority.rank`). This decides what a busy owner should do first
   when the clock doesn't dictate it.
4. **Duration** — the final tiebreaker: between two equal-priority floating tasks,
   the shorter one goes first, so quick wins get knocked out early.

**How I decided the ordering:** the guiding question was "which constraints can
the owner *not* negotiate?" A scheduled appointment is the hardest constraint —
missing it has real consequences — so time wins. Priority is our judgment call
about importance, so it comes next. Duration is a pure convenience heuristic, so
it breaks ties last. Completion status sits above all of them because scheduling a
done task is simply meaningless. Conflict detection and recurrence are handled as
*separate* concerns (`detectConflicts`, `nextOccurrence`) rather than folded into
the sort, keeping each piece of logic focused and testable.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

**Tradeoff: conflict detection compares clock time only, not the calendar date.**

`Scheduler.detectConflicts()` decides whether two tasks collide using only their
`startTime` (minutes since midnight) and `durationMinutes` — it never looks at
each task's `dueDate`. Two tasks overlap when `a.start < b.end and b.start < a.end`.

This means the scheduler treats every task as if it happens on the *same day*.
It correctly catches real overlaps within one day (e.g. Feed 08:00–08:10 vs.
Morning walk 08:05–08:35), which is better than only checking for *exact* start-time
matches — a task that starts partway through another is still flagged. But it has a
known blind spot: a recurring task's next occurrence (due tomorrow) and today's task
at the same clock time would be reported as "conflicting" even though they fall on
different dates.

**Why this is reasonable here:** PawPal+ builds a plan for a *single day* at a time,
and `generateDailySchedule` is meant to answer "what does today look like?" Within
that one-day frame, ignoring the date is not just acceptable — it keeps the overlap
check to simple integer math (fast and easy to reason about) instead of full
`datetime` comparisons. The cost is only felt if we later mix multiple days' tasks
into one conflict check, at which point the fix is small and localized: add a
`task.dueDate` equality guard (or compare full datetimes) before testing the minute
windows. Choosing the simpler same-day model now, with a clear upgrade path, fit the
scope of a daily pet-care planner.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
