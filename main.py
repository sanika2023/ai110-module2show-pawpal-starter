from pawpal_system import Owner, Pet, Task, TaskStatus
from datetime import date

# Create Owner
owner = Owner(name="John", available_time_per_day=480, preferences={}, pets=[])

# Create Pets
pet1 = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
pet2 = Pet(name="Whiskers", type="cat", age=2, needs={}, owner=owner, tasks=[])

# Add pets to owner
owner.add_pet(pet1)
owner.add_pet(pet2)

# Create Tasks with different durations
task1 = Task(id="1", name="Walk", type="exercise", duration_minutes=30, priority=1, deadline=None, recurrence="daily", preferred_window=None, status=TaskStatus.PENDING, pet=pet1)
task2 = Task(id="2", name="Feed", type="feeding", duration_minutes=10, priority=2, deadline=None, recurrence="daily", preferred_window=None, status=TaskStatus.PENDING, pet=pet1)
task3 = Task(id="3", name="Play", type="enrichment", duration_minutes=20, priority=1, deadline=None, recurrence="daily", preferred_window=None, status=TaskStatus.PENDING, pet=pet2)

# Add tasks to pets
pet1.add_task(task1)
pet1.add_task(task2)
pet2.add_task(task3)

# Plan today's schedule
today = date.today()
schedule = owner.plan_daily_schedule(today)

# Print Today's Schedule
print("Today's Schedule")
print(schedule.format_for_ui())
