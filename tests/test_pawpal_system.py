from pawpal_system import Owner, Pet, Priority, Scheduler, Task


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
