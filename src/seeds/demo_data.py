"""
Comprehensive seed script: Populates all tables with test data.

Usage:
    python -m src.seeds.demo_data
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_factory, engine
from src.core.security import hash_password
from src.models import *


def uid():
    return uuid.uuid4()


async def get_school(db: AsyncSession):
    result = await db.execute(select(School).where(School.code == "SCH001"))
    return result.scalar_one()


async def seed_academic(db: AsyncSession, school_id: uuid.UUID):
    """Seed academic year, classes, sections, subjects, class_sections."""
    # Academic Year
    ay_id = uid()
    ay = AcademicYear(
        id=ay_id, school_id=school_id, name="2025-2026",
        start_date=date(2025, 6, 1), end_date=date(2026, 3, 31), is_current=True,
    )
    db.add(ay)

    # Classes
    class_ids = {}
    for i, name in enumerate(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], 1):
        cid = uid()
        class_ids[name] = cid
        db.add(Class(id=cid, school_id=school_id, name=name, display_name=f"Class {name}", sort_order=i))

    # Sections
    section_ids = {}
    for i, name in enumerate(["A", "B", "C"], 1):
        sid = uid()
        section_ids[name] = sid
        db.add(Section(id=sid, school_id=school_id, name=name, sort_order=i))

    # Subjects
    subject_ids = {}
    subjects = ["Mathematics", "English", "Science", "Social Studies", "Hindi", "Computer Science", "Physical Education", "Art"]
    for s in subjects:
        sid = uid()
        subject_ids[s] = sid
        db.add(Subject(id=sid, school_id=school_id, name=s, code=s[:3].upper()))

    # ClassSections (Class 8A, 8B, 9A, 9B, 10A, 10B)
    cs_ids = {}
    for cls in ["8", "9", "10"]:
        for sec in ["A", "B"]:
            csid = uid()
            cs_ids[f"{cls}{sec}"] = csid
            db.add(ClassSection(
                id=csid, school_id=school_id,
                class_id=class_ids[cls], section_id=section_ids[sec],
                academic_year_id=ay_id,
            ))

    await db.flush()
    print("  ✓ Academic year, classes, sections, subjects, class_sections")
    return ay_id, class_ids, section_ids, subject_ids, cs_ids


async def seed_staff(db: AsyncSession, school_id, ay_id, subject_ids, cs_ids):
    """Seed staff, staff_subjects, class_assignments."""
    staff_ids = {}
    teachers = [
        ("Jane Smith", "jane@teacher.com", "EMP001", "Mathematics", "Teaching"),
        ("Robert Brown", "robert@teacher.com", "EMP002", "English", "Teaching"),
        ("Priya Sharma", "priya@teacher.com", "EMP003", "Science", "Teaching"),
        ("Amit Kumar", "amit@teacher.com", "EMP004", "Social Studies", "Teaching"),
        ("Sunita Devi", "sunita@teacher.com", "EMP005", "Hindi", "Teaching"),
        ("Rahul Verma", "rahul@teacher.com", "EMP006", "Computer Science", "Teaching"),
        ("Deepa Nair", "deepa@teacher.com", "EMP007", "Physical Education", "Teaching"),
        ("Vikram Singh", "vikram@teacher.com", "EMP008", "Art", "Teaching"),
        ("Meera Patel", "meera@admin.com", "EMP009", None, "Administration"),
        ("Suresh Reddy", "suresh@admin.com", "EMP010", None, "Administration"),
    ]

    for full_name, email, emp_id, subject, dept in teachers:
        sid = uid()
        parts = full_name.split()
        staff_ids[emp_id] = sid
        db.add(Staff(
            id=sid, school_id=school_id, employee_id=emp_id,
            first_name=parts[0], last_name=parts[1], full_name=full_name,
            email=email, phone=f"+91-98765{emp_id[-3:]}",
            department=dept, designation="Teacher" if subject else "Office Staff",
            employment_type="Full-Time", joining_date=date(2020, 6, 1),
            is_teacher=subject is not None, status="Active",
            salary=Decimal("50000") if subject else Decimal("35000"),
        ))
        # StaffSubject
        if subject and subject in subject_ids:
            db.add(StaffSubject(
                id=uid(), school_id=school_id,
                staff_id=sid, subject_id=subject_ids[subject], is_primary=True,
            ))

    await db.flush()

    # ClassAssignments - assign teachers to class-sections
    assignments = [
        ("EMP001", "8A", "Mathematics"), ("EMP001", "9A", "Mathematics"),
        ("EMP002", "8A", "English"), ("EMP002", "8B", "English"),
        ("EMP003", "9A", "Science"), ("EMP003", "9B", "Science"),
        ("EMP004", "10A", "Social Studies"), ("EMP004", "10B", "Social Studies"),
        ("EMP005", "8A", "Hindi"), ("EMP005", "9A", "Hindi"),
        ("EMP006", "10A", "Computer Science"), ("EMP006", "10B", "Computer Science"),
    ]
    for emp, cs, subj in assignments:
        db.add(ClassAssignment(
            id=uid(), school_id=school_id,
            staff_id=staff_ids[emp], class_section_id=cs_ids[cs],
            subject_id=subject_ids[subj], academic_year_id=ay_id,
            is_class_teacher=(cs == "8A" and emp == "EMP001"),
        ))

    await db.flush()
    print("  ✓ Staff, staff_subjects, class_assignments")
    return staff_ids


async def seed_students(db: AsyncSession, school_id, ay_id, cs_ids, staff_ids):
    """Seed students, parents, enrollments, student_parents, student_mentors."""
    student_ids = []
    parent_ids = []

    student_data = [
        ("Arjun Mehta", "STU001", "8A"), ("Sneha Gupta", "STU002", "8A"),
        ("Rohan Patel", "STU003", "8A"), ("Ananya Singh", "STU004", "8B"),
        ("Karthik Rao", "STU005", "8B"), ("Divya Sharma", "STU006", "9A"),
        ("Varun Nair", "STU007", "9A"), ("Pooja Reddy", "STU008", "9A"),
        ("Aditya Kumar", "STU009", "9B"), ("Meghna Das", "STU010", "9B"),
        ("Siddharth Joshi", "STU011", "10A"), ("Kavya Iyer", "STU012", "10A"),
        ("Nikhil Verma", "STU013", "10A"), ("Riya Chopra", "STU014", "10B"),
        ("Harsh Agarwal", "STU015", "10B"),
    ]

    for full_name, adm_no, cs_key in student_data:
        sid = uid()
        student_ids.append(sid)
        parts = full_name.split()
        db.add(Student(
            id=sid, school_id=school_id, admission_number=adm_no,
            first_name=parts[0], last_name=parts[1], full_name=full_name,
            email=f"{parts[0].lower()}@student.com", phone=f"+91-98700{adm_no[-3:]}",
            gender="Male" if parts[0] in ["Arjun","Rohan","Karthik","Varun","Aditya","Siddharth","Nikhil","Harsh"] else "Female",
            date_of_birth=date(2010, 3, 15), blood_group="B+",
            address_line1="123 Main St", city="Bangalore", state="Karnataka", pincode="560001",
            admission_date=date(2023, 6, 1), status="Active",
        ))
        # Enrollment
        db.add(StudentEnrollment(
            id=uid(), school_id=school_id,
            academic_year_id=ay_id, student_id=sid,
            class_section_id=cs_ids[cs_key], roll_number=adm_no[-3:],
            enrollment_date=date(2025, 6, 1), status="Active",
        ))

    await db.flush()

    # Parents (one per student for simplicity)
    for i, (full_name, adm_no, _) in enumerate(student_data):
        pid = uid()
        parent_ids.append(pid)
        parts = full_name.split()
        db.add(Parent(
            id=pid, school_id=school_id,
            first_name=f"Mr. {parts[1]}", last_name=parts[1],
            full_name=f"Mr. {parts[1]}", relation="Father",
            email=f"parent.{parts[1].lower()}@email.com",
            phone=f"+91-98800{i:03d}", occupation="Engineer",
            is_primary_contact=True,
        ))
        db.add(StudentParent(
            id=uid(), school_id=school_id,
            student_id=student_ids[i], parent_id=pid,
        ))

    await db.flush()

    # Student Mentors (first 5 students get mentors)
    mentor_staff = list(staff_ids.values())[:5]
    for i in range(5):
        db.add(StudentMentor(
            id=uid(), school_id=school_id,
            academic_year_id=ay_id, student_id=student_ids[i],
            staff_id=mentor_staff[i], assigned_date=date(2025, 6, 15),
        ))

    await db.flush()
    print("  ✓ Students, parents, enrollments, student_parents, student_mentors")
    return student_ids, parent_ids


async def seed_timetable(db: AsyncSession, school_id, ay_id, cs_ids, subject_ids, staff_ids):
    """Seed period_configs, timetable_slots."""
    period_ids = []
    periods = [
        ("Period 1", time(8, 0), time(8, 45)),
        ("Period 2", time(8, 45), time(9, 30)),
        ("Break", time(9, 30), time(9, 45)),
        ("Period 3", time(9, 45), time(10, 30)),
        ("Period 4", time(10, 30), time(11, 15)),
        ("Lunch", time(11, 15), time(12, 0)),
        ("Period 5", time(12, 0), time(12, 45)),
        ("Period 6", time(12, 45), time(13, 30)),
    ]
    for name, start, end in periods:
        pid = uid()
        period_ids.append(pid)
        db.add(PeriodConfig(
            id=pid, school_id=school_id, academic_year_id=ay_id,
            name=name, start_time=start, end_time=end,
            duration_minutes=45, is_break="Break" in name or "Lunch" in name,
            sort_order=len(period_ids),
        ))

    await db.flush()

    # Timetable slots for 8A Monday
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    subjects_list = ["Mathematics", "English", "Science", "Hindi", "Computer Science"]
    staff_list = ["EMP001", "EMP002", "EMP003", "EMP005", "EMP006"]
    teaching_periods = [p for i, p in enumerate(period_ids) if i not in [2, 5]]  # skip breaks

    for day in days[:2]:  # Mon, Tue for 8A
        for i, pid in enumerate(teaching_periods[:5]):
            subj = subjects_list[i % len(subjects_list)]
            emp = staff_list[i % len(staff_list)]
            db.add(TimetableSlot(
                id=uid(), school_id=school_id, academic_year_id=ay_id,
                class_section_id=cs_ids["8A"], period_config_id=pid,
                day_of_week=day, subject_id=subject_ids[subj],
                staff_id=staff_ids[emp], slot_type="Lecture",
            ))

    await db.flush()
    print("  ✓ Period configs, timetable slots")
    return period_ids


async def seed_attendance(db: AsyncSession, school_id, ay_id, cs_ids, staff_ids, student_ids):
    """Seed attendance_sessions, attendance_records."""
    # Create 5 days of attendance for 8A
    for day_offset in range(5):
        d = date(2025, 11, 10) + timedelta(days=day_offset)
        session_id = uid()
        db.add(AttendanceSession(
            id=session_id, school_id=school_id, academic_year_id=ay_id,
            class_section_id=cs_ids["8A"], date=d,
            submitted_by=staff_ids["EMP001"],
            submitted_at=datetime(2025, 11, 10 + day_offset, 9, 0),
            status="Submitted", total_present=4, total_absent=1,
        ))
        # Records for first 5 students (8A students)
        for i, sid in enumerate(student_ids[:5]):
            status = "Absent" if i == 4 and day_offset % 3 == 0 else "Present"
            db.add(AttendanceRecord(
                id=uid(), school_id=school_id,
                attendance_session_id=session_id, student_id=sid, status=status,
            ))

    await db.flush()
    print("  ✓ Attendance sessions and records")


async def seed_assignments(db: AsyncSession, school_id, ay_id, cs_ids, subject_ids, staff_ids, student_ids):
    """Seed assignments, assignment_submissions."""
    assignments_created = []
    assign_data = [
        ("Algebra Homework Ch.5", "Mathematics", "EMP001", "8A", date(2025, 11, 20)),
        ("Essay Writing", "English", "EMP002", "8A", date(2025, 11, 22)),
        ("Science Lab Report", "Science", "EMP003", "9A", date(2025, 11, 25)),
    ]
    for title, subj, emp, cs, due in assign_data:
        aid = uid()
        assignments_created.append(aid)
        db.add(Assignment(
            id=aid, school_id=school_id, academic_year_id=ay_id,
            class_section_id=cs_ids[cs], subject_id=subject_ids[subj],
            staff_id=staff_ids[emp], title=title,
            description=f"Complete {title} and submit before due date.",
            due_date=due, max_marks=Decimal("100"), status="Active",
            assigned_date=due - timedelta(days=7),
        ))

    await db.flush()

    # Submissions for first assignment (8A students)
    for i, sid in enumerate(student_ids[:5]):
        db.add(AssignmentSubmission(
            id=uid(), school_id=school_id,
            assignment_id=assignments_created[0], student_id=sid,
            status="Graded" if i < 3 else "Submitted",
            submitted_at=datetime(2025, 11, 18, 10 + i, 0),
            marks=Decimal(str(75 + i * 5)) if i < 3 else None,
            is_late=(i == 4),
        ))

    await db.flush()
    print("  ✓ Assignments and submissions")


async def seed_exams(db: AsyncSession, school_id, ay_id, cs_ids, subject_ids, staff_ids, student_ids):
    """Seed exams, exam_results, grade_systems, grade_scales."""
    # Grade System
    gs_id = uid()
    db.add(GradeSystem(id=gs_id, school_id=school_id, academic_year_id=ay_id, name="CBSE Grading", is_default=True))
    grades = [
        ("A1", 91, 100, 10), ("A2", 81, 90, 9), ("B1", 71, 80, 8),
        ("B2", 61, 70, 7), ("C1", 51, 60, 6), ("C2", 41, 50, 5),
        ("D", 33, 40, 4), ("E", 0, 32, 0),
    ]
    for i, (g, mn, mx, gp) in enumerate(grades):
        db.add(GradeScale(
            id=uid(), school_id=school_id, grade_system_id=gs_id,
            grade=g, min_percentage=Decimal(str(mn)), max_percentage=Decimal(str(mx)),
            grade_point=Decimal(str(gp)), sort_order=i,
        ))

    # Exams
    exam_ids = []
    exam_data = [
        ("Mid-Term Math", "Mid-Term", "8A", "Mathematics", "EMP001"),
        ("Mid-Term English", "Mid-Term", "8A", "English", "EMP002"),
        ("Mid-Term Science", "Mid-Term", "9A", "Science", "EMP003"),
    ]
    for name, etype, cs, subj, emp in exam_data:
        eid = uid()
        exam_ids.append(eid)
        db.add(Exam(
            id=eid, school_id=school_id, academic_year_id=ay_id,
            name=name, exam_type=etype, class_section_id=cs_ids[cs],
            subject_id=subject_ids[subj], date=date(2025, 10, 15),
            start_time=time(9, 0), end_time=time(12, 0),
            total_marks=Decimal("100"), passing_marks=Decimal("33"),
            status="Published", examiner_id=staff_ids[emp], term="Term 1",
            published_at=datetime(2025, 10, 20, 10, 0),
        ))

    await db.flush()

    # Exam Results for first exam (8A students)
    for i, sid in enumerate(student_ids[:5]):
        marks = Decimal(str(65 + i * 7))
        db.add(ExamResult(
            id=uid(), school_id=school_id, exam_id=exam_ids[0],
            student_id=sid, marks_obtained=marks,
            grade="A2" if marks >= 81 else "B1" if marks >= 71 else "B2",
            rank=i + 1, attendance="Present", is_pass=True,
        ))

    await db.flush()
    print("  ✓ Exams, exam results, grade system")


async def seed_leaves(db: AsyncSession, school_id, ay_id, staff_ids):
    """Seed leave_policies, leave_applications, leave_balances."""
    # Policies
    leave_types = [("Casual Leave", "CL", 12), ("Sick Leave", "SL", 10), ("Earned Leave", "EL", 15)]
    for lt, code, total in leave_types:
        db.add(LeavePolicy(
            id=uid(), school_id=school_id, academic_year_id=ay_id,
            leave_type=lt, code=code, total_per_year=total,
            carry_forward=lt == "Earned Leave", requires_approval=True,
            half_day_allowed=True,
        ))

    # Balances for all teachers
    for emp_id, sid in list(staff_ids.items())[:8]:
        for lt, code, total in leave_types:
            db.add(LeaveBalance(
                id=uid(), school_id=school_id, academic_year_id=ay_id,
                staff_id=sid, leave_type=lt, total_allocated=total,
                used=Decimal("2"), pending=Decimal("0"),
            ))

    # Applications
    apps = [
        ("EMP001", "Casual Leave", date(2025, 11, 25), date(2025, 11, 26), "Family function", "Approved"),
        ("EMP002", "Sick Leave", date(2025, 12, 1), date(2025, 12, 2), "Fever", "Approved"),
        ("EMP003", "Casual Leave", date(2025, 12, 10), date(2025, 12, 10), "Personal work", "Pending"),
        ("EMP004", "Earned Leave", date(2025, 12, 20), date(2025, 12, 25), "Vacation", "Pending"),
    ]
    for emp, lt, fd, td, reason, status in apps:
        days = (td - fd).days + 1
        db.add(LeaveApplication(
            id=uid(), school_id=school_id, academic_year_id=ay_id,
            staff_id=staff_ids[emp], leave_type=lt,
            from_date=fd, to_date=td, days=Decimal(str(days)),
            reason=reason, status=status,
            applied_on=datetime(2025, 11, 20, 10, 0),
        ))

    await db.flush()
    print("  ✓ Leave policies, balances, applications")


async def seed_fees(db: AsyncSession, school_id, ay_id, cs_ids, student_ids, admin_user_id):
    """Seed fee_structures, fee_records, fee_payments, fee_reminders, fee_penalties."""
    # Fee Structures
    fs_ids = []
    fee_types = [
        ("Tuition Fee", "academic", Decimal("5000"), "Monthly"),
        ("Lab Fee", "academic", Decimal("2000"), "Quarterly"),
        ("Transport Fee", "transport", Decimal("3000"), "Monthly"),
    ]
    for ft, cat, amt, freq in fee_types:
        fsid = uid()
        fs_ids.append(fsid)
        db.add(FeeStructure(
            id=fsid, school_id=school_id, academic_year_id=ay_id,
            class_section_id=cs_ids["8A"], fee_type=ft,
            fee_category=cat, amount=amt, frequency=freq,
        ))

    await db.flush()

    # Fee Records and Payments for first 5 students
    for i, sid in enumerate(student_ids[:5]):
        frid = uid()
        paid = Decimal("5000") if i < 3 else Decimal("0")
        pending = Decimal("0") if i < 3 else Decimal("5000")
        db.add(FeeRecord(
            id=frid, school_id=school_id, academic_year_id=ay_id,
            student_id=sid, fee_structure_id=fs_ids[0],
            fee_type="Tuition Fee", fee_category="academic",
            total_amount=Decimal("5000"), paid=paid, pending=pending,
            due_date=date(2025, 11, 10),
            status="Paid" if i < 3 else "Pending",
        ))
        if i < 3:
            db.add(FeePayment(
                id=uid(), school_id=school_id, fee_record_id=frid,
                amount=Decimal("5000"), payment_date=date(2025, 11, 5 + i),
                payment_method="Online", reference=f"TXN{1000 + i}",
            ))
        if i >= 3:
            db.add(FeePenalty(
                id=uid(), school_id=school_id, fee_record_id=frid,
                penalty_type="Late Fee", amount=Decimal("100"),
                applied_on=datetime(2025, 11, 15, 10, 0),
                applied_by=admin_user_id,
            ))

    # Fee Reminder
    db.add(FeeReminder(
        id=uid(), school_id=school_id, academic_year_id=ay_id,
        target_group="class", class_name="8", section="A",
        message="Please pay pending fees by Nov 30.",
        send_via="in_app", sent_to_count=5, sent_by=admin_user_id,
        sent_at=datetime(2025, 11, 12, 9, 0),
    ))

    await db.flush()
    print("  ✓ Fee structures, records, payments, penalties, reminders")


async def seed_transport(db: AsyncSession, school_id, ay_id, student_ids):
    """Seed vehicles, drivers, helpers, routes, route_assignments, student_transport."""
    v_ids, d_ids, h_ids, r_ids = [], [], [], []

    for i in range(3):
        vid = uid()
        v_ids.append(vid)
        db.add(Vehicle(
            id=vid, school_id=school_id, vehicle_number=f"KA01AB{1000+i}",
            plate_number=f"KA-01-AB-{1000+i}", type="Bus",
            capacity=40, occupied_seats=15 + i * 5, status="Operational",
        ))

    for i in range(3):
        did = uid()
        d_ids.append(did)
        db.add(Driver(
            id=did, school_id=school_id, driver_id=f"DRV00{i+1}",
            full_name=f"Driver {i+1}", phone=f"+91-99000{i:04d}",
            license_number=f"KA0120250{i:03d}", license_type="Heavy Vehicle",
            status="Available",
        ))

    for i in range(2):
        hid = uid()
        h_ids.append(hid)
        db.add(Helper(
            id=hid, school_id=school_id, helper_id=f"HLP00{i+1}",
            full_name=f"Helper {i+1}", phone=f"+91-99100{i:04d}", status="Available",
        ))

    for i in range(3):
        rid = uid()
        r_ids.append(rid)
        db.add(Route(
            id=rid, school_id=school_id, route_code=f"R{i+1:02d}",
            name=f"Route {i+1} - {'Koramangala' if i==0 else 'Whitefield' if i==1 else 'Indiranagar'}",
            area="South" if i == 0 else "East", shift="Morning",
            distance_km=12.5 + i * 3, status="Active",
        ))

    await db.flush()

    for i in range(3):
        db.add(RouteAssignment(
            id=uid(), school_id=school_id,
            route_id=r_ids[i], vehicle_id=v_ids[i],
            driver_id=d_ids[i], helper_id=h_ids[i] if i < 2 else None,
            status="Active",
        ))

    for i in range(5):
        db.add(StudentTransport(
            id=uid(), school_id=school_id,
            student_id=student_ids[i], route_id=r_ids[i % 3],
            academic_year_id=ay_id, pickup_point=f"Stop {i+1}",
            drop_point=f"Stop {i+1}",
        ))

    await db.flush()
    print("  ✓ Vehicles, drivers, helpers, routes, route_assignments, student_transport")


async def seed_notifications(db: AsyncSession, school_id):
    """Seed notifications, notification_recipients."""
    notifs = [
        ("School Reopens", "School will reopen on June 1st after summer break.", "General"),
        ("Fee Reminder", "Please clear pending fees by Nov 30.", "Fee"),
        ("PTM Scheduled", "Parent-Teacher meeting on Dec 5th.", "Meeting"),
        ("Holiday Notice", "School closed on Nov 14 for Children's Day.", "Holiday"),
    ]
    for title, msg, ntype in notifs:
        nid = uid()
        db.add(Notification(
            id=nid, school_id=school_id, title=title, message=msg,
            type=ntype, target_type="all", send_via="in_app",
            status="Sent", recipients_count=50, read_count=30,
            sent_at=datetime(2025, 11, 1, 9, 0),
        ))

    await db.flush()
    print("  ✓ Notifications")


async def seed_payroll(db: AsyncSession, school_id, ay_id, staff_ids):
    """Seed salary_structures, payslips, salary_advances, salary_revisions."""
    for emp_id, sid in list(staff_ids.items())[:8]:
        basic = Decimal("40000")
        db.add(SalaryStructure(
            id=uid(), school_id=school_id, staff_id=sid, academic_year_id=ay_id,
            basic_salary=basic, hra=Decimal("10000"), da=Decimal("5000"),
            transport_allowance=Decimal("3000"), medical_allowance=Decimal("2000"),
            pf_deduction=Decimal("4800"), professional_tax=Decimal("200"),
            tds=Decimal("2000"), net_salary=Decimal("53000"),
            effective_from=date(2025, 6, 1),
        ))
        # Payslip for Oct
        db.add(Payslip(
            id=uid(), school_id=school_id, staff_id=sid, academic_year_id=ay_id,
            month=10, year=2025, basic_salary=basic,
            total_allowances=Decimal("20000"), total_deductions=Decimal("7000"),
            net_salary=Decimal("53000"), status="Paid",
            paid_on=date(2025, 10, 28), payment_method="Bank Transfer",
            generated_at=datetime(2025, 10, 25, 10, 0),
        ))

    # Salary Advance
    db.add(SalaryAdvance(
        id=uid(), school_id=school_id, staff_id=list(staff_ids.values())[0],
        amount=Decimal("20000"), reason="Medical emergency",
        recovery_months=4, per_month_deduction=Decimal("5000"),
        status="Approved", applied_on=datetime(2025, 10, 1, 10, 0),
    ))

    # Salary Revision
    db.add(SalaryRevision(
        id=uid(), school_id=school_id, staff_id=list(staff_ids.values())[0],
        academic_year_id=ay_id, effective_date=date(2025, 6, 1),
        previous_basic=Decimal("38000"), new_basic=Decimal("40000"),
        revision_type="Annual Increment", percentage=Decimal("5.26"),
        increment_amount=Decimal("2000"),
    ))

    await db.flush()
    print("  ✓ Salary structures, payslips, advances, revisions")


async def seed_activities(db: AsyncSession, school_id, ay_id, student_ids, staff_ids):
    """Seed activities, awards, disciplinary_records."""
    # Activities
    acts = [("Cricket Club", "Sports"), ("Science Club", "Academic"), ("Art Club", "Cultural")]
    for i, (name, atype) in enumerate(acts):
        db.add(Activity(
            id=uid(), school_id=school_id, academic_year_id=ay_id,
            student_id=student_ids[i], activity_type=atype, name=name,
            role="Member", start_date=date(2025, 7, 1), status="Active",
        ))

    # Awards
    db.add(Award(
        id=uid(), school_id=school_id, academic_year_id=ay_id,
        student_id=student_ids[0], title="Best in Mathematics",
        category="Academic", awarded_date=date(2025, 10, 15),
        awarded_by="Principal", level="School",
    ))
    db.add(Award(
        id=uid(), school_id=school_id, academic_year_id=ay_id,
        student_id=student_ids[1], title="Art Competition Winner",
        category="Cultural", awarded_date=date(2025, 9, 20),
        awarded_by="Art Department", level="Inter-School",
    ))

    # Disciplinary Record
    db.add(DisciplinaryRecord(
        id=uid(), school_id=school_id, academic_year_id=ay_id,
        student_id=student_ids[4], incident_date=date(2025, 10, 5),
        category="Misconduct", severity="Low",
        description="Talking during class", action_taken="Verbal warning",
        reported_by=list(staff_ids.values())[0], status="Resolved",
    ))

    await db.flush()
    print("  ✓ Activities, awards, disciplinary records")


async def seed_meetings(db: AsyncSession, school_id, ay_id, student_ids, staff_ids, parent_ids):
    """Seed parent_meetings."""
    for i in range(3):
        db.add(ParentMeeting(
            id=uid(), school_id=school_id, academic_year_id=ay_id,
            student_id=student_ids[i], meeting_date=date(2025, 11, 5 + i),
            meeting_time=time(10, 0), conducted_by=list(staff_ids.values())[0],
            parent_id=parent_ids[i], agenda="Academic progress discussion",
            discussion_notes="Student performing well overall.",
            status="Completed", meeting_type="Regular PTM",
        ))

    await db.flush()
    print("  ✓ Parent meetings")


async def seed_adhoc_classes(db: AsyncSession, school_id, ay_id, cs_ids, subject_ids, staff_ids):
    """Seed adhoc_classes."""
    db.add(AdhocClass(
        id=uid(), school_id=school_id, academic_year_id=ay_id,
        staff_id=staff_ids["EMP002"], class_section_id=cs_ids["8A"],
        subject_id=subject_ids["English"], date=date(2025, 11, 12),
        start_time=time(9, 45), end_time=time(10, 30),
        duration_minutes=45, type="Substitute",
        reason="Regular teacher on leave",
        original_staff_id=staff_ids["EMP001"],
        student_count=30, status="Completed",
    ))

    await db.flush()
    print("  ✓ Adhoc classes")


async def seed_settings(db: AsyncSession, school_id):
    """Seed settings, enum_configs."""
    db.add(Settings(
        id=uid(), school_id=school_id, category="general",
        key="academic_year_format", value={"format": "YYYY-YYYY"},
    ))
    db.add(Settings(
        id=uid(), school_id=school_id, category="attendance",
        key="minimum_percentage", value={"value": 75},
    ))

    enums = [
        ("fee_type", "Tuition Fee", "Tuition Fee"),
        ("fee_type", "Lab Fee", "Lab Fee"),
        ("fee_type", "Transport Fee", "Transport Fee"),
        ("leave_type", "Casual Leave", "Casual Leave"),
        ("leave_type", "Sick Leave", "Sick Leave"),
        ("leave_type", "Earned Leave", "Earned Leave"),
    ]
    for i, (cat, val, label) in enumerate(enums):
        db.add(EnumConfig(
            id=uid(), school_id=school_id, category=cat,
            value=val, label=label, sort_order=i,
        ))

    await db.flush()
    print("  ✓ Settings, enum configs")


async def main():
    async with async_session_factory() as db:
        school = await get_school(db)
        sid = school.id

        # Get admin user ID for FK references
        from src.models.core import User
        result = await db.execute(select(User).where(User.school_id == sid))
        users = result.scalars().all()
        admin_user_id = users[0].id if users else uid()

        print(f"\nSeeding demo data for: {school.name} ({school.code})\n")

        ay_id, class_ids, section_ids, subject_ids, cs_ids = await seed_academic(db, sid)
        staff_ids = await seed_staff(db, sid, ay_id, subject_ids, cs_ids)
        student_ids, parent_ids = await seed_students(db, sid, ay_id, cs_ids, staff_ids)
        await seed_timetable(db, sid, ay_id, cs_ids, subject_ids, staff_ids)
        await seed_attendance(db, sid, ay_id, cs_ids, staff_ids, student_ids)
        await seed_assignments(db, sid, ay_id, cs_ids, subject_ids, staff_ids, student_ids)
        await seed_exams(db, sid, ay_id, cs_ids, subject_ids, staff_ids, student_ids)
        await seed_leaves(db, sid, ay_id, staff_ids)
        await seed_fees(db, sid, ay_id, cs_ids, student_ids, admin_user_id)
        await seed_transport(db, sid, ay_id, student_ids)
        await seed_notifications(db, sid)
        await seed_payroll(db, sid, ay_id, staff_ids)
        await seed_activities(db, sid, ay_id, student_ids, staff_ids)
        await seed_meetings(db, sid, ay_id, student_ids, staff_ids, parent_ids)
        await seed_adhoc_classes(db, sid, ay_id, cs_ids, subject_ids, staff_ids)
        await seed_settings(db, sid)

        await db.commit()
        print("\n✅ All demo data seeded successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
