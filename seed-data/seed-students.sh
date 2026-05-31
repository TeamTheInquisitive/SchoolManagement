#!/bin/bash
# Seed 200 students from students_200.json
BASE_URL="${BASE_URL:-https://schoolmanagement-prod.up.railway.app/api/v1}"
COOKIE_FILE="${COOKIE_FILE:-/tmp/school_seed_cookies.txt}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_FILE="$SCRIPT_DIR/students_200.json"

if [ ! -f "$DATA_FILE" ]; then
  echo "ERROR: $DATA_FILE not found!"
  exit 1
fi

SUCCESS=0; FAIL=0; TOTAL=$(python3 -c "import json; print(len(json.load(open('$DATA_FILE'))))")

echo "Inserting $TOTAL students..."

# Read each student from JSON and POST
python3 -c "
import json, subprocess, sys

with open('$DATA_FILE') as f:
    students = json.load(f)

success = 0
fail = 0

for i, student in enumerate(students):
    result = subprocess.run([
        'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
        '$BASE_URL/admin/students',
        '-X', 'POST',
        '-H', 'Content-Type: application/json',
        '-H', 'X-School-Code: SCH001',
        '-b', '$COOKIE_FILE',
        '--data-raw', json.dumps(student)
    ], capture_output=True, text=True)

    code = result.stdout.strip()
    if code == '201':
        success += 1
    else:
        fail += 1

    if (i + 1) % 25 == 0:
        print(f'  Progress: {i+1}/{len(students)} (success: {success}, fail: {fail})', flush=True)

print(f'Students: {success} created, {fail} skipped/failed')
"
