#!/bin/bash
# Seed script for examination data
# Creates 20 exams across various classes, subjects, and types
#
# NOTE: Uses classes 8, 9, 10 with sections A, B and subjects:
# Mathematics, English, Science, Social Studies, Hindi, Computer Science

BASE_URL="https://schoolmanagement-production-ff2e.up.railway.app/api/v1"
COOKIE_FILE="/tmp/exam_cookies.txt"

# Login first
echo "Logging in..."
curl -s "${BASE_URL}/auth/login" -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-School-Code: SCH001' \
  -c "$COOKIE_FILE" \
  --data-raw '{"email":"admin@school.com","password":"password123"}'
echo ""
echo ""

SUCCESS=0
FAIL=0

create_exam() {
  local payload="$1"
  local name="$2"

  echo -n "Creating: ${name} ... "
  RESPONSE=$(curl -s "${BASE_URL}/admin/examinations" -X POST \
    -H 'Content-Type: application/json' \
    -H 'X-School-Code: SCH001' \
    -b "$COOKIE_FILE" \
    --data-raw "$payload")

  if echo "$RESPONSE" | grep -q '"id"'; then
    echo "SUCCESS"
    SUCCESS=$((SUCCESS + 1))
  else
    echo "FAILED: $RESPONSE"
    FAIL=$((FAIL + 1))
  fi
}

# -----------------------------------------------------------------------
# 20 Exams - Spread across classes 8/9/10, sections A/B, various subjects
# Types: Unit Test (total=50), Mid-Term (total=100), Final (total=100), Practical (total=30)
# Status: Published (12), Scheduled (5), Draft (3)
# -----------------------------------------------------------------------

# Exam 1: Unit Test - Published - Term 1
create_exam '{"name":"Unit Test 1 - Mathematics Class 10A","exam_type":"Unit Test","class_name":"10","section":"A","subject":"Mathematics","date":"2025-08-20","start_time":"09:00","end_time":"10:00","total_marks":50,"passing_marks":18,"academic_year":"2025-2026","term":"Term 1","status":"Published","metadata":{}}' \
  "Unit Test 1 - Mathematics Class 10A"

# Exam 2: Unit Test - Published - Term 1
create_exam '{"name":"Unit Test 1 - Science Class 9B","exam_type":"Unit Test","class_name":"9","section":"B","subject":"Science","date":"2025-08-25","start_time":"10:00","end_time":"11:00","total_marks":50,"passing_marks":18,"academic_year":"2025-2026","term":"Term 1","status":"Published","metadata":{}}' \
  "Unit Test 1 - Science Class 9B"

# Exam 3: Unit Test - Scheduled - Term 1
create_exam '{"name":"Unit Test 2 - English Class 8A","exam_type":"Unit Test","class_name":"8","section":"A","subject":"English","date":"2025-09-10","start_time":"09:00","end_time":"10:00","total_marks":50,"passing_marks":18,"academic_year":"2025-2026","term":"Term 1","status":"Scheduled","metadata":{}}' \
  "Unit Test 2 - English Class 8A"

# Exam 4: Mid-Term - Published - Term 1
create_exam '{"name":"Mid-Term English 9A","exam_type":"Mid-Term","class_name":"9","section":"A","subject":"English","date":"2025-09-25","start_time":"09:00","end_time":"12:00","total_marks":100,"passing_marks":35,"academic_year":"2025-2026","term":"Term 1","status":"Published","metadata":{}}' \
  "Mid-Term English 9A"

# Exam 5: Mid-Term - Published - Term 1
create_exam '{"name":"Mid-Term Mathematics 10B","exam_type":"Mid-Term","class_name":"10","section":"B","subject":"Mathematics","date":"2025-09-28","start_time":"09:00","end_time":"12:00","total_marks":100,"passing_marks":35,"academic_year":"2025-2026","term":"Term 1","status":"Published","metadata":{}}' \
  "Mid-Term Mathematics 10B"

# Exam 6: Mid-Term - Published - Term 1
create_exam '{"name":"Mid-Term Science 8B","exam_type":"Mid-Term","class_name":"8","section":"B","subject":"Science","date":"2025-10-02","start_time":"09:00","end_time":"12:00","total_marks":100,"passing_marks":35,"academic_year":"2025-2026","term":"Term 1","status":"Published","metadata":{}}' \
  "Mid-Term Science 8B"

# Exam 7: Practical - Published - Term 1
create_exam '{"name":"Practical - Computer Science Lab 10A","exam_type":"Practical","class_name":"10","section":"A","subject":"Computer Science","date":"2025-10-10","start_time":"14:00","end_time":"16:00","total_marks":30,"passing_marks":11,"academic_year":"2025-2026","term":"Term 1","status":"Published","metadata":{}}' \
  "Practical - Computer Science Lab 10A"

# Exam 8: Practical - Scheduled - Term 1
create_exam '{"name":"Practical - Science Lab 9A","exam_type":"Practical","class_name":"9","section":"A","subject":"Science","date":"2025-10-15","start_time":"14:00","end_time":"16:00","total_marks":30,"passing_marks":11,"academic_year":"2025-2026","term":"Term 1","status":"Scheduled","metadata":{}}' \
  "Practical - Science Lab 9A"

# Exam 9: Unit Test - Draft - Term 2
create_exam '{"name":"Unit Test 2 - Hindi Class 8A","exam_type":"Unit Test","class_name":"8","section":"A","subject":"Hindi","date":"2025-11-05","start_time":"09:00","end_time":"10:00","total_marks":50,"passing_marks":18,"academic_year":"2025-2026","term":"Term 2","status":"Draft","metadata":{}}' \
  "Unit Test 2 - Hindi Class 8A"

# Exam 10: Mid-Term - Published - Term 1
create_exam '{"name":"Mid-Term Computer Science 10B","exam_type":"Mid-Term","class_name":"10","section":"B","subject":"Computer Science","date":"2025-11-15","start_time":"09:00","end_time":"12:00","total_marks":100,"passing_marks":35,"academic_year":"2025-2026","term":"Term 1","status":"Published","metadata":{}}' \
  "Mid-Term Computer Science 10B"

# Exam 11: Final - Published - Term 1
create_exam '{"name":"Final Examination - Mathematics 8B","exam_type":"Final","class_name":"8","section":"B","subject":"Mathematics","date":"2025-12-10","start_time":"09:00","end_time":"12:00","total_marks":100,"passing_marks":35,"academic_year":"2025-2026","term":"Term 1","status":"Published","metadata":{}}' \
  "Final Examination - Mathematics 8B"

# Exam 12: Final - Published - Term 1
create_exam '{"name":"Final Examination - Social Studies 9A","exam_type":"Final","class_name":"9","section":"A","subject":"Social Studies","date":"2025-12-12","start_time":"09:00","end_time":"12:00","total_marks":100,"passing_marks":35,"academic_year":"2025-2026","term":"Term 1","status":"Published","metadata":{}}' \
  "Final Examination - Social Studies 9A"

# Exam 13: Unit Test - Scheduled - Term 2
create_exam '{"name":"Unit Test 3 - Science Class 9B","exam_type":"Unit Test","class_name":"9","section":"B","subject":"Science","date":"2026-01-15","start_time":"10:00","end_time":"11:00","total_marks":50,"passing_marks":18,"academic_year":"2025-2026","term":"Term 2","status":"Scheduled","metadata":{}}' \
  "Unit Test 3 - Science Class 9B"

# Exam 14: Mid-Term - Published - Term 2
create_exam '{"name":"Mid-Term Hindi 8B","exam_type":"Mid-Term","class_name":"8","section":"B","subject":"Hindi","date":"2026-01-28","start_time":"09:00","end_time":"12:00","total_marks":100,"passing_marks":35,"academic_year":"2025-2026","term":"Term 2","status":"Published","metadata":{}}' \
  "Mid-Term Hindi 8B"

# Exam 15: Practical - Draft - Term 2
create_exam '{"name":"Practical - Computer Science Lab 9B","exam_type":"Practical","class_name":"9","section":"B","subject":"Computer Science","date":"2026-02-05","start_time":"14:00","end_time":"16:00","total_marks":30,"passing_marks":11,"academic_year":"2025-2026","term":"Term 2","status":"Draft","metadata":{}}' \
  "Practical - Computer Science Lab 9B"

# Exam 16: Unit Test - Published - Term 2
create_exam '{"name":"Unit Test 3 - English Class 10A","exam_type":"Unit Test","class_name":"10","section":"A","subject":"English","date":"2026-02-15","start_time":"09:00","end_time":"10:00","total_marks":50,"passing_marks":18,"academic_year":"2025-2026","term":"Term 2","status":"Published","metadata":{}}' \
  "Unit Test 3 - English Class 10A"

# Exam 17: Mid-Term - Scheduled - Term 2
create_exam '{"name":"Mid-Term Social Studies 10B","exam_type":"Mid-Term","class_name":"10","section":"B","subject":"Social Studies","date":"2026-03-01","start_time":"09:00","end_time":"12:00","total_marks":100,"passing_marks":35,"academic_year":"2025-2026","term":"Term 2","status":"Scheduled","metadata":{}}' \
  "Mid-Term Social Studies 10B"

# Exam 18: Final - Published - Term 2
create_exam '{"name":"Final Examination - Science 9A","exam_type":"Final","class_name":"9","section":"A","subject":"Science","date":"2026-03-20","start_time":"09:00","end_time":"12:00","total_marks":100,"passing_marks":35,"academic_year":"2025-2026","term":"Term 2","status":"Published","metadata":{}}' \
  "Final Examination - Science 9A"

# Exam 19: Practical - Draft - Term 2
create_exam '{"name":"Practical - Science Lab 10B","exam_type":"Practical","class_name":"10","section":"B","subject":"Science","date":"2026-04-01","start_time":"14:00","end_time":"16:00","total_marks":30,"passing_marks":11,"academic_year":"2025-2026","term":"Term 2","status":"Draft","metadata":{}}' \
  "Practical - Science Lab 10B"

# Exam 20: Final - Scheduled - Term 2
create_exam '{"name":"Final Examination - Mathematics 8A","exam_type":"Final","class_name":"8","section":"A","subject":"Mathematics","date":"2026-04-10","start_time":"09:00","end_time":"12:00","total_marks":100,"passing_marks":35,"academic_year":"2025-2026","term":"Term 2","status":"Scheduled","metadata":{}}' \
  "Final Examination - Mathematics 8A"

echo ""
echo "================================="
echo "Results: $SUCCESS succeeded, $FAIL failed out of 20"
echo "================================="
