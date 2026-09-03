import asyncio

import pytest

from mcp_server.tools.nutrition import calculate_protein_intake


def test_calculate_protein_intake_general_fitness():
    result = asyncio.run(calculate_protein_intake(70, goal="general_fitness"))
    assert result == {
        "weight_kg": 70,
        "goal": "general_fitness",
        "protein_g_min": 84.0,
        "protein_g_max": 112.0,
    }


def test_calculate_protein_intake_defaults_to_general_fitness():
    result = asyncio.run(calculate_protein_intake(70))
    assert result["goal"] == "general_fitness"


def test_calculate_protein_intake_muscle_gain_is_higher_than_sedentary():
    sedentary = asyncio.run(calculate_protein_intake(80, goal="sedentary"))
    muscle_gain = asyncio.run(calculate_protein_intake(80, goal="muscle_gain"))
    assert muscle_gain["protein_g_min"] > sedentary["protein_g_max"]


def test_calculate_protein_intake_rejects_non_positive_weight():
    with pytest.raises(ValueError):
        asyncio.run(calculate_protein_intake(0))
