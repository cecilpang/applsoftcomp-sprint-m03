"""Preference learning system."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class PreferenceManager:
    """Manage user preferences across sessions."""

    def __init__(self, preferences_path: str):
        self.preferences_path = Path(preferences_path)

    def read_preferences(self) -> str:
        """Read existing preferences."""
        if not self.preferences_path.exists():
            return ""
        with open(self.preferences_path, "r", encoding="utf-8") as f:
            return f.read()

    def has_preferences(self) -> bool:
        """Check if preferences file has content."""
        content = self.read_preferences()
        return bool(content.strip() and "## Flight Preferences" in content)

    def add_explicit_preferences(self, feedback: str, session_id: str):
        """Add explicit preferences from user feedback."""
        if not feedback:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d")

        content = self.read_preferences()

        flight_prefs = self._extract_flight_prefs(feedback)
        hotel_prefs = self._extract_hotel_prefs(feedback)
        activity_prefs = self._extract_activity_prefs(feedback)

        sections = []

        if flight_prefs:
            sections.append(
                f"## Flight Preferences\n{flight_prefs} (added: {timestamp}, session: {session_id})"
            )
        if hotel_prefs:
            sections.append(
                f"## Hotel Preferences\n{hotel_prefs} (added: {timestamp}, session: {session_id})"
            )
        if activity_prefs:
            sections.append(
                f"## Activity Preferences\n{activity_prefs} (added: {timestamp}, session: {session_id})"
            )

        if sections:
            content += "\n\n" + "\n\n".join(sections)

            with open(self.preferences_path, "w", encoding="utf-8") as f:
                f.write(content)

    def add_inferred_preferences(self, requirements: Dict, session_id: str):
        """Infer preferences from user choices."""
        timestamp = datetime.now().strftime("%Y-%m-%d")

        inferred = []

        budget = requirements.get("budget", "")
        if budget:
            numbers = re.findall(r"\d+", budget.replace(",", ""))
            if numbers:
                inferred.append(f"Budget: {budget} (inferred: {timestamp})")

        group = requirements.get("group", "")
        if group:
            inferred.append(f"Group size: {group} (inferred: {timestamp})")

        interests = requirements.get("interests", "")
        if interests:
            inferred.append(f"Interests: {interests} (inferred: {timestamp})")

        if inferred:
            content = self.read_preferences()
            content += "\n\n## Inferred Preferences\n" + "\n".join(inferred)

            with open(self.preferences_path, "w", encoding="utf-8") as f:
                f.write(content)

    def _extract_flight_prefs(self, text: str) -> str:
        prefs = []
        text_lower = text.lower()

        airlines = [
            "ana",
            "j al",
            "united",
            "delta",
            "air france",
            "lufthansa",
            "singapore air",
        ]
        for airline in airlines:
            if airline in text_lower:
                prefs.append(f"Airline preference: {airline.upper()}")

        if "window" in text_lower:
            prefs.append("Seat preference: Window")
        elif "aisle" in text_lower:
            prefs.append("Seat preference: Aisle")

        if "direct" in text_lower or "nonstop" in text_lower:
            prefs.append("Preference: Non-stop flights")

        return "\n".join(prefs) if prefs else ""

    def _extract_hotel_prefs(self, text: str) -> str:
        prefs = []
        text_lower = text.lower()

        if "budget" in text_lower:
            prefs.append("Price range: Budget")
        elif "mid-range" in text_lower or "mid range" in text_lower:
            prefs.append("Price range: Mid-range")
        elif "premium" in text_lower or "luxury" in text_lower:
            prefs.append("Price range: Premium")

        if "central" in text_lower or "downtown" in text_lower:
            prefs.append("Location: Central/Downtown")

        if "clean" in text_lower:
            prefs.append("Amenity: Clean")

        return "\n".join(prefs) if prefs else ""

    def _extract_activity_prefs(self, text: str) -> str:
        prefs = []
        text_lower = text.lower()

        interests = [
            "food",
            "temple",
            "culture",
            "shopping",
            "relaxation",
            "adventure",
            "sightseeing",
        ]
        for interest in interests:
            if interest in text_lower:
                prefs.append(f"Interest: {interest.title()}")

        if "relaxed" in text_lower:
            prefs.append("Pace: Relaxed")
        elif "active" in text_lower:
            prefs.append("Pace: Active")

        return "\n".join(prefs) if prefs else ""

    def append_past_feedback(self, session_id: str, feedback: str):
        """Append session feedback to Past Feedback section."""
        timestamp = datetime.now().strftime("%Y-%m-%d")

        content = self.read_preferences()

        past_section = "## Past Feedback\n"
        if past_section not in content:
            content += f"\n\n{past_section}"

        content += f"\n### Session {session_id} ({timestamp})\n{feedback}\n"

        with open(self.preferences_path, "w", encoding="utf-8") as f:
            f.write(content)
