---
name: trip-planner
description: Create personalized trip plans by searching airline/hotel info, interacting with users for preferences, producing approved itineraries with costs.
---

Shared files: preferences.md (accumulated user preferences/feedbacks), trip_draft.md (draft plan for review), trip_final.md (approved final plan), progress.txt (task/review/revision log), requirements.txt (session CLI prompts & responses).

Templates (initialize from templates/ on first run)
templates/preferences.md → preferences.md
templates/trip_draft.md → trip_draft.md
templates/trip_final.md → trip_final.md
templates/progress.txt → progress.txt
templates/requirements.txt → requirements.txt (re-initialized every session)

Lead Agent (trip coordinator)
1. Init: copy templates to working dir if not exist. Initialize progress.txt and requirements.txt (fresh every session).
2. Collect trip requirements via CLI prompts. Log each prompt/response to requirements.txt.
3. Read preferences.md for accumulated preferences from past sessions.
4. Update progress.txt: mark requirements collected.
5. Spawn Search Agent for flights. Wait. Mark done in progress.txt.
6. Spawn Search Agent for hotels. Wait. Mark done in progress.txt.
7. Spawn Search Agent for activities/attractions. Wait. Mark done in progress.txt.
8. Spawn Planning Agent to create draft itinerary. Wait. Mark done in progress.txt.
9. Present trip_draft.md to user; collect feedback. Log prompt/response to requirements.txt, summary to progress.txt.
10. If revisions needed: update requirements, increment loop count in progress.txt, loop back to step 8.
11. If approved: finalize trip_final.md, append feedback to preferences.md, mark finalized in progress.txt and requirements.txt. Stop.

Sub-Agents (spawned via Task tool, general/mode: subagent)

Flight Search (uses webfetch):
1. Search airline websites/aggregators for flights matching dates, route, group size.
2. Extract: airline, flight numbers, times, duration, price per person, total cost.
3. Find 3 options at different price points (budget/mid-range/premium).
4. Append results to trip_draft.md under ## Flights. Append only; do not read.

Hotel Search (uses webfetch):
1. Search hotel booking sites for accommodations matching dates, destination, group size.
2. Extract: hotel name, location, rating, amenities, price per night, total cost.
3. Find 3 options at different price points (budget/mid-range/premium).
4. Append results to trip_draft.md under ## Hotels. Append only; do not read.

Activities Search (uses webfetch):
1. Search for attractions, tours, restaurants at destination.
2. Extract: name, description, location, cost, duration, booking platform.
3. Curate options matching user interests and budget.
4. Append results to trip_draft.md under ## Activities. Append only; do not read.

Planning (creates draft itinerary):
1. Read trip_draft.md for all search results.
2. Read preferences.md for user preferences.
3. Create day-by-day itinerary with: activities, timing, costs, booking platform recommendations.
4. Include total estimated cost breakdown (flights + hotels + activities + buffer).
5. Overwrite trip_draft.md with complete draft: Itinerary, Options, Cost Summary.

Finalization (after user approval):
1. Read trip_draft.md and user feedback.
2. Apply revisions if any.
3. Overwrite trip_final.md with approved plan.
4. Append new preferences/feedback to preferences.md.

CLI Prompts (Lead Agent asks user)

Initial:
- Departure city?
- Destination?
- Travel dates (departure and return)?
- Group size (adults/children)?
- Budget range (total or per person)?
- Interests/activities (sightseeing, food, adventure, relaxation, etc.)?
- Any preferences from past trips (airline, hotel chain, seat class, etc.)?

Review:
- Present draft plan summary with cost breakdown.
- What would you like to change? (dates, hotels, activities, budget)
- Approve this plan? (yes/no)

Output Format (trip_final.md)

# Trip Plan: [Destination]

## Travelers
- Group: [N] adults, [M] children
- Dates: [YYYY-MM-DD] to [YYYY-MM-DD]

## Itinerary
### Day 1: [Date]
- Morning: [activity]
- Afternoon: [activity]
- Evening: [activity]
...

## Bookings
### Flights
- Recommended: [Airline] [Flight#] - [Platform]
- Cost: $[X] per person × [N] = $[Total]

### Hotels
- Recommended: [Hotel] - [Platform]
- Cost: $[X]/night × [N] nights = $[Total]

### Activities
- [Activity] - [Platform] - $[Cost]
...

## Cost Summary
- Flights: $[X]
- Hotels: $[X]
- Activities: $[X]
- Buffer (10%): $[X]
- **Total: $[X]**

Writing Style
- Concise, practical
- Clear cost breakdowns
- Platform names without URLs (e.g., "Book on Expedia")
- Present options at different price points
- Note assumptions and uncertainties

Stop Conditions
- User approves final plan and trip_final.md created
- User cancels session
- Search fails for critical components (flights/hotels unavailable)
