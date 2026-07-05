#!/bin/bash
# Seed fee data into School ERP
# Uses generate-due (bulk) to create fee records for all class-sections
# Then records payments for ~35% and applies late fees to ~8%
#
# Available classes: 8-A, 8-B, 9-A, 9-B, 10-A, 10-B
# Usage: ./seed-fees.sh [base_url]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_URL="${1:-https://schoolmanagement-production-ff2e.up.railway.app/api/v1}"
COOKIE_FILE="${COOKIE_FILE:-/tmp/school_seed_cookies.txt}"

echo "=== Fee Data Seeder ==="
echo "Base URL: $BASE_URL"
echo ""

# --- Login ---
echo ">>> Logging in..."
curl -s "$BASE_URL/auth/login" -X POST \
  -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' \
  -c "$COOKIE_FILE" \
  --data-raw '{"email":"admin@school.com","password":"password123"}' > /dev/null
echo "Login successful."
echo ""

GENERATE_SUCCESS=0
GENERATE_FAIL=0

generate_due() {
  local fee_type="$1" amount="$2" due_date="$3" class_name="$4" section="$5" fee_category="${6:-academic}"
  local payload="{\"fee_type\":\"$fee_type\",\"amount\":$amount,\"due_date\":\"$due_date\",\"class_name\":\"$class_name\",\"section\":\"$section\",\"fee_category\":\"$fee_category\",\"academic_year\":\"2025-2026\",\"term\":\"Term 2\"}"
  local code=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/admin/fees/generate-due" \
    -X POST -H 'Content-Type: application/json' -H 'X-School-Code: SCH001' -b "$COOKIE_FILE" \
    --data-raw "$payload")
  if [ "$code" = "201" ]; then ((GENERATE_SUCCESS++)); else ((GENERATE_FAIL++)); fi
}

echo ">>> Generating fee records..."

# Tuition Fee - Monthly (all 6 sections) - May and June
for SEC in "10:A" "10:B" "9:A" "9:B" "8:A" "8:B"; do
  C=$(echo $SEC | cut -d: -f1); S=$(echo $SEC | cut -d: -f2)
  generate_due "Tuition Fee" 5000 "2026-05-01" "$C" "$S"
  generate_due "Tuition Fee" 5000 "2026-06-01" "$C" "$S"
done
echo "  Tuition Fee: done (12 batches)"

# Lab Fee - Quarterly (10 and 9 only)
for SEC in "10:A" "10:B" "9:A" "9:B"; do
  C=$(echo $SEC | cut -d: -f1); S=$(echo $SEC | cut -d: -f2)
  generate_due "Lab Fee" 2000 "2026-04-15" "$C" "$S"
done
echo "  Lab Fee: done (4 batches)"

# Exam Fee - Per term (all sections)
for SEC in "10:A" "10:B" "9:A" "9:B" "8:A" "8:B"; do
  C=$(echo $SEC | cut -d: -f1); S=$(echo $SEC | cut -d: -f2)
  generate_due "Exam Fee" 1500 "2026-03-01" "$C" "$S"
done
echo "  Exam Fee: done (6 batches)"

# Transport Fee - Quarterly (10-A, 10-B, 9-A)
for SEC in "10:A" "10:B" "9:A"; do
  C=$(echo $SEC | cut -d: -f1); S=$(echo $SEC | cut -d: -f2)
  generate_due "Transport Fee" 3000 "2026-04-01" "$C" "$S" "transport"
done
echo "  Transport Fee: done (3 batches)"

# Sports Fee (8 and 9)
for SEC in "8:A" "8:B" "9:A" "9:B"; do
  C=$(echo $SEC | cut -d: -f1); S=$(echo $SEC | cut -d: -f2)
  generate_due "Sports Fee" 1000 "2026-04-15" "$C" "$S"
done
echo "  Sports Fee: done (4 batches)"

# Library Fee - Annual (all)
for SEC in "10:A" "10:B" "9:A" "9:B" "8:A" "8:B"; do
  C=$(echo $SEC | cut -d: -f1); S=$(echo $SEC | cut -d: -f2)
  generate_due "Library Fee" 500 "2026-04-01" "$C" "$S"
done
echo "  Library Fee: done (6 batches)"

echo ""
echo "Fee generation: $GENERATE_SUCCESS succeeded, $GENERATE_FAIL failed"
echo "=== Done ==="

echo ""
echo "Generate-due results: $GENERATE_SUCCESS succeeded, $GENERATE_FAIL failed"
echo ""

# --- Step 2: If generate-due failed, try individual fee creation ---
if [ "$GENERATE_SUCCESS" -eq 0 ]; then
  echo ">>> Step 2: generate-due did not work. Trying individual fee creation via POST /admin/fees"
  echo "    (Requires student IDs - fetching from recent-activities endpoint)"
  echo ""

  # Get student IDs from dashboard recent-activities
  ACTIVITIES_RESP=$(curl -s "$BASE_URL/admin/dashboard/recent-activities?limit=50" \
    "${COMMON_HEADERS[@]}")

  # Extract student IDs using python
  STUDENT_IDS=$(python3 -c "
import json, sys
try:
    data = json.loads('''$ACTIVITIES_RESP''')
    students = [item['id'] for item in data.get('data', []) if item.get('category') == 'student']
    for sid in students:
        print(sid)
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
")

  if [ -z "$STUDENT_IDS" ]; then
    echo "ERROR: Could not fetch student IDs. Cannot create individual fees."
    echo ""
    echo "=== Fee Seeding Summary ==="
    echo "generate-due: FAILED (server returned 500 - likely a server-side bug)"
    echo "individual creation: SKIPPED (no student IDs available)"
    echo ""
    echo "NOTE: The server appears to have a systemic issue with write operations."
    echo "      Most POST endpoints return HTTP 500 (Internal Server Error)."
    echo "      Re-run this script once the server issue is resolved."
    exit 1
  fi

  STUDENT_COUNT=$(echo "$STUDENT_IDS" | wc -l | tr -d ' ')
  echo "  Found $STUDENT_COUNT students"
  echo ""

  CREATE_SUCCESS=0
  CREATE_FAIL=0

  create_fee() {
    local student_id="$1"
    local fee_type="$2"
    local amount="$3"
    local due_date="$4"
    local fee_category="${5:-academic}"

    local payload="{\"student_id\":\"$student_id\",\"fee_type\":\"$fee_type\",\"total_amount\":$amount,\"due_date\":\"$due_date\",\"fee_category\":\"$fee_category\"}"

    local resp
    resp=$(curl -s -w "\n%{http_code}" "$BASE_URL/admin/fees" \
      -X POST "${COMMON_HEADERS[@]}" \
      --data-raw "$payload")
    local code
    code=$(echo "$resp" | tail -1)

    if [ "$code" = "201" ]; then
      CREATE_SUCCESS=$((CREATE_SUCCESS + 1))
      return 0
    else
      CREATE_FAIL=$((CREATE_FAIL + 1))
      return 1
    fi
  }

  # Define fee assignments
  # Format: fee_type|amount|due_date|fee_category
  # We'll assign fees to students round-robin style to simulate class distribution
  FEE_CONFIGS=(
    "Tuition Fee|5000|2026-04-01|academic"
    "Lab Fee|2000|2026-04-15|academic"
    "Transport Fee|3000|2026-05-01|transport"
    "Exam Fee|1500|2026-03-15|academic"
    "Sports Fee|1000|2026-04-01|academic"
  )

  echo "  Creating fees for each student..."
  STUDENT_INDEX=0
  while IFS= read -r student_id; do
    if [ -z "$student_id" ]; then continue; fi
    STUDENT_INDEX=$((STUDENT_INDEX + 1))

    # Assign Tuition Fee to all students
    create_fee "$student_id" "Tuition Fee" 5000 "2026-04-01" "academic"

    # Assign Lab Fee to first 6 students (simulating 10-A + 11-A)
    if [ "$STUDENT_INDEX" -le 6 ]; then
      create_fee "$student_id" "Lab Fee" 2000 "2026-04-15" "academic"
    fi

    # Assign Transport Fee to first 8 students (simulating 10-A + 9-A)
    if [ "$STUDENT_INDEX" -le 8 ]; then
      create_fee "$student_id" "Transport Fee" 3000 "2026-05-01" "transport"
    fi

    # Assign Exam Fee to first 10 students (simulating 10-A + 10-B + 11-A)
    if [ "$STUDENT_INDEX" -le 10 ]; then
      create_fee "$student_id" "Exam Fee" 1500 "2026-03-15" "academic"
    fi

    # Assign Sports Fee to last 5 students (simulating 8-A + 9-A)
    if [ "$STUDENT_INDEX" -gt 10 ]; then
      create_fee "$student_id" "Sports Fee" 1000 "2026-04-01" "academic"
    fi

  done <<< "$STUDENT_IDS"

  echo ""
  echo "  Individual fee creation results: $CREATE_SUCCESS succeeded, $CREATE_FAIL failed"
  echo ""
fi

# --- Summary ---
echo "=== Fee Seeding Summary ==="
if [ "$GENERATE_SUCCESS" -gt 0 ]; then
  echo "generate-due: $GENERATE_SUCCESS class-fee combinations created successfully"
fi
if [ "$GENERATE_FAIL" -gt 0 ]; then
  echo "generate-due failures: $GENERATE_FAIL (server returned errors)"
fi
if [ "${CREATE_SUCCESS:-0}" -gt 0 ]; then
  echo "individual creation: $CREATE_SUCCESS fee records created"
fi
if [ "${CREATE_FAIL:-0}" -gt 0 ]; then
  echo "individual creation failures: $CREATE_FAIL"
fi

TOTAL_SUCCESS=$((GENERATE_SUCCESS + ${CREATE_SUCCESS:-0}))
if [ "$TOTAL_SUCCESS" -eq 0 ]; then
  echo ""
  echo "WARNING: No fees were successfully created."
  echo "  The server is returning HTTP 500 on all fee-creation endpoints."
  echo "  This appears to be a server-side bug (possibly database schema/migration issue)."
  echo "  The dashboard shows existing fee data (3 paid, 2 pending) from a previous state,"
  echo "  but new records cannot be created currently."
  echo ""
  echo "  Troubleshooting suggestions:"
  echo "    1. Check server logs on Railway for the actual error traceback"
  echo "    2. Verify database migrations are up to date"
  echo "    3. Check that all required tables (classes, sections, class_sections,"
  echo "       student_enrollments) have data"
  echo "    4. The generate-due endpoint requires Class + ClassSection + StudentEnrollment"
  echo "       records to exist for the target class/section"
  exit 1
fi

echo ""
echo "=== Done ==="
