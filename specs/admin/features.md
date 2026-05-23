# School ERP Admin Module - Features

## 1. Authentication & Session
- Login with email/password (Zod validation, demo credentials)
- Role-based access control (admin, super_admin)
- Cookie-based session with auto-refresh
- Logout

## 2. Dashboard
- KPI cards (Total Students, Teachers, Active Classes, Fee Collection %)
- Attendance trends (line chart)
- Fee collection status (pie chart)
- Student distribution by class/gender (bar chart)
- Quick action shortcuts
- Recent activities feed

## 3. Students Management
- Student list table with search, filters (status, class, section, gender)
- Add Student dialog
- Bulk Import (placeholder), Export CSV
- KPI cards (Total, Active, Alumni, Filtered)

## 4. Student Details
- Class-based student browser with profile header
- Tabs: Personal Info, Exam Results (with charts), Parent Meetings, Activities, Fee History

## 5. Teachers Management
- Teacher list table with search
- Add Teacher dialog
- Export CSV
- View/Edit/Delete actions

## 6. Teacher Privileges & Assignments
- KPI cards (Total, Assigned, Class Teachers, Total Assignments)
- Assign class/subject to teacher
- Edit privileges (permission toggles)
- Remove assignment

## 7. Leave Management
- KPI cards (Total, Used, Pending, Remaining)
- Leave applications table with status filter
- Approve/Reject actions

## 8. Timetable
- Class/section timetable grid (6 days x 6 periods)
- Add/Edit period dialog with conflict detection

## 9. Examinations
- KPI cards (Total Exams, Published, Avg Pass Rate)
- Exam list table with filters (type, class, subject)
- Status chips (Published/Draft)

## 10. Library
- Book Catalog tab (title, author, ISBN, category, availability)
- Issue Book / Return Book dialogs (with fine calculation)
- Overdue Books tab

## 11. Fee Management
- KPI cards (Collected, Pending, Overdue, Fine)
- Fee assignments table with filters (class, status, type)
- Send Reminder dialog (target group selection + message)

## 12. Transport
- Routes tab (name, stops, status)
- Buses tab (number, route, driver, capacity, status)
- Add Route / Add Bus dialogs

## 13. Staff Management
- Staff list table with department filter
- Add Staff dialog

## 14. Payroll
- KPI cards (Total Staff, Salary Disbursed, Pending)
- Salary Structure tab (Basic, HRA, DA, Deductions, Net)
- Payslips tab with Generate Payslips button

## 15. Notifications & Announcements
- KPI cards (Total Sent, This Month, Scheduled, Read Rate)
- Notifications table with tabs (All/Sent/Scheduled), search, type filter
- Create Notification dialog (title, type, target audience, message, send via channel, schedule)
- View notification details
- Edit/Delete actions

## 16. Layout & Navigation
- Collapsible sidebar with 13 navigation items
- Top header with search, notification bell, user avatar
- Responsive design (MUI-based)

---

**Tech stack:** React 18 + Vite, MUI 5, Redux Toolkit, React Router 6, Recharts, React Hook Form + Zod, Axios
