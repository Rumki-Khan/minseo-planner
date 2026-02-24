


import os
import pytest
from minseo_planner.data_loader import DataLoader
from minseo_planner.models import Relative, TransportMode
from minseo_planner.scoring import ScoringEngine
from minseo_planner.decorators import measure_runtime

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------
# TEST 1 — Data Loading
# ---------------------------------------------------------
def test_load_relatives():
    loader = DataLoader()
    relatives = loader.load_relatives("relatives.csv")
    assert len(relatives) > 0
    assert isinstance(relatives[0], Relative)

def test_load_transport_modes():
    loader = DataLoader()
    modes = loader.load_transport("transport.csv")       
    assert len(modes) > 0
    assert isinstance(modes[0], TransportMode)



# ---------------------------------------------------------
# TEST 2 — Scoring Engine
# ---------------------------------------------------------
def test_scoring_full_bonus():
    scoring = ScoringEngine(alpha=0.05, beta=0.02)

    # Fake relative
    r = Relative(
        name="Test",
        district="Gangnam",
        latitude=0,
        longitude=0,
        preferred_days=["Mon"],
        preferred_window=("18:00", "20:00"),
        happiness_bonus=10,
        duration=60
    )

    visit = {
        "name": "Test",
        "arrival": "18:30",
        "travel_time": 10,
        "cost": 5,
        "day": "Mon"
    }

    score = scoring.compute_visit_score(visit, r)
    assert score == 10  # full bonus


def test_scoring_half_bonus():
    scoring = ScoringEngine(alpha=0.05, beta=0.02)

    r = Relative(
        name="Test",
        district="Gangnam",
        latitude=0,
        longitude=0,
        preferred_days=["Mon"],
        preferred_window=("18:00", "20:00"),
        happiness_bonus=10,
        duration=60
    )

    visit = {
        "name": "Test",
        "arrival": "21:00",  # outside preferred window
        "travel_time": 10,
        "cost": 5,
        "day": "Mon"
    }

    score = scoring.compute_visit_score(visit, r)
    assert score == 5  # half bonus


# ---------------------------------------------------------
# TEST 3 — Regex Validation
# ---------------------------------------------------------
def test_time_validation():
    scoring = ScoringEngine()

    scoring.validate_time("18:30")  # should not raise

    with pytest.raises(ValueError):
        scoring.validate_time("invalid")


# ---------------------------------------------------------
# TEST 4 — Decorator (measure_runtime)
# ---------------------------------------------------------
def test_measure_runtime_decorator(capsys):
    @measure_runtime
    def dummy():
        return 42

    result = dummy()
    captured = capsys.readouterr()

    assert result == 42
    assert "completed in" in captured.out  # decorator printed runtime


# ---------------------------------------------------------
# TEST 5 — Fatigue Penalty
# ---------------------------------------------------------
def test_fatigue_penalty():
    scoring = ScoringEngine()

    schedule = {
        "Sat": [{"name": "A"}, {"name": "B"}, {"name": "C"}],
        "Sun": [],
        "Mon": []
    }

    penalty = scoring.compute_fatigue_penalty(schedule)
    assert penalty == -2  # only Sat has 3 visits
