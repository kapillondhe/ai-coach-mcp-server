from mcp_server.data.store import WorkoutEntry, store


async def log_workout(
    user_id: str,
    exercise: str,
    sets: int,
    reps: int,
    weight_kg: float | None = None,
) -> dict:
    """Record a completed workout set for a user.

    Args:
        user_id: Unique identifier for the user.
        exercise: Name of the exercise, e.g. "squat".
        sets: Number of sets performed.
        reps: Number of reps per set.
        weight_kg: Weight used, in kilograms, if applicable.
    """
    entry = WorkoutEntry(exercise=exercise, sets=sets, reps=reps, weight_kg=weight_kg)
    store.add_workout(user_id, entry)
    return {
        "exercise": entry.exercise,
        "sets": entry.sets,
        "reps": entry.reps,
        "weight_kg": entry.weight_kg,
    }


async def get_workout_history(user_id: str, limit: int = 10) -> list[dict]:
    """Get a user's most recent logged workouts, most recent last.

    Args:
        user_id: Unique identifier for the user.
        limit: Maximum number of workouts to return.
    """
    return [
        {
            "exercise": entry.exercise,
            "sets": entry.sets,
            "reps": entry.reps,
            "weight_kg": entry.weight_kg,
        }
        for entry in store.get_workouts(user_id, limit)
    ]
