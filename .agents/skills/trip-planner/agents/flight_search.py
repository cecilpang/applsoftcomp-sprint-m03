"""Flight Search Agent."""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.file_utils import read_file, write_file, append_file
from utils.web_utils import search_flights, fetch_with_retry


class FlightSearchAgent:
    """Search for flights matching user requirements."""

    def __init__(self, config_path: str, output_path: str):
        self.config_path = Path(config_path)
        self.output_path = Path(output_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        with open(self.config_path) as f:
            return json.load(f)

    def search(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        departure = requirements.get("departure", "")
        destination = requirements.get("destination", "")
        dates = requirements.get("dates", "")
        group = requirements.get("group", "2")
        budget = requirements.get("budget", "")
        luggage = requirements.get("luggage", "")

        group_size = self._parse_group_size(group)
        budget_range = self._parse_budget(budget)
        luggage_req = self._parse_luggage(luggage)

        results = []
        sources = self.config.get("flight_sources", [])

        for source in sources:
            if source.get("fallback"):
                continue
            flights = search_flights(
                source["url"],
                departure,
                destination,
                dates,
                group_size,
                budget_range,
                luggage_req,
            )
            if flights:
                results.extend(flights)

        if len(results) < 3:
            for source in sources:
                if not source.get("fallback"):
                    continue
                flights = search_flights(
                    source["url"],
                    departure,
                    destination,
                    dates,
                    group_size,
                    budget_range,
                    luggage_req,
                )
                if flights:
                    results.extend(flights)
                    if len(results) >= 3:
                        break

        return self._filter_and_sort(results, budget_range, luggage_req)

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

    def _parse_luggage(self, luggage: str) -> Dict[str, Any]:
        check_in = re.search(r"(\d+)\s*check-?in", luggage, re.IGNORECASE)
        carry_on = re.search(r"(\d+)\s*carry-?on", luggage, re.IGNORECASE)
        return {
            "check_in_bags": int(check_in.group(1)) if check_in else 0,
            "carry_on_bags": int(carry_on.group(1)) if carry_on else 1,
        }

    def _filter_and_sort(
        self, results: List[Dict], budget_range: Dict, luggage_req: Dict
    ) -> List[Dict]:
        filtered = []
        for flight in results:
            if flight.get("price", 0) < budget_range.get("min", 0):
                continue
            if (
                budget_range.get("max", 10000)
                and flight.get("price", 0) > budget_range["max"]
            ):
                continue
            if luggage_req.get("check_in_bags", 0) > 0:
                allowance = flight.get("luggage_allowance", "")
                if not re.search(r"check-?in", allowance, re.IGNORECASE):
                    continue
            filtered.append(flight)

        filtered.sort(key=lambda x: x.get("price", 0))

        budget_options = []
        mid_options = []
        premium_options = []

        multipliers = self.config.get(
            "flight_multipliers", {"budget": 0.7, "mid_range": 1.0, "premium": 1.5}
        )
        mid_price = (
            budget_range.get("min", 1000)
            + (budget_range.get("max", 1500) - budget_range.get("min", 1000)) / 2
        )

        for flight in filtered:
            price = flight.get("price", 0)
            if price <= mid_price * multipliers["budget"]:
                budget_options.append(flight)
            elif price <= mid_price * multipliers["premium"]:
                mid_options.append(flight)
            else:
                premium_options.append(flight)

        result = []
        if budget_options:
            result.append(budget_options[0])
        if mid_options:
            result.append(mid_options[0])
        if premium_options:
            result.append(premium_options[0])

        return result[:3]

    def format_options(self, flights: List[Dict]) -> str:
        if not flights:
            return ""

        output = "\n## Flight Options\n\n"

        options = [
            ("Budget Option", flights[0] if len(flights) > 0 else None),
            ("Mid-Range Option", flights[1] if len(flights) > 1 else None),
            ("Premium Option", flights[2] if len(flights) > 2 else None),
        ]

        for label, flight in options:
            if not flight:
                continue
            output += f"### {label}\n"
            output += f"Airline: {flight.get('airline', 'N/A')}\n"
            output += f"Flight #: {flight.get('flight_number', 'N/A')}\n"
            output += f"Times: {flight.get('departure_time', 'N/A')} - {flight.get('arrival_time', 'N/A')}\n"
            output += f"Duration: {flight.get('duration', 'N/A')}\n"
            output += f"Price: ${flight.get('price', 0)} per person\n"
            output += f"Total: ${flight.get('total', 0)} ({flight.get('group_size', 2)} adults)\n"
            output += f"Luggage Allowance: {flight.get('luggage_allowance', 'N/A')}\n\n"

        output += "\n*Prices are estimates and may change. Verify before booking.*\n"
        return output

    def append_results(self, requirements: Dict[str, Any], progress_path: str):
        flights = self.search(requirements)
        formatted = self.format_options(flights)

        current = read_file(self.output_path)
        if "## Flight Options" not in current:
            current += "\n## Flight Options\n"
        current += formatted
        write_file(self.output_path, current)

        timestamp = self._get_timestamp()
        progress = read_file(progress_path)
        progress = progress.replace(
            "- [ ] Search flights", f"- [x] Search flights ({timestamp})"
        )
        write_file(progress_path, progress)

    def _get_timestamp(self) -> str:
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M")
