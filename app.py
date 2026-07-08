from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Priority, Recurrence, Scheduler, Task, formatTime

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Map the UI's friendly labels onto the Priority enum from the core system.
PRIORITY_MAP = {"low": Priority.Low, "medium": Priority.Med, "high": Priority.High}

# Friendly labels for how a task repeats; "one-time" maps to no recurrence.
RECURRENCE_MAP = {
    "one-time": None,
    "daily": Recurrence.Daily,
    "weekly": Recurrence.Weekly,
}

# Create the Owner once and keep it in the session "vault" so it (and every
# pet/task added to it) persists across Streamlit's top-to-bottom reruns.
owner_name = st.text_input("Owner name", value="Jordan")
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
owner = st.session_state.owner

st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    health_status = st.text_input("Health status", value="healthy")
    energy_level = st.slider("Energy level", min_value=0, max_value=100, value=50)
    if st.form_submit_button("Add pet"):
        # Owner.addPet is the core method that owns this mutation.
        owner.addPet(
            Pet(
                name=pet_name,
                species=species,
                healthStatus=health_status,
                energyLevel=int(energy_level),
            )
        )
        st.success(f"Added {pet_name} to {owner.name}'s pets.")

# Re-read the persisted owner and repaint the current pets on every rerun.
if owner.pets:
    st.write("Current pets:")
    for pet in owner.pets:
        st.write(
            f"- **{pet.name}** ({pet.species}) — energy {pet.energyLevel}, "
            f"{len(pet.tasks)} task(s)"
        )
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Add a Task")
if owner.pets:
    with st.form("add_task_form"):
        pet_choice = st.selectbox("For which pet?", [pet.name for pet in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        repeats = st.selectbox("Repeats", ["one-time", "daily", "weekly"])
        scheduled = st.checkbox("Schedule at a specific time?", value=True)
        start_time = st.time_input("Start time", value=time(9, 0))
        if st.form_submit_button("Add task"):
            target_pet = next(pet for pet in owner.pets if pet.name == pet_choice)
            # Store the start time as minutes since midnight, or None if floating.
            start_minutes = (
                start_time.hour * 60 + start_time.minute if scheduled else None
            )
            # Pet.addTask is the core method that attaches a Task to a pet.
            target_pet.addTask(
                Task(
                    taskID=f"{target_pet.name}-{len(target_pet.tasks) + 1}",
                    name=task_title,
                    priority=PRIORITY_MAP[priority],
                    durationMinutes=int(duration),
                    startTime=start_minutes,
                    recurrence=RECURRENCE_MAP[repeats],
                )
            )
            st.success(f"Added '{task_title}' to {target_pet.name}.")
else:
    st.info("Add a pet first, then you can give it tasks.")

st.divider()

st.subheader("Complete a Task")
st.caption("Completing a daily/weekly task auto-creates its next occurrence.")

# Build a list of (pet, task) pairs for every open task so the user can pick one.
open_tasks = [
    (pet, task) for pet in owner.pets for task in pet.getNeeds()
]
if open_tasks:
    with st.form("complete_task_form"):
        labels = [
            f"{pet.name}: {task.name}"
            + (f" ({task.recurrence.value})" if task.recurrence else "")
            for pet, task in open_tasks
        ]
        choice_index = st.selectbox(
            "Which task did you finish?",
            range(len(open_tasks)),
            format_func=lambda i: labels[i],
        )
        if st.form_submit_button("Mark complete"):
            target_pet, target_task = open_tasks[choice_index]
            # Pet.completeTask marks it done and appends the next occurrence if recurring.
            next_task = target_pet.completeTask(target_task)
            if next_task is not None:
                st.success(
                    f"Completed '{target_task.name}'. Next {target_task.recurrence.value} "
                    f"occurrence scheduled for {next_task.dueDate.isoformat()}."
                )
            else:
                st.success(f"Completed '{target_task.name}'.")
else:
    st.info("No open tasks to complete.")

st.divider()

st.subheader("Build Schedule")
st.caption("Runs the Scheduler over every incomplete task across all pets.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    tasks = scheduler.retrieveTasks()
    if not tasks:
        st.warning("No tasks to schedule yet. Add a pet and some tasks first.")
    else:
        day_plan = scheduler.generateDailySchedule(tasks)
        st.write("### Your Day Plan")
        st.table(
            [
                {
                    "Time": formatTime(task.startTime)
                    if task.startTime is not None
                    else "—",
                    "Task": task.name,
                    "Priority": task.priority.value,
                    "Duration (min)": task.durationMinutes,
                    "Repeats": task.recurrence.value if task.recurrence else "one-time",
                }
                for task in day_plan
            ]
        )
        st.info(scheduler.generateReasoning())

        conflicts = scheduler.detectConflicts(tasks)
        if conflicts:
            st.warning("⚠️ Scheduling conflicts detected:")
            for first, second in conflicts:
                st.write(
                    f"- **{first.name}** ({formatTime(first.startTime)}–"
                    f"{formatTime(first.endMinutes)}) overlaps **{second.name}** "
                    f"({formatTime(second.startTime)}–{formatTime(second.endMinutes)})"
                )
        else:
            st.success("No scheduling conflicts. 🎉")
