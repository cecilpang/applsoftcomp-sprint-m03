"""Planning Agent - Creates draft itinerary."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.file_utils import read_file, write_file
from utils.cost_calculator import CostCalculator
from utils.web_utils import (
    fetch_visa_requirements,
    fetch_emergency_contacts,
    fetch_travel_warnings,
)


class PlanningAgent:
    """Create day-by-day itinerary from search results."""

    def __init__(self, draft_path: str, preferences_path: str, config_path: str):
        self.draft_path = Path(draft_path)
        self.preferences_path = Path(preferences_path)
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.cost_calc = CostCalculator(self.config)

    def _load_config(self) -> Dict:
        with open(self.config_path) as f:
            return json.load(f)

    def create_itinerary(self, requirements: Dict[str, Any]) -> str:
        draft_content = read_file(self.draft_path)
        preferences = self._read_preferences()

        dates = requirements.get("dates", "")
        num_days = self._parse_duration(dates)

        flights = self._extract_flights(draft_content)
        hotels = self._extract_hotels(draft_content)
        activities = self._extract_activities(draft_content)

        itinerary = self._build_itinerary(
            num_days, flights, hotels, activities, requirements
        )

        cost_summary = self.cost_calc.calculate(
            flights, hotels, activities, num_days, requirements.get("group", "2")
        )

        visa_info = self._fetch_visa_info(requirements.get("destination", ""))
        emergency = self._fetch_emergency_info(requirements.get("destination", ""))
        warnings = self._fetch_warnings(requirements.get("destination", ""))

        output = self._format_output(
            requirements, itinerary, cost_summary, visa_info, emergency, warnings
        )

        write_file(self.draft_path, output)
        return output

    def _read_preferences(self) -> str:
        if self.preferences_path.exists():
            return read_file(self.preferences_path)
        return ""

    def _parse_duration(self, dates: str) -> int:
        match = re.search(r"(\d+)\s*day", dates, re.IGNORECASE)
        if match:
            return int(match.group(1))
        date_patterns = re.findall(r"\d{4}-\d{2}-\d{2}", dates)
        if len(date_patterns) >= 2:
            d1 = datetime.strptime(date_patterns[0], "%Y-%m-%d")
            d2 = datetime.strptime(date_patterns[1], "%Y-%m-%d")
            return (d2 - d1).days
        return 7

    def _extract_flights(self, content: str) -> List[Dict]:
        flights = []
        section = re.search(
            r"## Flight Options.*?(?=##|\Z)", content, re.DOTALL | re.IGNORECASE
        )
        if not section:
            return flights

        options = re.findall(
            r"### (?:Budget|Mid-Range|Premium) Option.*?(?=###|\Z)",
            section.group(0),
            re.DOTALL,
        )
        for opt in options:
            flight = {}
            flight["airline"] = self._extract_field(opt, "Airline:")
            flight["flight_number"] = self._extract_field(opt, "Flight #:")
            flight["times"] = self._extract_field(opt, "Times:")
            flight["duration"] = self._extract_field(opt, "Duration:")
            flight["price"] = self._extract_price(opt)
            flight["luggage"] = self._extract_field(opt, "Luggage Allowance:")
            if flight.get("airline"):
                flights.append(flight)
        return flights

    def _extract_hotels(self, content: str) -> List[Dict]:
        hotels = []
        section = re.search(
            r"## Hotel Options.*?(?=##|\Z)", content, re.DOTALL | re.IGNORECASE
        )
        if not section:
            return hotels

        options = re.findall(
            r"### (?:Budget|Mid-Range|Premium) Option.*?(?=###|\Z)",
            section.group(0),
            re.DOTALL,
        )
        for opt in options:
            hotel = {}
            hotel["name"] = self._extract_field(opt, "Name:")
            hotel["location"] = self._extract_field(opt, "Location:")
            hotel["rating"] = self._extract_field(opt, "Rating:")
            hotel["price_per_night"] = self._extract_price(opt)
            hotel["cancellation"] = self._extract_field(opt, "Cancellation:")
            if hotel.get("name"):
                hotels.append(hotel)
        return hotels

    def _extract_activities(self, content: str) -> List[Dict]:
        activities = []
        section = re.search(
            r"## Activities.*?(?=##|\Z)", content, re.DOTALL | re.IGNORECASE
        )
        if not section:
            return activities

        items = re.findall(
            r"### \d+\. (.*?)\n.*?Description: (.*?)\n", section.group(0), re.DOTALL
        )
        for name, desc in items:
            activity = {"name": name.strip(), "description": desc.strip()}
            cost_match = re.search(r"Cost: \$?(\d+)", section.group(0))
            if cost_match:
                activity["cost"] = int(cost_match.group(1))
            activities.append(activity)
        return activities

    def _extract_field(self, text: str, field: str) -> str:
        match = re.search(rf"{field}\s*(.+?)(?:\n|$)", text)
        return match.group(1).strip() if match else ""

    def _extract_price(self, text: str) -> int:
        match = re.search(r"\$(\d+)", text)
        return int(match.group(1)) if match else 0

    def _build_itinerary(
        self,
        num_days: int,
        flights: List,
        hotels: List,
        activities: List,
        requirements: Dict,
    ) -> List[Dict]:
        itinerary = []
        date_str = requirements.get("dates", "")
        start_date = self._parse_start_date(date_str)

        for day in range(1, num_days + 1):
            current_date = start_date + timedelta(days=day - 1)
            day_plan = {
                "day": day,
                "date": current_date.strftime("%Y-%m-%d"),
                "weekday": current_date.strftime("%A"),
                "morning": None,
                "afternoon": None,
                "evening": None,
            }

            idx = (day - 1) * 2
            if idx < len(activities):
                day_plan["morning"] = activities[idx]
            if idx + 1 < len(activities):
                day_plan["afternoon"] = activities[idx + 1]

            if day == 1 and flights:
                day_plan["evening"] = {
                    "name": "Arrive at destination",
                    "description": f"Flight {flights[0].get('airline', '')}",
                }
            elif day == num_days and flights:
                day_plan["evening"] = {
                    "name": "Departure",
                    "description": "Return flight",
                }

            itinerary.append(day_plan)

        return itinerary

    def _parse_start_date(self, dates: str) -> datetime:
        match = re.search(r"(\d{4}-\d{2}-\d{2})", dates)
        if match:
            return datetime.strptime(match.group(1), "%Y-%m-%d")
        return datetime.now()

    def _fetch_visa_info(self, destination: str) -> str:
        try:
            return fetch_visa_requirements(destination)
        except:
            return "Check visa requirements for your nationality before travel."

    def _fetch_emergency_info(self, destination: str) -> Dict[str, str]:
        try:
            return fetch_emergency_contacts(destination)
        except:
            return {
                "local_emergency": "112 or local emergency number",
                "embassy": "Check your country's embassy website",
            }

    def _fetch_warnings(self, destination: str) -> str:
        try:
            return fetch_travel_warnings(destination)
        except:
            return "No current travel warnings."

    def _format_output(
        self,
        requirements: Dict,
        itinerary: List,
        cost_summary: Dict,
        visa_info: str,
        emergency: Dict,
        warnings: str,
    ) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        output = f"# Trip Plan Draft: {requirements.get('destination', 'TBD')}\n\n"
        output += f"Last Updated: {timestamp}\n\n"
        output += f"## Trip Details\n"
        output += f"Departure: {requirements.get('departure', 'TBD')}\n"
        output += f"Destination: {requirements.get('destination', 'TBD')}\n"
        output += f"Dates: {requirements.get('dates', 'TBD')}\n"
        output += f"Group: {requirements.get('group', 'TBD')}\n"
        output += f"Budget: {requirements.get('budget', 'TBD')}\n\n"

        output += "## Itinerary\n\n"
        for day in itinerary:
            output += f"### Day {day['day']}: {day['date']} ({day['weekday']})\n"
            if day.get("morning"):
                output += f"- Morning: {day['morning'].get('name', 'TBD')} - {day['morning'].get('description', '')}\n"
            if day.get("afternoon"):
                output += f"- Afternoon: {day['afternoon'].get('name', 'TBD')} - {day['afternoon'].get('description', '')}\n"
            if day.get("evening"):
                output += f"- Evening: {day['evening'].get('name', 'TBD')} - {day['evening'].get('description', '')}\n"
            output += "\n"

        output += "## Cost Summary\n"
        for key, value in cost_summary.items():
            output += f"- {key}: ${value}\n"
        output += "\n"

        output += f"## Visa/Entry Requirements\n{visa_info}\n\n"
        output += f"## Emergency Contacts\nLocal Emergency: {emergency.get('local_emergency', 'N/A')}\nEmbassy: {emergency.get('embassy', 'N/A')}\n\n"
        output += f"## Travel Tips\n- Transportation: Use public transit or ride-sharing apps\n- Currency: Exchange currency at local banks or ATMs\n- Customs: Check local customs regulations\n\n"

        output += f"## Travel Warnings\n{warnings}\n\n"
        output += f"## Price Disclaimer\n*Prices are estimates and may change. Verify all prices and bookings before confirming.*\n"

        return output
