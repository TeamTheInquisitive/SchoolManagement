#!/bin/bash
# Master seed script - runs all seed operations
# Usage: ./seed-all.sh [base_url]

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export BASE_URL="${1:-https://schoolmanagement-production-ff2e.up.railway.app/api/v1}"
export COOKIE_FILE="/tmp/school_seed_cookies.txt"

echo "=== School ERP Data Seeder ==="
echo "Base URL: $BASE_URL"
echo ""

# Login first
echo ">>> Logging in..."
bash "$SCRIPT_DIR/login.sh"
echo ""

# Seed in dependency order
echo ">>> Seeding Teachers..."
bash "$SCRIPT_DIR/seed-teachers.sh"
echo ""

echo ">>> Seeding Students..."
bash "$SCRIPT_DIR/seed-students.sh"
echo ""

echo ">>> Seeding Transport (Vehicles, Drivers, Helpers, Routes)..."
bash "$SCRIPT_DIR/seed-transport.sh"
echo ""

echo ">>> Seeding Notifications..."
bash "$SCRIPT_DIR/seed-notifications.sh"
echo ""

echo ">>> Seeding Examinations + Results..."
bash "$SCRIPT_DIR/seed-examinations.sh"
echo ""

echo ">>> Seeding Fees + Payments..."
bash "$SCRIPT_DIR/seed-fees.sh"
echo ""

echo ">>> Seeding Timetable..."
bash "$SCRIPT_DIR/seed-timetable.sh"
echo ""

echo "=== Seeding Complete ==="
