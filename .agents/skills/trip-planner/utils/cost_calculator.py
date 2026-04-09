"""Cost calculation utilities."""

import json
from typing import Dict, List, Any


class CostCalculator:
    """Calculate trip cost breakdowns."""

    def __init__(self, config: Dict):
        self.config = config
        self.daily_food_transport = config.get("daily_food_transport", 50)
        self.buffer_percentage = config.get("buffer_percentage", 10)

    def calculate(
        self,
        flights: List[Dict],
        hotels: List[Dict],
        activities: List[Dict],
        num_days: int,
        group: str,
    ) -> Dict[str, Any]:
        """Calculate total cost breakdown."""
        group_size = self._parse_group_size(group)

        flight_cost = self._get_mid_price(flights) * group_size
        hotel_cost = self._get_mid_price(hotels) * num_days
        activity_cost = sum(a.get("cost", 0) for a in activities)

        food_transport = self.daily_food_transport * num_days * group_size

        subtotal = flight_cost + hotel_cost + activity_cost + food_transport
        buffer = subtotal * (self.buffer_percentage / 100)
        total = subtotal + buffer

        per_person = total / group_size if group_size > 0 else total

        return {
            "Flights": flight_cost,
            "Hotels": hotel_cost,
            "Activities": activity_cost,
            "Food (estimated)": food_transport,
            "Local transport": 0,
            "Subtotal": subtotal,
            "Buffer (10%)": buffer,
            "TOTAL": total,
            "Per person": per_person,
        }

    def _parse_group_size(self, group: str) -> int:
        import re

        match = re.search(r"(\d+)", group)
        return int(match.group(1)) if match else 2

    def _get_mid_price(self, items: List[Dict]) -> float:
        if not items:
            return 0
        mid_idx = len(items) // 2
        return items[mid_idx].get("price", 0) or items[mid_idx].get(
            "price_per_night", 0
        )

    def format_summary(self, cost_summary: Dict) -> str:
        """Format cost summary as text."""
        lines = ["## Cost Summary"]
        for key, value in cost_summary.items():
            if key == "TOTAL":
                lines.append(f"- **{key}: ${value:.2f}**")
            elif key == "Per person":
                lines.append(f"- {key}: ${value:.2f}")
            else:
                lines.append(f"- {key}: ${value:.2f}")
        return "\n".join(lines)
