"""Lead Agent - Trip Coordinator."""

import os
import json
import shutil
import datetime
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.file_utils import copy_templates, read_file, write_file, append_file
from utils.preferences import PreferenceManager
from utils.cost_calculator import CostCalculator


class LeadAgent:
    """Coordinates trip planning workflow."""

    def __init__(self, working_dir: str, templates_dir: str):
        self.working_dir = Path(working_dir)
        self.templates_dir = Path(templates_dir)
        self.session_id = self._generate_session_id()
        self.revision_count = 0
        self.max_revisions = 5
        self.requirements = {}
        self.pref_manager = PreferenceManager(self.working_dir / "preferences.md")

    def _generate_session_id(self) -> str:
        return datetime.datetime.now().strftime("%Y%m%d-%H%M")

    def _generate_timestamp(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def initialize_session(self):
        copy_templates(self.templates_dir, self.working_dir)
        self._init_progress_txt()
        self._init_requirements_txt()

    def _init_progress_txt(self):
        content = f"""# Trip Planner Progress
## Session Info
Started: {self._generate_timestamp()}
Status: in-progress
## Tasks Completed
- [ ] Collect user requirements
- [ ] Read preferences.md
- [ ] Search flights
- [ ] Search hotels
- [ ] Search activities
- [ ] Create draft itinerary
- [ ] Present draft to user
- [ ] Collect user feedback
- [ ] Revise plan (if needed)
- [ ] Finalize plan
- [ ] Update preferences.md
## Current Stage
[Stage name]
## User Feedback & Revisions
[Log each feedback iteration and changes made]
### Revision 1
Requested:
Applied:
### Revision 2
Requested:
Applied:
## Loop Count
Drafts created: 0
Revisions made: 0
## Notes
[Any issues, blockers or observations]
"""
        write_file(self.working_dir / "progress.txt", content)

    def _init_requirements_txt(self):
        content = f"""# Trip Requirements (Session Log)
## Session Info
Date: {self._generate_timestamp()}
Session ID: {self.session_id}
## Initial Requirements (CLI Prompts & Responses)
### Departure
Prompt: Departure city?
Response:
### Destination
Prompt: Destination?
Response:
### Travel Dates
Prompt: Travel dates (departure and return)?
Response:
### Group Size
Prompt: Group size (adults/children)?
Response:
### Budget
Prompt: Budget range (total or per person)?
Response:
### Interests
Prompt: Interests/activities (sightseeing, food, adventure, relaxation, etc.)?
Response:
### Past Preferences
Prompt: Any preferences from past trips (airline, hotel chain, seat class, etc.)?
Response:
### Luggage
Prompt: Luggage requirements?
Response:
## User Feedback (During Review)
### Feedback Round 1
Presented: [Draft version/timestamp]
User comments:
Requested changes:
Agent actions taken:
### Feedback Round 2
Presented: [Draft version/timestamp]
User comments:
Requested changes:
Agent actions taken:
### Feedback Round N
Presented: [Draft version/timestamp]
User comments:
Requested changes:
Agent actions taken:
## Final Approval
Approved: [yes/no]
Approval timestamp:
Final draft version:
"""
        write_file(self.working_dir / "requirements.txt", content)

    def collect_requirements(self) -> Dict[str, Any]:
        return self.requirements

    def update_requirements(self, requirements: Dict[str, Any]):
        self.requirements.update(requirements)
        self._update_requirements_txt(requirements)
        self._update_progress_txt("Requirements collected")

    def _update_requirements_txt(self, requirements: Dict[str, Any]):
        lines = []
        for key, value in requirements.items():
            if key == "departure":
                lines.append(
                    f"### Departure\nPrompt: Departure city?\nResponse: {value}"
                )
            elif key == "destination":
                lines.append(
                    f"### Destination\nPrompt: Destination?\nResponse: {value}"
                )
            elif key == "dates":
                lines.append(
                    f"### Travel Dates\nPrompt: Travel dates?\nResponse: {value}"
                )
            elif key == "group":
                lines.append(f"### Group Size\nPrompt: Group size?\nResponse: {value}")
            elif key == "budget":
                lines.append(f"### Budget\nPrompt: Budget range?\nResponse: {value}")
            elif key == "interests":
                lines.append(f"### Interests\nPrompt: Interests?\nResponse: {value}")
            elif key == "past_preferences":
                lines.append(
                    f"### Past Preferences\nPrompt: Past preferences?\nResponse: {value}"
                )
            elif key == "luggage":
                lines.append(
                    f"### Luggage\nPrompt: Luggage requirements?\nResponse: {value}"
                )
        content = read_file(self.working_dir / "requirements.txt")
        content += "\n" + "\n\n".join(lines)
        write_file(self.working_dir / "requirements.txt", content)

    def _update_progress_txt(self, stage: str, revision_num: Optional[int] = None):
        content = read_file(self.working_dir / "progress.txt")
        timestamp = self._generate_timestamp()
        content = re.sub(
            r"## Current Stage\n\[Stage name\]", f"## Current Stage\n{stage}", content
        )
        if revision_num:
            content = re.sub(
                r"Revisions made: (\d+)", f"Revisions made: {revision_num}", content
            )
        write_file(self.working_dir / "progress.txt", content)

    def mark_task_done(self, task_name: str):
        content = read_file(self.working_dir / "progress.txt")
        timestamp = self._generate_timestamp()
        task_map = {
            "flights": "Search flights",
            "hotels": "Search hotels",
            "activities": "Search activities",
            "planning": "Create draft itinerary",
        }
        search = f"- [ ] {task_map.get(task_name, task_name)}"
        replace = f"- [x] {task_map.get(task_name, task_name)} ({timestamp})"
        content = content.replace(search, replace)
        content = re.sub(
            r"## Current Stage\n.*", f"## Current Stage\n{task_name} completed", content
        )
        write_file(self.working_dir / "progress.txt", content)

    def read_preferences(self) -> str:
        prefs_path = self.working_dir / "preferences.md"
        if prefs_path.exists():
            return read_file(prefs_path)
        return ""

    def check_and_apply_past_preferences(self) -> bool:
        prefs = self.read_preferences()
        return bool(prefs.strip() and "## Flight Preferences" in prefs)

    def increment_revision(self):
        self.revision_count += 1

    def can_revision(self) -> bool:
        return self.revision_count < self.max_revisions

    def route_revision(self, feedback: str) -> List[str]:
        feedback_lower = feedback.lower()
        routes = []
        if any(x in feedback_lower for x in ["date", "route", "luggage"]):
            routes.extend(["flights", "hotels"])
        elif "hotel" in feedback_lower:
            routes.append("hotels")
        elif "activity" in feedback_lower:
            routes.append("activities")
        if "itinerary" in feedback_lower or "schedule" in feedback_lower:
            routes.append("planning")
        return list(set(routes))

    def finalize_trip(self, feedback: str):
        self._update_progress_txt("Finalized", self.revision_count)
        content = read_file(self.working_dir / "requirements.txt")
        content = re.sub(
            r"## Final Approval\nApproved: \[yes/no\]",
            f"## Final Approval\nApproved: yes\nApproval timestamp: {self._generate_timestamp()}",
            content,
        )
        write_file(self.working_dir / "requirements.txt", content)
        self.pref_manager.add_explicit_preferences(feedback, self.session_id)
        self.pref_manager.add_inferred_preferences(self.requirements, self.session_id)

    def cancel_trip(self):
        self._update_progress_txt("Cancelled")
        content = read_file(self.working_dir / "progress.txt")
        content = content.replace("Status: in-progress", "Status: cancelled")
        write_file(self.working_dir / "progress.txt", content)

    def get_session_id(self) -> str:
        return self.session_id
