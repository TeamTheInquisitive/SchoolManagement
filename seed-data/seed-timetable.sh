#!/bin/bash
# =============================================================================
# Seed Timetable Data: 6 Period Configs + 30 Timetable Slots for Class 10-A
# =============================================================================
# Usage: ./seed-timetable.sh [base_url]
# Requires: curl, python3 (for JSON parsing)

set -uo pipefail

BASE_URL="${1:-https://schoolmanagement-production-ff2e.up.railway.app/api/v1}"
COOKIE_FILE="/tmp/tt_cookies.txt"
HEADERS='-H "Content-Type: application/json" -H "X-School-Code: SCH001"'

echo "=== Timetable Seeder ==="
echo "Base URL: $BASE_URL"
echo ""

# ---------------------------------------------------------------------------
# Helper function for API calls
# ---------------------------------------------------------------------------
api_post() {
  local endpoint="$1"
  local data="$2"
  curl -s -w "\n%{http_code}" "${BASE_URL}${endpoint}" \
    -X POST -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' \
    -b "$COOKIE_FILE" --data-raw "$data"
}

api_get() {
  local endpoint="$1"
  curl -s "${BASE_URL}${endpoint}" \
    -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' \
    -b "$COOKIE_FILE"
}

# ---------------------------------------------------------------------------
# Step 0: Login
# ---------------------------------------------------------------------------
echo ">>> Logging in..."
LOGIN_RESP=$(curl -s "${BASE_URL}/auth/login" -X POST \
  -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' \
  -c "$COOKIE_FILE" \
  --data-raw '{"email":"admin@school.com","password":"password123"}')

if echo "$LOGIN_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('user')" 2>/dev/null; then
  echo "    Login successful."
else
  echo "    ERROR: Login failed. Response: $LOGIN_RESP"
  exit 1
fi
echo ""

# ---------------------------------------------------------------------------
# Step 0.5: Create missing subjects (Physics, Chemistry, Biology, Library, Free)
# ---------------------------------------------------------------------------
echo ">>> Ensuring required subjects exist..."
EXISTING_SUBJECTS=$(api_get "/admin/settings/subjects")
MISSING_SUBJECTS="[]"

# Check which subjects need to be created
MISSING_SUBJECTS=$(python3 -c "
import json, sys
existing = json.loads('''$EXISTING_SUBJECTS''')
existing_names = {s['name'] for s in existing}
needed = ['Physics', 'Chemistry', 'Biology', 'Library', 'Free Period']
missing = []
for name in needed:
    if name not in existing_names:
        code = name[:3].upper()
        if name == 'Physics': code = 'PHY2'
        elif name == 'Chemistry': code = 'CHE'
        elif name == 'Biology': code = 'BIO'
        elif name == 'Library': code = 'LIB'
        elif name == 'Free Period': code = 'FREE'
        missing.append({'name': name, 'code': code})
print(json.dumps(missing))
")

if [ "$MISSING_SUBJECTS" != "[]" ]; then
  BULK_PAYLOAD="{\"subjects\":$MISSING_SUBJECTS}"
  RESP=$(api_post "/admin/settings/subjects/bulk" "$BULK_PAYLOAD")
  HTTP_CODE=$(echo "$RESP" | tail -1)
  BODY=$(echo "$RESP" | sed '$d')
  if [ "$HTTP_CODE" = "201" ]; then
    echo "    Created missing subjects: $BODY"
  else
    echo "    Warning: Could not create subjects (HTTP $HTTP_CODE): $BODY"
  fi
else
  echo "    All required subjects already exist."
fi

# Refresh subjects list
SUBJECTS_JSON=$(api_get "/admin/settings/subjects")
echo ""

# ---------------------------------------------------------------------------
# Step 1: Create 6 Period Configs
# ---------------------------------------------------------------------------
echo ">>> Creating 6 Period Configs..."

declare -a PERIODS=(
  '{"start_time":"08:00:00","end_time":"08:45:00","name":"Period 1","is_break":false}'
  '{"start_time":"08:50:00","end_time":"09:35:00","name":"Period 2","is_break":false}'
  '{"start_time":"09:40:00","end_time":"10:25:00","name":"Period 3","is_break":false}'
  '{"start_time":"10:45:00","end_time":"11:30:00","name":"Period 4","is_break":false}'
  '{"start_time":"11:35:00","end_time":"12:20:00","name":"Period 5","is_break":false}'
  '{"start_time":"13:00:00","end_time":"13:45:00","name":"Period 6","is_break":false}'
)

PERIOD_IDS=()
PERIOD_SUCCESS=0
PERIOD_FAIL=0

for i in "${!PERIODS[@]}"; do
  RESP=$(api_post "/admin/timetable/periods" "${PERIODS[$i]}")
  HTTP_CODE=$(echo "$RESP" | tail -1)
  BODY=$(echo "$RESP" | sed '$d')

  if [ "$HTTP_CODE" = "201" ]; then
    PERIOD_ID=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
    if [ -n "$PERIOD_ID" ]; then
      PERIOD_IDS+=("$PERIOD_ID")
      PERIOD_SUCCESS=$((PERIOD_SUCCESS + 1))
      echo "    Period $((i+1)): Created (ID: $PERIOD_ID)"
    else
      PERIOD_FAIL=$((PERIOD_FAIL + 1))
      echo "    Period $((i+1)): Created but couldn't parse ID. Body: $BODY"
    fi
  else
    PERIOD_FAIL=$((PERIOD_FAIL + 1))
    echo "    Period $((i+1)): FAILED (HTTP $HTTP_CODE) - $BODY"
  fi
done

echo "    Summary: $PERIOD_SUCCESS created, $PERIOD_FAIL failed"
echo ""

# ---------------------------------------------------------------------------
# Step 1.5: Fetch period IDs if creation failed (maybe they already exist)
# ---------------------------------------------------------------------------
if [ ${#PERIOD_IDS[@]} -lt 6 ]; then
  echo ">>> Attempting to fetch existing periods..."
  PERIODS_LIST=$(api_get "/admin/timetable/periods")
  FETCHED_IDS=$(python3 -c "
import json, sys
try:
    data = json.loads('''$PERIODS_LIST''')
    periods = data.get('periods', [])
    for p in periods:
        print(p['id'])
except:
    pass
" 2>/dev/null)

  if [ -n "$FETCHED_IDS" ]; then
    PERIOD_IDS=()
    while IFS= read -r pid; do
      PERIOD_IDS+=("$pid")
    done <<< "$FETCHED_IDS"
    echo "    Found ${#PERIOD_IDS[@]} existing periods."
  else
    echo "    Could not fetch existing periods."
  fi
  echo ""
fi

# ---------------------------------------------------------------------------
# Step 2: Lookup class_section_id for Class 10-A
# ---------------------------------------------------------------------------
echo ">>> Looking up class_section_id for Class 10-A..."
CLASS_SECTION_ID=""

# Try the class-sections endpoint
CS_RESP=$(api_get "/admin/settings/class-sections")
CLASS_SECTION_ID=$(python3 -c "
import json, sys
try:
    data = json.loads('''$CS_RESP''')
    for cs in data:
        if cs.get('class_name') == '10' and cs.get('section') == 'A':
            print(cs['id'])
            break
except:
    pass
" 2>/dev/null)

if [ -n "$CLASS_SECTION_ID" ]; then
  echo "    Found class_section_id: $CLASS_SECTION_ID"
else
  echo "    WARNING: Could not find Class 10-A section. API response: $CS_RESP"
  echo "    Slots creation will likely fail."
fi
echo ""

# ---------------------------------------------------------------------------
# Step 3: Lookup teacher IDs
# ---------------------------------------------------------------------------
echo ">>> Looking up teacher IDs..."
TEACHER_ID=""

# Try to get any teacher from the teachers list
TEACHERS_RESP=$(api_get "/admin/teachers?page=1&page_size=1")
TEACHER_ID=$(python3 -c "
import json, sys
try:
    data = json.loads('''$TEACHERS_RESP''')
    teachers = data.get('teachers', data.get('items', data.get('data', [])))
    if isinstance(teachers, list) and len(teachers) > 0:
        print(teachers[0].get('id', teachers[0].get('teacher_id', '')))
except:
    pass
" 2>/dev/null)

if [ -z "$TEACHER_ID" ]; then
  # Use a placeholder - the API might accept it or reject it
  TEACHER_ID="00000000-0000-0000-0000-000000000000"
  echo "    WARNING: Could not fetch teacher ID. Using placeholder: $TEACHER_ID"
else
  echo "    Found teacher_id: $TEACHER_ID"
fi
echo ""

# ---------------------------------------------------------------------------
# Step 4: Map subject names to IDs
# ---------------------------------------------------------------------------
echo ">>> Mapping subject names to IDs..."

get_subject_id() {
  local subject_name="$1"
  python3 -c "
import json, sys
subjects = json.loads('''$SUBJECTS_JSON''')
name_map = {
    'Mathematics': 'Mathematics',
    'Math': 'Mathematics',
    'Physics': 'Physics',
    'Chemistry': 'Chemistry',
    'Biology': 'Biology',
    'English': 'English',
    'Hindi': 'Hindi',
    'Computer': 'Computer Science',
    'PE': 'Physical Education',
    'Art': 'Art',
    'Library': 'Library',
    'Free': 'Free Period',
}
target = name_map.get('$subject_name', '$subject_name')
for s in subjects:
    if s['name'] == target:
        print(s['id'])
        break
" 2>/dev/null
}

# Test subject mapping
MATH_ID=$(get_subject_id "Mathematics")
echo "    Mathematics -> $MATH_ID"
PHYSICS_ID=$(get_subject_id "Physics")
echo "    Physics -> $PHYSICS_ID"
ENGLISH_ID=$(get_subject_id "English")
echo "    English -> $ENGLISH_ID"
echo ""

# ---------------------------------------------------------------------------
# Step 5: Create 30 Timetable Slots for Class 10-A
# ---------------------------------------------------------------------------
echo ">>> Creating 30 Timetable Slots for Class 10-A (Monday-Saturday)..."

# Schedule: [day] = "subject1,subject2,subject3,subject4,subject5,subject6"
declare -A SCHEDULE
SCHEDULE[Monday]="Mathematics,Physics,English,Chemistry,Hindi,Free"
SCHEDULE[Tuesday]="English,Mathematics,Biology,Hindi,Computer,PE"
SCHEDULE[Wednesday]="Physics,Mathematics,Hindi,English,Art,Free"
SCHEDULE[Thursday]="Mathematics,English,Physics,Chemistry,Hindi,Computer"
SCHEDULE[Friday]="Chemistry,Biology,Mathematics,English,Library,Free"
SCHEDULE[Saturday]="Biology,Hindi,PE,Art,Free,Free"

# Subjects that are practical-type
PRACTICAL_SUBJECTS="Physics Chemistry Biology Computer"

SLOT_SUCCESS=0
SLOT_FAIL=0
SLOT_SKIP=0
# Note: Using $((var + 1)) instead of ((var++)) to avoid exit code issues with set -e

DAYS=("Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday")

for day in "${DAYS[@]}"; do
  IFS=',' read -ra SUBJECTS <<< "${SCHEDULE[$day]}"
  echo "  $day:"

  for period_idx in "${!SUBJECTS[@]}"; do
    subject="${SUBJECTS[$period_idx]}"

    # Check if we have the period ID
    if [ $period_idx -ge ${#PERIOD_IDS[@]} ]; then
      echo "    Period $((period_idx+1)): SKIPPED (no period_config_id available)"
      SLOT_SKIP=$((SLOT_SKIP + 1))
      continue
    fi

    PERIOD_CONFIG_ID="${PERIOD_IDS[$period_idx]}"
    SUBJECT_ID=$(get_subject_id "$subject")

    if [ -z "$SUBJECT_ID" ]; then
      echo "    Period $((period_idx+1)) ($subject): SKIPPED (subject not found)"
      SLOT_SKIP=$((SLOT_SKIP + 1))
      continue
    fi

    if [ -z "$CLASS_SECTION_ID" ]; then
      echo "    Period $((period_idx+1)) ($subject): SKIPPED (no class_section_id)"
      SLOT_SKIP=$((SLOT_SKIP + 1))
      continue
    fi

    # Determine slot_type
    SLOT_TYPE="Lecture"
    if echo "$PRACTICAL_SUBJECTS" | grep -qw "$subject"; then
      SLOT_TYPE="Practical"
    fi

    # Build slot payload
    SLOT_PAYLOAD=$(python3 -c "
import json
payload = {
    'class_section_id': '$CLASS_SECTION_ID',
    'day': '$day',
    'period_config_id': '$PERIOD_CONFIG_ID',
    'subject_id': '$SUBJECT_ID',
    'teacher_id': '$TEACHER_ID',
    'slot_type': '$SLOT_TYPE'
}
print(json.dumps(payload))
")

    RESP=$(api_post "/admin/timetable/slot" "$SLOT_PAYLOAD")
    HTTP_CODE=$(echo "$RESP" | tail -1)
    BODY=$(echo "$RESP" | sed '$d')

    if [ "$HTTP_CODE" = "201" ]; then
      SLOT_SUCCESS=$((SLOT_SUCCESS + 1))
      echo "    Period $((period_idx+1)) ($subject): OK [$SLOT_TYPE]"
    elif [ "$HTTP_CODE" = "422" ]; then
      # Validation error - try without teacher_id
      SLOT_PAYLOAD_NO_TEACHER=$(python3 -c "
import json
payload = {
    'class_section_id': '$CLASS_SECTION_ID',
    'day': '$day',
    'period_config_id': '$PERIOD_CONFIG_ID',
    'subject_id': '$SUBJECT_ID',
    'slot_type': '$SLOT_TYPE'
}
print(json.dumps(payload))
")
      RESP2=$(api_post "/admin/timetable/slot" "$SLOT_PAYLOAD_NO_TEACHER")
      HTTP_CODE2=$(echo "$RESP2" | tail -1)
      BODY2=$(echo "$RESP2" | sed '$d')
      if [ "$HTTP_CODE2" = "201" ]; then
        SLOT_SUCCESS=$((SLOT_SUCCESS + 1))
        echo "    Period $((period_idx+1)) ($subject): OK (no teacher) [$SLOT_TYPE]"
      else
        SLOT_FAIL=$((SLOT_FAIL + 1))
        echo "    Period $((period_idx+1)) ($subject): FAILED (HTTP $HTTP_CODE2) - $BODY2"
      fi
    else
      SLOT_FAIL=$((SLOT_FAIL + 1))
      echo "    Period $((period_idx+1)) ($subject): FAILED (HTTP $HTTP_CODE) - $BODY"
    fi
  done
done

echo ""
echo "=== Timetable Seeding Summary ==="
echo "Periods: $PERIOD_SUCCESS created, $PERIOD_FAIL failed"
echo "Slots:   $SLOT_SUCCESS created, $SLOT_FAIL failed, $SLOT_SKIP skipped"
echo "================================="
