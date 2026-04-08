#!/usr/bin/env python3
"""
Flight search tool for trip-planner skill.
Searches airline and aggregator websites for flight options.

Usage: python3 tools/search_flights.py <departure> <destination> <depart_date> <return_date> <passengers>
"""

import sys
from datetime import datetime


def search_flights(
    departure: str,
    destination: str,
    depart_date: str,
    return_date: str,
    passengers: int,
):
    """
    Search for flights at different price points.

    Returns list of flight options with:
    - airline, flight_number, departure_time, arrival_time, duration
    - price_per_person, total_price, booking_platform
    - tier: 'budget', 'mid-range', 'premium'
    """

    # Search queries to execute with webfetch:
    queries = [
        f"flights from {departure} to {destination} departing {depart_date} returning {return_date}",
        f"{departure} to {destination} flight prices {depart_date}",
        f"best flight deals {departure} {destination} {depart_date}",
    ]

    # Expected output format (to be appended to trip_draft.md):
    output_template = f"""
### Budget Option
- Airline: [Airline name]
- Flight #: [Flight number]
- Times: [Departure time] - [Arrival time]
- Duration: [X]h [Y]m
- Price: $[X] per person

### Mid-Range Option
- Airline: [Airline name]
- Flight #: [Flight number]
- Times: [Departure time] - [Arrival time]
- Duration: [X]h [Y]m
- Price: $[X] per person

### Premium Option
- Airline: [Airline name]
- Flight #: [Flight number]
- Times: [Departure time] - [Arrival time]
- Duration: [X]h [Y]m
- Price: $[X] per person
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

    print(f"Search queries for flights: {departure} → {destination}")
    for q in result["queries"]:
        print(f"  - {q}")
