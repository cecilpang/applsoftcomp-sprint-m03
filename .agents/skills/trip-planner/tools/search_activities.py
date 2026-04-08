#!/usr/bin/env python3
"""
Activities search tool for trip-planner skill.
Searches for attractions, tours, and restaurants at destination.

Usage: python3 tools/search_activities.py <destination> <interests> <duration_days> <budget>
"""

import sys


def search_activities(
    destination: str, interests: str, duration_days: int, budget: str
):
    """
    Search for activities matching user interests.

    Returns list of activities with:
    - name, description, location
    - cost, duration, booking_platform
    - category: 'attraction', 'tour', 'restaurant', 'entertainment'
    """

    interest_list = [i.strip() for i in interests.split(",")]

    # Search queries to execute with webfetch:
    queries = [
        f"top attractions in {destination}",
        f"best tours {destination}",
        f"{destination} restaurants food guide",
    ]

    for interest in interest_list:
        queries.append(f"{destination} {interest} activities")

    # Expected output format (to be appended to trip_draft.md):
    output_template = f"""
## Activities & Attractions

### Sightseeing
- [Attraction name]: [Brief description] - $[X] - [Platform]

### Tours
- [Tour name]: [Duration], [Description] - $[X] - [Platform]

### Restaurants
- [Restaurant name]: [Cuisine], [Price range] - [Neighborhood]

### Entertainment
- [Activity name]: [Description] - $[X] - [Platform]
"""

    return {
        "queries": queries,
        "output_template": output_template,
        "section": "## Activities & Attractions",
    }


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python3 tools/search_activities.py <destination> <interests> <duration_days> <budget>"
        )
        sys.exit(1)

    destination, interests, duration_days, budget = sys.argv[1:5]
    result = search_activities(destination, interests, duration_days, budget)

    print(f"Search queries for activities: {destination}")
    print(f"Interests: {interests}")
    for q in result["queries"]:
        print(f"  - {q}")
