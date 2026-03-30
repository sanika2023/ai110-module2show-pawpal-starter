from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, time, timedelta
from enum import Enum
import uuid
import uuid

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
class ConflictWarning:
    """Represents a scheduling conflict with detailed information for user notification.
    
    Attributes:
        severity (str): The severity level of the conflict (e.g., "overlap").
        pet_names (List[str]): Names of pets involved in the conflict.
        tasks (Tuple['Task', 'Task']): The two conflicting tasks.
        time_overlap (str): String representation of the overlapping time period.
        message (str): User-friendly warning message describing the conflict.
    """
    severity: str  # "overlap" or "tight"
    pet_names: List[str]
    tasks: Tuple['Task', 'Task']
    time_overlap: str
    message: str

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

    def can_fit_tasks(self, target_date: date) -> bool:
        """Check if all pending tasks fit in available time."""
        total_time = sum(p.total_required_time(target_date) for p in self.pets)
        return total_time <= self.available_time_per_day

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
        """Mark the task as completed and create next recurring instance if applicable."""
        self.status = TaskStatus.DONE
        
        # If this is a recurring task, create the next instance
        if self.recurrence in ["daily", "weekly"]:
            self._create_next_recurring_task()

    def _create_next_recurring_task(self) -> None:
        """Create the next instance of a recurring task (daily or weekly)."""
        if self.recurrence not in ["daily", "weekly"]:
            return  # Only handle recognized recurrence patterns
        
        # Calculate next deadline based on recurrence pattern
        next_deadline = None
        if self.deadline is not None:
            if self.recurrence == "daily":
                next_deadline = self.deadline + timedelta(days=1)
            elif self.recurrence == "weekly":
                next_deadline = self.deadline + timedelta(days=7)
        
        # Generate unique ID for new task instance
        new_id = str(uuid.uuid4())
        
        # Create new task with updated deadline and same attributes
        new_task = Task(
            id=new_id,
            name=self.name,
            type=self.type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            deadline=next_deadline,
            recurrence=self.recurrence,  # Keep recurrence for future instances
            preferred_window=self.preferred_window,  # Preserve time preferences
            status=TaskStatus.PENDING,  # New tasks start as pending
            pet=self.pet
        )
        
        # Add new task to pet's task list
        self.pet.tasks.append(new_task)

    def reschedule(self, new_time: time) -> None:
        """Reschedule the task to a new time."""
        self.preferred_window = (new_time, new_time)

    def is_due(self, date: date) -> bool:
        """Check if the task is due (pending status)."""
        return self.status == TaskStatus.PENDING

    def score_for_planning(self, owner_preferences: Dict[str, Any], constraints: Dict[str, Any]) -> float:
        """Calculate a priority score for scheduling purposes."""
        return self.priority

    def _create_next_recurring_task(self) -> None:
        """Create the next instance of a recurring task."""
        if self.recurrence not in ["daily", "weekly"]:
            return  # Invalid recurrence, skip
        
        # Calculate next deadline
        next_deadline = None
        if self.deadline is not None:
            if self.recurrence == "daily":
                next_deadline = self.deadline + timedelta(days=1)
            elif self.recurrence == "weekly":
                next_deadline = self.deadline + timedelta(days=7)
        
        # Generate unique ID
        new_id = str(uuid.uuid4())
        
        # Create new task with same attributes but updated id, deadline, and status
        new_task = Task(
            id=new_id,
            name=self.name,
            type=self.type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            deadline=next_deadline,
            recurrence=self.recurrence,  # Keep recurrence for future instances
            preferred_window=self.preferred_window,  # Preserve preferred window
            status=TaskStatus.PENDING,
            pet=self.pet
        )
        
        # Add to pet's task list
        self.pet.tasks.append(new_task)

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

    def filter_tasks(self, tasks: List['Task'], pet_name: Optional[str] = None, 
                     status: Optional[TaskStatus] = None, task_type: Optional[str] = None) -> List['Task']:
        """Filter tasks by pet name, status, and/or task type."""
        result = tasks
        if pet_name:
            result = [t for t in result if t.pet.name == pet_name]
        if status:
            result = [t for t in result if t.status == status]
        if task_type:
            result = [t for t in result if t.type == task_type]
        return result

    def sort_by_time(self, tasks: List['Task']) -> List['Task']:
        """Sort tasks by their preferred window start time in HH:MM format."""
        def get_time_key(task: 'Task') -> str:
            """Extract start time from preferred_window as HH:MM string, or default to end of day."""
            if task.preferred_window:
                start_time = task.preferred_window[0]
                return f"{start_time.hour:02d}:{start_time.minute:02d}"
            return "23:59"  # Tasks without preferred window go at the end
        
        return sorted(tasks, key=get_time_key)

    def detect_conflicts_with_warnings(self, entries: List['ScheduleEntry']) -> Dict[str, any]:
        """
        Detect overlapping task time slots and return detailed conflict information.
        
        Analyzes all pairs of scheduled entries to identify time overlaps between tasks.
        For each conflict found, creates a ConflictWarning with detailed information
        including severity, involved pets, tasks, and a user-friendly message.
        
        Args:
            entries (List[ScheduleEntry]): List of scheduled task entries to check for conflicts.
            
        Returns:
            Dict containing:
                - 'conflicts': List of ConflictWarning objects with detailed conflict info
                - 'warning_messages': List of user-friendly warning message strings
                - 'conflict_count': Total number of conflicts detected
                - 'has_conflicts': Boolean indicating if any conflicts were found
        """
        conflicts = []
        warning_messages = []
        
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                e1 = entries[i]
                e2 = entries[j]
                
                # Check for time overlap
                overlap = self._time_overlaps(e1, e2)
                
                if overlap:
                    # Create a conflict record
                    conflict = ConflictWarning(
                        severity="overlap",
                        pet_names=[e1.task.pet.name, e2.task.pet.name],
                        tasks=(e1.task, e2.task),
                        time_overlap=f"{max(e1.start_time, e2.start_time)} to {min(e1.end_time, e2.end_time)}",
                        message=self._generate_conflict_message(e1.task, e2.task, overlap)
                    )
                    conflicts.append(conflict)
                    warning_messages.append(conflict.message)
        
        return {
            "conflicts": conflicts,
            "warning_messages": warning_messages,
            "conflict_count": len(conflicts),
            "has_conflicts": len(conflicts) > 0
        }
    
    def _time_overlaps(self, entry1: 'ScheduleEntry', entry2: 'ScheduleEntry') -> bool:
        """Check if two scheduled time slots overlap.
        
        Determines if the time periods of two schedule entries overlap by checking
        if the start time of one is before the end time of the other and vice versa.
        
        Args:
            entry1 (ScheduleEntry): First schedule entry to compare.
            entry2 (ScheduleEntry): Second schedule entry to compare.
            
        Returns:
            bool: True if the time slots overlap, False otherwise.
        """
        return (entry1.start_time < entry2.end_time and 
                entry2.start_time < entry1.end_time)
    
    def _generate_conflict_message(self, task1: 'Task', task2: 'Task', 
                                   overlap_info: bool) -> str:
        """Generate a user-friendly warning message for a scheduling conflict.
        
        Creates a detailed message that differentiates between conflicts involving
        the same pet (more critical) versus different pets (capacity issue).
        Includes task names, durations, and actionable advice.
        
        Args:
            task1 (Task): First task involved in the conflict.
            task2 (Task): Second task involved in the conflict.
            overlap_info (bool): Whether the tasks overlap (currently unused but reserved for future enhancement).
            
        Returns:
            str: Formatted warning message with emoji, conflict details, and resolution suggestion.
        """
        pet1_name = task1.pet.name
        pet2_name = task2.pet.name
        
        if pet1_name == pet2_name:
            # Same pet: more critical
            return (f"⚠️ CONFLICT: {pet1_name} has overlapping tasks:\n"
                    f"   • {task1.name} ({task1.duration_minutes}min)\n"
                    f"   • {task2.name} ({task2.duration_minutes}min)\n"
                    f"   → Reschedule one task to resolve.")
        else:
            # Different pets: owner capacity issue
            return (f"⚠️ CONFLICT: Overlapping tasks for different pets:\n"
                    f"   • {pet1_name}: {task1.name}\n"
                    f"   • {pet2_name}: {task2.name}\n"
                    f"   → Owner may not have time for both simultaneously.")

    def generate_schedule(self, owner: 'Owner', date: date) -> 'Schedule':
        """Create a time-ordered schedule for the day, respecting preferred windows."""
        tasks = self.retrieve_tasks(owner, date)
        # Sort by preferred window start time, then by priority
        organized = self.sort_by_time(tasks)
        entries = []
        total_duration = 0
        
        for task in organized:
            if task.preferred_window:
                # Use preferred start time
                start = task.preferred_window[0]
            else:
                # Use sequential scheduling starting from 8 AM
                if entries:
                    # Start after the last task ends
                    last_end = entries[-1].end_time
                    start = last_end
                else:
                    start = time(8, 0)  # Start at 8 AM
            
            end_dt = datetime.combine(date, start) + timedelta(minutes=task.duration_minutes)
            end = end_dt.time()
            entries.append(ScheduleEntry(task=task, start_time=start, end_time=end))
            total_duration += task.duration_minutes
        
        # Build explanation with validation
        explanation_parts = [f"Scheduled {len(entries)} tasks respecting preferred windows, prioritized by urgency."]
        
        # Check capacity
        if not owner.can_fit_tasks(date):
            explanation_parts.append(f"⚠️ Warning: Total time ({total_duration}min) exceeds available time ({owner.available_time_per_day}min).")
        
        # Detect conflicts with detailed warnings
        conflict_data = self.detect_conflicts_with_warnings(entries)
        if conflict_data["has_conflicts"]:
            for msg in conflict_data["warning_messages"]:
                explanation_parts.append(msg)
        
        explanation = "\n".join(explanation_parts)
        return Schedule(date=date, entries=entries, total_duration=total_duration, confidence_explanation=explanation, conflict_info=conflict_data)

    def explain_schedule(self, schedule: 'Schedule') -> str:
        """Return the schedule's reasoning explanation."""
        return schedule.confidence_explanation

@dataclass
class Schedule:
    date: date
    entries: List[ScheduleEntry]
    total_duration: int
    confidence_explanation: str
    conflict_info: Dict = None

    def add_entry(self, task: 'Task', start: time, end: time) -> None:
        """Add a scheduled task with start and end times."""
        self.entries.append(ScheduleEntry(task=task, start_time=start, end_time=end))

    def is_over_capacity(self, max_minutes: int) -> bool:
        """Check if total duration exceeds the maximum allowed time."""
        return self.total_duration > max_minutes

    def has_conflicts(self) -> bool:
        """Check if the schedule contains any detected conflicts.
        
        Returns:
            bool: True if conflict_info exists and indicates conflicts were found, False otherwise.
        """
        return self.conflict_info and self.conflict_info.get("has_conflicts", False)
    
    def get_conflict_summary(self) -> str:
        """Get a summary string of conflict status.
        
        Returns:
            str: Either a success message if no conflicts, or a count of conflicts found.
        """
        if not self.has_conflicts():
            return "✓ No scheduling conflicts detected."
        
        count = self.conflict_info.get("conflict_count", 0)
        return f"⚠️ {count} conflict(s) found. Review warnings above."

    def format_for_ui(self) -> str:
        """Format the schedule for display to the user."""
        lines = [f"Schedule for {self.date}:"]
        for entry in self.entries:
            lines.append(f"{entry.start_time} - {entry.end_time}: {entry.task.name} for {entry.task.pet.name}")
        lines.append(f"Total time: {self.total_duration} minutes")
        lines.append(self.confidence_explanation)
        return "\n".join(lines)
