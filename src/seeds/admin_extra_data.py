"""
Supplemental seed: Expands data for the admin module.
Adds more fee records, transport, leaves, notifications, payslips.

Usage:
    python -m src.seeds.admin_extra_data
"""
from __future__ import annotations

import asyncio
import random
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory, engine
from src.models import *

random.seed(100)


def uid():
    return uuid.uuid4()


async def main():
    async with async_session_factory() as db:
        r = await db.execute(text("SELECT id FROM schools WHERE code='SCH001'"))
        school_id = r.scalar()

        r = await db.execute(text(f"SELECT id FROM academic_years WHERE school_id='{school_id}' AND is_current=1"))
        ay_id = r.scalar()

        r = await db.execute(text(f"SELECT id FROM students WHERE school_id='{school_id}' ORDER BY admission_number"))
        student_ids = [row[0] for row in r.fetchall()]

        r = await db.execute(text(f"SELECT id, employee_id FROM staff WHERE school_id='{school_id}'"))
        staff_rows = r.fetchall()
        staff_ids = {row[1]: row[0] for row in staff_rows}
        staff_list = list(staff_ids.values())[:8]

        r = await db.execute(text(f"SELECT id, fee_type FROM fee_structures WHERE school_id='{school_id}'"))
        fee_structs = r.fetchall()

        r = await db.execute(text(f"SELECT id FROM users WHERE school_id='{school_id}' AND role='admin'"))
        admin_id = r.scalar()

        print(f"\nExpanding admin data for school {school_id}\n")

        # ===== FEE RECORDS (48 students × 5 months) =====
        await db.execute(text(f"DELETE FROM fee_payments WHERE school_id='{school_id}'"))
        await db.execute(text(f"DELETE FROM fee_penalties WHERE school_id='{school_id}'"))
        await db.execute(text(f"DELETE FROM fee_records WHERE school_id='{school_id}'"))
        await db.flush()

        months = [(2025, 7), (2025, 8), (2025, 9), (2025, 10), (2025, 11)]
        fee_count = 0
        for sid in student_ids:
            for year, month in months:
                frid = uid()
                is_paid = random.random() < 0.75
                paid_amt = Decimal("5000") if is_paid else Decimal("0")
                pending_amt = Decimal("0") if is_paid else Decimal("5000")
                db.add(FeeRecord(
                    id=frid, school_id=school_id, academic_year_id=ay_id,
                    student_id=sid, fee_structure_id=fee_structs[0][0],
                    fee_type="Tuition Fee", fee_category="academic",
                    total_amount=Decimal("5000"), paid=paid_amt, pending=pending_amt,
                    due_date=date(year, month, 10),
                    status="Paid" if is_paid else "Pending",
                ))
                if is_paid:
                    db.add(FeePayment(
                        id=uid(), school_id=school_id, fee_record_id=frid,
                        amount=Decimal("5000"),
                        payment_date=date(year, month, random.randint(1, 9)),
                        payment_method=random.choice(["Online", "Cash", "Cheque", "UPI"]),
                        reference=f"TXN{random.randint(10000, 99999)}",
                    ))
                else:
                    if random.random() < 0.5:
                        db.add(FeePenalty(
                            id=uid(), school_id=school_id, fee_record_id=frid,
                            penalty_type="Late Fee", amount=Decimal("100"),
                            applied_on=datetime(year, month, 15, 10, 0),
                            applied_by=admin_id,
                        ))
                fee_count += 1
        print(f"  ✓ Fee records: {fee_count}")

        # ===== LEAVE APPLICATIONS (8 staff × 3 each) =====
        await db.execute(text(f"DELETE FROM leave_applications WHERE school_id='{school_id}'"))
        await db.flush()

        leave_types = ["Casual Leave", "Sick Leave", "Earned Leave"]
        statuses = ["Approved", "Approved", "Approved", "Pending", "Rejected"]
        reasons = ["Family function", "Medical appointment", "Personal work", "Fever",
                   "Wedding", "Out of station", "Child unwell", "Festival"]
        for i, sid in enumerate(staff_list):
            for j in range(3):
                lt = leave_types[(i + j) % 3]
                fd = date(2025, 7 + j * 2, random.randint(1, 20))
                days = random.randint(1, 3)
                td = fd + timedelta(days=days - 1)
                status = statuses[(i + j) % len(statuses)]
                db.add(LeaveApplication(
                    id=uid(), school_id=school_id, academic_year_id=ay_id,
                    staff_id=sid, leave_type=lt,
                    from_date=fd, to_date=td, days=Decimal(str(days)),
                    reason=reasons[(i + j) % len(reasons)], status=status,
                    applied_on=datetime(fd.year, fd.month, max(1, fd.day - 3), 10, 0),
                ))
        print("  ✓ Leave applications: 24")

        # ===== NOTIFICATIONS =====
        await db.execute(text(f"DELETE FROM notifications WHERE school_id='{school_id}'"))
        await db.flush()

        notifs = [
            ("School Reopens After Summer", "School will reopen on June 1st after summer break.", "General"),
            ("Fee Reminder - July", "Please clear pending fees for July by July 15.", "Fee"),
            ("PTM Scheduled - Class 8", "Parent-Teacher meeting for Class 8 on Aug 10th.", "Meeting"),
            ("Independence Day Celebration", "Flag hoisting at 8 AM. Cultural program 9-11 AM.", "Event"),
            ("Mid-Term Exam Schedule", "Mid-term exams start from Sep 15.", "Exam"),
            ("Fee Reminder - September", "Please clear pending September fees by Sep 15.", "Fee"),
            ("Annual Sports Day", "Annual sports day on Oct 25.", "Event"),
            ("Holiday Notice - Diwali", "School closed Oct 30 - Nov 3 for Diwali.", "Holiday"),
            ("Fee Reminder - November", "Pending fee reminder. Last date Nov 30.", "Fee"),
            ("Science Exhibition", "Inter-class science exhibition on Nov 20.", "Event"),
            ("Winter Uniform Notice", "Winter uniform mandatory from Nov 15.", "General"),
            ("Pre-Final Exam Schedule", "Pre-final exams start Dec 10.", "Exam"),
            ("Christmas Celebration", "Christmas party on Dec 23.", "Event"),
            ("Republic Day Event", "Republic Day celebration Jan 26.", "Event"),
            ("Final Exam Prep Workshop", "Revision workshops for Class 10 starting Feb 1.", "Exam"),
            ("Annual Day Rehearsals", "Annual day rehearsals begin Feb 10.", "Event"),
        ]
        for i, (title, msg, ntype) in enumerate(notifs):
            month = min(12, 6 + i // 2)
            db.add(Notification(
                id=uid(), school_id=school_id, title=title, message=msg,
                type=ntype, target_type="all", send_via="in_app",
                status="Sent", recipients_count=random.randint(40, 100),
                read_count=random.randint(20, 60),
                sent_at=datetime(2025, month, random.randint(1, 25), 9, 0),
            ))
        print(f"  ✓ Notifications: {len(notifs)}")

        # ===== PAYSLIPS (8 staff × 6 months) =====
        await db.execute(text(f"DELETE FROM payslips WHERE school_id='{school_id}'"))
        await db.flush()

        for sid in staff_list:
            for month in range(6, 12):
                db.add(Payslip(
                    id=uid(), school_id=school_id, staff_id=sid, academic_year_id=ay_id,
                    month=month, year=2025, basic_salary=Decimal("40000"),
                    total_allowances=Decimal("20000"), total_deductions=Decimal("7000"),
                    net_salary=Decimal("53000"),
                    status="Paid" if month < 11 else "Generated",
                    paid_on=date(2025, month, 28) if month < 11 else None,
                    payment_method="Bank Transfer",
                    generated_at=datetime(2025, month, 25, 10, 0),
                ))
        print("  ✓ Payslips: 48")

        # ===== TRANSPORT (6 vehicles, 6 drivers, 4 helpers, 6 routes) =====
        await db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        await db.execute(text(f"DELETE FROM student_transport WHERE school_id='{school_id}'"))
        await db.execute(text(f"DELETE FROM route_assignments WHERE school_id='{school_id}'"))
        await db.execute(text(f"DELETE FROM vehicles WHERE school_id='{school_id}'"))
        await db.execute(text(f"DELETE FROM drivers WHERE school_id='{school_id}'"))
        await db.execute(text(f"DELETE FROM helpers WHERE school_id='{school_id}'"))
        await db.execute(text(f"DELETE FROM routes WHERE school_id='{school_id}'"))
        await db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        await db.flush()

        v_ids, d_ids, h_ids, r_ids = [], [], [], []
        vehicle_data = [
            ("KA01AB1001", "Bus", 50, 25), ("KA01AB1002", "Bus", 50, 30),
            ("KA01AB1003", "Bus", 40, 20), ("KA01AB1004", "Mini Bus", 30, 15),
            ("KA01AB1005", "Mini Bus", 30, 18), ("KA01AB1006", "Van", 15, 10),
        ]
        for vnum, vtype, cap, occ in vehicle_data:
            vid = uid()
            v_ids.append(vid)
            db.add(Vehicle(
                id=vid, school_id=school_id, vehicle_number=vnum,
                plate_number=vnum.replace("AB", "-AB-"), type=vtype,
                capacity=cap, occupied_seats=occ, status="Operational",
            ))

        driver_names = ["Raju Kumar", "Suresh Yadav", "Mohan Lal", "Prakash Shetty", "Ganesh Patil", "Ramesh Gowda"]
        for i, name in enumerate(driver_names):
            did = uid()
            d_ids.append(did)
            db.add(Driver(
                id=did, school_id=school_id, driver_id=f"DRV{i+1:03d}",
                full_name=name, phone=f"+91-99000{i:04d}",
                license_number=f"KA012025{i:04d}", license_type="Heavy Vehicle",
                status="Available",
            ))

        helper_names = ["Lakshmi", "Savitri", "Kamala", "Geetha"]
        for i, name in enumerate(helper_names):
            hid = uid()
            h_ids.append(hid)
            db.add(Helper(
                id=hid, school_id=school_id, helper_id=f"HLP{i+1:03d}",
                full_name=name, phone=f"+91-99100{i:04d}", status="Available",
            ))

        route_data = [
            ("R01", "Koramangala - School", "South", 12.5),
            ("R02", "Whitefield - School", "East", 18.0),
            ("R03", "Indiranagar - School", "Central", 8.5),
            ("R04", "HSR Layout - School", "South", 10.0),
            ("R05", "Electronic City - School", "South-East", 22.0),
            ("R06", "JP Nagar - School", "South-West", 14.0),
        ]
        for code, name, area, dist in route_data:
            rid = uid()
            r_ids.append(rid)
            db.add(Route(
                id=rid, school_id=school_id, route_code=code,
                name=name, area=area, shift="Morning",
                distance_km=dist, status="Active",
            ))

        await db.flush()
        for i in range(6):
            db.add(RouteAssignment(
                id=uid(), school_id=school_id,
                route_id=r_ids[i], vehicle_id=v_ids[i],
                driver_id=d_ids[i], helper_id=h_ids[i] if i < len(h_ids) else None,
                status="Active",
            ))

        pickup_points = ["Koramangala Signal", "MG Road Metro", "Whitefield Main",
                         "Indiranagar 100ft", "HSR Layout", "BTM 2nd Stage",
                         "JP Nagar 6th Phase", "Marathahalli Bridge",
                         "Sarjapur Road", "Electronic City"]
        for i in range(24):
            pp = pickup_points[i % len(pickup_points)]
            db.add(StudentTransport(
                id=uid(), school_id=school_id,
                student_id=student_ids[i], route_id=r_ids[i % len(r_ids)],
                academic_year_id=ay_id, pickup_point=pp, drop_point=pp,
            ))
        print("  ✓ Transport: 6 vehicles, 6 drivers, 4 helpers, 6 routes, 24 students")

        # ===== SALARY ADVANCES =====
        await db.execute(text(f"DELETE FROM salary_advances WHERE school_id='{school_id}'"))
        await db.flush()
        advance_data = [
            (0, Decimal("20000"), "Medical emergency", 4),
            (1, Decimal("15000"), "Home repair", 3),
            (3, Decimal("30000"), "Wedding expenses", 6),
            (5, Decimal("10000"), "Education fee", 2),
        ]
        for idx, amount, reason, months in advance_data:
            db.add(SalaryAdvance(
                id=uid(), school_id=school_id, staff_id=staff_list[idx],
                amount=amount, reason=reason,
                recovery_months=months, per_month_deduction=amount / months,
                status="Approved", applied_on=datetime(2025, 10, 1, 10, 0),
            ))
        print("  ✓ Salary advances: 4")

        await db.commit()
        print("\n✅ Admin extra data seeded successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
