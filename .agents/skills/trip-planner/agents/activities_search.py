"""Activities Search Agent."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.file_utils import read_file, write_file
from utils.web_utils import search_activities


class ActivitiesSearchAgent:
    """Search for activities matching user interests."""

    def __init__(self, config_path: str, output_path: str):
        self.config_path = Path(config_path)
        self.output_path = Path(output_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        with open(self.config_path) as f:
            return json.load(f)

    def search(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        destination = requirements.get("destination", "")
        dates = requirements.get("dates", "")
        group = requirements.get("group", "2")
        budget = requirements.get("budget", "")
        interests = requirements.get("interests", "")

        group_size = self._parse_group_size(group)
        budget_per_day = self._parse_budget_per_day(budget)
        num_days = self._parse_duration(dates)

        results = []
        sources = self.config.get("activity_sources", [])

        for source in sources:
            if source.get("fallback"):
                continue
            activities = search_activities(
                source["url"], destination, dates, group_size, budget_per_day, interests
            )
            if activities:
                results.extend(activities)

        if len(results) < num_days * 2:
            for source in sources:
                if not source.get("fallback"):
                    continue
                activities = search_activities(
                    source["url"],
                    destination,
                    dates,
                    group_size,
                    budget_per_day,
                    interests,
                )
                if activities:
                    results.extend(activities)
                    if len(results) >= num_days * 2:
                        break

        return self._filter_and_prioritize(results, interests, num_days)

    def _parse_group_size(self, group: str) -> int:
        match = re.search(r"(\d+)", group)
        return int(match.group(1)) if match else 2

    def _parse_budget_per_day(self, budget: str) -> int:
        numbers = re.findall(r"\d+", budget.replace(",", ""))
        if len(numbers) >= 2:
            total = int(numbers[1])
            return total // 7
        return 100

    def _parse_duration(self, dates: str) -> int:
        match = re.search(r"(\d+)\s*day", dates, re.IGNORECASE)
        if match:
            return int(match.group(1))
        date_patterns = re.findall(r"\d{4}-\d{2}-\d{2}", dates)
        if len(date_patterns) >= 2:
            from datetime import datetime

            d1 = datetime.strptime(date_patterns[0], "%Y-%m-%d")
            d2 = datetime.strptime(date_patterns[1], "%Y-%m-%d")
            return (d2 - d1).days
        return 7

    def _filter_and_prioritize(
        self, results: List[Dict], interests: str, num_days: int
    ) -> List[Dict]:
        interest_list = [i.strip().lower() for i in interests.split(",")]

        category_map = {
            "food": ["food", "dining", "restaurant", "culinary", "food tour"],
            "temple": ["temple", "shrine", "culture", "historical", "museum"],
            "shopping": ["shopping", "market", "mall", "shopping district"],
            "relaxation": ["relaxation", "spa", "onsen", "garden", "nature"],
        }

        categorized = {cat: [] for cat in category_map}
        categorized["other"] = []

        for activity in results:
            desc = (
                activity.get("description", "") + " " + activity.get("name", "")
            ).lower()
            assigned = False
            for cat, keywords in category_map.items():
                if any(kw in desc for kw in keywords):
                    categorized[cat].append(activity)
                    assigned = True
                    break
            if not assigned:
                categorized["other"].append(activity)

        prioritized = []
        target_per_day = 2

        for _ in range(target_per_day):
            for cat in ["food", "temple", "shopping", "relaxation"]:
                if categorized[cat]:
                    prioritized.append(categorized[cat].pop(0))

        while len(prioritized) < num_days * target_per_day:
            if categorized["other"]:
                prioritized.append(categorized["other"].pop(0))
            else:
                break

        return prioritized[: num_days * target_per_day]

    def format_options(self, activities: List[Dict]) -> str:
        if not activities:
            return ""

        output = "\n## Activities & Attractions\n\n"

        for i, activity in enumerate(activities, 1):
            output += f"### {i}. {activity.get('name', 'N/A')}\n"
            output += f"Description: {activity.get('description', 'N/A')}\n"
            output += f"Location: {activity.get('location', 'N/A')}\n"
            output += f"Cost: ${activity.get('cost', 0)}\n"
            output += f"Duration: {activity.get('duration', 'N/A')}\n"
            output += f"Booking: {activity.get('booking_platform', 'N/A')}\n"
            output += f"Hours: {activity.get('hours', 'N/A')}\n"

            if activity.get("advance_booking"):
                output += f"Note: Advance booking required\n"
            if activity.get("seasonal_closure"):
                output += f"Warning: {activity.get('seasonal_closure')}\n"
            output += "\n"

        output += "\n*Prices are estimates and may change. Verify before booking.*\n"
        return output

    def append_results(self, requirements: Dict[str, Any], progress_path: str):
        activities = self.search(requirements)
        formatted = self.format_options(activities)

        current = read_file(self.output_path)
        if "## Activities & Attractions" not in current:
            current += "\n## Activities & Attractions\n"
        current += formatted
        write_file(self.output_path, current)

        timestamp = self._get_timestamp()
        progress = read_file(progress_path)
        progress = progress.replace(
            "- [ ] Search activities", f"- [x] Search activities ({timestamp})"
        )
        write_file(progress_path, progress)

    def _get_timestamp(self) -> str:
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M")
