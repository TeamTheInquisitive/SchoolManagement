/**
 * API Configuration — Single source of truth for all API endpoints.
 *
 * Environment is controlled via .env files:
 *   .env.local       → local dev (localhost:8000)
 *   .env.development → dev/staging server
 *   .env.production  → production server
 *
 * Build commands:
 *   npm run dev                    → uses .env.local
 *   npm run build                  → uses .env.production
 *   npm run build -- --mode development → uses .env.development
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// --- Endpoint Definitions ---
// Grouped by module. Each returns the path relative to API_BASE_URL.

export const ENDPOINTS = {
  // Auth routes - NO trailing slash (backend defines without)
  auth: {
    login: '/auth/login',
    logout: '/auth/logout',
    me: '/auth/me',
    refreshToken: '/auth/refresh-token',
  },

  // Admin routes - WITH trailing slash (backend defines with)
  dashboard: {
    stats: '/admin/dashboard/stats',
    attendanceTrends: '/admin/dashboard/attendance-trends',
    feeCollection: '/admin/dashboard/fee-collection-status',
    studentDistribution: '/admin/dashboard/student-distribution',
    recentActivities: '/admin/dashboard/recent-activities',
    leaveOverview: '/admin/dashboard/leave-overview',
    lowAttendance: '/admin/dashboard/low-attendance',
    analyticsAttendanceByClass: '/admin/dashboard/analytics/attendance-by-class',
    analyticsFeeTrend: '/admin/dashboard/analytics/fee-collection-trend',
    analyticsExamPerformance: '/admin/dashboard/analytics/exam-performance',
    analyticsTeacherWorkload: '/admin/dashboard/analytics/teacher-workload',
    analyticsEnrollmentTrend: '/admin/dashboard/analytics/enrollment-trend',
    analyticsFeeDefaulters: '/admin/dashboard/analytics/fee-defaulters-by-class',
    analyticsAttendanceComparison: '/admin/dashboard/analytics/attendance-monthly-comparison',
    analyticsStudentTypeRatio: '/admin/dashboard/analytics/student-type-ratio',
    analyticsSubjectPerformance: '/admin/dashboard/analytics/subject-performance',
    analyticsClassToppers: '/admin/dashboard/analytics/class-toppers',
    analyticsCorrelation: '/admin/dashboard/analytics/attendance-marks-correlation',
    analyticsRevenueTarget: '/admin/dashboard/analytics/revenue-vs-target',
    analyticsTeacherLeavePatterns: '/admin/dashboard/analytics/teacher-leave-patterns',
    analyticsTransportUtilization: '/admin/dashboard/analytics/transport-utilization',
    analyticsConcessionSummary: '/admin/dashboard/analytics/concession-summary',
    analyticsGrowthRate: '/admin/dashboard/analytics/growth-rate',
    analyticsFeeCollectionRate: '/admin/dashboard/analytics/fee-collection-rate',
  },

  students: {
    list: '/admin/students',
    bulkImport: '/admin/students/bulk-import-json',
    detail: (id) => `/admin/students/${id}`,
    examResults: (id) => `/admin/students/${id}/exam-results`,
    feeHistory: (id) => `/admin/students/${id}/fee-history`,
    attendance: (id) => `/admin/students/${id}/attendance`,
    activities: (id) => `/admin/students/${id}/activities`,
    activityDetail: (studentId, activityId) => `/admin/students/${studentId}/activities/${activityId}`,
    awards: (studentId) => `/admin/students/${studentId}/awards`,
    awardDetail: (studentId, awardId) => `/admin/students/${studentId}/awards/${awardId}`,
    disciplinary: (id) => `/admin/students/${id}/disciplinary-records`,
    disciplinaryDetail: (studentId, recordId) => `/admin/students/${studentId}/disciplinary-records/${recordId}`,
    parentMeetings: (id) => `/admin/students/${id}/parent-meetings`,
    parentMeetingDetail: (studentId, meetingId) => `/admin/students/${studentId}/parent-meetings/${meetingId}`,
    resetPassword: (id) => `/admin/students/${id}/reset-password`,
  },

  teachers: {
    list: '/admin/teachers',
    bulkImport: '/admin/teachers/bulk-import',
    detail: (id) => `/admin/teachers/${id}`,
    assignments: (id) => `/admin/teachers/${id}/assignments`,
    history: (id) => `/admin/teachers/${id}/history`,
    byClass: '/admin/teachers/by-class',
    assignClass: (id) => `/admin/teachers/${id}/assign-class`,
    bulkAssign: (id) => `/admin/teachers/${id}/bulk-assign`,
    removeAssignment: (teacherId, assignmentId) => `/admin/teachers/${teacherId}/class-assignment/${assignmentId}`,
    resetPassword: (id) => `/admin/teachers/${id}/reset-password`,
    awards: (id) => `/admin/teachers/${id}/awards`,
    awardDetail: (id, awardId) => `/admin/teachers/${id}/awards/${awardId}`,
  },

  staff: {
    list: '/admin/staff',
    detail: (id) => `/admin/staff/${id}`,
    bulkImport: '/admin/staff/bulk-import',
  },

  leaves: {
    list: '/admin/leaves',
    teacher: (teacherId) => `/admin/leaves/teacher/${teacherId}`,
    balances: '/admin/leaves/balances',
    policy: '/admin/leaves/policy',
    calendar: '/admin/leaves/calendar',
    approve: (id) => `/admin/leaves/${id}/approve`,
    reject: (id) => `/admin/leaves/${id}/reject`,
    allocate: '/admin/leaves/allocate',
  },

  examinations: {
    list: '/admin/examinations',
    detail: (id) => `/admin/examinations/${id}`,
    results: (examId) => `/admin/examinations/${examId}/results`,
    publish: (id) => `/admin/examinations/${id}/publish`,
    gradeSystem: '/admin/examinations/grade-system',
    reportCard: (studentId) => `/admin/examinations/report-card/${studentId}`,
  },

  fees: {
    list: '/admin/fees',
    detail: (id) => `/admin/fees/${id}`,
    receipt: (id) => `/admin/fees/${id}/receipt`,
    student: (studentId) => `/admin/fees/student/${studentId}`,
    studentReceipt: (studentId) => `/admin/fees/student/${studentId}/receipt`,
    bulkRecordPayment: (studentId) => `/admin/fees/student/${studentId}/bulk-record-payment`,
    structures: '/admin/fees/structures',
    recordPayment: (id) => `/admin/fees/${id}/record-payment`,
    reminders: '/admin/fees/send-reminder',
    export: '/admin/fees/export',
    generateDue: '/admin/fees/generate-due',
  },

  transport: {
    stats: '/admin/transport/stats',
    vehicles: '/admin/transport/vehicles',
    vehicleDetail: (id) => `/admin/transport/vehicles/${id}`,
    drivers: '/admin/transport/drivers',
    driverDetail: (id) => `/admin/transport/drivers/${id}`,
    helpers: '/admin/transport/helpers',
    helperDetail: (id) => `/admin/transport/helpers/${id}`,
    routes: '/admin/transport/routes',
    routeDetail: (id) => `/admin/transport/routes/${id}`,
    assignments: '/admin/transport/assignments',
    assignmentDetail: (id) => `/admin/transport/assignments/${id}`,
    routeStudents: (routeId) => `/admin/transport/routes/${routeId}/students`,
    removeRouteStudent: (routeId, studentId) => `/admin/transport/routes/${routeId}/students/${studentId}`,
    studentTransport: '/admin/transport/student-transport',
  },

  attendance: {
    get: '/admin/attendance',
    submit: '/admin/attendance',
    update: '/admin/attendance',
    classSubjectsStatus: '/admin/attendance/class-subjects-status',
  },

  notifications: {
    list: '/admin/notifications',
    detail: (id) => `/admin/notifications/${id}`,
    templates: '/admin/notifications/templates',
  },

  library: {
    books: '/admin/library/books',
    issued: '/admin/library/issued',
    overdue: '/admin/library/overdue',
    issue: '/admin/library/issue',
    return: '/admin/library/return',
  },

  payroll: {
    list: '/admin/staff/payroll',
    staffPayslips: (staffId) => `/admin/staff/payroll/staff/${staffId}/payslips`,
    history: '/admin/staff/payroll/history',
    salaryStructure: (employeeId) => `/admin/staff/payroll/salary-structure/${employeeId}`,
    salaryRevisions: (staffId) => `/admin/staff/payroll/salary-revisions/${staffId}`,
    generate: '/admin/staff/payroll/run',
    update: (id) => `/admin/staff/payroll/${id}`,
    pay: (id) => `/admin/staff/payroll/${id}/pay`,
    markAllPaid: '/admin/staff/payroll/mark-all-paid',
    undoAllPaid: '/admin/staff/payroll/undo-all-paid',
    deletePayroll: '/admin/staff/payroll/delete',
    advances: '/admin/staff/salary-advances',
    approveAdvance: (id) => `/admin/staff/salary-advances/${id}/approve`,
  },

  timetable: {
    list: '/admin/timetable',
    periods: '/admin/timetable/periods',
    slot: '/admin/timetable/slot',
    slotDetail: (id) => `/admin/timetable/slot/${id}`,
    resetSlots: (classSectionId) => `/admin/timetable/slots/class-section/${classSectionId}`,
  },

  mentoring: {
    list: '/admin/mentoring',
    teacherStudents: (staffId) => `/admin/mentoring/teacher/${staffId}/students`,
    teachers: '/admin/mentoring/teachers',
    students: '/admin/mentoring/students',
    assign: '/admin/mentoring/assign',
    shuffleAssign: '/admin/mentoring/shuffle-assign',
    remove: (id) => `/admin/mentoring/${id}`,
  },

  settings: {
    school: '/admin/settings/school-profile',
    academicYear: '/admin/settings/academic-year',
    academicYears: '/admin/settings/academic-years',
    academicYearDetail: (id) => `/admin/settings/academic-years/${id}`,
    academicYearSetCurrent: (id) => `/admin/settings/academic-years/${id}/set-current`,
    clonePreview: (id) => `/admin/settings/academic-years/${id}/clone-preview`,
    cloneInitialize: (targetId, sourceId) => `/admin/settings/academic-years/${targetId}/initialize-from/${sourceId}`,
    enums: (category) => `/admin/settings/enums/${category}`,
    classSections: '/admin/settings/class-sections',
    createClasses: '/admin/settings/classes/bulk',
    deleteClass: (id) => `/admin/settings/classes/${id}`,
    createSections: '/admin/settings/sections/bulk',
    deleteClassSection: (id) => `/admin/settings/class-sections/${id}`,
    subjects: '/admin/settings/subjects',
    subjectDetail: (id) => `/admin/settings/subjects/${id}`,
    createSubjects: '/admin/settings/subjects/bulk',
    assignSubjectClasses: (id) => `/admin/settings/subjects/${id}/classes`,
    classSubjects: '/admin/settings/class-subjects',
    updateClassSubjects: (classId) => `/admin/settings/class-subjects/${classId}`,
    classSectionAssignments: '/admin/settings/class-section-assignments',
    updateClassSectionAssignment: (csId) => `/admin/settings/class-section-assignments/${csId}`,
    feeStructures: '/admin/settings/fee-structures',
    feeStructureDetail: (id) => `/admin/settings/fee-structures/${id}`,
    uploadLogo: '/admin/settings/upload-logo',
    idGeneration: '/admin/settings/id-generation',
    checkPrefix: (prefix) => `/admin/settings/check-prefix?prefix=${prefix}`,
    nextId: (type) => `/admin/settings/next-id?type=${type}`,
    holidays: '/admin/settings/holidays',
    attendanceConfig: '/admin/settings/attendance-config',
  },
};
