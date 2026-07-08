from pawpal_system import Owner, Pet, Priority, Recurrence, Scheduler, Task, formatTime


def main() -> None:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="cat", healthStatus="healthy", energyLevel=80)
    biscuit = Pet(name="Biscuit", species="dog", healthStatus="healthy", energyLevel=90)

    owner.addPet(mochi)
    owner.addPet(biscuit)

    # Tasks are added out of chronological order on purpose, so sort_by_time
    # has something real to reorder. startTime is minutes since midnight.
    mochi.addTask(Task(taskID="t1", name="Play session", priority=Priority.Med, durationMinutes=20, startTime=15 * 60))  # 15:00
    mochi.addTask(Task(taskID="t2", name="Feed breakfast", priority=Priority.High, durationMinutes=10, startTime=8 * 60, recurrence=Recurrence.Daily))  # 08:00, every day
    biscuit.addTask(Task(taskID="t3", name="Evening walk", priority=Priority.Med, durationMinutes=30, startTime=18 * 60))  # 18:00
    biscuit.addTask(Task(taskID="t4", name="Morning walk", priority=Priority.High, durationMinutes=30, startTime=8 * 60 + 5))  # 08:05 (overlaps Feed)
    biscuit.addTask(Task(taskID="t5", name="Nail trim", priority=Priority.Low, durationMinutes=15, recurrence=Recurrence.Weekly))  # unscheduled, weekly

    # Mark one task done to show the completion-status filter in action.
    mochi.tasks[0].markComplete()

    scheduler = Scheduler(owner=owner)

    print("Day Plan (sorted by time)")
    print("=========================")
    for task in scheduler.sort_by_time(scheduler.retrieveTasks()):
        when = formatTime(task.startTime) if task.startTime is not None else "--:--"
        print(f"{when}  {task.name} ({task.durationMinutes} min) [{task.priority.value}]")

    print("\nBiscuit's tasks only")
    print("====================")
    for task in scheduler.filterTasks(petName="Biscuit"):
        print(f"- {task.name}")

    print("\nCompleted tasks")
    print("===============")
    for task in scheduler.filterTasks(completed=True):
        print(f"- {task.name}")

    print("\nConflicts")
    print("=========")
    conflicts = scheduler.detectConflicts(scheduler.retrieveTasks())
    if conflicts:
        for first, second in conflicts:
            print(f"- {first.name} overlaps {second.name}")
    else:
        print("None")

    print("\nRecurring task rollover")
    print("=======================")
    feed = mochi.tasks[1]  # "Feed breakfast", a daily task due today
    print(f"Before: {feed.name} due {feed.dueDate.isoformat()}, completed={feed.isCompleted}")
    # completeTask marks it done and auto-appends tomorrow's occurrence.
    next_feed = mochi.completeTask(feed)
    print(f"After:  {feed.name} completed={feed.isCompleted}")
    print(f"New occurrence: {next_feed.name} due {next_feed.dueDate.isoformat()}, completed={next_feed.isCompleted}")


if __name__ == "__main__":
    main()
