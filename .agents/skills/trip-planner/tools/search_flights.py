#!/usr/bin/env python3
"""Flight search tool for trip-planner skill."""

import sys


def search_flights(departure, destination, depart_date, return_date, passengers):
    """Search flights at different price points."""
    queries = [
        f"flights from {departure} to {destination} departing {depart_date} returning {return_date}",
        f"{departure} to {destination} flight prices {depart_date}",
        f"best flight deals {departure} {destination} {depart_date}",
    ]
    output_template = """
### Budget Option
Airline:
Flight #:
Times:
Duration:
Price: $[X] per person

### Mid-Range Option
Airline:
Flight #:
Times:
Duration:
Price: $[X] per person

### Premium Option
Airline:
Flight #:
Times:
Duration:
Price: $[X] per person
"""
    return {
        "queries": queries,
        "output_template": output_template,
        "section": "## Flight Options",
    }


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(
            "Usage: python3 tools/search_flights.py <departure> <destination> <depart_date> <return_date> <passengers>"
        )
        sys.exit(1)
    departure, destination, depart_date, return_date, passengers = sys.argv[1:6]
    result = search_flights(
        departure, destination, depart_date, return_date, int(passengers)
    )
    print(f"Search queries for flights: {departure} to {destination}")
    for q in result["queries"]:
        print(f"  - {q}")
