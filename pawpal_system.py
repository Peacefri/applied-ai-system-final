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
        pass

    def markComplete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    healthStatus: str
    energyLevel: int

    def energyLevelUpdate(self) -> None:
        pass

    def setSpecies(self, species: str) -> None:
        pass

    def getNeeds(self) -> List[Task]:
        pass


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


class UserScheduler:
    def __init__(self, ownerName: str, pet: Pet) -> None:
        self.ownerName: str = ownerName
        self.pet: Pet = pet
        self.busyTimeBlocks: List[TimeBlock] = []
        self.freeTimeBlocks: List[TimeBlock] = []
        self.dayPlan: List[Task] = []
        self.planReasoning: str = ""

    def calculateFreeTime(self) -> List[TimeBlock]:
        pass

    def generateDailySchedule(self, taskList: List[Task]) -> List[Task]:
        pass

    def generateReasoning(self) -> str:
        pass


class LoggerBasedHabits:
    def __init__(self) -> None:
        self.completedLogs: List[Log] = []
        self.missedTasks: List[Task] = []
        self.userPatterns: List[Pattern] = []

    def logActivity(self, task: Task, status: str) -> None:
        pass

    def analyzeHabits(self) -> List[Pattern]:
        pass
