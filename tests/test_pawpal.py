import pytest
from datetime import date
from pawpal_system import Owner, Pet, Task, TaskStatus


class TestTaskCompletion:
    """Test that task completion changes status correctly."""

    def test_mark_done_changes_status(self):
        """Verify that calling mark_done() changes the task status to DONE."""
        # Create a pet and owner
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        # Create a task with PENDING status
        task = Task(
            id="1",
            name="Walk",
            type="exercise",
            duration_minutes=30,
            priority=1,
            deadline=None,
            recurrence="daily",
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        # Verify initial status is PENDING
        assert task.status == TaskStatus.PENDING
        
        # Mark task as done
        task.mark_done()
        
        # Verify status changed to DONE
        assert task.status == TaskStatus.DONE


class TestTaskAddition:
    """Test that adding tasks to pets works correctly."""

    def test_add_task_increases_pet_task_count(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        # Create a pet and owner
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Whiskers", type="cat", age=2, needs={}, owner=owner, tasks=[])
        
        # Verify pet starts with no tasks
        assert len(pet.tasks) == 0
        
        # Create and add a task
        task1 = Task(
            id="1",
            name="Feed",
            type="feeding",
            duration_minutes=10,
            priority=1,
            deadline=None,
            recurrence="daily",
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        pet.add_task(task1)
        
        # Verify task count increased to 1
        assert len(pet.tasks) == 1
        assert pet.tasks[0] == task1
        
        # Add a second task
        task2 = Task(
            id="2",
            name="Play",
            type="enrichment",
            duration_minutes=20,
            priority=2,
            deadline=None,
            recurrence="daily",
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        pet.add_task(task2)
        
        # Verify task count increased to 2
        assert len(pet.tasks) == 2
        assert pet.tasks[1] == task2
