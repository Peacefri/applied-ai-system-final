from datetime import date, timedelta

from pawpal_system import Owner, Pet, Priority, Recurrence, Scheduler, Task


def test_mark_complete_changes_task_status() -> None:
    task = Task(taskID="t1", name="Feed", priority=Priority.High, durationMinutes=10)

    task.markComplete()

    assert task.isCompleted is True


def test_task_can_be_edited_and_marked_complete() -> None:
    task = Task(taskID="t1", name="Walk", priority=Priority.High, durationMinutes=20)

    task.editTask(name="Morning walk", priority=Priority.Med, duration=30)

    assert task.name == "Morning walk"
    assert task.priority == Priority.Med
    assert task.durationMinutes == 30

    task.markComplete()

    assert task.isCompleted is True


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="cat", healthStatus="healthy", energyLevel=80)

    initial_count = len(pet.tasks)
    pet.addTask(Task(taskID="t2", name="Play", priority=Priority.Med, durationMinutes=15))

    assert len(pet.tasks) == initial_count + 1


def test_scheduler_retrieves_tasks_from_all_pets() -> None:
    owner = Owner(name="Jordan")
    pet_one = Pet(name="Mochi", species="cat", healthStatus="healthy", energyLevel=80)
    pet_two = Pet(name="Biscuit", species="dog", healthStatus="healthy", energyLevel=90)

    pet_one.addTask(Task(taskID="t1", name="Feed", priority=Priority.High, durationMinutes=10))
    pet_two.addTask(Task(taskID="t2", name="Walk", priority=Priority.Med, durationMinutes=25))

    owner.addPet(pet_one)
    owner.addPet(pet_two)

    scheduler = Scheduler(owner=owner)
    tasks = scheduler.retrieveTasks()

    assert [task.name for task in tasks] == ["Feed", "Walk"]


def test_schedule_orders_timed_tasks_chronologically() -> None:
    owner = Owner(name="Jordan")
    scheduler = Scheduler(owner=owner)

    noon = Task(taskID="t1", name="Lunch", priority=Priority.Low, durationMinutes=20, startTime=720)
    morning = Task(taskID="t2", name="Walk", priority=Priority.Med, durationMinutes=30, startTime=480)

    plan = scheduler.generateDailySchedule([noon, morning])

    assert [task.name for task in plan] == ["Walk", "Lunch"]


def test_schedule_places_unscheduled_tasks_after_timed_by_priority() -> None:
    owner = Owner(name="Jordan")
    scheduler = Scheduler(owner=owner)

    timed = Task(taskID="t1", name="Walk", priority=Priority.Low, durationMinutes=30, startTime=540)
    floating_low = Task(taskID="t2", name="Brush", priority=Priority.Low, durationMinutes=10)
    floating_high = Task(taskID="t3", name="Meds", priority=Priority.High, durationMinutes=5)

    plan = scheduler.generateDailySchedule([floating_low, timed, floating_high])

    assert [task.name for task in plan] == ["Walk", "Meds", "Brush"]


def test_detect_conflicts_finds_overlapping_tasks() -> None:
    owner = Owner(name="Jordan")
    scheduler = Scheduler(owner=owner)

    walk = Task(taskID="t1", name="Walk", priority=Priority.High, durationMinutes=60, startTime=540)
    vet = Task(taskID="t2", name="Vet", priority=Priority.High, durationMinutes=30, startTime=570)
    play = Task(taskID="t3", name="Play", priority=Priority.Med, durationMinutes=20, startTime=660)

    conflicts = scheduler.detectConflicts([walk, vet, play])

    assert len(conflicts) == 1
    assert {conflicts[0][0].name, conflicts[0][1].name} == {"Walk", "Vet"}


def test_detect_conflicts_ignores_adjacent_and_unscheduled_tasks() -> None:
    owner = Owner(name="Jordan")
    scheduler = Scheduler(owner=owner)

    first = Task(taskID="t1", name="Feed", priority=Priority.High, durationMinutes=30, startTime=480)
    back_to_back = Task(taskID="t2", name="Walk", priority=Priority.Med, durationMinutes=30, startTime=510)
    floating = Task(taskID="t3", name="Brush", priority=Priority.Low, durationMinutes=15)

    conflicts = scheduler.detectConflicts([first, back_to_back, floating])

    assert conflicts == []


def test_completing_daily_task_returns_next_occurrence_one_day_later() -> None:
    today = date(2026, 7, 7)
    task = Task(
        taskID="t1", name="Feed", priority=Priority.High, durationMinutes=10,
        recurrence=Recurrence.Daily, dueDate=today,
    )

    next_task = task.markComplete()

    assert task.isCompleted is True
    assert next_task is not None
    assert next_task.isCompleted is False
    assert next_task.dueDate == today + timedelta(days=1)
    assert next_task.recurrence == Recurrence.Daily


def test_completing_weekly_task_advances_seven_days() -> None:
    today = date(2026, 7, 7)
    task = Task(
        taskID="t1", name="Bath", priority=Priority.Low, durationMinutes=30,
        recurrence=Recurrence.Weekly, dueDate=today,
    )

    next_task = task.markComplete()

    assert next_task.dueDate == today + timedelta(weeks=1)


def test_recurrence_rollover_crosses_month_boundary() -> None:
    task = Task(
        taskID="t1", name="Feed", priority=Priority.High, durationMinutes=10,
        recurrence=Recurrence.Daily, dueDate=date(2026, 1, 31),
    )

    next_task = task.markComplete()

    assert next_task.dueDate == date(2026, 2, 1)


def test_completing_one_time_task_returns_none() -> None:
    task = Task(taskID="t1", name="Vet visit", priority=Priority.High, durationMinutes=60)

    next_task = task.markComplete()

    assert next_task is None
    assert task.isCompleted is True


def test_pet_complete_task_appends_next_occurrence() -> None:
    pet = Pet(name="Mochi", species="cat", healthStatus="healthy", energyLevel=80)
    task = Task(
        taskID="t1", name="Feed", priority=Priority.High, durationMinutes=10,
        recurrence=Recurrence.Daily, dueDate=date(2026, 7, 7),
    )
    pet.addTask(task)

    next_task = pet.completeTask(task)

    assert len(pet.tasks) == 2
    assert next_task in pet.tasks
    # The completed original is filtered out; only the fresh occurrence is a "need".
    assert pet.getNeeds() == [next_task]


def test_pet_complete_task_on_one_time_task_adds_nothing() -> None:
    pet = Pet(name="Mochi", species="cat", healthStatus="healthy", energyLevel=80)
    task = Task(taskID="t1", name="Vet visit", priority=Priority.High, durationMinutes=60)
    pet.addTask(task)

    next_task = pet.completeTask(task)

    assert next_task is None
    assert len(pet.tasks) == 1
