from dataclasses import dataclass


@dataclass
class WorkoutEntry:
    exercise: str
    sets: int
    reps: int
    weight_kg: float | None = None


class InMemoryStore:
    """Placeholder repository - swap for real persistence once a DB is chosen.

    Kept as a plain in-process object (not a DB client) so tools stay simple
    to unit test; the tool functions in tools/workouts.py are the boundary
    that would need to change if this is replaced.
    """

    def __init__(self) -> None:
        self._workouts: dict[str, list[WorkoutEntry]] = {}

    def add_workout(self, user_id: str, entry: WorkoutEntry) -> None:
        self._workouts.setdefault(user_id, []).append(entry)

    def get_workouts(self, user_id: str, limit: int) -> list[WorkoutEntry]:
        return self._workouts.get(user_id, [])[-limit:]


store = InMemoryStore()
