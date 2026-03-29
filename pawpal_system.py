from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, time, timedelta
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    DONE = "done"
    SKIPPED = "skipped"

@dataclass
class ScheduleEntry:
    task: 'Task'
    start_time: time
    end_time: time

@dataclass
class Owner:
    name: str
    available_time_per_day: int
    preferences: Dict[str, Any]
    pets: List['Pet']

    def add_pet(self, pet: 'Pet') -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet: 'Pet') -> None:
        """Remove a pet from the owner's pet list."""
        if pet in self.pets:
            self.pets.remove(pet)

    def add_task(self, task: 'Task') -> None:
        """Add a task to a pet's task list."""
        task.pet.tasks.append(task)

    def plan_daily_schedule(self, date: date) -> 'Schedule':
        """Generate a daily schedule for all of the owner's pets."""
        scheduler = Scheduler()
        return scheduler.generate_schedule(self, date)

    def explain_schedule(self, schedule: 'Schedule') -> str:
        """Provide reasoning for why the schedule was organized this way."""
        scheduler = Scheduler()
        return scheduler.explain_schedule(schedule)

@dataclass
class Pet:
    name: str
    type: str
    age: int
    needs: Dict[str, Any]
    owner: 'Owner'
    tasks: List['Task']

    def add_task(self, task: 'Task') -> None:
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def get_pending_tasks(self, date: date) -> List['Task']:
        """Return all pending tasks for the pet."""
        return [t for t in self.tasks if t.status == TaskStatus.PENDING]

    def total_required_time(self, date: date) -> int:
        """Calculate the total time required for all pending tasks."""
        return sum(t.duration_minutes for t in self.get_pending_tasks(date))

@dataclass
class Task:
    id: str
    name: str
    type: str
    duration_minutes: int
    priority: int
    deadline: Optional[datetime]
    recurrence: Optional[str]
    preferred_window: Optional[Tuple[time, time]]
    status: TaskStatus
    pet: 'Pet'

    def mark_done(self) -> None:
        """Mark the task as completed."""
        self.status = TaskStatus.DONE

    def reschedule(self, new_time: time) -> None:
        """Reschedule the task to a new time."""
        self.preferred_window = (new_time, new_time)

    def is_due(self, date: date) -> bool:
        """Check if the task is due (pending status)."""
        return self.status == TaskStatus.PENDING

    def score_for_planning(self, owner_preferences: Dict[str, Any], constraints: Dict[str, Any]) -> float:
        """Calculate a priority score for scheduling purposes."""
        return self.priority

@dataclass
class Scheduler:
    """The 'Brain' that retrieves, organizes, and manages tasks across pets."""

    def retrieve_tasks(self, owner: 'Owner', date: date) -> List['Task']:
        """Get all pending tasks from an owner's pets."""
        tasks = []
        for pet in owner.pets:
            tasks.extend(pet.tasks)
        return [t for t in tasks if t.status == TaskStatus.PENDING]

    def organize_tasks(self, tasks: List['Task'], owner_preferences: Dict[str, Any]) -> List['Task']:
        """Sort tasks by priority for optimal scheduling."""
        return sorted(tasks, key=lambda t: t.priority)

    def generate_schedule(self, owner: 'Owner', date: date) -> 'Schedule':
        """Create a time-ordered schedule for the day."""
        tasks = self.retrieve_tasks(owner, date)
        organized = self.organize_tasks(tasks, owner.preferences)
        entries = []
        current_time = time(8, 0)  # Start at 8 AM
        total_duration = 0
        for task in organized:
            start = current_time
            end_dt = datetime.combine(date, start) + timedelta(minutes=task.duration_minutes)
            end = end_dt.time()
            entries.append(ScheduleEntry(task=task, start_time=start, end_time=end))
            current_time = end
            total_duration += task.duration_minutes
        explanation = f"Scheduled {len(entries)} tasks starting from 8 AM, prioritized by urgency."
        return Schedule(date=date, entries=entries, total_duration=total_duration, confidence_explanation=explanation)

    def explain_schedule(self, schedule: 'Schedule') -> str:
        """Return the schedule's reasoning explanation."""
        return schedule.confidence_explanation

@dataclass
class Schedule:
    date: date
    entries: List[ScheduleEntry]
    total_duration: int
    confidence_explanation: str

    def add_entry(self, task: 'Task', start: time, end: time) -> None:
        """Add a scheduled task with start and end times."""
        self.entries.append(ScheduleEntry(task=task, start_time=start, end_time=end))

    def is_over_capacity(self, max_minutes: int) -> bool:
        """Check if total duration exceeds the maximum allowed time."""
        return self.total_duration > max_minutes

    def format_for_ui(self) -> str:
        """Format the schedule for display to the user."""
        lines = [f"Schedule for {self.date}:"]
        for entry in self.entries:
            lines.append(f"{entry.start_time} - {entry.end_time}: {entry.task.name} for {entry.task.pet.name}")
        lines.append(f"Total time: {self.total_duration} minutes")
        lines.append(self.confidence_explanation)
        return "\n".join(lines)
