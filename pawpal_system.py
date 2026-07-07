from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Priority(Enum):
    High = "High"
    Med = "Med"
    Low = "Low"


@dataclass
class Task:
    taskID: str
    name: str
    priority: Priority
    durationMinutes: int
    isCompleted: bool = False

    def editTask(self, name: str, priority: Priority, duration: int) -> None:
        """Update the task's name, priority, and duration."""
        self.name = name
        self.priority = priority
        self.durationMinutes = duration

    def markComplete(self) -> None:
        """Mark the task as completed."""
        self.isCompleted = True


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
        """Sort tasks into a daily plan by priority and duration."""
        self.dayPlan = sorted(
            taskList,
            key=lambda task: (task.priority.value != "High", task.priority.value != "Med", task.durationMinutes),
        )
        return self.dayPlan

    def generateReasoning(self) -> str:
        """Describe the scheduled plan using the current day plan."""
        if not self.dayPlan:
            return "No tasks scheduled yet."
        task_names = ", ".join(task.name for task in self.dayPlan)
        return f"Scheduled tasks in priority order: {task_names}"


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
