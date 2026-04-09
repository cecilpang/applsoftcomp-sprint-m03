"""Finalization Agent - Creates approved trip_final.md."""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.file_utils import read_file, write_file
from utils.preferences import PreferenceManager


class FinalizationAgent:
    """Finalize trip plan after user approval."""

    def __init__(self, draft_path: str, final_path: str, preferences_path: str):
        self.draft_path = Path(draft_path)
        self.final_path = Path(final_path)
        self.preferences_path = Path(preferences_path)
        self.pref_manager = PreferenceManager(preferences_path)

    def finalize(
        self, requirements: Dict[str, Any], feedback: str, session_id: str
    ) -> str:
        draft_content = read_file(self.draft_path)

        output = self._format_final(draft_content, requirements)

        write_file(self.final_path, output)

        self.pref_manager.add_explicit_preferences(feedback, session_id)
        self.pref_manager.add_inferred_preferences(requirements, session_id)

        return output

    def _format_final(self, draft_content: str, requirements: Dict[str, Any]) -> str:
        session_id = requirements.get("session_id", "N/A")

        output = f"# Trip Plan: {requirements.get('destination', 'TBD')}\n\n"
        output += f"Session ID: {session_id}\n\n"

        output += "## Travelers\n"
        output += f"Group: {requirements.get('group', 'TBD')}\n"
        output += f"Dates: {requirements.get('dates', 'TBD')}\n"
        output += f"Departure: {requirements.get('departure', 'TBD')} to {requirements.get('destination', 'TBD')}\n\n"

        itinerary_match = re.search(
            r"## Itinerary\n(.*?)(?=## Cost Summary|$)", draft_content, re.DOTALL
        )
        if itinerary_match:
            output += "## Itinerary\n"
            output += itinerary_match.group(1)

        flights_match = re.search(
            r"## Flight Options\n(.*?)(?=##|\Z)", draft_content, re.DOTALL
        )
        hotels_match = re.search(
            r"## Hotel Options\n(.*?)(?=##|\Z)", draft_content, re.DOTALL
        )

        output += "\n## Bookings\n\n### Flights\n"
        if flights_match:
            flights_section = flights_match.group(0)
            mid_flight = re.search(
                r"### Mid-Range Option\n(.*?)(?=###|\Z)", flights_section, re.DOTALL
            )
            if mid_flight:
                lines = mid_flight.group(1).strip().split("\n")
                for line in lines:
                    if line.startswith("Airline:"):
                        output += f"Selected: {line.replace('Airline:', '').strip()}\n"
                    if line.startswith("Flight #:"):
                        output += f"Flight: {line.replace('Flight #:', '').strip()}\n"
                    if line.startswith("Times:"):
                        output += f"Times: {line.replace('Times:', '').strip()}\n"
        output += "Book on: [Platform name]\n\n"

        output += "### Hotels\n"
        if hotels_match:
            hotels_section = hotels_match.group(0)
            mid_hotel = re.search(
                r"### Mid-Range Option\n(.*?)(?=###|\Z)", hotels_section, re.DOTALL
            )
            if mid_hotel:
                lines = mid_hotel.group(1).strip().split("\n")
                for line in lines:
                    if line.startswith("Name:"):
                        output += f"Selected: {line.replace('Name:', '').strip()}\n"
                    if line.startswith("Location:"):
                        output += f"Address: {line.replace('Location:', '').strip()}\n"
        output += "Book on: [Platform name]\n\n"

        output += "### Activities & Tours\n"
        activities_match = re.search(
            r"## Activities.*?(?=## Cost Summary|$)", draft_content, re.DOTALL
        )
        if activities_match:
            output += activities_match.group(0)
            output += "\n"

        cost_match = re.search(
            r"## Cost Summary\n(.*?)(?=##|\Z)", draft_content, re.DOTALL
        )
        output += "\n## Cost Summary\n"
        if cost_match:
            output += cost_match.group(1)
        else:
            output += "- Flights: $[X]\n- Hotels: $[X]\n- Activities: $[X]\n- Buffer (10%): $[X]\n- **TOTAL: $[X]**\n"
        output += "\n"

        sections = [
            ("Visa/Entry Requirements", "visa"),
            ("Emergency Contacts", "emergency"),
            ("Travel Tips", "tips"),
            ("Travel Warnings", "warnings"),
            ("Price Disclaimer", "disclaimer"),
        ]

        for section_name, key in sections:
            match = re.search(
                rf"## {section_name}\n(.*?)(?=##|\Z)", draft_content, re.DOTALL
            )
            output += f"\n## {section_name}\n"
            if match:
                output += match.group(1).strip()
            else:
                output += "[To be added]"
            output += "\n"

        output += f"\n## Approval\nPlan approved by user: [x]\nDate finalized: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"

        return output
