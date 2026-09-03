import asyncio

from mcp_server.tools.workouts import get_workout_history, log_workout


def test_log_and_get_workout_history():
    user_id = "test-user-log-and-history"

    logged = asyncio.run(log_workout(user_id, "squat", sets=3, reps=10, weight_kg=60))
    assert logged == {"exercise": "squat", "sets": 3, "reps": 10, "weight_kg": 60}

    history = asyncio.run(get_workout_history(user_id))
    assert history == [{"exercise": "squat", "sets": 3, "reps": 10, "weight_kg": 60}]


def test_get_workout_history_respects_limit():
    user_id = "test-user-limit"
    for i in range(3):
        asyncio.run(log_workout(user_id, f"exercise-{i}", sets=1, reps=1))

    history = asyncio.run(get_workout_history(user_id, limit=2))
    assert [entry["exercise"] for entry in history] == ["exercise-1", "exercise-2"]
