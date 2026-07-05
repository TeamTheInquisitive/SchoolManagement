#!/bin/bash
# Login and save cookies for subsequent API calls
BASE_URL="${BASE_URL:-https://schoolmanagement-production-ff2e.up.railway.app/api/v1}"
COOKIE_FILE="${COOKIE_FILE:-/tmp/school_seed_cookies.txt}"

curl -s "$BASE_URL/auth/login" \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-School-Code: SCH001' \
  -c "$COOKIE_FILE" \
  --data-raw '{"email":"admin@school.com","password":"password123"}'

echo ""
echo "Cookies saved to $COOKIE_FILE"
