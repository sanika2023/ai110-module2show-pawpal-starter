#!/usr/bin/env python3
"""
Demo script showing recurring task functionality in PawPal+
"""

from datetime import datetime, date, timedelta
from pawpal_system import Owner, Pet, Task, TaskStatus

def demo_recurring_tasks():
    """Demonstrate how recurring tasks work."""
    print("=== PawPal+ Recurring Task Demo ===\n")
    
    # Create owner and pet
    owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
    pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
    owner.pets.append(pet)
    
    # Create a daily recurring task
    initial_deadline = datetime(2024, 3, 29, 10, 0)  # March 29, 2024, 10:00 AM
    daily_task = Task(
        id="daily-walk-001",
        name="Morning Walk",
        type="exercise",
        duration_minutes=30,
        priority=1,
        deadline=initial_deadline,
        recurrence="daily",
        preferred_window=None,
        status=TaskStatus.PENDING,
        pet=pet
    )
    pet.tasks.append(daily_task)
    
    print(f"Initial task: {daily_task.name}")
    print(f"  ID: {daily_task.id}")
    print(f"  Deadline: {daily_task.deadline}")
    print(f"  Status: {daily_task.status.value}")
    print(f"  Recurrence: {daily_task.recurrence}")
    print(f"  Total tasks for {pet.name}: {len(pet.tasks)}\n")
    
    # Mark the task as done - this should create a new recurring instance
    print("Marking task as DONE...")
    daily_task.mark_done()
    
    print(f"After marking done:")
    print(f"  Original task status: {daily_task.status.value}")
    print(f"  Total tasks for {pet.name}: {len(pet.tasks)}")
    
    # Find the new recurring task
    new_tasks = [t for t in pet.tasks if t.id != daily_task.id]
    if new_tasks:
        new_task = new_tasks[0]
        print(f"\nNew recurring task created:")
        print(f"  ID: {new_task.id}")
        print(f"  Name: {new_task.name}")
        print(f"  Deadline: {new_task.deadline}")
        print(f"  Status: {new_task.status.value}")
        print(f"  Recurrence: {new_task.recurrence}")
        
        # Verify deadline calculation
        expected_deadline = initial_deadline + timedelta(days=1)
        print(f"  Expected deadline: {expected_deadline}")
        print(f"  Deadline correct: {new_task.deadline == expected_deadline}")
    
    print("\n=== Weekly Recurring Task Demo ===\n")
    
    # Create a weekly recurring task
    weekly_deadline = datetime(2024, 3, 29, 14, 0)  # March 29, 2024, 2:00 PM
    weekly_task = Task(
        id="weekly-groom-001",
        name="Weekly Grooming",
        type="grooming",
        duration_minutes=60,
        priority=2,
        deadline=weekly_deadline,
        recurrence="weekly",
        preferred_window=None,
        status=TaskStatus.PENDING,
        pet=pet
    )
    pet.tasks.append(weekly_task)
    
    print(f"Weekly task: {weekly_task.name}")
    print(f"  Deadline: {weekly_task.deadline}")
    print(f"  Recurrence: {weekly_task.recurrence}")
    
    # Mark as done
    weekly_task.mark_done()
    
    # Find the new weekly task
    weekly_new_tasks = [t for t in pet.tasks if t.id != weekly_task.id and t.name == "Weekly Grooming"]
    if weekly_new_tasks:
        weekly_new = weekly_new_tasks[0]
        print(f"\nNew weekly task:")
        print(f"  Deadline: {weekly_new.deadline}")
        expected_weekly = weekly_deadline + timedelta(days=7)
        print(f"  Expected: {expected_weekly}")
        print(f"  Correct: {weekly_new.deadline == expected_weekly}")

if __name__ == "__main__":
    demo_recurring_tasks()