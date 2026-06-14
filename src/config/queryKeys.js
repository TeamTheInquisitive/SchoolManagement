export const queryKeys = {
  dashboard: {
    all: ['dashboard'],
    stats: ['dashboard', 'stats'],
    attendanceTrends: ['dashboard', 'attendance-trends'],
    feeCollection: ['dashboard', 'fee-collection'],
    studentDistribution: ['dashboard', 'student-distribution'],
    recentActivities: ['dashboard', 'recent-activities'],
    leaveOverview: ['dashboard', 'leave-overview'],
    lowAttendance: ['dashboard', 'low-attendance'],
  },

  students: {
    all: ['students'],
    list: (params) => ['students', params],
    detail: (id) => ['students', id],
    examResults: (id) => ['students', id, 'exam-results'],
    feeHistory: (id) => ['students', id, 'fee-history'],
    attendance: (id) => ['students', id, 'attendance'],
    activities: (id) => ['students', id, 'activities'],
    disciplinary: (id) => ['students', id, 'disciplinary'],
    parentMeetings: (id) => ['students', id, 'parent-meetings'],
  },

  teachers: {
    all: ['teachers'],
    list: (params) => ['teachers', params],
    lookup: ['teachers-list'],
    detail: (id) => ['teachers', id],
    assignments: (id) => ['teachers', id, 'assignments'],
    history: (id) => ['teachers', id, 'history'],
    awards: (id) => ['teachers', id, 'awards'],
    byClass: (params) => ['teachers', 'by-class', params],
  },

  staff: {
    all: ['staff'],
    list: (params) => ['staff', params],
  },

  settings: {
    all: ['settings'],
    school: ['settings', 'school'],
    academicYear: ['settings', 'academic-year'],
    academicYears: ['settings', 'academic-years'],
    classSections: ['settings', 'class-sections'],
    classSectionsLookup: ['class-sections-lookup'],
    subjects: ['settings', 'subjects'],
    classSubjects: ['settings', 'class-subjects'],
    feeStructures: ['settings', 'fee-structures'],
    idGeneration: ['settings', 'id-generation'],
    holidays: ['settings', 'holidays'],
    attendanceConfig: ['settings', 'attendance-config'],
    classSectionAssignments: ['settings', 'class-section-assignments'],
    enums: (category) => ['settings', 'enums', category],
  },

  timetable: {
    all: ['timetable'],
    grid: (params) => ['timetable', params],
    periods: ['timetable', 'periods'],
    teacherAvailability: (periodId, day) => ['timetable', 'teacher-availability', periodId, day],
    slotTypes: ['settings', 'enums', 'slot_types'],
  },

  transport: {
    all: ['transport'],
    stats: ['transport', 'stats'],
    vehicles: (params) => ['transport', 'vehicles', params],
    drivers: (params) => ['transport', 'drivers', params],
    helpers: (params) => ['transport', 'helpers', params],
    routes: (params) => ['transport', 'routes', params],
    assignments: (params) => ['transport', 'assignments', params],
    routeStudents: (routeId) => ['transport', 'route-students', routeId],
  },

  examinations: {
    all: ['examinations'],
    list: (params) => ['examinations', params],
    detail: (id) => ['examinations', id],
    results: (examId) => ['examinations', examId, 'results'],
    gradeSystem: ['examinations', 'grade-system'],
    reportCard: (studentId) => ['examinations', 'report-card', studentId],
  },

  fees: {
    all: ['fees'],
    list: (params) => ['fees', params],
    detail: (id) => ['fees', id],
    student: (studentId) => ['fees', 'student', studentId],
    studentReceipt: (studentId) => ['fees', 'student-receipt', studentId],
    structures: ['fees', 'structures'],
    studentFeeDetail: ['student-fee-detail'],
  },

  leaves: {
    all: ['leaves'],
    list: (params) => ['leaves', params],
    teacher: (teacherId) => ['leaves', 'teacher', teacherId],
    balances: ['leaves', 'balances'],
    policy: ['leaves', 'policy'],
    calendar: (params) => ['leaves', 'calendar', params],
  },

  payroll: {
    all: ['payroll'],
    list: (params) => ['payroll', params],
    salaryStructure: (employeeId) => ['payroll', 'salary-structure', employeeId],
    salaryRevisions: (staffId) => ['payroll', 'salary-revisions', staffId],
    advances: ['payroll', 'advances'],
  },

  notifications: {
    all: ['notifications'],
    list: (params) => ['notifications', params],
    detail: (id) => ['notifications', id],
    templates: ['notifications', 'templates'],
  },

  attendance: {
    overview: ['attendance-overview'],
    classSubjectsStatus: ['class-subjects-status'],
  },

  library: {
    all: ['library'],
  },

  mentoring: {
    all: ['mentoring'],
    list: ['mentoring', 'list'],
    teacherStudents: (staffId) => ['mentoring', 'teacher-students', staffId],
    teachers: ['mentoring', 'teachers'],
    students: (classSectionId) => ['mentoring', 'students', classSectionId],
  },
};
