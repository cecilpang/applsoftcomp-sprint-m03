# Trip Planner Skill - Implementation Plan

## Overview
Create a multi-agent trip-planning skill that searches flight/hotel/activity information, interacts with users for preferences, and produces approved itineraries with cost breakdowns.

## Project Structure
```
trip-planner/
├── __init__.py
├── config/
│   └── travel_sites.json        # Configurable travel websites list with fallback sources
├── agents/
│   ├── __init__.py
│   ├── lead_agent.py            # Trip Coordinator (Task 1)
│   ├── flight_search.py        # Flight Search Agent (Task 2)
│   ├── hotel_search.py         # Hotel Search Agent (Task 3)
│   ├── activities_search.py    # Activities Search Agent (Task 4)
│   ├── planning_agent.py       # Draft Itinerary Agent (Task 5)
│   └── finalization_agent.py   # Finalization Agent (Task 6)
├── utils/
│   ├── __init__.py
│   ├── file_utils.py           # File operations, template copying
│   ├── preferences.py          # Preference learning system (Task 7)
│   └── cost_calculator.py      # Cost breakdown calculations
├── templates/                  # Template files (copied on session init)
│   ├── preferences.md
│   ├── progress.txt
│   ├── requirements.txt
│   ├── trip_draft.md
│   └── trip_final.md
└── tests/
    ├── conftest.py
    ├── test_lead_agent.py
    ├── test_flight_search.py
    ├── test_hotel_search.py
    ├── test_activities_search.py
    ├── test_planning_agent.py
    ├── test_finalization_agent.py
    ├── test_preferences.py
    └── test_integration.py
```

## Configuration

### travel_sites.json Structure
```json
{
  "flight_sources": [
    {"name": "Google Flights", "url": "https://www.google.com/travel/flights", "fallback": false},
    {"name": "Kayak", "url": "https://www.kayak.com/flights", "fallback": true}
  ],
  "hotel_sources": [
    {"name": "Booking.com", "url": "https://www.booking.com", "fallback": false},
    {"name": "Expedia", "url": "https://www.expedia.com", "fallback": true}
  ],
  "activity_sources": [
    {"name": "Viator", "url": "https://www.viator.com", "fallback": false},
    {"name": "GetYourGuide", "url": "https://www.getyourguide.com", "fallback": true}
  ],
  "embassy_info_url": "https://travel.state.gov/content/travel/en/international-travel/US-Passports.html",
  "travel_advisories_url": "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html"
}
```

### Session ID Format
- Timestamp-based: `YYYYMMDD-HHMM` (e.g., `20260409-1430`)
- Re-initializes each new session

### Timestamps Format
- `YYYY-MM-DD HH:MM` (simpler format)

## Implementation Details

### Task 1: Lead Agent (Trip Coordinator)
**File:** `agents/lead_agent.py`

**Flow:**
1. Initialize session:
   - Copy templates to working directory
   - Generate session ID from timestamp
   - Re-initialize progress.txt and requirements.txt with session ID and timestamp
2. Collect requirements via question tool (batched):
   - Departure city, Destination, Travel dates, Group size, Budget, Interests, Past preferences, Luggage requirements
3. Log all prompts/responses to requirements.txt (batched after collection)
4. Read preferences.md, ask if user wants to apply past preferences
5. Update progress.txt with timestamp after requirements collected
6. Spawn Flight Search Agent via task tool → wait → read progress.txt → mark done
7. Spawn Hotel Search Agent via task tool → wait → read progress.txt → mark done
8. Spawn Activities Search Agent via task tool → wait → read progress.txt → mark done
9. Spawn Planning Agent → wait → read progress.txt → mark done
10. Present trip_draft.md summary to user via question tool:
    - Open-ended: "What would you like to change?"
    - Structured: "Approve this plan? (yes/no)"
11. Track revision count (max 5, user-requested only)
12. Route revisions based on change type (parallel re-search for multiple types):
    - Dates/route/luggage: re-run Flight + Hotel search
    - Hotel-only: re-run Hotel search
    - Activity-only: re-run Activities search
    - Itinerary structure: re-run Planning only
13. On approval:
    - Finalize trip_final.md
    - Append explicit and inferred preferences to preferences.md
    - Mark finalized with timestamp in progress.txt and requirements.txt
14. On cancel: discard intermediate outputs (trip_draft.md not copied)
15. On webfetch failure (3+ times): try fallback sources automatically

### Task 2: Flight Search Agent
**File:** `agents/flight_search.py`

**Flow:**
1. Read input parameters: departure, destination, dates, group size, budget, luggage requirements
2. Search flight sources from travel_sites.json:
   - Filter by luggage requirements (check-in bags included)
   - Filter by budget range
3. Extract: airline, flight #, times, duration, price/person, total, luggage allowance
4. Find 3 options: budget (70% mid), mid-range, premium (150% mid)
5. If exact dates unavailable: propose ±3 days alternatives
6. Append to trip_draft.md under ## Flights section (append only)
7. Include price disclaimer
8. On webfetch failure: try fallback sources, after 3 failures report to Lead Agent
9. Write completion marker to progress.txt

### Task 3: Hotel Search Agent
**File:** `agents/hotel_search.py`

**Flow:**
1. Read input parameters: destination, dates, group size, budget, preferences
2. Search hotel sources from travel_sites.json:
   - Match user preferences (location priority)
   - Filter by budget range
3. Extract: name, location, rating, amenities, price/night, total, cancellation policy
4. Find 3 options: budget (50% mid), mid-range ($150-250), premium (200% mid)
5. If exact dates unavailable: propose ±3 days alternatives
6. Append to trip_draft.md under ## Hotels section (append only)
7. Include price disclaimer
8. On webfetch failure: try fallback sources, after 3 failures report to Lead Agent
9. Write completion marker to progress.txt

### Task 4: Activities Search Agent
**File:** `agents/activities_search.py`

**Flow:**
1. Read input parameters: destination, dates, group size, budget, interests, preferences
2. Search activity sources from travel_sites.json:
   - Prioritize by user interests (e.g., 50% Food if Food is top interest)
   - Curate 1-2 activities per day
   - Include variety across interest categories
3. Extract: name, description, location, cost, duration, booking platform, hours
4. Flag activities requiring advance booking or having seasonal closures
5. Append to trip_draft.md under ## Activities section (append only)
6. Include price disclaimer
7. On webfetch failure: try fallback sources, after 3 failures report to Lead Agent
8. Write completion marker to progress.txt

### Task 5: Planning Agent (Draft Itinerary)
**File:** `agents/planning_agent.py`

**Flow:**
1. Read trip_draft.md for all search results
2. Read preferences.md for user preferences
3. Create day-by-day itinerary with general time blocks (Morning/Afternoon/Evening)
4. Include time estimates + travel time (via Google Maps web fetch)
5. Flag scheduling conflicts/unrealistic timing
6. Calculate total cost breakdown:
   - Flights + Hotels + Activities + Food/Transport ($50/day/person) + Buffer (10%)
7. Fetch visa/entry requirements from travel.state.gov
8. Fetch emergency contacts (local emergency + embassy from official site)
9. Fetch travel warnings from travel.state.gov
10. Include travel tips (transportation, currency, customs)
11. Include luggage/packing recommendations
12. Overwrite trip_draft.md with complete draft including "Last Updated" timestamp
13. Append price disclaimer once

### Task 6: Finalization Agent
**File:** `agents/finalization_agent.py`

**Flow:**
1. Read trip_draft.md and user feedback
2. Apply final revisions if requested (within 5-revision limit)
3. Overwrite trip_final.md with approved plan sections:
   - Travelers, Itinerary, Bookings, Cost Summary, Visa/Entry Requirements
   - Emergency Contacts, Travel Tips, Luggage/Packing, Warnings, Disclaimer
4. Append to preferences.md by category with dates:
   - Flight Preferences, Hotel Preferences, Activity Preferences, Budget Preferences
   - Past Feedback with session ID and date
5. Mark finalized in progress.txt and requirements.txt with timestamp

### Task 7: Preference Learning System
**File:** `utils/preferences.py`

**Flow:**
1. Read preferences.md at session start
2. Ask user if applying past preferences (apply all if yes)
3. Capture explicit preferences from user feedback
4. Infer preferences from user choices
5. Organize by category with date added
6. Append new preferences (don't overwrite)
7. Track most recent preference for conflicts

## Testing Strategy

### Test Framework
- **pytest** with fixtures for session/mocking
- **Rate limiting**: 30-second delay between same-domain calls
- **Timeout**: 120 seconds for webfetch calls
- **Live website testing** (not mocked)

### Unit Tests
- Test each agent's core functions independently
- Test preference parsing and accumulation
- Test cost calculations

### Integration Tests
- Full workflow test with Japan trip test case
- Revision flow test
- Finalization flow test

### Test Cases (from PRD)

**Task 1 Test Case:**
- Session: Japan trip, Tokyo, 2026-08-15 to 2026-08-22, 2 adults, $4000-6000 budget
- Interests: Food & Dining, Temples & Culture, Shopping
- Luggage: 1 check-in bag included
- Apply past preferences: Yes
- Revision 1: Change hotel from budget to mid-range
- Revision 2: Add day trip to Kyoto
- Finalize after 2 revisions

**Task 2 Test Case:**
- Route: SFO to NRT (Tokyo)
- Dates: 2026-08-15 to 2026-08-22
- Group: 2 adults
- Luggage: 1 check-in bag (23kg) included
- Budget: Mid-range ($1000-1500/person)

**Task 3 Test Case:**
- Destination: Tokyo, Japan
- Dates: 2026-08-15 to 2026-08-22 (7 nights)
- Group: 2 adults
- Preferences: Central location, clean, safe neighborhood
- Budget: Mid-range ($150-250/night)

**Task 4 Test Case:**
- Destination: Tokyo, Japan
- Interests: Food & Dining, Temples & Culture, Shopping
- Budget: $50-150/day per person for activities
- Duration: 7 days

**Task 5-6 Test Case:**
- Input: Flight/hotel/activity search results for Tokyo 7-day trip
- Preferences: Food & Dining priority, mid-range budget

## Acceptance Criteria (from PRD)

### Task 1
- [ ] Session ID and timestamp present in requirements.txt header
- [ ] All CLI question responses logged to requirements.txt immediately
- [ ] progress.txt contains timestamps for each task and revision
- [ ] Revision count tracked correctly (does not exceed 5)
- [ ] Correct re-search routing based on change type
- [ ] trip_final.md created only after user approval
- [ ] Intermediate outputs discarded if user cancels
- [ ] Preferences.md updated with both explicit and inferred preferences

### Task 2
- [ ] 3 flight options provided at different price points
- [ ] All options meet luggage requirement (1 check-in included)
- [ ] Flight details include: airline, flight number, times, duration, price, luggage allowance
- [ ] Price disclaimer present
- [ ] Alternative dates proposed if original dates unavailable
- [ ] Multiple sources attempted if initial search fails
- [ ] Results appended to trip_draft.md without reading file

### Task 3
- [ ] 3 hotel options provided at different price points
- [ ] Hotel details include: name, location, rating, amenities, price/night, total cost, cancellation policy
- [ ] Options match user preferences (location prioritized)
- [ ] Price disclaimer present
- [ ] Alternative dates proposed if original dates unavailable
- [ ] Multiple sources attempted if initial search fails
- [ ] Results appended to trip_draft.md without reading file

### Task 4
- [ ] Activities curated to match stated interests (Food, Temples, Shopping)
- [ ] Activity details include: name, description, location, cost, duration, booking platform
- [ ] Variety of options across interest categories
- [ ] Price disclaimer present
- [ ] Advance booking requirements flagged
- [ ] Seasonal closures noted if applicable
- [ ] Results appended to trip_draft.md without reading file

### Task 5
- [ ] Day-by-day itinerary covers all days of trip
- [ ] Each day includes morning, afternoon, evening activities
- [ ] Time estimates provided for each activity
- [ ] Travel time between locations included
- [ ] Scheduling conflicts flagged with warnings
- [ ] Total cost breakdown includes: flights, hotels, activities, food/transport ($50/day/person), 10% buffer
- [ ] Visa/entry requirements section present
- [ ] Emergency contacts section present (embassy, local emergency numbers)
- [ ] Travel tips section present (transportation, currency, customs)
- [ ] Luggage/packing recommendations included
- [ ] Travel warnings/restrictions section present if applicable
- [ ] Price disclaimer present
- [ ] "Last Updated" timestamp in header
- [ ] trip_draft.md overwritten completely (not appended)

### Task 6
- [ ] trip_final.md contains all required sections (Travelers, Itinerary, Bookings, Cost Summary, Visa, Emergency, Tips, Luggage, Warnings, Disclaimer)
- [ ] Price disclaimer present stating estimates may change and to verify before booking
- [ ] Session ID present in trip_final.md header
- [ ] preferences.md updated with explicit preferences
- [ ] preferences.md updated with inferred preferences (from user choices during session)
- [ ] Preferences organized by category with dates
- [ ] Past Feedback section includes session ID and date
- [ ] progress.txt marked as finalized with timestamp
- [ ] requirements.txt marked as finalized with timestamp

### Task 7
- [ ] Past preferences read at session start
- [ ] User asked if applying past preferences
- [ ] Explicit preferences captured and categorized
- [ ] Inferred preferences deduced from user choices
- [ ] Preferences organized by category (Flight, Hotel, Activity, Budget)
- [ ] Each preference entry includes date added
- [ ] Past Feedback section includes session ID and summary
- [ ] Most recent preference takes priority in case of conflict
- [ ] New preferences appended without overwriting existing
