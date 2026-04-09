"""Trip Planner Tests."""

import sys
import os
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))
os.chdir(BASE_DIR)


def test_core():
    """Test core functionality."""
    from utils.preferences import PreferenceManager
    from utils.cost_calculator import CostCalculator
    from utils.file_utils import read_file, write_file

    print("Testing Preferences...")
    with tempfile.TemporaryDirectory() as tmpdir:
        prefs_path = Path(tmpdir) / "preferences.md"
        prefs_path.write_text("# User Preferences\n## Flight Preferences\n")
        pm = PreferenceManager(str(prefs_path))
        pm.add_explicit_preferences("prefer ANA", "TEST")
        content = pm.read_preferences()
        assert "ANA" in content

    print("Testing Cost Calculator...")
    config = {"daily_food_transport": 50, "buffer_percentage": 10}
    calc = CostCalculator(config)
    flights = [{"price": 1000}]
    hotels = [{"price_per_night": 200}]
    activities = [{"cost": 300}]
    summary = calc.calculate(flights, hotels, activities, 7, "2 adults")
    assert summary["TOTAL"] > 0

    print("Testing File Utils...")
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        write_file(test_file, "test content")
        content = read_file(test_file)
        assert content == "test content"

    print("Testing Lead Agent...")
    from agents.lead_agent import LeadAgent

    with tempfile.TemporaryDirectory() as td:
        with tempfile.TemporaryDirectory() as wd:
            (Path(td) / "preferences.md").write_text("# Prefs\n")
            (Path(td) / "trip_draft.md").write_text("# Draft\n")
            (Path(td) / "trip_final.md").write_text("# Final\n")
            (Path(td) / "progress.txt").write_text("# Progress\n")
            (Path(td) / "requirements.txt").write_text("# Reqs\n")
            agent = LeadAgent(str(wd), str(td))
            agent.initialize_session()
            assert (Path(wd) / "progress.txt").exists()
            routes = agent.route_revision("change hotel")
            assert "hotels" in routes

    print("ALL TESTS PASSED!")


if __name__ == "__main__":
    test_core()
