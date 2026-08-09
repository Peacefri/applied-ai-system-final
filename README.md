# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
## Sample Output for mian.py 
Today's Schedule
================
- Feed breakfast (10 min) [High]
- Play session (20 min) [Med]
- Morning walk (30 min) [High]

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

PawPal+ goes beyond a flat task list with four pieces of scheduling logic. Each
is implemented in `pawpal_system.py` and named below.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.generateDailySchedule()` | Chronological order; unscheduled tasks trail, then priority then shortest duration |
| Filtering | `Scheduler.filterTasks(petName=..., completed=...)` | Compose filters by pet name and/or completion status |
| Conflict handling | `Scheduler.detectConflicts()`, `Task.overlaps()` | Detects overlapping time windows (not just exact-time clashes) |
| Recurring tasks | `Task.markComplete()`, `Task.nextOccurrence()`, `Pet.completeTask()` | Completing a daily/weekly task auto-creates the next occurrence |

### Sorting behavior — `Scheduler.sort_by_time()`

Orders tasks chronologically by `startTime` (minutes since midnight). Unscheduled
("floating") tasks are pushed to the end rather than crashing on a `None`
comparison, using a tuple sort key `(startTime is None, startTime or 0)`.
`Scheduler.generateDailySchedule()` builds on the same idea with a richer key:
timed tasks first, then **priority** (High → Med → Low via `Priority.rank`), then
**shortest duration** as the final tiebreaker.

### Filtering behavior — `Scheduler.filterTasks()`

Returns tasks across all of the owner's pets, narrowed by two optional, composable
filters:

- `filterTasks(petName="Biscuit")` — only that pet's tasks
- `filterTasks(completed=True)` — only completed tasks (`False` for open ones)
- `filterTasks(petName="Biscuit", completed=False)` — both at once
- `filterTasks()` — everything

A filter left as `None` is simply not applied.

### Conflict detection — `Scheduler.detectConflicts()`

Returns every pair of scheduled tasks whose time windows overlap, using the
half-open interval test `a.start < b.end and b.start < a.end` (also exposed as
`Task.overlaps()`). Tasks are sorted by start time so the inner scan can stop
early once a later task starts after the current one ends — effectively linear
when overlaps are rare. Back-to-back tasks (one ends exactly when the next
begins) correctly do **not** conflict.

### Recurring task logic — `Task.markComplete()` / `Pet.completeTask()`

Tasks carry an optional `recurrence` (`Recurrence.Daily` or `Recurrence.Weekly`)
and a `dueDate`. When a recurring task is completed, `Task.nextOccurrence()`
builds a fresh, incomplete copy due `dueDate + recurrence.delta` — `+1 day` for
daily, `+1 week` for weekly — computed with `datetime.timedelta` so month/year
rollovers (e.g. Jan 31 → Feb 1) are handled automatically. `Pet.completeTask()`
ties it together: it marks the task done and auto-appends the next occurrence to
the pet's task list.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
