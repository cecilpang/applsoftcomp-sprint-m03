#!/usr/bin/env python3
"""Hotel search tool for trip-planner skill."""

import sys


def search_hotels(destination, check_in, check_out, guests):
    """Search hotels at different price points."""
    queries = [
        f"hotels in {destination} check in {check_in} check out {check_out}",
        f"best hotel deals {destination} {check_in}",
        f"{destination} hotels by price rating reviews",
    ]
    output_template = """
### Budget Option
Name:
Location:
Rating:
Price: $[X]/night

### Mid-Range Option
Name:
Location:
Rating:
Price: $[X]/night

### Premium Option
Name:
Location:
Rating:
Price: $[X]/night
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
