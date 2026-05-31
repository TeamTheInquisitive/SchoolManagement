from __future__ import annotations

# Import all models so Alembic autogenerate can detect them
from src.models.core import AcademicYear, EnumConfig, School, Settings, User  # noqa: F401
from src.models.academic import Class, ClassSection, ClassSubject, Section, Subject  # noqa: F401
from src.models.staff import ClassAssignment, Staff, StaffSubject  # noqa: F401
from src.models.student import (  # noqa: F401
    Parent,
    Student,
    StudentEnrollment,
    StudentMentor,
    StudentParent,
)
from src.models.timetable import PeriodConfig, TimetableSlot  # noqa: F401
from src.models.attendance import AttendanceRecord, AttendanceSession  # noqa: F401
from src.models.assignment import Assignment, AssignmentSubmission  # noqa: F401
from src.models.examination import Exam, ExamResult, GradeScale, GradeSystem  # noqa: F401
from src.models.leave import LeaveApplication, LeaveBalance, LeavePolicy  # noqa: F401
from src.models.fee import (  # noqa: F401
    FeePenalty,
    FeePayment,
    FeeRecord,
    FeeReminder,
    FeeStructure,
)
from src.models.transport import (  # noqa: F401
    Driver,
    Helper,
    Route,
    RouteAssignment,
    StudentTransport,
    Vehicle,
)
from src.models.notification import Notification, NotificationRecipient  # noqa: F401
from src.models.payroll import (  # noqa: F401
    Payslip,
    SalaryAdvance,
    SalaryRevision,
    SalaryStructure,
)
from src.models.activity import Activity, Award, DisciplinaryRecord  # noqa: F401
from src.models.meeting import ParentMeeting  # noqa: F401
from src.models.adhoc_class import AdhocClass  # noqa: F401
from src.models.library import Book, BookIssue  # noqa: F401
