from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, time
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
        pass

    def remove_pet(self, pet: 'Pet') -> None:
        pass

    def add_task(self, task: 'Task') -> None:
        pass

    def plan_daily_schedule(self, date: date) -> 'Schedule':
        pass

    def explain_schedule(self, schedule: 'Schedule') -> str:
        pass

@dataclass
class Pet:
    name: str
    type: str
    age: int
    needs: Dict[str, Any]
    owner: 'Owner'
    tasks: List['Task']

    def add_task(self, task: 'Task') -> None:
        pass

    def get_pending_tasks(self, date: date) -> List['Task']:
        pass

    def total_required_time(self, date: date) -> int:
        pass

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
        pass

    def reschedule(self, new_time: time) -> None:
        pass

    def is_due(self, date: date) -> bool:
        pass

    def score_for_planning(self, owner_preferences: Dict[str, Any], constraints: Dict[str, Any]) -> float:
        pass

@dataclass
class Schedule:
    date: date
    entries: List[ScheduleEntry]
    total_duration: int
    confidence_explanation: str

    def add_entry(self, task: 'Task', start: time, end: time) -> None:
        pass

    def is_over_capacity(self, max_minutes: int) -> bool:
        pass

    def format_for_ui(self) -> str:
        pass
