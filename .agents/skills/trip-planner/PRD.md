# Trip Planner Skill - Product Requirements Document

## Overview

The trip-planner skill creates personalized trip itineraries by searching flight/hotel/activity information, interacting with users to learn preferences, and producing approved itineraries with cost breakdowns. Users book themselves, but all information must be accurate and up-to-date.

**Key Features:**
- Multi-agent architecture with lead coordinator and specialized search agents
- Accumulates user preferences across sessions (explicit and inferred)
- Supports up to 5 revision cycles per session with timestamped logging
- Handles edge cases with alternative proposals
- Produces booking-ready itineraries with disclaimers about price estimates

**Shared Files:**
- `preferences.md` - Accumulated user preferences organized by category with dates
- `trip_draft.md` - Draft plan with Last Updated timestamp for review
- `trip_final.md` - Approved final plan
- `progress.txt` - Task/revision log with timestamps
- `requirements.txt` - Session CLI prompts & responses with session ID

**Templates:** Located in `templates/` directory, copied on first run and re-initialized each session.

---

## Task 1: Lead Agent (Trip Coordinator)

- Implemented: false
- Test Passed: false
- Goal: Coordinate the trip planning workflow by collecting requirements, spawning sub-agents, managing revisions, and finalizing the plan
- Inputs: User responses to CLI questions, search results from sub-agents, preferences.md
- Outputs: Updated progress.txt, requirements.txt, trip_draft.md, trip_final.md, preferences.md

**Specifications:**
1. Initialize session by copying templates to working directory; re-initialize progress.txt and requirements.txt fresh every session with session ID and timestamp
2. Collect trip requirements via question tool prompts; log each prompt/response to requirements.txt immediately after receiving answers
3. Read preferences.md for accumulated preferences from past sessions; ask if user wants to apply past preferences
4. Ask luggage requirements (e.g., check-in luggage allowance)
5. Update progress.txt with timestamp after requirements collected
6. Spawn Flight Search Agent; wait for completion; read progress.txt then mark done with timestamp
7. Spawn Hotel Search Agent; wait for completion; read progress.txt then mark done with timestamp
8. Spawn Activities Search Agent; wait for completion; read progress.txt then mark done with timestamp
9. Spawn Planning Agent to create draft itinerary; wait for completion; read progress.txt then mark done with timestamp
10. Present trip_draft.md summary to user; collect feedback via both open-ended and structured questions; log to requirements.txt and progress.txt with timestamp
11. Track revision count (max 5 per session); if exceeded, prompt user to finalize or cancel
12. If revisions needed, route to appropriate re-search based on change type:
    - Dates/route/luggage changed: re-run Flight + Hotel search
    - Hotel-only preference changed: re-run Hotel search
    - Activity-only preference changed: re-run Activities search
    - Itinerary structure changed: re-run Planning only
13. If approved: finalize trip_final.md, append inferred and explicit preferences to preferences.md, mark finalized with timestamp
14. If user cancels: discard intermediate outputs (trip_draft.md not copied to trip_final.md)
15. If webfetch fails repeatedly (3+ times), confirm with user before creating alternative search tools

**Test Case:**
- Session: Japan trip, Tokyo, 2026-08-15 to 2026-08-22, 2 adults, $4000-6000 budget
- User interests: Food & Dining, Temples & Culture, Shopping
- Luggage requirement: 1 check-in bag included
- Apply past preferences: Yes
- Revision 1: Change hotel from budget to mid-range
- Revision 2: Add day trip to Kyoto
- Finalize after 2 revisions

**Evaluation Criteria:**
- [ ] Session ID and timestamp present in requirements.txt header
- [ ] All CLI question responses logged to requirements.txt immediately
- [ ] progress.txt contains timestamps for each task and revision
- [ ] Revision count tracked correctly (does not exceed 5)
- [ ] Correct re-search routing based on change type
- [ ] trip_final.md created only after user approval
- [ ] Intermediate outputs discarded if user cancels
- [ ] Preferences.md updated with both explicit and inferred preferences

---

## Task 2: Flight Search Agent

- Implemented: false
- Test Passed: false
- Goal: Search for flights matching user requirements and luggage needs, providing multiple price points
- Inputs: Departure city, destination, dates, group size, budget, luggage requirements
- Outputs: 3 flight options (budget/mid-range/premium) appended to trip_draft.md

**Specifications:**
1. Search multiple airline websites and aggregators for flights matching criteria
2. Filter results to include only flights meeting luggage requirements (e.g., 1 check-in bag included)
3. Extract: airline, flight numbers, departure/arrival times, duration, price per person, total cost, luggage allowance
4. Find 3 options at different price points (budget/mid-range/premium)
5. If exact dates unavailable, propose alternative dates (±3 days) and confirm with user via Lead Agent
6. If webfetch fails, try multiple sources; after 3 failures, report to Lead Agent
7. Append results to trip_draft.md under ## Flights section; append only, do not read existing content
8. Include price disclaimer: prices are estimates and may change; verify before booking

**Test Case:**
- Route: SFO to NRT (Tokyo)
- Dates: 2026-08-15 to 2026-08-22
- Group: 2 adults
- Luggage: 1 check-in bag (23kg) included
- Budget: Mid-range ($1000-1500/person)

**Evaluation Criteria:**
- [ ] 3 flight options provided at different price points
- [ ] All options meet luggage requirement (1 check-in included)
- [ ] Flight details include: airline, flight number, times, duration, price, luggage allowance
- [ ] Price disclaimer present
- [ ] Alternative dates proposed if original dates unavailable
- [ ] Multiple sources attempted if initial search fails
- [ ] Results appended to trip_draft.md without reading file

---

## Task 3: Hotel Search Agent

- Implemented: false
- Test Passed: false
- Goal: Search for accommodations matching user requirements and preferences
- Inputs: Destination, dates, group size, budget, preferences (from preferences.md)
- Outputs: 3 hotel options (budget/mid-range/premium) appended to trip_draft.md

**Specifications:**
1. Search multiple hotel booking sites for accommodations matching criteria
2. Extract: hotel name, location, rating, amenities, price per night, total cost, cancellation policy
3. Find 3 options at different price points (budget/mid-range/premium)
4. Match options to user preferences (e.g., if user prefers central location, prioritize location over price)
5. If exact dates unavailable, propose alternative dates (±3 days) and confirm with user via Lead Agent
6. If webfetch fails, try multiple sources; after 3 failures, report to Lead Agent
7. Append results to trip_draft.md under ## Hotels section; append only, do not read existing content
8. Include price disclaimer: prices are estimates and may change; verify before booking

**Test Case:**
- Destination: Tokyo, Japan
- Dates: 2026-08-15 to 2026-08-22 (7 nights)
- Group: 2 adults
- Preferences: Central location, clean, safe neighborhood
- Budget: Mid-range ($150-250/night)

**Evaluation Criteria:**
- [ ] 3 hotel options provided at different price points
- [ ] Hotel details include: name, location, rating, amenities, price/night, total cost, cancellation policy
- [ ] Options match user preferences (location prioritized)
- [ ] Price disclaimer present
- [ ] Alternative dates proposed if original dates unavailable
- [ ] Multiple sources attempted if initial search fails
- [ ] Results appended to trip_draft.md without reading file

---

## Task 4: Activities Search Agent

- Implemented: false
- Test Passed: false
- Goal: Search for attractions, tours, and restaurants matching user interests
- Inputs: Destination, dates, group size, budget, interests, preferences
- Outputs: Curated activity options appended to trip_draft.md

**Specifications:**
1. Search for attractions, tours, restaurants, and experiences at destination
2. Extract: name, description, location, cost, duration, booking platform, opening hours
3. Curate options matching user interests and budget (prioritize by stated preferences)
4. Include variety: cultural sites, food experiences, shopping, relaxation
5. If webfetch fails, try multiple sources; after 3 failures, report to Lead Agent
6. Append results to trip_draft.md under ## Activities section; append only, do not read existing content
7. Include price disclaimer: prices are estimates and may change; verify before booking
8. Flag any activities requiring advance booking or having seasonal closures

**Test Case:**
- Destination: Tokyo, Japan
- Interests: Food & Dining, Temples & Culture, Shopping
- Budget: $50-150/day per person for activities
- Duration: 7 days

**Evaluation Criteria:**
- [ ] Activities curated to match stated interests (Food, Temples, Shopping)
- [ ] Activity details include: name, description, location, cost, duration, booking platform
- [ ] Variety of options across interest categories
- [ ] Price disclaimer present
- [ ] Advance booking requirements flagged
- [ ] Seasonal closures noted if applicable
- [ ] Results appended to trip_draft.md without reading file

---

## Task 5: Planning Agent (Draft Itinerary)

- Implemented: false
- Test Passed: false
- Goal: Create day-by-day itinerary combining search results into coherent schedule
- Inputs: trip_draft.md (all search results), preferences.md, user requirements
- Outputs: Complete draft itinerary overwriting trip_draft.md

**Specifications:**
1. Read trip_draft.md for all search results (flights, hotels, activities)
2. Read preferences.md for user preferences
3. Create day-by-day itinerary with: activities, timing, costs, booking platform recommendations
4. Include time estimates for each activity plus travel time between locations
5. Flag scheduling conflicts or unrealistic timing (e.g., too many activities in one day)
6. Include total estimated cost breakdown: flights + hotels + activities + buffer (10%)
7. Include visa/entry requirements section
8. Include emergency contacts section (embassy, local emergency numbers)
9. Include travel tips section (transportation, currency, customs)
10. Include luggage/packing recommendations based on user requirements and destination
11. Include travel warnings/restrictions section if applicable
12. Overwrite trip_draft.md with complete draft including: Itinerary, Options, Cost Summary, Disclaimers
13. Add "Last Updated" timestamp to trip_draft.md header

**Test Case:**
- Input: Flight/hotel/activity search results for Tokyo 7-day trip
- Preferences: Food & Dining priority, mid-range budget
- Output: Day-by-day itinerary with timing, costs, travel time estimates

**Evaluation Criteria:**
- [ ] Day-by-day itinerary covers all days of trip
- [ ] Each day includes morning, afternoon, evening activities
- [ ] Time estimates provided for each activity
- [ ] Travel time between locations included
- [ ] Scheduling conflicts flagged with warnings
- [ ] Total cost breakdown includes: flights, hotels, activities, 10% buffer
- [ ] Visa/entry requirements section present
- [ ] Emergency contacts section present (embassy, local emergency numbers)
- [ ] Travel tips section present (transportation, currency, customs)
- [ ] Luggage/packing recommendations included
- [ ] Travel warnings/restrictions section present if applicable
- [ ] Price disclaimer present
- [ ] "Last Updated" timestamp in header
- [ ] trip_draft.md overwritten completely (not appended)

---

## Task 6: Finalization Agent

- Implemented: false
- Test Passed: false
- Goal: Apply final revisions and produce approved trip_final.md
- Inputs: trip_draft.md, user feedback, preferences.md
- Outputs: trip_final.md, updated preferences.md

**Specifications:**
1. Read trip_draft.md and user feedback from Lead Agent
2. Apply final revisions if requested (within 5-revision limit)
3. Overwrite trip_final.md with approved plan including all sections:
   - Travelers (group size, dates)
   - Itinerary (day-by-day with timing)
   - Bookings (flights, hotels, activities with platform recommendations)
   - Cost Summary (breakdown with 10% buffer)
   - Visa/Entry Requirements
   - Emergency Contacts
   - Travel Tips
   - Luggage/Packing Recommendations
   - Travel Warnings/Restrictions (if applicable)
   - Price Disclaimer
4. Append new preferences to preferences.md organized by category:
   - Flight Preferences (with date added)
   - Hotel Preferences (with date added)
   - Activity Preferences (with date added)
   - Budget Preferences (with date added)
   - Past Feedback (session-specific notes with session ID and date)
5. Include both explicit preferences (stated by user) and inferred preferences (deduced from choices)
6. Mark finalized in progress.txt and requirements.txt with timestamp
7. Include session ID in all output files

**Test Case:**
- Input: trip_draft.md after 2 revision cycles
- User feedback: "Approve this plan, prefer ANA airlines for future, like mid-range hotels in central location"
- Output: trip_final.md with all sections, preferences.md updated

**Evaluation Criteria:**
- [ ] trip_final.md contains all required sections (Travelers, Itinerary, Bookings, Cost Summary, Visa, Emergency, Tips, Luggage, Warnings, Disclaimer)
- [ ] Price disclaimer present stating estimates may change and to verify before booking
- [ ] Session ID present in trip_final.md header
- [ ] preferences.md updated with explicit preferences (ANA airlines, mid-range central hotels)
- [ ] preferences.md updated with inferred preferences (from user choices during session)
- [ ] Preferences organized by category with dates
- [ ] Past Feedback section includes session ID and date
- [ ] progress.txt marked as finalized with timestamp
- [ ] requirements.txt marked as finalized with timestamp

---

## Task 7: Preference Learning System

- Implemented: false
- Test Passed: false
- Goal: Accumulate and summarize user preferences across sessions
- Inputs: User feedback, user choices during session, past preferences.md
- Outputs: Updated preferences.md with categorized, dated entries

**Specifications:**
1. Read existing preferences.md at session start to learn past preferences
2. Ask user if they want to apply past preferences to current trip
3. Capture explicit preferences from user feedback (e.g., "prefer ANA airlines")
4. Infer preferences from user choices (e.g., if user selects mid-range hotel, infer "prefers mid-range accommodations")
5. Organize preferences by category:
   - Flight Preferences: airline, seat class, luggage, timing
   - Hotel Preferences: price range, location, amenities, chain
   - Activity Preferences: interests, pace, group vs solo
   - Budget Preferences: total budget, per-day, price sensitivity
6. Include date when each preference was added/updated
7. Summarize past session preferences in Past Feedback section with session ID
8. When multiple preferences conflict, note the most recent takes priority
9. Append new preferences to preferences.md; do not overwrite existing preferences

**Test Case:**
- Session 1: User states "prefer window seats, like relaxation activities"
- Session 2: User selects mid-range hotel, chooses food tours
- Output: preferences.md with both explicit (window seats, relaxation) and inferred (mid-range, food tours) preferences with dates

**Evaluation Criteria:**
- [ ] Past preferences read at session start
- [ ] User asked if applying past preferences
- [ ] Explicit preferences captured and categorized
- [ ] Inferred preferences deduced from user choices
- [ ] Preferences organized by category (Flight, Hotel, Activity, Budget)
- [ ] Each preference entry includes date added
- [ ] Past Feedback section includes session ID and summary
- [ ] Most recent preference takes priority in case of conflict
- [ ] New preferences appended without overwriting existing
