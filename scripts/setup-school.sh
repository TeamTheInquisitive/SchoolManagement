#!/bin/bash
# School Setup Script
# Usage: ./setup-school.sh <email> <password>
# Example: ./setup-school.sh admin@school.com password123

set -e

API_BASE="https://schoolmanagement-production-ff2e.up.railway.app/api/v1"
COOKIE_FILE="/tmp/school_setup_cookies.txt"

EMAIL="${1:?Usage: $0 <email> <password>}"
PASSWORD="${2:?Usage: $0 <email> <password>}"

echo "============================================"
echo "  School ERP Setup Script"
echo "============================================"
echo ""

# --- 1. Login ---
echo "[1/8] Logging in as $EMAIL..."
LOGIN_RESPONSE=$(curl -s -c "$COOKIE_FILE" -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

USER_NAME=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['user']['full_name'])" 2>/dev/null)
if [ -z "$USER_NAME" ]; then
  echo "ERROR: Login failed!"
  echo "$LOGIN_RESPONSE"
  exit 1
fi
echo "  ✓ Logged in as: $USER_NAME"
echo ""

# --- 2. Check ID Generation Config ---
echo "[2/8] Checking ID generation config..."
ID_CONFIG=$(curl -s -b "$COOKIE_FILE" "$API_BASE/admin/settings/id-generation")
echo "  $ID_CONFIG" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"  Prefix: {d.get('prefix', 'NOT SET')}\")
print(f\"  Student pattern: {d.get('student', {}).get('pattern', '—')} → preview: {d.get('student', {}).get('preview', '—')}\")
print(f\"  Teacher pattern: {d.get('teacher', {}).get('pattern', '—')} → preview: {d.get('teacher', {}).get('preview', '—')}\")
print(f\"  Staff pattern:   {d.get('staff', {}).get('pattern', '—')} → preview: {d.get('staff', {}).get('preview', '—')}\")
"
echo ""

# --- 3. Check next IDs ---
echo "[3/8] Verifying next-id generation..."
NEXT_STUDENT=$(curl -s -b "$COOKIE_FILE" "$API_BASE/admin/settings/next-id?type=student")
NEXT_TEACHER=$(curl -s -b "$COOKIE_FILE" "$API_BASE/admin/settings/next-id?type=teacher")
NEXT_STAFF=$(curl -s -b "$COOKIE_FILE" "$API_BASE/admin/settings/next-id?type=staff")
echo "  Next Student ID: $(echo $NEXT_STUDENT | python3 -c "import sys,json; print(json.load(sys.stdin).get('id','—'))")"
echo "  Next Teacher ID: $(echo $NEXT_TEACHER | python3 -c "import sys,json; print(json.load(sys.stdin).get('id','—'))")"
echo "  Next Staff ID:   $(echo $NEXT_STAFF | python3 -c "import sys,json; print(json.load(sys.stdin).get('id','—'))")"
echo ""

# --- 4. Create Academic Year ---
echo "[4/8] Creating academic year 2026-2027..."
AY_RESPONSE=$(curl -s -b "$COOKIE_FILE" -X POST "$API_BASE/admin/settings/academic-years" \
  -H "Content-Type: application/json" \
  -d '{"name": "2026-2027", "start_date": "2026-04-01", "end_date": "2027-03-31"}')
AY_ID=$(echo "$AY_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
if [ -z "$AY_ID" ]; then
  echo "  WARNING: May already exist. Fetching existing..."
  AY_ID=$(curl -s -b "$COOKIE_FILE" "$API_BASE/admin/settings/academic-years" | python3 -c "
import sys,json
years = json.load(sys.stdin).get('academic_years', [])
for y in years:
    if y['name'] == '2026-2027':
        print(y['id'])
        break
")
fi
echo "  ✓ Academic Year ID: $AY_ID"

# Set as current
echo "  Setting as current academic year..."
curl -s -b "$COOKIE_FILE" -X POST "$API_BASE/admin/settings/academic-years/$AY_ID/set-current" \
  -H "Content-Type: application/json" > /dev/null
echo "  ✓ Set as current"
echo ""

# --- 5. Create Subjects ---
echo "[5/8] Creating 10 subjects..."
SUBJECTS_RESPONSE=$(curl -s -b "$COOKIE_FILE" -X POST "$API_BASE/admin/settings/subjects/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "subjects": [
      {"name": "Mathematics", "code": "MATH", "description": "Mathematics"},
      {"name": "English", "code": "ENG", "description": "English Language and Literature"},
      {"name": "Hindi", "code": "HIN", "description": "Hindi Language"},
      {"name": "Science", "code": "SCI", "description": "General Science"},
      {"name": "Social Studies", "code": "SST", "description": "History, Geography, Civics"},
      {"name": "Computer Science", "code": "CS", "description": "Computer Science and IT"},
      {"name": "Physical Education", "code": "PE", "description": "Physical Education and Sports"},
      {"name": "Art", "code": "ART", "description": "Visual Arts and Craft"},
      {"name": "Music", "code": "MUS", "description": "Music and Performing Arts"},
      {"name": "Moral Science", "code": "MS", "description": "Value Education and Ethics"}
    ]
  }')
echo "  ✓ $(echo $SUBJECTS_RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message', d))")"
echo ""

# --- 6. Create Classes ---
echo "[6/8] Creating 12 classes (LKG, UKG, 1-10)..."
CLASSES_RESPONSE=$(curl -s -b "$COOKIE_FILE" -X POST "$API_BASE/admin/settings/classes/bulk" \
  -H "Content-Type: application/json" \
  -d '{"classes": ["LKG", "UKG", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]}')
echo "  ✓ $(echo $CLASSES_RESPONSE | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message', d))")"
echo ""

# --- 7. Add Sections to Classes ---
echo "[7/8] Adding sections to classes..."

# Get class IDs
CLASS_DATA=$(curl -s -b "$COOKIE_FILE" "$API_BASE/admin/settings/class-sections")

# Parse class IDs
get_class_id() {
  echo "$CLASS_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data['classes']:
    if c['name'] == '$1':
        print(c['id'])
        break
"
}

# LKG & UKG: 2 sections (A, B)
for CLASS_NAME in LKG UKG; do
  CID=$(get_class_id "$CLASS_NAME")
  curl -s -b "$COOKIE_FILE" -X POST "$API_BASE/admin/settings/sections/bulk" \
    -H "Content-Type: application/json" \
    -d "{\"sections\": [\"A\", \"B\"], \"class_id\": \"$CID\"}" > /dev/null
  echo "  ✓ $CLASS_NAME → A, B"
done

# Class 1-5: 3 sections (A, B, C)
for CLASS_NAME in 1 2 3 4 5; do
  CID=$(get_class_id "$CLASS_NAME")
  curl -s -b "$COOKIE_FILE" -X POST "$API_BASE/admin/settings/sections/bulk" \
    -H "Content-Type: application/json" \
    -d "{\"sections\": [\"A\", \"B\", \"C\"], \"class_id\": \"$CID\"}" > /dev/null
  echo "  ✓ Class $CLASS_NAME → A, B, C"
done

# Class 6-10: 4 sections (A, B, C, D)
for CLASS_NAME in 6 7 8 9 10; do
  CID=$(get_class_id "$CLASS_NAME")
  curl -s -b "$COOKIE_FILE" -X POST "$API_BASE/admin/settings/sections/bulk" \
    -H "Content-Type: application/json" \
    -d "{\"sections\": [\"A\", \"B\", \"C\", \"D\"], \"class_id\": \"$CID\"}" > /dev/null
  echo "  ✓ Class $CLASS_NAME → A, B, C, D"
done
echo ""

# --- 8. Map Subjects to Classes ---
echo "[8/8] Mapping subjects to classes..."

# Get subject IDs
SUBJECTS_DATA=$(curl -s -b "$COOKIE_FILE" "$API_BASE/admin/settings/subjects")

get_subject_id() {
  echo "$SUBJECTS_DATA" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data:
    if s['name'] == '$1':
        print(s['id'])
        break
"
}

MATH=$(get_subject_id "Mathematics")
ENG=$(get_subject_id "English")
HIN=$(get_subject_id "Hindi")
SCI=$(get_subject_id "Science")
SST=$(get_subject_id "Social Studies")
CS=$(get_subject_id "Computer Science")
PE=$(get_subject_id "Physical Education")
ART=$(get_subject_id "Art")
MUS=$(get_subject_id "Music")
MS=$(get_subject_id "Moral Science")

# LKG & UKG: 6 subjects
LKG_UKG_SUBJECTS="[\"$ENG\", \"$HIN\", \"$MATH\", \"$ART\", \"$MUS\", \"$PE\"]"
for CLASS_NAME in LKG UKG; do
  CID=$(get_class_id "$CLASS_NAME")
  curl -s -b "$COOKIE_FILE" -X PUT "$API_BASE/admin/settings/class-subjects/$CID" \
    -H "Content-Type: application/json" \
    -d "{\"subject_ids\": $LKG_UKG_SUBJECTS}" > /dev/null
  echo "  ✓ $CLASS_NAME → 6 subjects (Eng, Hin, Math, Art, Music, PE)"
done

# Class 1-5: 8 subjects
CLASS_1_5_SUBJECTS="[\"$ENG\", \"$HIN\", \"$MATH\", \"$SCI\", \"$SST\", \"$ART\", \"$PE\", \"$MS\"]"
for CLASS_NAME in 1 2 3 4 5; do
  CID=$(get_class_id "$CLASS_NAME")
  curl -s -b "$COOKIE_FILE" -X PUT "$API_BASE/admin/settings/class-subjects/$CID" \
    -H "Content-Type: application/json" \
    -d "{\"subject_ids\": $CLASS_1_5_SUBJECTS}" > /dev/null
  echo "  ✓ Class $CLASS_NAME → 8 subjects"
done

# Class 6-10: All 10 subjects
CLASS_6_10_SUBJECTS="[\"$ENG\", \"$HIN\", \"$MATH\", \"$SCI\", \"$SST\", \"$CS\", \"$PE\", \"$ART\", \"$MUS\", \"$MS\"]"
for CLASS_NAME in 6 7 8 9 10; do
  CID=$(get_class_id "$CLASS_NAME")
  curl -s -b "$COOKIE_FILE" -X PUT "$API_BASE/admin/settings/class-subjects/$CID" \
    -H "Content-Type: application/json" \
    -d "{\"subject_ids\": $CLASS_6_10_SUBJECTS}" > /dev/null
  echo "  ✓ Class $CLASS_NAME → 10 subjects (all)"
done
echo ""

# --- Done ---
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "Summary:"
echo "  • Academic Year: 2026-2027 (current)"
echo "  • Subjects: 10"
echo "  • Classes: 12 (LKG, UKG, 1-10)"
echo "  • Sections: LKG/UKG(A,B) | 1-5(A,B,C) | 6-10(A,B,C,D)"
echo "  • Subject mappings: LKG/UKG(6) | 1-5(8) | 6-10(10)"
echo ""

# Cleanup
rm -f "$COOKIE_FILE"
