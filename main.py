from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="cat", healthStatus="healthy", energyLevel=80)
    biscuit = Pet(name="Biscuit", species="dog", healthStatus="healthy", energyLevel=90)

    owner.addPet(mochi)
    owner.addPet(biscuit)

    mochi.addTask(Task(taskID="t1", name="Feed breakfast", priority=Priority.High, durationMinutes=10))
    mochi.addTask(Task(taskID="t2", name="Play session", priority=Priority.Med, durationMinutes=20))
    biscuit.addTask(Task(taskID="t3", name="Morning walk", priority=Priority.High, durationMinutes=30))

    scheduler = Scheduler(owner=owner)
    tasks = scheduler.retrieveTasks()

    print("Today's Schedule")
    print("================")
    for task in tasks:
        print(f"- {task.name} ({task.durationMinutes} min) [{task.priority.value}]")


if __name__ == "__main__":
    main()
