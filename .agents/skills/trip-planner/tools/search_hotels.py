#!/usr/bin/env python3
"""
Hotel search tool for trip-planner skill.
Searches hotel booking sites for accommodation options.

Usage: python3 tools/search_hotels.py <destination> <check_in> <check_out> <guests>
"""

import sys


def search_hotels(destination: str, check_in: str, check_out: str, guests: int):
    """
    Search for hotels at different price points.

    Returns list of hotel options with:
    - name, location, rating, amenities
    - price_per_night, total_price, booking_platform
    - tier: 'budget', 'mid-range', 'premium'
    """

    # Search queries to execute with webfetch:
    queries = [
        f"hotels in {destination} check in {check_in} check out {check_out}",
        f"best hotel deals {destination} {check_in}",
        f"{destination} hotels by price rating reviews",
    ]

    # Expected output format (to be appended to trip_draft.md):
    output_template = f"""
### Budget Option
- Name: [Hotel name]
- Location: [Neighborhood/Area]
- Rating: [X]/5 ([N] reviews)
- Amenities: [List key amenities]
- Price: $[X]/night

### Mid-Range Option
- Name: [Hotel name]
- Location: [Neighborhood/Area]
- Rating: [X]/5 ([N] reviews)
- Amenities: [List key amenities]
- Price: $[X]/night

### Premium Option
- Name: [Hotel name]
- Location: [Neighborhood/Area]
- Rating: [X]/5 ([N] reviews)
- Amenities: [List key amenities]
- Price: $[X]/night
"""

    return {
        "queries": queries,
        "output_template": output_template,
        "section": "## Hotel Options",
    }


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python3 tools/search_hotels.py <destination> <check_in> <check_out> <guests>"
        )
        sys.exit(1)

    destination, check_in, check_out, guests = sys.argv[1:5]
    result = search_hotels(destination, check_in, check_out, int(guests))

    print(f"Search queries for hotels: {destination}")
    for q in result["queries"]:
        print(f"  - {q}")
