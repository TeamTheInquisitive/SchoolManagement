"""
Master seed runner: Sets up the complete database with all demo data.

Usage:
    cd backend
    source venv/bin/activate
    python -m src.seeds.seed_all

This will:
  1. Run DB migrations (alembic upgrade head)
  2. Create default school + users (initial.py)
  3. Seed comprehensive demo data (demo_data.py)
  4. Expand admin-specific data (admin_extra_data.py)

Prerequisites:
  - MySQL running on localhost:3306
  - Database 'school_erp' created
  - .env configured (see .env in project root)
  - Python venv activated with requirements installed
"""
from __future__ import annotations

import asyncio
import subprocess
import sys


def run_migrations():
    print("\n[1/4] Running database migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  Migration error: {result.stderr}")
        sys.exit(1)
    print("  ✓ Migrations applied")


async def run_initial_seed():
    print("\n[2/4] Creating school and users...")
    from src.seeds.initial import seed_initial_data
    await seed_initial_data()


async def run_demo_data():
    print("\n[3/4] Seeding demo data (students, staff, exams, etc.)...")
    from src.seeds.demo_data import main as demo_main
    await demo_main()


async def run_admin_extra():
    print("\n[4/4] Expanding admin module data...")
    from src.seeds.admin_extra_data import main as admin_main
    await admin_main()


async def main():
    print("=" * 60)
    print("  School ERP - Full Database Seed")
    print("=" * 60)

    run_migrations()
    await run_initial_seed()
    await run_demo_data()
    await run_admin_extra()

    print("\n" + "=" * 60)
    print("  ✅ All done! Database fully seeded.")
    print("=" * 60)
    print("\n  Demo Credentials:")
    print("  ─────────────────────────────────────────")
    print("  Admin portal  (http://localhost:5173)")
    print("    Email:    admin@school.com")
    print("    Password: password123")
    print("")
    print("  Teacher portal (http://localhost:5175)")
    print("    Email:    jane@teacher.com")
    print("    Password: password123")
    print("  ─────────────────────────────────────────")
    print("")


if __name__ == "__main__":
    asyncio.run(main())
