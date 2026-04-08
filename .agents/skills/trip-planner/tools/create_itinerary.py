#!/usr/bin/env python3
"""
Itinerary creation tool for trip-planner skill.
Combines search results into a day-by-day itinerary.

Usage: python3 tools/create_itinerary.py <trip_draft.md> <preferences.md>
"""

import sys


def create_itinerary(
    trip_details: dict, flights: list, hotels: list, activities: list, preferences: dict
):
    """
    Create day-by-day itinerary from search results.

    Returns structured itinerary with:
    - Daily schedule (morning, afternoon, evening)
    - Recommended flight/hotel selection with rationale
    - Cost breakdown
    - Booking platform recommendations
    """

    # This tool is called by the Planning Sub-Agent
    # It reads trip_draft.md and preferences.md, then produces the draft itinerary

    output_template = f"""
## Recommended Itinerary

### Pre-Trip
- **Flight:** [Selected option with rationale]
- **Hotel:** [Selected option with rationale]

### Day 1: [Date] - [Theme]
| Time | Activity | Cost | Notes |
|------|----------|------|-------|
| Morning | [Activity] | $[X] | [Notes] |
| Afternoon | [Activity] | $[X] | [Notes] |
| Evening | [Activity] | $[X] | [Notes] |

[Continue for all days...]

## Cost Summary

| Category | Budget | Mid-Range | Premium |
|----------|--------|-----------|---------|
| Flights | $[X] | $[X] | $[X] |
| Hotels | $[X] | $[X] | $[X] |
| Activities | $[X] | $[X] | $[X] |
| **Total** | **$[X]** | **$[X]** | **$[X]** |

## Booking Platforms
- Flights: [Platform recommendations]
- Hotels: [Platform recommendations]
- Activities: [Platform recommendations]
"""

    return output_template


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python3 tools/create_itinerary.py <trip_draft.md> <preferences.md>"
        )
        sys.exit(1)

    draft_file, preferences_file = sys.argv[1:3]

    print(f"Creating itinerary from:")
    print(f"  - {draft_file}")
    print(f"  - {preferences_file}")
    print("\nPlanning Agent will combine search results into day-by-day schedule.")
