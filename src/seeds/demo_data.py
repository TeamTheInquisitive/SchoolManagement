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
    """Seed staff, staff_subjects, class_assignments, and link users to staff."""
    from src.models.core import User

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

    # Link User records to Staff records by matching email
    for full_name, email, emp_id, subject, dept in teachers:
        result = await db.execute(
            select(User).where(User.school_id == school_id, User.email == email)
        )
        user = result.scalar_one_or_none()
        if user:
            user.staff_id = staff_ids[emp_id]

    await db.flush()

    # ClassAssignments - assign teachers to class-sections
    # Jane (EMP001) is class teacher of 8A and also teaches Math to 8B, 9A, 9B
    assignments = [
        ("EMP001", "8A", "Mathematics"), ("EMP001", "8B", "Mathematics"),
        ("EMP001", "9A", "Mathematics"), ("EMP001", "9B", "Mathematics"),
        ("EMP002", "8A", "English"), ("EMP002", "8B", "English"),
        ("EMP002", "9A", "English"), ("EMP002", "9B", "English"),
        ("EMP003", "9A", "Science"), ("EMP003", "9B", "Science"),
        ("EMP003", "10A", "Science"), ("EMP003", "10B", "Science"),
        ("EMP004", "10A", "Social Studies"), ("EMP004", "10B", "Social Studies"),
        ("EMP004", "8A", "Social Studies"), ("EMP004", "8B", "Social Studies"),
        ("EMP005", "8A", "Hindi"), ("EMP005", "8B", "Hindi"),
        ("EMP005", "9A", "Hindi"), ("EMP005", "9B", "Hindi"),
        ("EMP006", "10A", "Computer Science"), ("EMP006", "10B", "Computer Science"),
        ("EMP006", "9A", "Computer Science"), ("EMP006", "9B", "Computer Science"),
    ]
    for emp, cs, subj in assignments:
        db.add(ClassAssignment(
            id=uid(), school_id=school_id,
            staff_id=staff_ids[emp], class_section_id=cs_ids[cs],
            subject_id=subject_ids[subj], academic_year_id=ay_id,
            is_class_teacher=(cs == "8A" and emp == "EMP001"),
        ))

    await db.flush()
    print("  ✓ Staff, staff_subjects, class_assignments, user-staff links")
    return staff_ids


async def seed_students(db: AsyncSession, school_id, ay_id, cs_ids, staff_ids):
    """Seed students, parents, enrollments, student_parents, student_mentors."""
    student_ids = []
    parent_ids = []

    male_names = ["Arjun","Rohan","Karthik","Varun","Aditya","Siddharth","Nikhil","Harsh",
                  "Rahul","Vikash","Manish","Sunil","Deepak","Rajesh","Ankit","Mohit",
                  "Gaurav","Sachin","Pavan","Rishi","Aman","Vivek","Akash","Kunal"]
    female_names = ["Sneha","Ananya","Divya","Pooja","Meghna","Kavya","Riya","Priyanka",
                    "Sakshi","Neha","Tanvi","Shreya","Ishita","Nandini","Anjali","Kritika",
                    "Simran","Aishwarya","Tanya","Diya","Palak","Aarti","Swati","Komal"]
    last_names = ["Mehta","Gupta","Patel","Singh","Rao","Sharma","Nair","Reddy",
                  "Kumar","Das","Joshi","Iyer","Verma","Chopra","Agarwal","Mishra",
                  "Saxena","Tiwari","Pandey","Malhotra","Banerjee","Mukherjee","Ghosh","Bose"]

    student_data = []
    stu_counter = 1

    # 8 students per section for 8A, 8B, 9A, 9B, 10A, 10B = 48 students total
    for cs_key in ["8A", "8B", "9A", "9B", "10A", "10B"]:
        for i in range(8):
            idx = (stu_counter - 1) % 24
            if stu_counter % 2 == 1:
                first = male_names[idx % len(male_names)]
                gender = "Male"
            else:
                first = female_names[idx % len(female_names)]
                gender = "Female"
            last = last_names[idx % len(last_names)]
            full_name = f"{first} {last}"
            adm_no = f"STU{stu_counter:03d}"
            student_data.append((full_name, adm_no, cs_key, gender))
            stu_counter += 1

    blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

    for i, (full_name, adm_no, cs_key, gender) in enumerate(student_data):
        sid = uid()
        student_ids.append(sid)
        parts = full_name.split()
        dob = date(2010 + (i % 3), (i % 12) + 1, (i % 28) + 1)
        db.add(Student(
            id=sid, school_id=school_id, admission_number=adm_no,
            first_name=parts[0], last_name=parts[1], full_name=full_name,
            email=f"{parts[0].lower()}.{parts[1].lower()}{i}@student.com",
            phone=f"+91-98700{int(adm_no[-3:]):04d}",
            gender=gender,
            date_of_birth=dob, blood_group=blood_groups[i % len(blood_groups)],
            address_line1=f"{100 + i} Main St", city="Bangalore", state="Karnataka", pincode=f"5600{(i % 90) + 10:02d}",
            admission_date=date(2023, 6, 1), status="Active",
        ))
        db.add(StudentEnrollment(
            id=uid(), school_id=school_id,
            academic_year_id=ay_id, student_id=sid,
            class_section_id=cs_ids[cs_key], roll_number=f"{(i % 8) + 1:03d}",
            enrollment_date=date(2025, 6, 1), status="Active",
        ))

    await db.flush()

    # Parents (father + mother per student)
    occupations = ["Engineer", "Doctor", "Teacher", "Business", "Lawyer", "Architect", "Banker", "Scientist"]
    for i, (full_name, adm_no, _, _) in enumerate(student_data):
        parts = full_name.split()
        # Father
        fpid = uid()
        parent_ids.append(fpid)
        db.add(Parent(
            id=fpid, school_id=school_id,
            first_name=f"Mr. {parts[1]}", last_name=parts[1],
            full_name=f"Mr. {parts[1]}", relation="Father",
            email=f"father.{parts[1].lower()}{i}@email.com",
            phone=f"+91-98800{i:04d}", occupation=occupations[i % len(occupations)],
            is_primary_contact=True,
        ))
        db.add(StudentParent(
            id=uid(), school_id=school_id,
            student_id=student_ids[i], parent_id=fpid,
        ))
        # Mother
        mpid = uid()
        db.add(Parent(
            id=mpid, school_id=school_id,
            first_name=f"Mrs. {parts[1]}", last_name=parts[1],
            full_name=f"Mrs. {parts[1]}", relation="Mother",
            email=f"mother.{parts[1].lower()}{i}@email.com",
            phone=f"+91-98801{i:04d}", occupation=occupations[(i + 3) % len(occupations)],
            is_primary_contact=False,
        ))
        db.add(StudentParent(
            id=uid(), school_id=school_id,
            student_id=student_ids[i], parent_id=mpid,
        ))

    await db.flush()

    # Student Mentors - Jane (EMP001) mentors first 8 students (8A), other teachers mentor their class students
    mentor_assignments = [
        ("EMP001", range(0, 8)),    # 8A students
        ("EMP002", range(8, 16)),   # 8B students
        ("EMP003", range(16, 24)),  # 9A students
        ("EMP004", range(24, 32)),  # 9B students
        ("EMP005", range(32, 40)),  # 10A students
        ("EMP006", range(40, 48)),  # 10B students
    ]
    for emp_id, student_range in mentor_assignments:
        for i in student_range:
            db.add(StudentMentor(
                id=uid(), school_id=school_id,
                academic_year_id=ay_id, student_id=student_ids[i],
                staff_id=staff_ids[emp_id], assigned_date=date(2025, 6, 15),
            ))

    # Link john@student.com user to first student
    from src.models.core import User
    result = await db.execute(
        select(User).where(User.school_id == school_id, User.email == "john@student.com")
    )
    user = result.scalar_one_or_none()
    if user:
        user.student_id = student_ids[0]

    await db.flush()
    print("  ✓ Students (48), parents, enrollments, student_parents, student_mentors")
    return student_ids, parent_ids


async def seed_timetable(db: AsyncSession, school_id, ay_id, cs_ids, subject_ids, staff_ids):
    """Seed period_configs, timetable_slots for full week across all classes."""
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

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    teaching_periods = [p for i, p in enumerate(period_ids) if i not in [2, 5]]  # skip breaks

    # Full timetable: Jane teaches Math in 8A, 8B, 9A, 9B
    # Each class gets Math 5 days a week in different periods
    jane_schedule = [
        ("8A", "Monday", 0), ("8A", "Tuesday", 1), ("8A", "Wednesday", 2),
        ("8A", "Thursday", 3), ("8A", "Friday", 4),
        ("8B", "Monday", 1), ("8B", "Tuesday", 2), ("8B", "Wednesday", 3),
        ("8B", "Thursday", 4), ("8B", "Friday", 0),
        ("9A", "Monday", 2), ("9A", "Tuesday", 3), ("9A", "Wednesday", 4),
        ("9A", "Thursday", 0), ("9A", "Friday", 1),
        ("9B", "Monday", 3), ("9B", "Tuesday", 4), ("9B", "Wednesday", 0),
        ("9B", "Thursday", 1), ("9B", "Friday", 2),
    ]
    for cs, day, period_idx in jane_schedule:
        db.add(TimetableSlot(
            id=uid(), school_id=school_id, academic_year_id=ay_id,
            class_section_id=cs_ids[cs], period_config_id=teaching_periods[period_idx],
            day_of_week=day, subject_id=subject_ids["Mathematics"],
            staff_id=staff_ids["EMP001"], slot_type="Lecture",
        ))

    # Other teachers - at least some slots
    other_schedule = [
        ("EMP002", "English", [("8A", "Monday", 3), ("8A", "Wednesday", 0), ("8B", "Tuesday", 0), ("9A", "Friday", 3)]),
        ("EMP003", "Science", [("9A", "Monday", 4), ("9A", "Wednesday", 1), ("9B", "Tuesday", 0), ("10A", "Thursday", 2)]),
        ("EMP005", "Hindi", [("8A", "Tuesday", 4), ("8A", "Thursday", 1), ("8B", "Wednesday", 4), ("9A", "Monday", 0)]),
        ("EMP006", "Computer Science", [("10A", "Monday", 4), ("10A", "Wednesday", 2), ("9A", "Tuesday", 0), ("9B", "Friday", 4)]),
    ]
    for emp, subj, slots in other_schedule:
        for cs, day, period_idx in slots:
            db.add(TimetableSlot(
                id=uid(), school_id=school_id, academic_year_id=ay_id,
                class_section_id=cs_ids[cs], period_config_id=teaching_periods[period_idx],
                day_of_week=day, subject_id=subject_ids[subj],
                staff_id=staff_ids[emp], slot_type="Lecture",
            ))

    await db.flush()
    print("  ✓ Period configs, full timetable slots")
    return period_ids


async def seed_attendance(db: AsyncSession, school_id, ay_id, cs_ids, staff_ids, student_ids):
    """Seed attendance_sessions, attendance_records for 30 days across multiple classes."""
    import random
    random.seed(42)

    # 8A: students 0-7, 8B: 8-15, 9A: 16-23, 9B: 24-31, 10A: 32-39, 10B: 40-47
    class_student_map = {
        "8A": student_ids[0:8],
        "8B": student_ids[8:16],
        "9A": student_ids[16:24],
        "9B": student_ids[24:32],
    }

    # 30 days of attendance for 8A and 8B (Jane's classes), 20 for 9A/9B
    for cs_key, students in class_student_map.items():
        num_days = 30 if cs_key in ["8A", "8B"] else 20
        for day_offset in range(num_days):
            d = date(2025, 10, 1) + timedelta(days=day_offset)
            if d.weekday() >= 5:
                continue  # skip weekends
            total_present = 0
            total_absent = 0
            session_id = uid()

            records = []
            for i, sid in enumerate(students):
                # ~90% attendance rate, some students more absent
                if random.random() < (0.80 if i in [2, 5] else 0.95):
                    status = "Present"
                    total_present += 1
                else:
                    status = "Absent"
                    total_absent += 1
                records.append((sid, status))

            db.add(AttendanceSession(
                id=session_id, school_id=school_id, academic_year_id=ay_id,
                class_section_id=cs_ids[cs_key], date=d,
                submitted_by=staff_ids["EMP001"],
                submitted_at=datetime(d.year, d.month, d.day, 9, 0),
                status="Submitted", total_present=total_present, total_absent=total_absent,
            ))
            for sid, status in records:
                db.add(AttendanceRecord(
                    id=uid(), school_id=school_id,
                    attendance_session_id=session_id, student_id=sid, status=status,
                ))

    await db.flush()
    print("  ✓ Attendance sessions and records (30 days, 4 classes)")


async def seed_assignments(db: AsyncSession, school_id, ay_id, cs_ids, subject_ids, staff_ids, student_ids):
    """Seed many assignments with submissions for Jane's classes."""
    import random
    random.seed(43)

    assignments_created = []

    # Jane's assignments across her 4 classes
    jane_assignments = [
        ("Algebra Homework Ch.1", "8A", date(2025, 7, 15)),
        ("Algebra Homework Ch.2", "8A", date(2025, 8, 5)),
        ("Geometry Worksheet", "8A", date(2025, 8, 20)),
        ("Algebra Homework Ch.3", "8A", date(2025, 9, 10)),
        ("Mensuration Problems", "8A", date(2025, 9, 25)),
        ("Algebra Homework Ch.4", "8A", date(2025, 10, 10)),
        ("Algebra Homework Ch.5", "8A", date(2025, 10, 25)),
        ("Mid-Term Practice Set", "8A", date(2025, 11, 5)),
        ("Trigonometry Basics", "8A", date(2025, 11, 20)),
        ("Statistics Project", "8A", date(2025, 12, 5)),
        ("Number Systems", "8B", date(2025, 7, 20)),
        ("Linear Equations", "8B", date(2025, 8, 10)),
        ("Quadrilaterals", "8B", date(2025, 9, 5)),
        ("Data Handling", "8B", date(2025, 9, 30)),
        ("Exponents & Powers", "8B", date(2025, 10, 20)),
        ("Polynomials Ch.1", "9A", date(2025, 7, 25)),
        ("Coordinate Geometry", "9A", date(2025, 8, 15)),
        ("Linear Equations in Two Variables", "9A", date(2025, 9, 10)),
        ("Triangles Worksheet", "9A", date(2025, 10, 5)),
        ("Surface Area & Volume", "9A", date(2025, 10, 30)),
        ("Probability Assignment", "9A", date(2025, 11, 15)),
        ("Quadratic Equations", "9B", date(2025, 8, 1)),
        ("Arithmetic Progressions", "9B", date(2025, 9, 1)),
        ("Circles Assignment", "9B", date(2025, 10, 1)),
    ]

    # 8A: students 0-7, 8B: 8-15, 9A: 16-23, 9B: 24-31
    class_student_map = {
        "8A": student_ids[0:8],
        "8B": student_ids[8:16],
        "9A": student_ids[16:24],
        "9B": student_ids[24:32],
    }

    for title, cs, due in jane_assignments:
        aid = uid()
        assignments_created.append((aid, cs))
        is_past = due < date(2025, 11, 15)
        db.add(Assignment(
            id=aid, school_id=school_id, academic_year_id=ay_id,
            class_section_id=cs_ids[cs], subject_id=subject_ids["Mathematics"],
            staff_id=staff_ids["EMP001"], title=title,
            description=f"Complete {title}. Show all working steps.",
            due_date=due, max_marks=Decimal("100"),
            status="Active",
            assigned_date=due - timedelta(days=7),
        ))

    await db.flush()

    # Submissions for all past assignments
    for aid, cs in assignments_created:
        students = class_student_map.get(cs, [])
        for i, sid in enumerate(students):
            submitted = random.random() < 0.90
            if not submitted:
                continue
            graded = random.random() < 0.80
            marks = Decimal(str(random.randint(55, 98))) if graded else None
            is_late = random.random() < 0.1
            db.add(AssignmentSubmission(
                id=uid(), school_id=school_id,
                assignment_id=aid, student_id=sid,
                status="Graded" if graded else "Submitted",
                submitted_at=datetime(2025, 10, 15, 9 + i, 0),
                marks=marks,
                is_late=is_late,
            ))

    # Other teacher assignments
    other_assigns = [
        ("Essay Writing - My School", "English", "EMP002", "8A", date(2025, 11, 22)),
        ("Grammar Exercises Ch.4", "English", "EMP002", "8A", date(2025, 10, 15)),
        ("Science Lab Report - Acids", "Science", "EMP003", "9A", date(2025, 11, 25)),
        ("Photosynthesis Diagram", "Science", "EMP003", "9A", date(2025, 10, 10)),
        ("Hindi Nibandh", "Hindi", "EMP005", "8A", date(2025, 11, 10)),
    ]
    for title, subj, emp, cs, due in other_assigns:
        aid = uid()
        db.add(Assignment(
            id=aid, school_id=school_id, academic_year_id=ay_id,
            class_section_id=cs_ids[cs], subject_id=subject_ids[subj],
            staff_id=staff_ids[emp], title=title,
            description=f"Complete {title} and submit before due date.",
            due_date=due, max_marks=Decimal("100"), status="Active",
            assigned_date=due - timedelta(days=7),
        ))

    await db.flush()
    print("  ✓ Assignments (24 for Jane + 5 others) and submissions")


async def seed_exams(db: AsyncSession, school_id, ay_id, cs_ids, subject_ids, staff_ids, student_ids):
    """Seed exams, exam_results, grade_systems, grade_scales with comprehensive data."""
    import random
    random.seed(44)

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

    def get_grade(marks_val):
        m = int(marks_val)
        if m >= 91: return "A1"
        if m >= 81: return "A2"
        if m >= 71: return "B1"
        if m >= 61: return "B2"
        if m >= 51: return "C1"
        if m >= 41: return "C2"
        if m >= 33: return "D"
        return "E"

    # Jane's exams across all her classes
    exam_data = [
        ("Unit Test 1 - Mathematics", "Unit Test", "8A", "Mathematics", "EMP001", date(2025, 7, 25), "Published"),
        ("Mid-Term Mathematics", "Mid-Term", "8A", "Mathematics", "EMP001", date(2025, 9, 15), "Published"),
        ("Unit Test 2 - Mathematics", "Unit Test", "8A", "Mathematics", "EMP001", date(2025, 10, 20), "Published"),
        ("Pre-Final Mathematics", "Pre-Final", "8A", "Mathematics", "EMP001", date(2025, 11, 25), "Published"),
        ("Unit Test 1 - Mathematics", "Unit Test", "8B", "Mathematics", "EMP001", date(2025, 7, 26), "Published"),
        ("Mid-Term Mathematics", "Mid-Term", "8B", "Mathematics", "EMP001", date(2025, 9, 16), "Published"),
        ("Unit Test 2 - Mathematics", "Unit Test", "8B", "Mathematics", "EMP001", date(2025, 10, 21), "Published"),
        ("Unit Test 1 - Mathematics", "Unit Test", "9A", "Mathematics", "EMP001", date(2025, 7, 28), "Published"),
        ("Mid-Term Mathematics", "Mid-Term", "9A", "Mathematics", "EMP001", date(2025, 9, 18), "Published"),
        ("Unit Test 2 - Mathematics", "Unit Test", "9A", "Mathematics", "EMP001", date(2025, 10, 22), "Published"),
        ("Unit Test 1 - Mathematics", "Unit Test", "9B", "Mathematics", "EMP001", date(2025, 7, 29), "Published"),
        ("Mid-Term Mathematics", "Mid-Term", "9B", "Mathematics", "EMP001", date(2025, 9, 19), "Published"),
        # Upcoming scheduled exams
        ("Final Exam Mathematics", "Final", "8A", "Mathematics", "EMP001", date(2026, 2, 15), "Scheduled"),
        ("Final Exam Mathematics", "Final", "8B", "Mathematics", "EMP001", date(2026, 2, 16), "Scheduled"),
        ("Final Exam Mathematics", "Final", "9A", "Mathematics", "EMP001", date(2026, 2, 18), "Scheduled"),
    ]

    # Other teacher exams
    other_exams = [
        ("Mid-Term English", "Mid-Term", "8A", "English", "EMP002", date(2025, 9, 14), "Published"),
        ("Mid-Term Science", "Mid-Term", "9A", "Science", "EMP003", date(2025, 9, 17), "Published"),
        ("Mid-Term Hindi", "Mid-Term", "8A", "Hindi", "EMP005", date(2025, 9, 13), "Published"),
    ]

    class_student_map = {
        "8A": student_ids[0:8],
        "8B": student_ids[8:16],
        "9A": student_ids[16:24],
        "9B": student_ids[24:32],
    }

    all_exams = exam_data + other_exams
    for name, etype, cs, subj, emp, exam_date, status in all_exams:
        eid = uid()
        db.add(Exam(
            id=eid, school_id=school_id, academic_year_id=ay_id,
            name=name, exam_type=etype, class_section_id=cs_ids[cs],
            subject_id=subject_ids[subj], date=exam_date,
            start_time=time(9, 0), end_time=time(12, 0),
            total_marks=Decimal("100"), passing_marks=Decimal("33"),
            status=status, examiner_id=staff_ids[emp], term="Term 1",
            published_at=datetime(exam_date.year, exam_date.month, exam_date.day, 10, 0) if status == "Published" else None,
        ))
        await db.flush()

        # Results for published exams
        if status == "Published":
            students = class_student_map.get(cs, [])
            sorted_marks = sorted([random.randint(45, 98) for _ in students], reverse=True)
            for rank, (sid, marks_int) in enumerate(zip(students, sorted_marks), 1):
                marks = Decimal(str(marks_int))
                db.add(ExamResult(
                    id=uid(), school_id=school_id, exam_id=eid,
                    student_id=sid, marks_obtained=marks,
                    grade=get_grade(marks), rank=rank,
                    attendance="Present" if random.random() < 0.95 else "Absent",
                    is_pass=marks_int >= 33,
                ))

    await db.flush()
    print("  ✓ Exams (15 for Jane + 3 others), exam results, grade system")


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

    # Fee Records and Payments for first 16 students (8A + 8B)
    import random
    random.seed(45)
    for i, sid in enumerate(student_ids[:16]):
        frid = uid()
        is_paid = random.random() < 0.7
        paid = Decimal("5000") if is_paid else Decimal("0")
        pending = Decimal("0") if is_paid else Decimal("5000")
        db.add(FeeRecord(
            id=frid, school_id=school_id, academic_year_id=ay_id,
            student_id=sid, fee_structure_id=fs_ids[0],
            fee_type="Tuition Fee", fee_category="academic",
            total_amount=Decimal("5000"), paid=paid, pending=pending,
            due_date=date(2025, 11, 10),
            status="Paid" if is_paid else "Pending",
        ))
        if is_paid:
            db.add(FeePayment(
                id=uid(), school_id=school_id, fee_record_id=frid,
                amount=Decimal("5000"), payment_date=date(2025, 11, random.randint(1, 9)),
                payment_method=random.choice(["Online", "Cash", "Cheque"]),
                reference=f"TXN{1000 + i}",
            ))
        else:
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
    """Seed activities, awards, disciplinary_records for multiple students."""
    # Activities - many students in clubs
    activities_data = [
        ("Cricket Club", "Sports", [0, 2, 4, 8, 10, 16, 18]),
        ("Science Club", "Academic", [1, 3, 5, 9, 16, 17, 20]),
        ("Art Club", "Cultural", [6, 7, 11, 12, 19, 22, 23]),
        ("Debate Society", "Academic", [0, 1, 8, 9, 16, 24, 25]),
        ("Basketball Team", "Sports", [3, 5, 10, 14, 18, 26, 30]),
        ("Music Club", "Cultural", [2, 6, 11, 15, 20, 28, 32]),
        ("Coding Club", "Academic", [0, 4, 8, 12, 16, 20, 24]),
        ("Chess Club", "Academic", [1, 7, 9, 13, 17, 21, 25]),
    ]
    for name, atype, indices in activities_data:
        for idx in indices:
            if idx < len(student_ids):
                db.add(Activity(
                    id=uid(), school_id=school_id, academic_year_id=ay_id,
                    student_id=student_ids[idx], activity_type=atype, name=name,
                    role="Member" if idx % 3 != 0 else "Captain",
                    start_date=date(2025, 7, 1), status="Active",
                ))

    # Awards - spread across Jane's students
    awards_data = [
        (0, "Best in Mathematics", "Academic", "Principal", "School"),
        (1, "Art Competition Winner", "Cultural", "Art Department", "Inter-School"),
        (2, "Cricket Tournament MVP", "Sports", "Sports Department", "School"),
        (3, "Science Fair 1st Place", "Academic", "Science Dept", "District"),
        (4, "Debate Champion", "Academic", "Principal", "Inter-School"),
        (8, "Essay Writing Winner", "Academic", "English Dept", "School"),
        (16, "Math Olympiad Gold", "Academic", "Principal", "State"),
        (0, "Perfect Attendance Award", "Discipline", "Class Teacher", "School"),
        (5, "Best Project - Statistics", "Academic", "Math Dept", "School"),
        (6, "Music Recital 1st Place", "Cultural", "Cultural Committee", "Inter-School"),
    ]
    for idx, title, category, awarded_by, level in awards_data:
        if idx < len(student_ids):
            db.add(Award(
                id=uid(), school_id=school_id, academic_year_id=ay_id,
                student_id=student_ids[idx], title=title,
                category=category, awarded_date=date(2025, 9 + idx % 3, 10 + idx % 20),
                awarded_by=awarded_by, level=level,
            ))

    # Disciplinary Records
    discipline_data = [
        (4, "Talking during class", "Misconduct", "Low", "Verbal warning"),
        (5, "Late to class 3 times", "Tardiness", "Low", "Written warning"),
        (10, "Incomplete homework repeatedly", "Academic", "Medium", "Parent meeting scheduled"),
        (14, "Using phone during exam", "Misconduct", "High", "Exam cancelled, re-exam scheduled"),
    ]
    for idx, desc, category, severity, action in discipline_data:
        if idx < len(student_ids):
            db.add(DisciplinaryRecord(
                id=uid(), school_id=school_id, academic_year_id=ay_id,
                student_id=student_ids[idx], incident_date=date(2025, 10, 5 + idx),
                category=category, severity=severity,
                description=desc, action_taken=action,
                reported_by=staff_ids["EMP001"], status="Resolved",
            ))

    await db.flush()
    print("  ✓ Activities (8 clubs), awards (10), disciplinary records")


async def seed_meetings(db: AsyncSession, school_id, ay_id, student_ids, staff_ids, parent_ids):
    """Seed parent_meetings for many students."""
    meeting_data = [
        (0, date(2025, 8, 10), "Academic progress - excellent in Math", "Completed"),
        (1, date(2025, 8, 11), "Discuss improvement in Science", "Completed"),
        (2, date(2025, 8, 12), "Attendance concern - need improvement", "Completed"),
        (3, date(2025, 9, 5), "Behavioral issue discussion", "Completed"),
        (4, date(2025, 9, 6), "Mid-term performance review", "Completed"),
        (5, date(2025, 9, 7), "Discuss low attendance", "Completed"),
        (0, date(2025, 10, 15), "Post mid-term review - top of class", "Completed"),
        (6, date(2025, 10, 16), "Extra-curricular participation", "Completed"),
        (7, date(2025, 10, 17), "Career counseling discussion", "Completed"),
        (2, date(2025, 11, 5), "Follow up on attendance improvement", "Completed"),
        (5, date(2025, 11, 6), "Follow up - attendance still low", "Completed"),
        (8, date(2025, 11, 20), "New student orientation meeting", "Completed"),
        (0, date(2025, 12, 10), "Pre-final exam preparation discussion", "Scheduled"),
        (1, date(2025, 12, 11), "Annual progress review", "Scheduled"),
    ]
    for idx, meeting_date, notes, status in meeting_data:
        if idx < len(student_ids) and idx < len(parent_ids):
            db.add(ParentMeeting(
                id=uid(), school_id=school_id, academic_year_id=ay_id,
                student_id=student_ids[idx], meeting_date=meeting_date,
                meeting_time=time(10, 0), conducted_by=staff_ids["EMP001"],
                parent_id=parent_ids[idx], agenda=notes,
                discussion_notes=notes if status == "Completed" else None,
                status=status, meeting_type="Regular PTM",
            ))

    await db.flush()
    print("  ✓ Parent meetings (14)")


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
