import streamlit as st
from pawpal_system import Owner, Pet, Task, TaskStatus, Schedule, Scheduler, ScheduleEntry
from datetime import date

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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialize Owner in session state if it doesn't exist
if owner_name:
    if 'owner' not in st.session_state:
        st.session_state.owner = Owner(name=owner_name, available_time_per_day=480, preferences={}, pets=[])
    owner = st.session_state.owner
else:
    owner = None

# Add Pet button
if st.button("Add Pet") and owner and pet_name and species:
    # Check if pet already exists
    if not any(p.name == pet_name for p in owner.pets):
        pet = Pet(name=pet_name, type=species, age=1, needs={}, owner=owner, tasks=[])
        owner.add_pet(pet)
        st.success(f"Added pet {pet_name}!")
    else:
        st.warning(f"Pet {pet_name} already exists!")

# Display current pets
if owner and owner.pets:
    st.write("Current Pets:")
    pet_data = [{"Name": p.name, "Type": p.type, "Age": p.age} for p in owner.pets]
    st.table(pet_data)
elif owner:
    st.info("No pets added yet. Add one above.")
else:
    st.info("Enter an owner name to get started.")

st.markdown("### Tasks")
st.caption("Add tasks to your pets. These will be used in the schedule.")

if owner and owner.pets:
    # Select which pet to add task to
    pet_options = {p.name: p for p in owner.pets}
    selected_pet_name = st.selectbox("Select pet for task", list(pet_options.keys()))
    selected_pet = pet_options[selected_pet_name]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority_map = {"low": 3, "medium": 2, "high": 1}
        priority_label = st.selectbox("Priority", ["high", "medium", "low"], index=0)
        priority = priority_map[priority_label]
    with col4:
        task_type = st.text_input("Task type", value="exercise")
    
    if st.button("Add task to pet"):
        new_task = Task(
            id=f"{selected_pet.name}_{len(selected_pet.tasks) + 1}",
            name=task_title,
            type=task_type,
            duration_minutes=int(duration),
            priority=priority,
            deadline=None,
            recurrence="daily",
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=selected_pet
        )
        selected_pet.add_task(new_task)
        st.success(f"Added '{task_title}' to {selected_pet.name}!")
    
    # Display tasks for each pet
    for pet in owner.pets:
        if pet.tasks:
            st.write(f"**{pet.name}'s Tasks:**")
            task_data = [
                {"Task": t.name, "Type": t.type, "Duration (min)": t.duration_minutes, "Priority": t.priority, "Status": t.status.value}
                for t in pet.tasks
            ]
            st.table(task_data)
else:
    st.info("Add at least one pet to start adding tasks.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily schedule based on your pets' tasks and priority levels.")

if st.button("Generate schedule"):
    if owner:
        # Count total pending tasks
        total_pending = sum(len(p.get_pending_tasks(date.today())) for p in owner.pets)
        
        if total_pending > 0:
            schedule = owner.plan_daily_schedule(date.today())
            
            st.success("Schedule generated!")
            st.markdown("### Today's Schedule")
            st.text(schedule.format_for_ui())
            
            st.markdown("### Schedule Explanation")
            st.info(owner.explain_schedule(schedule))
        else:
            st.warning("No pending tasks to schedule. Add some tasks to your pets first!")
    else:
        st.warning("Create an owner and add pets with tasks before generating a schedule.")
