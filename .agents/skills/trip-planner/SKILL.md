---
name: trip-planner
description: Create personalized trip plans by searching airline/hotel info, interacting with users for preferences, producing approved itineraries with costs.
---

Shared files: `preferences.md` (accumulated user preferences/feedbacks), `trip_draft.md` (draft itinerary for review), `trip_final.md` (final itinerary), `progress.txt` (task/review/revision log), `queries.txt` (session CLI prompts & responses).

Templates: copy from `templates/` on session init. Session re-init: `queries.txt` fresh each session.

Session ID: YYYYMMDD-HHMM timestamp based minute level. Timestamps: YYYY-MM-DD HH:MM.

## Lead Agent
1. Init (first run only): copy `./agents/skills/trip-planner/templates/{preferences.md,trip_draft.md,trip_final.md,progress.txt,queries.txt}` into working dir if not exist. 
2. Initialize `trip_draft.md`, `trip_final.md`, `progress.txt`, `queries.txt` with session ID timestamp.
3. Read `preferences.md`. Ask if apply past preferences.
4. Collect requirements via question tool batched: departure, destination, dates, group, budget, interests, past_preferences, luggage. 
5. Log prompts + responses to `queries.txt` batch after collection. Read `progress.txt` mark Requirements Collection is done.  
6. Spawn Flight Search Sub-Agent via Task tool. Wait.
7. Spawn Hotel Search Sub-Agent via Task tool. Wait.
8. Spawn Activities Search Sub-Agent via Task tool. Wait.
9. Spawn Planning Sub-Agent via Task tool. Wait.
10. Present `trip_draft.md` to user via question tool. Open-ended: what change, structured: approve yes/no. Update `queries.txt` with user feedback. Append trip preferences with session ID to `preferences.md`
11. Track revision count max 5 user-requested only.
12. Route revisions(Parallel re-search multiple change types): 
    - dates/route/luggage changed → re-run flight+hotel; 
    - hotel pref changed → re-run hotel; 
    - activity pref changed → re-run activities; 
    - itinerary structure → re-run planning. 
13. Spawn Finalization Sub-Agent via Task tool on approval. Wait.
14. On cancel: discard intermediate outputs. `trip_draft.md` not copied.

## Flight Search Agent
    Inputs: departure, destination, dates, group, budget, luggage.
    1. Search flight sources from config. Filter by luggage requirements and budget.
    2. Extract: airline, flight#, times, duration, price/person, total, luggage allowance.
    3. Find 3 options: budget 70% mid, mid-range, premium 150% mid.
    4. If exact dates unavailable: propose +-3 days alternatives.
    5. Overwrite `trip_draft.md` ## Flights section.
    6. On webfetch fail: try fallback sources, after 3 failures report to Lead Agent.
    7. Mark completion in `progress.txt`.

## Hotel Search Agent
    Inputs: destination, dates, group, budget, preferences.
    1. Search hotel sources from config. Match preferences, prioritize location. Filter by budget.
    2. Extract: name, location, rating, amenities, price/night, total, cancellation policy.
    3. Find 3 options: budget 50% mid, mid-range 150-250, premium 200% mid.
    4. If exact dates unavailable: propose +-3 days alternatives.
    5. Overwrite `trip_draft.md` ## Hotels section.
    6. On webfetch fail: try fallback sources, after 3 failures report to Lead Agent.
    7. Mark completion in `progress.txt`.

## Activities Search Agent
    Inputs: destination, dates, group, budget, interests, preferences.
    1. Search activity sources from config. Prioritize by user interests. If Food top interest show 50% food activities.
    2. Curate 1-2 activities per day. Include variety across interest categories.
    3. Extract: name, description, location, cost, duration, booking platform, opening hours.
    4. Flag activities requiring advance booking or seasonal closures.
    5. Overwrite `trip_draft.md` ## Activities section.
    6. On webfetch fail: try fallback sources, after 3 failures report to Lead Agent.
    7. Mark completion in `progress.txt`.

## Planning Agent
    Inputs: `trip_draft.md`, `preferences.md`.
    1. Read `trip_draft.md` and `preferences.md`.
    2. Create day-by-day itinerary with Morning/Afternoon/Evening time blocks.
    3. Include time estimates for each activity plus travel time between locations via Google Maps webfetch.
    4. Flag scheduling conflicts or unrealistic timing (too many activities one day).
    5. Calculate total cost: flights + hotels + activities + food/transport $50/day/person + buffer 10%.
    6. Fetch visa/entry requirements from travel.state.gov; emergency contacts: local emergency number + embassy from official embassy website.
    7. Fetch travel warnings from travel.state.gov for US citizens.
    8. Include travel tips: transportation, currency, customs.
    9. Include luggage/packing recommendations based on user requirements and destination.
    10. Overwrite `trip_draft.md` with complete draft: Itinerary, Options, Cost Summary, Disclaimers.
    11. Add Last Updated timestamp to header.
    12. Mark completion in `progress.txt`.

## Finalization Agent
    Inputs: `trip_draft.md`, user feedback, `preferences.md`.
    1. Read `trip_draft.md` and user feedback.
    2. Apply final revisions if any.
    3. Overwrite `trip_final.md` with all sections: Travelers, Itinerary, Bookings, Cost Summary, Visa/Entry Requirements, Emergency Contacts, Travel Tips, Luggage/Packing Recommendations, Travel Warnings/Restrictions, Price Disclaimer.
    4. Summarize all trips preferences by category in `preferences.md`: flight, hotel, activity, budget.
    5. Label preferences stated by user or inferred from choices.
    6. Include price disclaimer: prices are estimated may change verify before booking.
    7. Mark completion in `progress.txt`.

## CLI Prompts (Initial, batched)
- departure city?
- destination?
- travel dates (departure + return)?
- group size (adults + children)?
- budget range (total or per person)?
- interests (sightseeing, food, adventure, relaxation)?
- past preferences (airline, hotel chain, seat class)?
- luggage requirements (structured: check-in bags and carry-on with custom option)?

## CLI Prompts (Review)
- Present draft plan summary with cost breakdown.
- Open-ended: what would you like to change? (dates, hotels, activities, budget?)
- Structured: approve this plan yes/no.

## Stop Conditions
- User approves final plan → `trip_final.md` created
- User cancels session
- Search fails (critical components: flights, hotels unavailable)
