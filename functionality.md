# Admin Portal Functionality

## Authentication
- **Login** — Email/password with Zod validation, demo credentials displayed
- **Session** — httpOnly cookie-based, auto-refresh on 401, redirect to login on expiry
- **Logout** — Clears cookies via backend, removes cached user data

## Dashboard
- KPI cards: Total Students, Total Teachers, Active Classes, Fee Collection %
- Attendance Trends (line chart — monthly)
- Fee Collection Status (pie chart — paid/pending/partial/overdue)
- Student Distribution by Class (bar chart — male/female)
- Quick Actions grid (shortcuts to modules)
- Recent Activities feed

## Students Management
- Student list table with columns: Roll No, Name, Class, Section, Status, Email, Phone
- Filters: Status (Active), Class, Section, Gender
- Search by name or roll number
- Add Student dialog (roll number, name, email, phone, class, section, DOB, admission date, parent info, gender)
- Bulk Import button (UI placeholder)
- Export CSV button
- KPI cards: Total, Active, Alumni, Filtered count

## Student Details
- Left panel: Class filter + name search + scrollable student list
- Profile header: Avatar, name, roll, class, day scholar/hostler badge
- KPI cards: Attendance %, Avg Grade, Assignments, Fee Due
- **Tabs:**
  - Personal Info — DOB, address, parent/guardian, medical (blood group, conditions, allergies), mentor details, transport info
  - Exam Results — Filters (year/month/subject), performance trend line chart, subject-wise bar chart, results table with grades
  - Parent Meetings — Date, attended/absent status, notes
  - Activities — Extra-curricular activities, awards & achievements
  - Fee History — Total/paid/due summary cards, payment list with status

## Teachers Management
- Teacher list table: Employee ID, Name, Subject, Qualification, Email, Phone, Workload
- Search by name
- Add Teacher dialog (employee ID, name, email, phone, subject, qualification, join date, workload)
- Export CSV
- View/Edit/Delete actions

## Teacher Privileges & Assignments
- KPI cards: Total Teachers, Assigned, Class Teachers, Total Assignments
- Per-teacher card with avatar, subject, employee ID
- Assigned classes with progress bars (Attendance, Assignments, Grades, Exams)
- Assign Class dialog (class, section, subject, is_class_teacher checkbox)
- Edit Privileges dialog (toggle switches per permission category)
- Remove assignment with confirmation

## Leave Management
- KPI cards: Total Leaves, Used, Pending, Remaining
- Leave applications table: Employee, Type, Dates, Days, Status
- Filter by status (All/Pending/Approved/Rejected)
- Approve/Reject buttons for pending applications

## Examinations
- KPI cards: Total Exams, Published, Avg Pass Rate
- Exam list table: Name, Type, Class, Subject, Date, Attendance, Pass Rate
- Filters: Exam Type, Class, Subject
- Status chips (Published/Draft)

## Library
- **Tabs:** Book Catalog | Overdue Books
- Book catalog table: Title, Author, ISBN, Category, Available/Total copies
- Issue Book dialog: Select book, select user, number of days input
- Return Book dialog: Shows fine calculation based on overdue days
- Overdue list: Book, User, Due Date, Overdue Days, Fine Amount

## Fee Management
- KPI cards: Total Collected, Pending, Overdue, Fine Collected
- Fee assignments table: Student, Fee Type, Amount, Due Date, Paid, Status
- Filters: Class, Status (All/Pending/Paid/Overdue), Fee Type
- Send Reminder dialog: Group selection (All Students/Specific Class/Section/Overdue Only), message textarea
- Fine calculation display

## Transport
- **Tabs:** Routes | Buses
- Routes table: Name, Stops count, Status
- Buses table: Number, Route, Driver, Phone, Capacity, Status
- Add Route / Add Bus dialogs

## Staff & Payroll
- Staff table: Employee ID, Name, Department, Designation, Type, Status
- Department filter
- Add Staff dialog
- **Payroll tab:** Salary structures and payslip generation

## Layout & Navigation
- Collapsible dark navy sidebar with module icons
- Top header with welcome message, search bar, notification bell (badge), user avatar menu
- User menu dropdown: Profile, Settings, Logout
- Breadcrumb navigation
- Responsive design (MUI breakpoints)
