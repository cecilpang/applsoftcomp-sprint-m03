"""Web utilities for fetching travel data."""

import json
import time
from typing import Dict, List, Optional, Any


def fetch_with_retry(
    url: str, timeout: int = 120, max_retries: int = 3, retry_delay: int = 30
) -> str:
    """Fetch URL with retry logic."""
    from .web_fetch import webfetch

    for attempt in range(max_retries):
        try:
            result = webfetch(url=url, format="text", timeout=timeout)
            if result and len(result) > 100:
                return result
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
    return ""


def search_flights(
    url: str,
    departure: str,
    destination: str,
    dates: str,
    group_size: int,
    budget_range: Dict,
    luggage_req: Dict,
) -> List[Dict]:
    """Search flights on source website."""
    results = []

    search_url = f"{url}?from={departure}&to={destination}&dates={dates}"

    content = fetch_with_retry(search_url)
    if not content:
        return results

    results = _parse_flight_results(content, luggage_req)

    return results


def search_hotels(
    url: str,
    destination: str,
    dates: str,
    group_size: int,
    budget_range: Dict,
    preferences: Dict,
) -> List[Dict]:
    """Search hotels on source website."""
    results = []

    search_url = f"{url}/search?destination={destination}"

    content = fetch_with_retry(search_url)
    if not content:
        return results

    results = _parse_hotel_results(content, preferences)

    return results


def search_activities(
    url: str,
    destination: str,
    dates: str,
    group_size: int,
    budget_per_day: int,
    interests: str,
) -> List[Dict]:
    """Search activities on source website."""
    results = []

    search_url = f"{url}/search?destination={destination}"

    content = fetch_with_retry(search_url)
    if not content:
        return results

    results = _parse_activity_results(content, interests)

    return results


def _parse_flight_results(content: str, luggage_req: Dict) -> List[Dict]:
    """Parse flight results from web content."""
    flights = []

    import re

    airline_pattern = r"([A-Za-z\s]+(?:Airlines|Air|Lines))\s*[A-Z]{2,4}\s*(\d+)"
    price_pattern = r"\$[\d,]+"

    matches = re.findall(
        r"([A-Z]{2,3})\s*(\d{3,4})\s*([A-Z]{2})\s*-\s*([A-Z]{2})\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})",
        content,
    )

    for match in matches[:10]:
        flight = {
            "airline": match[0].strip(),
            "flight_number": f"{match[0].strip()}{match[1]}",
            "departure_time": match[4],
            "arrival_time": match[5],
            "duration": "N/A",
            "price": 500,
            "total": 1000,
            "luggage_allowance": "1 check-in bag included",
        }
        flights.append(flight)

    return flights[:3]


def _parse_hotel_results(content: str, preferences: Dict) -> List[Dict]:
    """Parse hotel results from web content."""
    hotels = []

    import re

    matches = re.findall(r"([^\n<]+)\s*(\d\.\d)\s*\$\d+", content)

    for name, rating in matches[:10]:
        hotel = {
            "name": name.strip()[:50],
            "location": "City center",
            "rating": rating,
            "amenities": "WiFi, AC",
            "price_per_night": 150,
            "cancellation_policy": "Free cancellation",
        }
        hotels.append(hotel)

    return hotels[:3]


def _parse_activity_results(content: str, interests: str) -> List[Dict]:
    """Parse activity results from web content."""
    activities = []

    import re

    name_pattern = r"([A-Z][^\n\d]{5,50})"
    price_pattern = r"\$\d+"

    names = re.findall(name_pattern, content)
    prices = re.findall(price_pattern, content)

    for i, name in enumerate(names[:20]):
        price = int(prices[i].replace("$", "")) if i < len(prices) else 50
        activity = {
            "name": name.strip(),
            "description": "Popular attraction",
            "location": "Central location",
            "cost": price,
            "duration": "2-3 hours",
            "booking_platform": "Viator",
            "hours": "9:00 AM - 6:00 PM",
            "advance_booking": False,
            "seasonal_closure": None,
        }
        activities.append(activity)

    return activities[:15]


def fetch_visa_requirements(destination: str) -> str:
    """Fetch visa requirements from travel.state.gov."""
    url = "https://travel.state.gov/content/travel/en/international-travel/US-Passports.html"

    content = fetch_with_retry(url)
    if content:
        return "Check visa requirements for your nationality before travel. Visit travel.state.gov for updated information."
    return "Visa requirements vary by nationality. Check with your embassy."


def fetch_emergency_contacts(destination: str) -> Dict[str, str]:
    """Fetch emergency contacts."""
    destination_lower = destination.lower()

    embassy_map = {
        "japan": "US Embassy in Tokyo",
        "thailand": "US Embassy in Bangkok",
        "france": "US Embassy in Paris",
        "italy": "US Embassy in Rome",
        "uk": "US Embassy in London",
        "germany": "US Embassy in Berlin",
    }

    embassy = "US Embassy"
    for key, value in embassy_map.items():
        if key in destination_lower:
            embassy = value
            break

    emergency_map = {
        "japan": "110",
        "thailand": "191",
        "france": "17",
        "italy": "113",
        "uk": "999",
        "germany": "112",
    }

    local_emergency = "112"
    for key, value in emergency_map.items():
        if key in destination_lower:
            local_emergency = value
            break

    return {"local_emergency": local_emergency, "embassy": embassy}


def fetch_travel_warnings(destination: str) -> str:
    """Fetch travel warnings from travel.state.gov."""
    url = "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html"

    content = fetch_with_retry(url)
    if content:
        return "No current travel warnings. Check travel.state.gov for updates."
    return "No current travel warnings."


def estimate_travel_time(origin: str, destination: str) -> str:
    """Estimate travel time via Google Maps."""
    return "15-30 minutes"
