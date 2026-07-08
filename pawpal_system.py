from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import List, Tuple


def formatTime(minutes: int) -> str:
    """Render minutes-since-midnight as a 24-hour HH:MM string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


class Priority(Enum):
    High = "High"
    Med = "Med"
    Low = "Low"

    @property
    def rank(self) -> int:
        """Sort rank where a lower number means higher priority."""
        return {Priority.High: 0, Priority.Med: 1, Priority.Low: 2}[self]


class Recurrence(Enum):
    Daily = "daily"
    Weekly = "weekly"

    @property
    def delta(self) -> timedelta:
        """How far ahead the next occurrence lands.

        timedelta does the calendar math correctly — adding it to a date rolls
        over month and year boundaries (e.g. Jan 31 + 1 day -> Feb 1) without
        any manual day-counting.
        """
        return {
            Recurrence.Daily: timedelta(days=1),
            Recurrence.Weekly: timedelta(weeks=1),
        }[self]


@dataclass
class Task:
    taskID: str
    name: str
    priority: Priority
    durationMinutes: int
    # Minutes since midnight for the task's start; None means unscheduled/floating.
    startTime: int | None = None
    # How the task repeats; None means it happens once.
    recurrence: Recurrence | None = None
    # When this occurrence is due. Defaults to today if not supplied.
    dueDate: date = field(default_factory=date.today)
    isCompleted: bool = False

    @property
    def endMinutes(self) -> int | None:
        """Minutes-since-midnight when the task ends, or None if unscheduled."""
        if self.startTime is None:
            return None
        return self.startTime + self.durationMinutes

    def overlaps(self, other: Task) -> bool:
        """Whether this task's time window overlaps another's.

        Uses the standard half-open interval test ``a.start < b.end and
        b.start < a.end``, so tasks that merely touch (one ends exactly when the
        next begins) do NOT count as overlapping.

        Args:
            other: The task to compare against.

        Returns:
            True if both tasks are scheduled (have a ``startTime``) and their
            time windows intersect; False otherwise.
        """
        if self.startTime is None or other.startTime is None:
            return False
        return self.startTime < other.endMinutes and other.startTime < self.endMinutes

    def editTask(self, name: str, priority: Priority, duration: int) -> None:
        """Update the task's name, priority, and duration."""
        self.name = name
        self.priority = priority
        self.durationMinutes = duration

    def nextOccurrence(self) -> Task | None:
        """Build the next occurrence of a recurring task.

        The new due date is this task's ``dueDate`` plus the recurrence delta
        (``+1 day`` for daily, ``+1 week`` for weekly), computed with
        ``timedelta`` so month and year rollovers are handled automatically
        (e.g. Jan 31 -> Feb 1). Name, priority, duration, start time, and
        recurrence all carry over; the copy starts out incomplete.

        Returns:
            A new incomplete ``Task`` for the next date, or ``None`` if this
            task is one-off (``recurrence`` is ``None``).
        """
        if self.recurrence is None:
            return None
        return Task(
            taskID=self.taskID,
            name=self.name,
            priority=self.priority,
            durationMinutes=self.durationMinutes,
            startTime=self.startTime,
            recurrence=self.recurrence,
            dueDate=self.dueDate + self.recurrence.delta,
            isCompleted=False,
        )

    def markComplete(self) -> Task | None:
        """Mark the task completed and return its next occurrence if it recurs.

        Returns:
            The next occurrence built by :meth:`nextOccurrence` for a recurring
            task, or ``None`` for a one-off task. ``Pet.completeTask`` uses this
            return value to append the follow-up to the pet automatically.
        """
        self.isCompleted = True
        return self.nextOccurrence()


@dataclass
class Pet:
    name: str
    species: str
    healthStatus: str
    energyLevel: int
    tasks: List[Task] = field(default_factory=list)

    def energyLevelUpdate(self, newEnergyLevel: int | None = None) -> None:
        """Adjust the pet's energy level, or reduce it by default if no value is provided."""
        if newEnergyLevel is None:
            self.energyLevel = max(0, self.energyLevel - 5)
        else:
            self.energyLevel = newEnergyLevel

    def setSpecies(self, species: str) -> None:
        """Set the pet's species."""
        self.species = species

    def addTask(self, task: Task) -> None:
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def completeTask(self, task: Task) -> Task | None:
        """Mark one of the pet's tasks complete, auto-scheduling its next occurrence.

        This is the "automatic rollover" entry point: it delegates the date math
        to :meth:`Task.markComplete` and owns the list mutation, so a recurring
        task never leaves the pet without a future occurrence on the books.

        Args:
            task: A task already belonging to this pet, to mark complete.

        Returns:
            The next occurrence (also appended to ``self.tasks``) if ``task``
            recurs, or ``None`` if it was one-off.
        """
        nextTask = task.markComplete()
        if nextTask is not None:
            self.addTask(nextTask)
        return nextTask

    def getNeeds(self) -> List[Task]:
        """Return all incomplete tasks for the pet."""
        return [task for task in self.tasks if not task.isCompleted]


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection."""
        self.pets.append(pet)

    def getAllTasks(self) -> List[Task]:
        """Collect all incomplete tasks across the owner's pets."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.getNeeds())
        return all_tasks


@dataclass
class TimeBlock:
    startTime: str
    endTime: str
    description: str


@dataclass
class Log:
    task: Task
    status: str
    timestamp: str


@dataclass
class Pattern:
    description: str
    frequency: int


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler with an owner and empty planning state."""
        self.owner: Owner = owner
        self.busyTimeBlocks: List[TimeBlock] = []
        self.freeTimeBlocks: List[TimeBlock] = []
        self.dayPlan: List[Task] = []
        self.planReasoning: str = ""

    def retrieveTasks(self) -> List[Task]:
        """Retrieve the owner's incomplete tasks."""
        return self.owner.getAllTasks()

    def calculateFreeTime(self) -> List[TimeBlock]:
        """Return the current free time blocks."""
        return self.freeTimeBlocks

    def generateDailySchedule(self, taskList: List[Task]) -> List[Task]:
        """Order tasks into a daily plan and cache it on ``self.dayPlan``.

        The sort key is a tuple applied left-to-right, so each field only breaks
        ties left unresolved by the fields before it:

        1. ``startTime is None`` — False (scheduled) sorts before True, so timed
           tasks lead and floating tasks trail.
        2. ``startTime or 0`` — chronological order among timed tasks (floating
           tasks all collapse to 0 here, which is harmless since field 1 already
           grouped them last).
        3. ``priority.rank`` — High(0) < Med(1) < Low(2) for the floating tasks.
        4. ``durationMinutes`` — shortest first as the final tiebreaker.

        Args:
            taskList: The tasks to order (typically the owner's incomplete tasks).

        Returns:
            The same tasks in plan order. Runs in O(n log n) for the sort.
        """
        self.dayPlan = sorted(
            taskList,
            key=lambda task: (
                task.startTime is None,
                task.startTime or 0,
                task.priority.rank,
                task.durationMinutes,
            ),
        )
        return self.dayPlan

    def filterTasks(
        self, petName: str | None = None, completed: bool | None = None
    ) -> List[Task]:
        """Return tasks across the owner's pets, optionally narrowed by filters.

        Both filters are optional and compose. A filter left as ``None`` is
        simply not applied, so passing neither returns every task. The pet-name
        filter is checked once per pet (skipping all of a non-matching pet's
        tasks at once), and the completion filter once per task.

        Args:
            petName: If given, keep only tasks belonging to the pet with this
                exact name.
            completed: If given, keep only tasks whose ``isCompleted`` equals
                this value — ``True`` for done tasks, ``False`` for open ones.

        Returns:
            The matching tasks in pet-then-insertion order. Runs in O(P + T)
            where P is the number of pets and T the total number of tasks.
        """
        results: List[Task] = []
        for pet in self.owner.pets:
            if petName is not None and pet.name != petName:
                continue
            for task in pet.tasks:
                if completed is not None and task.isCompleted != completed:
                    continue
                results.append(task)
        return results

    def sort_by_time(self, taskList: List[Task]) -> List[Task]:
        """Return the tasks ordered by start time, with unscheduled tasks last.

        The ``key`` lambda hands ``sorted`` a single value per task to compare.
        The tuple's leading ``task.startTime is None`` term is the trick that
        keeps floating tasks (no time) at the end: False sorts before True, and
        it also avoids comparing an ``int`` against ``None`` (a TypeError in
        Python 3). ``task.startTime or 0`` then orders the timed tasks; floating
        tasks fall back to 0 but stay last because of the first term.

        Args:
            taskList: The tasks to order.

        Returns:
            A new list sorted chronologically, unscheduled tasks trailing. Runs
            in O(n log n).
        """
        return sorted(
            taskList,
            key=lambda task: (task.startTime is None, task.startTime or 0),
        )

    def detectConflicts(self, taskList: List[Task]) -> List[Tuple[Task, Task]]:
        """Return every pair of scheduled tasks whose time windows overlap.

        Unscheduled tasks (no ``startTime``) can't conflict and are dropped
        first. The remaining tasks are sorted by start time so the inner loop
        can ``break`` the moment it meets a task that starts at or after the
        current task's end: because the list is sorted, every task after that
        one starts even later and therefore can't overlap either.

        Two windows overlap when ``a.start < b.end and b.start < a.end``. Note
        this compares clock time only, not ``dueDate`` — see the tradeoff noted
        in ``reflection.md``.

        Args:
            taskList: The tasks to check for overlaps.

        Returns:
            A list of ``(earlier, later)`` task pairs that overlap, ordered by
            start time. Cost is O(n log n) for the sort plus O(k) for the k
            overlapping pairs actually found — effectively linear when overlaps
            are rare, quadratic only if nearly everything overlaps.
        """
        timed = sorted(
            (task for task in taskList if task.startTime is not None),
            key=lambda task: task.startTime,
        )
        conflicts: List[Tuple[Task, Task]] = []
        for index, task in enumerate(timed):
            for other in timed[index + 1:]:
                if other.startTime >= task.endMinutes:
                    break  # sorted by start, so no later task can overlap either
                conflicts.append((task, other))
        return conflicts

    def generateReasoning(self) -> str:
        """Describe the scheduled plan using the current day plan."""
        if not self.dayPlan:
            return "No tasks scheduled yet."
        parts = []
        for task in self.dayPlan:
            when = formatTime(task.startTime) if task.startTime is not None else "unscheduled"
            parts.append(f"{task.name} ({when})")
        return "Planned order: " + ", ".join(parts)


class UserScheduler(Scheduler):
    def __init__(self, ownerName: str, pet: Pet) -> None:
        """Create a scheduler for a single owner and pet."""
        owner = Owner(name=ownerName)
        owner.addPet(pet)
        super().__init__(owner=owner)
        self.ownerName: str = ownerName
        self.pet: Pet = pet


class LoggerBasedHabits:
    def __init__(self) -> None:
        """Initialize the logger with empty activity and pattern tracking."""
        self.completedLogs: List[Log] = []
        self.missedTasks: List[Task] = []
        self.userPatterns: List[Pattern] = []

    def logActivity(self, task: Task, status: str) -> None:
        """Record an activity log entry and track missed tasks when applicable."""
        self.completedLogs.append(Log(task=task, status=status, timestamp="now"))
        if status == "missed":
            self.missedTasks.append(task)

    def analyzeHabits(self) -> List[Pattern]:
        """Return a simple habit pattern based on logged activity."""
        if not self.completedLogs:
            return []
        return [Pattern(description="Tracked activity", frequency=len(self.completedLogs))]
