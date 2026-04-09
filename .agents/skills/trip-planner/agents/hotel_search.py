"""Hotel Search Agent."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.file_utils import read_file, write_file
from utils.web_utils import search_hotels


class HotelSearchAgent:
    """Search for hotels matching user requirements."""

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
        preferences = requirements.get("preferences", {})

        group_size = self._parse_group_size(group)
        budget_range = self._parse_budget(budget)
        num_nights = self._parse_dates(dates)

        results = []
        sources = self.config.get("hotel_sources", [])

        for source in sources:
            if source.get("fallback"):
                continue
            hotels = search_hotels(
                source["url"], destination, dates, group_size, budget_range, preferences
            )
            if hotels:
                results.extend(hotels)

        if len(results) < 3:
            for source in sources:
                if not source.get("fallback"):
                    continue
                hotels = search_hotels(
                    source["url"],
                    destination,
                    dates,
                    group_size,
                    budget_range,
                    preferences,
                )
                if hotels:
                    results.extend(hotels)
                    if len(results) >= 3:
                        break

        return self._filter_and_sort(results, budget_range, preferences)

    def _parse_group_size(self, group: str) -> int:
        match = re.search(r"(\d+)", group)
        return int(match.group(1)) if match else 2

    def _parse_budget(self, budget: str) -> Dict[str, int]:
        numbers = re.findall(r"\d+", budget.replace(",", ""))
        if len(numbers) >= 2:
            return {"min": int(numbers[0]), "max": int(numbers[1])}
        elif len(numbers) == 1:
            return {"min": 0, "max": int(numbers[0])}
        return {"min": 0, "max": 10000}

    def _parse_dates(self, dates: str) -> int:
        match = re.search(r"(\d+)\s*night", dates, re.IGNORECASE)
        if match:
            return int(match.group(1))
        date_patterns = re.findall(r"\d{4}-\d{2}-\d{2}", dates)
        if len(date_patterns) >= 2:
            from datetime import datetime

            d1 = datetime.strptime(date_patterns[0], "%Y-%m-%d")
            d2 = datetime.strptime(date_patterns[1], "%Y-%m-%d")
            return (d2 - d1).days
        return 7

    def _filter_and_sort(
        self, results: List[Dict], budget_range: Dict, preferences: Dict
    ) -> List[Dict]:
        filtered = []
        mid_price = self.config.get("mid_range_hotel_price", 200)

        for hotel in results:
            price = hotel.get("price_per_night", 0)
            if price < budget_range.get("min", 0):
                continue
            if budget_range.get("max", 10000) and price > budget_range["max"]:
                continue
            filtered.append(hotel)

        filtered.sort(key=lambda x: x.get("price_per_night", 0))

        budget_options = []
        mid_options = []
        premium_options = []

        multipliers = self.config.get(
            "hotel_multipliers", {"budget": 0.5, "mid_range": 1.0, "premium": 2.0}
        )

        for hotel in filtered:
            price = hotel.get("price_per_night", 0)
            if price <= mid_price * multipliers["budget"]:
                budget_options.append(hotel)
            elif price <= mid_price * multipliers["premium"]:
                mid_options.append(hotel)
            else:
                premium_options.append(hotel)

        result = []
        if budget_options:
            result.append(budget_options[0])
        if mid_options:
            result.append(mid_options[0])
        if premium_options:
            result.append(premium_options[0])

        return result[:3]

    def format_options(self, hotels: List[Dict], num_nights: int) -> str:
        if not hotels:
            return ""

        output = "\n## Hotel Options\n\n"

        options = [
            ("Budget Option", hotels[0] if len(hotels) > 0 else None),
            ("Mid-Range Option", hotels[1] if len(hotels) > 1 else None),
            ("Premium Option", hotels[2] if len(hotels) > 2 else None),
        ]

        for label, hotel in options:
            if not hotel:
                continue
            total = hotel.get("price_per_night", 0) * num_nights
            output += f"### {label}\n"
            output += f"Name: {hotel.get('name', 'N/A')}\n"
            output += f"Location: {hotel.get('location', 'N/A')}\n"
            output += f"Rating: {hotel.get('rating', 'N/A')}\n"
            output += f"Amenities: {hotel.get('amenities', 'N/A')}\n"
            output += f"Price: ${hotel.get('price_per_night', 0)}/night\n"
            output += f"Total: ${total} ({num_nights} nights)\n"
            output += f"Cancellation: {hotel.get('cancellation_policy', 'N/A')}\n\n"

        output += "\n*Prices are estimates and may change. Verify before booking.*\n"
        return output

    def append_results(self, requirements: Dict[str, Any], progress_path: str):
        dates = requirements.get("dates", "")
        num_nights = self._parse_dates(dates)

        hotels = self.search(requirements)
        formatted = self.format_options(hotels, num_nights)

        current = read_file(self.output_path)
        if "## Hotel Options" not in current:
            current += "\n## Hotel Options\n"
        current += formatted
        write_file(self.output_path, current)

        timestamp = self._get_timestamp()
        progress = read_file(progress_path)
        progress = progress.replace(
            "- [ ] Search hotels", f"- [x] Search hotels ({timestamp})"
        )
        write_file(progress_path, progress)

    def _get_timestamp(self) -> str:
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M")
