# API Integration Documentation

## Overview

All API calls use **TanStack Query v5** (`@tanstack/react-query`) instead of raw axios/fetch. The service layer is in `src/services/` with one file per module.

- **Base URL:** `http://localhost:8000/api/v1`
- **Auth:** httpOnly cookies (withCredentials: true)
- **Multi-tenancy:** `X-School-Code` header from localStorage
- **Query defaults:** 5min staleTime, 1 retry, no refetch on window focus

---

## Service Files → Pages Mapping

| Service File | Page(s) |
|---|---|
| `dashboardService.js` | DashboardPage |
| `studentService.js` | StudentsPage, StudentDetailsPage |
| `teacherService.js` | TeachersPage, TeacherPrivilegesPage |
| `leaveService.js` | LeaveManagementPage |
| `examinationService.js` | ExaminationsPage |
| `feeService.js` | FeeManagementPage |
| `transportService.js` | TransportPage |
| `staffService.js` | StaffPage |
| `payrollService.js` | PayrollPage |
| `timetableService.js` | TimetablePage |
| `notificationService.js` | NotificationsPage |

---

## Dashboard (`src/services/dashboardService.js`)

**Page:** `src/pages/dashboard/DashboardPage.jsx`

| Hook | Method | Endpoint | Purpose |
|------|--------|----------|---------|
| `useDashboardStats` | GET | `/admin/dashboard/stats/` | KPI summary cards |
| `useAttendanceTrends` | GET | `/admin/dashboard/attendance-trends/` | Monthly attendance chart |
| `useFeeCollectionStatus` | GET | `/admin/dashboard/fee-collection-status/` | Fee pie chart |
| `useStudentDistribution` | GET | `/admin/dashboard/student-distribution/` | Class/gender bar chart |
| `useRecentActivities` | GET | `/admin/dashboard/recent-activities/` | Activity feed |
| `useLeaveOverview` | GET | `/admin/dashboard/leave-overview/` | Leave summary + pending |
| `useLowAttendance` | GET | `/admin/dashboard/low-attendance/` | Low attendance alerts |

---

## Students (`src/services/studentService.js`)

**Pages:** `src/pages/students/StudentsPage.jsx`, `src/pages/students/StudentDetailsPage.jsx`

| Hook | Type | Method | Endpoint | Purpose |
|------|------|--------|----------|---------|
| `useStudents` | Query | GET | `/admin/students/` | List (paginated, filtered) |
| `useStudent` | Query | GET | `/admin/students/:id/` | Student full details |
| `useStudentExamResults` | Query | GET | `/admin/students/:id/exam-results/` | Exam results + trends |
| `useStudentParentMeetings` | Query | GET | `/admin/students/:id/parent-meetings/` | Meeting history |
| `useStudentActivities` | Query | GET | `/admin/students/:id/activities/` | Activities + awards |
| `useStudentFeeHistory` | Query | GET | `/admin/students/:id/fee-history/` | Fee payments |
| `useStudentDisciplinaryRecords` | Query | GET | `/admin/students/:id/disciplinary-records/` | Disciplinary records |
| `useCreateStudent` | Mutation | POST | `/admin/students/` | Create student |
| `useUpdateStudent` | Mutation | PUT | `/admin/students/:id/` | Update student |
| `useDeleteStudent` | Mutation | DELETE | `/admin/students/:id/` | Soft-delete student |
| `useExportStudents` | Query | GET | `/admin/students/export/` | Export CSV (manual trigger) |
| `useBulkImportStudents` | Mutation | POST | `/admin/students/bulk-import/` | Bulk import CSV |

---

## Teachers (`src/services/teacherService.js`)

**Pages:** `src/pages/teachers/TeachersPage.jsx`, `src/pages/teachers/TeacherPrivilegesPage.jsx`

| Hook | Type | Method | Endpoint | Purpose |
|------|------|--------|----------|---------|
| `useTeachers` | Query | GET | `/admin/teachers/` | List teachers |
| `useTeacher` | Query | GET | `/admin/teachers/:id/` | Teacher full profile |
| `useTeacherAssignments` | Query | GET | `/admin/teachers/:id/assignments/` | Class assignments |
| `useTeacherHistory` | Query | GET | `/admin/teachers/:id/history/` | Historical records |
| `useTeachersByClass` | Query | GET | `/admin/teachers/by-class/` | Teachers for a class |
| `useCreateTeacher` | Mutation | POST | `/admin/teachers/` | Create teacher |
| `useUpdateTeacher` | Mutation | PUT | `/admin/teachers/:id/` | Update teacher |
| `useDeleteTeacher` | Mutation | DELETE | `/admin/teachers/:id/` | Soft-delete teacher |
| `useAssignClass` | Mutation | POST | `/admin/teachers/:id/assign-class/` | Assign class-subject |
| `useBulkAssign` | Mutation | POST | `/admin/teachers/:id/bulk-assign/` | Bulk assign classes |
| `useRemoveClassAssignment` | Mutation | DELETE | `/admin/teachers/:id/class-assignment/:aid/` | Remove assignment |

---

## Leaves (`src/services/leaveService.js`)

**Page:** `src/pages/leaves/LeaveManagementPage.jsx`

| Hook | Type | Method | Endpoint | Purpose |
|------|------|--------|----------|---------|
| `useLeaves` | Query | GET | `/admin/leaves/` | List leave applications |
| `useTeacherLeaves` | Query | GET | `/admin/leaves/teacher/:id/` | Teacher balance + history |
| `useLeaveBalances` | Query | GET | `/admin/leaves/balances/` | All balances overview |
| `useLeavePolicy` | Query | GET | `/admin/leaves/policy/` | Leave policy config |
| `useLeaveCalendar` | Query | GET | `/admin/leaves/calendar/` | Calendar view |
| `useUpdateLeavePolicy` | Mutation | PUT | `/admin/leaves/policy/` | Update policy |
| `useApproveLeave` | Mutation | POST | `/admin/leaves/:id/approve/` | Approve leave |
| `useRejectLeave` | Mutation | POST | `/admin/leaves/:id/reject/` | Reject leave |
| `useCancelLeave` | Mutation | POST | `/admin/leaves/:id/cancel/` | Cancel leave |
| `useBulkLeaveAction` | Mutation | POST | `/admin/leaves/bulk-action/` | Bulk approve/reject |

---

## Examinations (`src/services/examinationService.js`)

**Page:** `src/pages/examinations/ExaminationsPage.jsx`

| Hook | Type | Method | Endpoint | Purpose |
|------|------|--------|----------|---------|
| `useExaminations` | Query | GET | `/admin/examinations/` | List exams |
| `useExamination` | Query | GET | `/admin/examinations/:id/` | Exam details |
| `useExamResults` | Query | GET | `/admin/examinations/:id/results/` | Results for exam |
| `useGradeSystem` | Query | GET | `/admin/examinations/grade-system/` | Grade scale config |
| `useExamAnalytics` | Query | GET | `/admin/examinations/analytics/` | Performance analytics |
| `useExamSchedule` | Query | GET | `/admin/examinations/schedule/` | Exam timetable |
| `useReportCard` | Query | GET | `/admin/examinations/report-card/:id/` | Student report card |
| `useCreateExam` | Mutation | POST | `/admin/examinations/` | Create exam |
| `useUpdateExam` | Mutation | PUT | `/admin/examinations/:id/` | Update exam |
| `useDeleteExam` | Mutation | DELETE | `/admin/examinations/:id/` | Cancel exam |
| `useEnterResults` | Mutation | POST | `/admin/examinations/:id/results/` | Enter results |
| `usePublishResults` | Mutation | POST | `/admin/examinations/:id/publish/` | Publish results |
| `useUpdateGradeSystem` | Mutation | PUT | `/admin/examinations/grade-system/` | Update grade scale |

---

## Fees (`src/services/feeService.js`)

**Page:** `src/pages/fees/FeeManagementPage.jsx`

| Hook | Type | Method | Endpoint | Purpose |
|------|------|--------|----------|---------|
| `useFees` | Query | GET | `/admin/fees/` | List fee records |
| `useFee` | Query | GET | `/admin/fees/:id/` | Fee record + payments |
| `useStudentFees` | Query | GET | `/admin/fees/student/:id/` | Student fee summary |
| `useCreateFee` | Mutation | POST | `/admin/fees/` | Create fee record |
| `useGenerateDue` | Mutation | POST | `/admin/fees/generate-due/` | Bulk generate dues |
| `useRecordPayment` | Mutation | POST | `/admin/fees/:id/record-payment/` | Record payment |
| `useApplyLateFee` | Mutation | POST | `/admin/fees/:id/apply-late-fee/` | Apply late fee |
| `useBulkApplyLateFees` | Mutation | POST | `/admin/fees/bulk-apply-late-fees/` | Bulk late fees |
| `useSendReminder` | Mutation | POST | `/admin/fees/send-reminder/` | Send reminders |

---

## Transport (`src/services/transportService.js`)

**Page:** `src/pages/transport/TransportPage.jsx`

| Hook | Type | Method | Endpoint | Purpose |
|------|------|--------|----------|---------|
| `useTransportStats` | Query | GET | `/admin/transport/stats/` | KPI summary |
| `useVehicles` | Query | GET | `/admin/transport/vehicles/` | List vehicles |
| `useDrivers` | Query | GET | `/admin/transport/drivers/` | List drivers |
| `useHelpers` | Query | GET | `/admin/transport/helpers/` | List helpers |
| `useRoutes` | Query | GET | `/admin/transport/routes/` | List routes |
| `useRouteAssignments` | Query | GET | `/admin/transport/assignments/` | List assignments |
| `useCreateVehicle` | Mutation | POST | `/admin/transport/vehicles/` | Add vehicle |
| `useUpdateVehicle` | Mutation | PUT | `/admin/transport/vehicles/:id/` | Update vehicle |
| `useDeleteVehicle` | Mutation | DELETE | `/admin/transport/vehicles/:id/` | Remove vehicle |
| `useCreateDriver` | Mutation | POST | `/admin/transport/drivers/` | Add driver |
| `useUpdateDriver` | Mutation | PUT | `/admin/transport/drivers/:id/` | Update driver |
| `useDeleteDriver` | Mutation | DELETE | `/admin/transport/drivers/:id/` | Remove driver |
| `useCreateHelper` | Mutation | POST | `/admin/transport/helpers/` | Add helper |
| `useUpdateHelper` | Mutation | PUT | `/admin/transport/helpers/:id/` | Update helper |
| `useDeleteHelper` | Mutation | DELETE | `/admin/transport/helpers/:id/` | Remove helper |
| `useCreateRoute` | Mutation | POST | `/admin/transport/routes/` | Create route |
| `useUpdateRoute` | Mutation | PUT | `/admin/transport/routes/:id/` | Update route |
| `useDeleteRoute` | Mutation | DELETE | `/admin/transport/routes/:id/` | Remove route |
| `useCreateAssignment` | Mutation | POST | `/admin/transport/assignments/` | Create assignment |
| `useUpdateAssignment` | Mutation | PUT | `/admin/transport/assignments/:id/` | Update assignment |
| `useDeleteAssignment` | Mutation | DELETE | `/admin/transport/assignments/:id/` | Remove assignment |

---

## Staff (`src/services/staffService.js`)

**Page:** `src/pages/staff/StaffPage.jsx`

| Hook | Type | Method | Endpoint | Purpose |
|------|------|--------|----------|---------|
| `useStaff` | Query | GET | `/admin/staff/` | List staff |
| `useCreateStaff` | Mutation | POST | `/admin/staff/` | Create staff |
| `useUpdateStaff` | Mutation | PUT | `/admin/staff/:id/` | Update staff |
| `useDeleteStaff` | Mutation | DELETE | `/admin/staff/:id/` | Soft-delete staff |

---

## Payroll (`src/services/payrollService.js`)

**Page:** `src/pages/payroll/PayrollPage.jsx`

| Hook | Type | Method | Endpoint | Purpose |
|------|------|--------|----------|---------|
| `usePayroll` | Query | GET | `/admin/payroll/` | Payroll for month/year |
| `useSalaryStructure` | Query | GET | `/admin/payroll/salary-structure/:id/` | Salary breakdown |
| `useSalaryRevisions` | Query | GET | `/admin/payroll/salary-revisions/:id/` | Revision history |
| `useSalaryAdvances` | Query | GET | `/admin/salary-advances/` | Advance requests |
| `useRunPayroll` | Mutation | POST | `/admin/payroll/run/` | Run payroll |
| `useGeneratePayslips` | Mutation | POST | `/admin/payroll/generate-payslips/` | Generate PDFs |
| `useCreateSalaryRevision` | Mutation | POST | `/admin/payroll/salary-revisions/` | Create revision |
| `useCreateSalaryAdvance` | Mutation | POST | `/admin/salary-advances/` | Request advance |
| `useApproveSalaryAdvance` | Mutation | POST | `/admin/salary-advances/:id/approve/` | Approve advance |
| `useRejectSalaryAdvance` | Mutation | POST | `/admin/salary-advances/:id/reject/` | Reject advance |
| `useDisburseSalaryAdvance` | Mutation | POST | `/admin/salary-advances/:id/disburse/` | Disburse advance |

---

## Timetable (`src/services/timetableService.js`)

**Page:** `src/pages/timetable/TimetablePage.jsx`

| Hook | Type | Method | Endpoint | Purpose |
|------|------|--------|----------|---------|
| `usePeriods` | Query | GET | `/admin/timetable/periods/` | Period config |
| `useTimetable` | Query | GET | `/admin/timetable/` | Full timetable grid |
| `useTeacherSchedule` | Query | GET | `/admin/timetable/teacher/:id/` | Teacher schedule |
| `useTimetableConflicts` | Query | GET | `/admin/timetable/conflicts/` | Detect conflicts |
| `useCreatePeriod` | Mutation | POST | `/admin/timetable/periods/` | Add period |
| `useUpdatePeriod` | Mutation | PUT | `/admin/timetable/periods/:id/` | Update period |
| `useDeletePeriod` | Mutation | DELETE | `/admin/timetable/periods/:id/` | Remove period |
| `useAssignSlot` | Mutation | POST | `/admin/timetable/slot/` | Assign slot |
| `useUpdateSlot` | Mutation | PUT | `/admin/timetable/slot/:id/` | Update slot |
| `useDeleteSlot` | Mutation | DELETE | `/admin/timetable/slot/:id/` | Clear slot |
| `useBulkAssignSlots` | Mutation | POST | `/admin/timetable/bulk-assign/` | Bulk assign |

---

## Notifications (`src/services/notificationService.js`)

**Page:** `src/pages/notifications/NotificationsPage.jsx`

| Hook | Type | Method | Endpoint | Purpose |
|------|------|--------|----------|---------|
| `useNotifications` | Query | GET | `/admin/notifications/` | List notifications |
| `useNotification` | Query | GET | `/admin/notifications/:id/` | Notification details |
| `useCreateNotification` | Mutation | POST | `/admin/notifications/` | Create/send |
| `useUpdateNotification` | Mutation | PUT | `/admin/notifications/:id/` | Update |
| `useDeleteNotification` | Mutation | DELETE | `/admin/notifications/:id/` | Archive |

---

## Usage Pattern

```jsx
// Query (auto-fetches on mount, caches, refetches on stale)
const { data, isLoading, error } = useStudents({ page: 1, search: 'john' });
const students = data?.results ?? fallbackData;

// Mutation (manual trigger, invalidates cache on success)
const createMutation = useCreateStudent();
const handleSubmit = (formData) => {
  createMutation.mutate(formData, {
    onSuccess: () => { /* close dialog, show toast */ },
    onError: (err) => { /* show error */ },
  });
};
```

## Totals

- **Service files:** 11
- **Query hooks:** 54
- **Mutation hooks:** 62
- **Total hooks:** 116
- **Pages integrated:** 13
