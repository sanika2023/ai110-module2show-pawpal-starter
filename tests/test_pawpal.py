import pytest
from datetime import date, time, datetime, timedelta
from pawpal_system import Owner, Pet, Task, TaskStatus, Scheduler, ScheduleEntry


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


class TestSortingCorrectness:
    """Test that tasks are sorted in chronological order by preferred_window."""

    def test_sort_by_time_orders_tasks_chronologically(self):
        """Verify that sort_by_time() returns tasks ordered by start time."""
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        # Create tasks with different preferred_window times
        task_morning = Task(
            id="1",
            name="Morning Walk",
            type="exercise",
            duration_minutes=30,
            priority=1,
            deadline=None,
            recurrence=None,
            preferred_window=(time(8, 0), time(8, 30)),  # 8:00 AM
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        task_afternoon = Task(
            id="2",
            name="Afternoon Play",
            type="enrichment",
            duration_minutes=20,
            priority=2,
            deadline=None,
            recurrence=None,
            preferred_window=(time(14, 0), time(14, 20)),  # 2:00 PM
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        task_evening = Task(
            id="3",
            name="Evening Dinner",
            type="feeding",
            duration_minutes=15,
            priority=1,
            deadline=None,
            recurrence=None,
            preferred_window=(time(18, 0), time(18, 15)),  # 6:00 PM
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        # Shuffle the order
        unsorted_tasks = [task_afternoon, task_evening, task_morning]
        
        # Sort using the scheduler
        scheduler = Scheduler()
        sorted_tasks = scheduler.sort_by_time(unsorted_tasks)
        
        # Verify chronological order
        assert sorted_tasks[0] == task_morning  # 8:00 AM first
        assert sorted_tasks[1] == task_afternoon  # 2:00 PM second
        assert sorted_tasks[2] == task_evening  # 6:00 PM last

    def test_sort_by_time_defaults_no_window_to_end(self):
        """Verify that tasks without preferred_window are sorted to the end."""
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        task_with_window = Task(
            id="1",
            name="Morning Walk",
            type="exercise",
            duration_minutes=30,
            priority=1,
            deadline=None,
            recurrence=None,
            preferred_window=(time(8, 0), time(8, 30)),
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        task_no_window = Task(
            id="2",
            name="Flexible Task",
            type="enrichment",
            duration_minutes=20,
            priority=2,
            deadline=None,
            recurrence=None,
            preferred_window=None,  # No preferred window
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        scheduler = Scheduler()
        sorted_tasks = scheduler.sort_by_time([task_no_window, task_with_window])
        
        # Task with window should come first
        assert sorted_tasks[0] == task_with_window
        # Task without window should come last
        assert sorted_tasks[1] == task_no_window

    def test_sort_by_time_handles_same_start_time(self):
        """Verify tasks with the same start time are both included."""
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        # Two tasks with the same start time
        task_a = Task(
            id="1",
            name="Task A",
            type="exercise",
            duration_minutes=30,
            priority=1,
            deadline=None,
            recurrence=None,
            preferred_window=(time(8, 0), time(8, 30)),
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        task_b = Task(
            id="2",
            name="Task B",
            type="feeding",
            duration_minutes=15,
            priority=2,
            deadline=None,
            recurrence=None,
            preferred_window=(time(8, 0), time(8, 15)),
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        scheduler = Scheduler()
        sorted_tasks = scheduler.sort_by_time([task_b, task_a])
        
        # Both tasks should be present
        assert len(sorted_tasks) == 2
        assert task_a in sorted_tasks
        assert task_b in sorted_tasks


class TestRecurrenceLogic:
    """Test that recurring tasks create new instances when marked complete."""

    def test_daily_task_creates_next_day_task(self):
        """Verify that marking a daily task complete creates a new task for tomorrow."""
        test_date = datetime(2026, 3, 29, 10, 0)  # March 29, 2026
        
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        task = Task(
            id="1",
            name="Daily Walk",
            type="exercise",
            duration_minutes=30,
            priority=1,
            deadline=test_date,
            recurrence="daily",
            preferred_window=(time(8, 0), time(8, 30)),
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        pet.add_task(task)
        
        # Verify initial state
        assert len(pet.tasks) == 1
        assert pet.tasks[0].status == TaskStatus.PENDING
        
        # Mark task as done
        task.mark_done()
        
        # Verify original task is now DONE
        assert task.status == TaskStatus.DONE
        
        # Verify a new task was created
        assert len(pet.tasks) == 2
        new_task = pet.tasks[1]
        
        # Verify new task attributes
        assert new_task.status == TaskStatus.PENDING
        assert new_task.name == "Daily Walk"
        assert new_task.recurrence == "daily"
        assert new_task.deadline == test_date + timedelta(days=1)

    def test_weekly_task_creates_next_week_task(self):
        """Verify that marking a weekly task complete creates a new task for next week."""
        test_date = datetime(2026, 3, 29, 10, 0)
        
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Whiskers", type="cat", age=2, needs={}, owner=owner, tasks=[])
        
        task = Task(
            id="1",
            name="Weekly Grooming",
            type="grooming",
            duration_minutes=60,
            priority=2,
            deadline=test_date,
            recurrence="weekly",
            preferred_window=(time(10, 0), time(11, 0)),
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        pet.add_task(task)
        
        # Mark task as done
        task.mark_done()
        
        # Verify new task was created with correct deadline
        assert len(pet.tasks) == 2
        new_task = pet.tasks[1]
        
        assert new_task.status == TaskStatus.PENDING
        assert new_task.name == "Weekly Grooming"
        assert new_task.recurrence == "weekly"
        assert new_task.deadline == test_date + timedelta(days=7)

    def test_non_recurring_task_does_not_create_new(self):
        """Verify that non-recurring tasks do NOT create new instances when completed."""
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        task = Task(
            id="1",
            name="One-time Vet Visit",
            type="medical",
            duration_minutes=45,
            priority=1,
            deadline=datetime(2026, 3, 29, 14, 0),
            recurrence=None,  # Not recurring
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        pet.add_task(task)
        
        # Mark task as done
        task.mark_done()
        
        # Verify no new task was created
        assert len(pet.tasks) == 1
        assert pet.tasks[0].status == TaskStatus.DONE

    def test_recurring_task_preserves_all_attributes(self):
        """Verify that new recurring tasks preserve all original attributes."""
        test_date = datetime(2026, 3, 29, 10, 0)
        
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        original_window = (time(8, 30), time(9, 0))
        
        task = Task(
            id="original-id",
            name="Daily Breakfast",
            type="feeding",
            duration_minutes=15,
            priority=1,
            deadline=test_date,
            recurrence="daily",
            preferred_window=original_window,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        pet.add_task(task)
        task.mark_done()
        
        new_task = pet.tasks[1]
        
        # Verify attributes are preserved
        assert new_task.name == task.name
        assert new_task.type == task.type
        assert new_task.duration_minutes == task.duration_minutes
        assert new_task.priority == task.priority
        assert new_task.preferred_window == original_window
        assert new_task.recurrence == "daily"


class TestConflictDetection:
    """Test that the scheduler correctly detects overlapping task timeslots."""

    def test_detect_overlapping_times(self):
        """Verify that overlapping schedule entries are detected as conflicts."""
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        task1 = Task(
            id="1",
            name="Walk",
            type="exercise",
            duration_minutes=30,
            priority=1,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        task2 = Task(
            id="2",
            name="Play",
            type="enrichment",
            duration_minutes=30,
            priority=2,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        # Create overlapping schedule entries
        entry1 = ScheduleEntry(task=task1, start_time=time(8, 0), end_time=time(8, 30))
        entry2 = ScheduleEntry(task=task2, start_time=time(8, 15), end_time=time(8, 45))
        
        scheduler = Scheduler()
        conflict_data = scheduler.detect_conflicts_with_warnings([entry1, entry2])
        
        # Verify conflict was detected
        assert conflict_data["has_conflicts"] == True
        assert conflict_data["conflict_count"] == 1
        assert len(conflict_data["conflicts"]) == 1

    def test_non_overlapping_times_no_conflict(self):
        """Verify that non-overlapping times are NOT flagged as conflicts."""
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        task1 = Task(
            id="1",
            name="Walk",
            type="exercise",
            duration_minutes=30,
            priority=1,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        task2 = Task(
            id="2",
            name="Play",
            type="enrichment",
            duration_minutes=30,
            priority=2,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        # Create non-overlapping schedule entries
        entry1 = ScheduleEntry(task=task1, start_time=time(8, 0), end_time=time(8, 30))
        entry2 = ScheduleEntry(task=task2, start_time=time(8, 30), end_time=time(9, 0))
        
        scheduler = Scheduler()
        conflict_data = scheduler.detect_conflicts_with_warnings([entry1, entry2])
        
        # Verify no conflict
        assert conflict_data["has_conflicts"] == False
        assert conflict_data["conflict_count"] == 0

    def test_same_pet_conflict_detected(self):
        """Verify that overlapping tasks for the SAME pet are detected."""
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        task1 = Task(
            id="1",
            name="Walk",
            type="exercise",
            duration_minutes=30,
            priority=1,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        task2 = Task(
            id="2",
            name="Feed",
            type="feeding",
            duration_minutes=15,
            priority=2,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet  # Same pet
        )
        
        entry1 = ScheduleEntry(task=task1, start_time=time(8, 0), end_time=time(8, 30))
        entry2 = ScheduleEntry(task=task2, start_time=time(8, 15), end_time=time(8, 30))
        
        scheduler = Scheduler()
        conflict_data = scheduler.detect_conflicts_with_warnings([entry1, entry2])
        
        assert conflict_data["has_conflicts"] == True
        assert "CONFLICT" in conflict_data["warning_messages"][0]
        assert pet.name in conflict_data["warning_messages"][0]

    def test_different_pets_conflict_detected(self):
        """Verify that overlapping tasks for DIFFERENT pets are detected as capacity issues."""
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet1 = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        pet2 = Pet(name="Whiskers", type="cat", age=2, needs={}, owner=owner, tasks=[])
        
        task1 = Task(
            id="1",
            name="Walk the Dog",
            type="exercise",
            duration_minutes=30,
            priority=1,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet1
        )
        
        task2 = Task(
            id="2",
            name="Feed the Cat",
            type="feeding",
            duration_minutes=15,
            priority=2,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet2
        )
        
        entry1 = ScheduleEntry(task=task1, start_time=time(8, 0), end_time=time(8, 30))
        entry2 = ScheduleEntry(task=task2, start_time=time(8, 15), end_time=time(8, 30))
        
        scheduler = Scheduler()
        conflict_data = scheduler.detect_conflicts_with_warnings([entry1, entry2])
        
        assert conflict_data["has_conflicts"] == True
        message = conflict_data["warning_messages"][0]
        assert "Owner may not have time" in message

    def test_multiple_conflicts_detected(self):
        """Verify that multiple conflicts are all detected and counted."""
        owner = Owner(name="Alice", available_time_per_day=480, preferences={}, pets=[])
        pet = Pet(name="Buddy", type="dog", age=3, needs={}, owner=owner, tasks=[])
        
        task1 = Task(
            id="1",
            name="Task 1",
            type="exercise",
            duration_minutes=30,
            priority=1,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        task2 = Task(
            id="2",
            name="Task 2",
            type="enrichment",
            duration_minutes=30,
            priority=2,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        task3 = Task(
            id="3",
            name="Task 3",
            type="feeding",
            duration_minutes=30,
            priority=3,
            deadline=None,
            recurrence=None,
            preferred_window=None,
            status=TaskStatus.PENDING,
            pet=pet
        )
        
        # All three tasks overlap
        entry1 = ScheduleEntry(task=task1, start_time=time(8, 0), end_time=time(8, 30))
        entry2 = ScheduleEntry(task=task2, start_time=time(8, 15), end_time=time(8, 45))
        entry3 = ScheduleEntry(task=task3, start_time=time(8, 20), end_time=time(8, 50))
        
        scheduler = Scheduler()
        conflict_data = scheduler.detect_conflicts_with_warnings([entry1, entry2, entry3])
        
        # Should detect 3 pairs of overlaps: (1,2), (1,3), (2,3)
        assert conflict_data["conflict_count"] == 3
        assert len(conflict_data["conflicts"]) == 3
