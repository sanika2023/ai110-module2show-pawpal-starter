from pawpal_system import Owner, Pet, Task, TaskStatus, Scheduler
from datetime import date, time, datetime

# Create Owner
owner = Owner(name="John", available_time_per_day=480, preferences={}, pets=[])

# Create Pets
pet1 = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
pet2 = Pet(name="Whiskers", type="cat", age=2, needs={}, owner=owner, tasks=[])

# Add pets to owner
owner.add_pet(pet1)
owner.add_pet(pet2)

print("=" * 70)
print("RECURRING TASK AUTO-CREATION DEMO")
print("=" * 70)

# Create a daily recurring task with a deadline
today_datetime = datetime.combine(date.today(), time(8, 0))
daily_walk = Task(
    id="walk_1", 
    name="Morning Walk", 
    type="exercise", 
    duration_minutes=30, 
    priority=1, 
    deadline=today_datetime,  # Has a deadline for tracking
    recurrence="daily",        # Daily recurrence
    preferred_window=(time(7, 0), time(9, 0)),
    status=TaskStatus.PENDING, 
    pet=pet1
)

# Create a weekly recurring task
weekly_groom = Task(
    id="groom_1",
    name="Full Groom",
    type="grooming",
    duration_minutes=60,
    priority=2,
    deadline=today_datetime,
    recurrence="weekly",       # Weekly recurrence
    preferred_window=(time(10, 0), time(12, 0)),
    status=TaskStatus.PENDING,
    pet=pet2
)

# Add tasks to pets
pet1.add_task(daily_walk)
pet2.add_task(weekly_groom)

print("\n1. INITIAL STATE - Tasks before completion:")
print("-" * 70)
print(f"Pet: {pet1.name} | Task Count: {len(pet1.tasks)}")
for task in pet1.tasks:
    if task.deadline:
        print(f"  - {task.name} (ID: {task.id[:8]}...) | Deadline: {task.deadline.date()} | Recurrence: {task.recurrence}")

print(f"\nPet: {pet2.name} | Task Count: {len(pet2.tasks)}")
for task in pet2.tasks:
    if task.deadline:
        print(f"  - {task.name} (ID: {task.id[:8]}...) | Deadline: {task.deadline.date()} | Recurrence: {task.recurrence}")

print("\n2. MARKING DAILY TASK AS DONE:")
print("-" * 70)
print(f"Marking '{daily_walk.name}' as complete...")
daily_walk.mark_done()
print(f"Status: {daily_walk.status.value}")
print(f"Pet: {pet1.name} | Task Count: {len(pet1.tasks)} (was {len(pet1.tasks) - 1})")

print("\nNew recurring task created:")
new_daily = pet1.tasks[-1]  # Get the last added task
if new_daily.deadline:
    print(f"  - {new_daily.name} (ID: {new_daily.id[:8]}...)")
    print(f"    Status: {new_daily.status.value}")
    print(f"    Deadline: {new_daily.deadline.date()} (tomorrow, +1 day)")
    print(f"    Recurrence: {new_daily.recurrence}")
    print(f"    Time Window: {new_daily.preferred_window[0]} - {new_daily.preferred_window[1]}")

print("\n3. MARKING WEEKLY TASK AS DONE:")
print("-" * 70)
print(f"Marking '{weekly_groom.name}' as complete...")
weekly_groom.mark_done()
print(f"Status: {weekly_groom.status.value}")
print(f"Pet: {pet2.name} | Task Count: {len(pet2.tasks)} (was {len(pet2.tasks) - 1})")

print("\nNew recurring task created:")
new_weekly = pet2.tasks[-1]  # Get the last added task
if new_weekly.deadline:
    print(f"  - {new_weekly.name} (ID: {new_weekly.id[:8]}...)")
    print(f"    Status: {new_weekly.status.value}")
    print(f"    Deadline: {new_weekly.deadline.date()} (next week, +7 days)")
    print(f"    Recurrence: {new_weekly.recurrence}")
    print(f"    Time Window: {new_weekly.preferred_window[0]} - {new_weekly.preferred_window[1]}")

print("\n4. COMPLETED AND PENDING TASKS:")
print("-" * 70)
scheduler = Scheduler()
all_tasks = []
for pet in owner.pets:
    all_tasks.extend(pet.tasks)

completed = scheduler.filter_tasks(all_tasks, status=TaskStatus.DONE)
pending = scheduler.filter_tasks(all_tasks, status=TaskStatus.PENDING)

print(f"Total Tasks: {len(all_tasks)}")
print(f"Completed (DONE): {len(completed)}")
for task in completed:
    print(f"  ✓ {task.name} for {task.pet.name}")

print(f"Pending: {len(pending)}")
for task in pending:
    if task.deadline:
        print(f"  ○ {task.name} for {task.pet.name} | Due: {task.deadline.date()}")

print("\n" + "=" * 70)
print("DEMO COMPLETE: Recurring tasks are auto-created when marked done!")
print("=" * 70)

print("\n" + "=" * 70)
print("CONFLICT DETECTION DEMO")
print("=" * 70)

# Create two tasks at the same time for different pets
conflict_task1 = Task(
    id="feed_buddy", 
    name="Feed Buddy", 
    type="feeding", 
    duration_minutes=15, 
    priority=1, 
    deadline=today_datetime, 
    recurrence=None, 
    preferred_window=(time(9, 0), time(10, 0)),  # 9 AM
    status=TaskStatus.PENDING, 
    pet=pet1
)

conflict_task2 = Task(
    id="play_whiskers", 
    name="Play with Whiskers", 
    type="play", 
    duration_minutes=20, 
    priority=1, 
    deadline=today_datetime, 
    recurrence=None, 
    preferred_window=(time(9, 0), time(10, 0)),  # Same 9 AM window
    status=TaskStatus.PENDING, 
    pet=pet2
)

# Add conflicting tasks
pet1.add_task(conflict_task1)
pet2.add_task(conflict_task2)

print("\nAdded conflicting tasks:")
print(f"- {conflict_task1.name} for {pet1.name} at {conflict_task1.preferred_window[0]}")
print(f"- {conflict_task2.name} for {pet2.name} at {conflict_task2.preferred_window[0]}")

# Generate schedule and check for conflicts
scheduler = Scheduler()
schedule = scheduler.generate_schedule(owner, date.today())

print("\nSchedule generated:")
print(schedule.format_for_ui())

print("\nConflict Summary:")
print(schedule.get_conflict_summary())

if schedule.has_conflicts():
    print("\nDetailed Conflict Warnings:")
    for msg in schedule.conflict_info["warning_messages"]:
        print(msg)
