# Trip Planner Skill - Product Requirements & Test Cases

## Skill Overview
Create personalized trip plans by searching airline/hotel info, interacting with users for preferences, producing approved itineraries with costs.

## Test Cases

### Task 1: Basic Trip Plan Creation
**Goal:** Create a complete trip plan from user requirements

**Test Case Input:**
- Departure: New York
- Destination: Paris, France
- Dates: 2026-06-01 to 2026-06-08
- Group: 2 adults
- Budget: $3000-5000 per person
- Interests: sightseeing, food, museums

**Evaluation Criteria:**
1. trip_draft.md created with flight options at 3 price points (budget/mid-range/premium)
2. trip_draft.md created with hotel options at 3 price points
3. trip_draft.md contains activities matching interests (sightseeing, food, museums)
4. Day-by-day itinerary created with timing and costs
5. Cost summary includes flights, hotels, activities, buffer, and total
6. Booking platform recommendations provided (not direct URLs)
7. progress.txt shows all tasks completed

**Test Passed:** true

### Task 2: User Feedback & Revision Loop
**Goal:** Handle user feedback and revise the plan

**Test Case Input:**
- Initial plan created (from Task 1)
- User feedback: "Hotel budget too high, prefer budget option. Add more food experiences."
- Expected: Revised plan with budget hotel and additional restaurant recommendations

**Evaluation Criteria:**
1. requirements.txt logs the feedback round with user comments
2. progress.txt increments loop count
3. Revised trip_draft.md reflects budget hotel selection
4. Revised trip_draft.md includes additional food/restaurant options
5. Cost summary updated to reflect changes

**Test Passed:** true

### Task 3: Preferences Accumulation
**Goal:** Save user feedback to preferences.md for future sessions

**Test Case Input:**
- Completed trip plan with user preferences expressed during session
- Example preferences: "prefer aisle seat", "like boutique hotels", "vegetarian"

**Evaluation Criteria:**
1. preferences.md appended with new feedback section
2. Preferences structured under appropriate categories (Flight/Hotel/Activity/Budget)
3. Past feedback section contains session-specific notes

**Test Passed:** true

### Task 4: Date Change Revision (Re-search Required)
**Goal:** Handle major revision requiring flight/hotel re-search

**Test Case Input:**
- Initial plan created with dates 2026-06-01 to 2026-06-08
- User feedback: "Change dates to 2026-06-15 to 2026-06-22"
- Expected: New flight and hotel searches performed

**Evaluation Criteria:**
1. requirements.txt logs the date change request
2. progress.txt notes re-search performed
3. trip_draft.md contains NEW flight options for revised dates
4. trip_draft.md contains NEW hotel options for revised dates
5. Itinerary adjusted for new date range

**Test Passed:** true

### Task 5: Final Approval & Output
**Goal:** Finalize approved plan to trip_final.md

**Test Case Input:**
- User approves revised plan
- Expected: trip_final.md created with complete booking info

**Evaluation Criteria:**
1. trip_final.md created (not just draft)
2. Contains selected (not options) flights with booking platform
3. Contains selected hotel with booking platform
4. Contains finalized day-by-day itinerary
5. Contains complete cost summary with total
6. Contains important notes (visa, insurance, packing tips)
7. progress.txt marked as finalized
8. requirements.txt marked with approval timestamp

**Test Passed:** true
