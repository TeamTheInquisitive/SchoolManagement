# School ERP - Teacher Portal: Features Documentation

## Project Overview

A React-based Teacher Portal for a School ERP system. Built with Vite, Material UI, Redux Toolkit, React Router, React Hook Form + Zod validation, Recharts for visualizations, and Axios for API communication. The backend API is expected at `http://localhost:8000/api/v1`.

---

## 1. Authentication & Session Management

**Page:** `/login`

| Feature | Description |
|---------|-------------|
| Email/Password Login | Form-based login with email and password fields |
| Zod Validation | Client-side schema validation (valid email format, non-empty password) |
| Error Display | API error messages shown via MUI Alert component |
| Loading State | Submit button shows "Signing in..." and disables during API call |
| Session Persistence | User object stored in localStorage; rehydrated on app load |
| Token Refresh | Axios interceptor automatically retries on 401 using `/auth/refresh-token/` |
| Multi-tenant Support | `X-School-Code` header attached to all API requests from localStorage |
| Protected Routes | Unauthenticated users redirected to `/login` via `ProtectedRoute` wrapper |
| Logout | Clears local state, calls `/auth/logout/`, redirects to login |
| Demo Credentials | Displayed on login page: `jane@teacher.com / password123` |

---

## 2. Layout & Navigation

**Component:** `TeacherLayout`

| Feature | Description |
|---------|-------------|
| Permanent Sidebar | Dark-themed (navy #0f172a) drawer, 240px wide, always visible |
| User Profile | Avatar with initials, full name, and email displayed in sidebar |
| Navigation Menu | 10 menu items with icons and active-state highlighting (indigo #6366f1) |
| Top AppBar | Sticky white bar with welcome message, notification badge (hardcoded 3), and user avatar |
| Logout Button | Bottom of sidebar, dispatches logout and navigates to login |

**Navigation Items:**
1. Dashboard
2. My Classes
3. Student Details
4. Attendance
5. Assignments
6. Grades
7. Quiz Management
8. Notifications
9. Timetable
10. Leave Management

---

## 3. Dashboard

**Page:** `/dashboard`

| Feature | Description |
|---------|-------------|
| KPI Cards | 4 stat cards: Total Students (145), Pending Reviews (8), Upcoming Exams (3), Classes Today (4) |
| Today's Schedule | List of 4 class periods with time, class section, and subject |
| Pending Reviews | List of assignments showing title, class, and submission count (e.g., 38/45) |
| Upcoming Exams | List of 3 exams with name, class, date, and exam type chip |

---

## 4. My Classes

**Page:** `/classes`

| Feature | Description |
|---------|-------------|
| Class Cards | 3 selectable cards (10-A, 10-B, 11-A) showing subject and student count |
| Class Filter | Clicking a class card filters the student table to that class |
| Student Table (Tab 1) | Columns: Roll No, Name, Class, Attendance %, Grade |
| Search | Text field to filter students by name |
| Mentees Tab (Tab 2) | Shows assigned mentee cards with name, class, attendance, last meeting date, and status (Good/Needs Attention) |

---

## 5. Student Details

**Page:** `/student-details`

| Feature | Description |
|---------|-------------|
| Split-panel Layout | Left panel (320px) for student list, right panel for detailed view |
| Student Search/Filter | Filter by class dropdown + search by name |
| Student List | Clickable cards with avatar, name, roll number, and class |
| Action Buttons | Print Profile and Export PDF buttons |
| Profile Card | Avatar, name, roll, email, class, phone, type (Day Scholar) |
| Quick Stats | Attendance %, Avg Grade, Assignments count, Fee Due |
| Personal Information | Date of birth, admission date, address |
| Parent/Guardian Info | Parent name, phone, email, emergency contact, relationship |
| Medical Info | Blood group, gender, religion, medical conditions |
| Assigned Mentor | Mentor card with name, subject, qualification, email, phone |
| Examination Results | Expandable accordion per exam with subject-wise marks, percentage, and grade |
| Performance Analysis | 3 Recharts visualizations: Bar chart (subject marks), Radar chart (subject strengths), Line chart (performance trend across exams) |
| Parent Meeting History | Meeting list with type, date, conductor, attendee, notes, and attendance status |
| Assignments & Submissions | Section for assignment tracking (currently shows "No assignments found") |
| Extra-Curricular Activities | Activity list with name, year joined, role, and active status |
| Awards & Achievements | Award cards with name, category, year, and description |
| Disciplinary Records | Clean record indicator or issue listing |
| Fee Structure | Table of fee components with amount and frequency, plus total |
| Fee Payment History | Summary (Total/Paid/Due) + payment records with date, amount, method, status, and reference |
| Academic Performance Summary | Overall Attendance, Grade, Assignments Submitted, Class Rank |
| Behavior & Conduct | Overall Rating, Discipline %, Punctuality % |

---

## 6. Attendance

**Page:** `/attendance`

| Feature | Description |
|---------|-------------|
| Class Selector | Dropdown to pick class (10-A, 10-B, 11-A) |
| Date Picker | Native HTML date input, defaults to today |
| Attendance Table | Columns: Roll No, Name, Present (checkbox), Status (chip) |
| Toggle Presence | Checkbox to mark each student present/absent |
| Live Counter | Chip showing present count vs total (e.g., "4/5 Present") |
| Save Button | "Save Attendance" button to persist data |

---

## 7. Assignments

**Page:** `/assignments`

| Feature | Description |
|---------|-------------|
| Assignment Table | Columns: Title, Class, Due Date, Submissions (X/Y), Status, Actions |
| Status Indicators | "Active" (blue) or "Completed" (green) chips |
| Action Buttons | View, Edit, Delete icons per row |
| Create Dialog | Modal form with fields: Title, Description, Class, Due Date, Max Marks |
| Create Button | Top-right "Create Assignment" button opens the dialog |

---

## 8. Grades Management

**Page:** `/grades`

| Feature | Description |
|---------|-------------|
| Class Filter | Dropdown to select class |
| Exam Filter | Dropdown to select exam type (Unit Test, Mid-term, Final) |
| Editable Marks Table | Columns: Roll No, Name, Marks (editable number input), Grade |
| Inline Editing | Marks field is a number input, directly editable in the table |
| Save Button | "Save Grades" button to persist changes |

---

## 9. Quiz Management

**Page:** `/quizzes`

| Feature | Description |
|---------|-------------|
| Quiz Table | Columns: Title, Class, Questions count, Duration, Attempts, Status, Actions |
| Status Indicators | "Published" (green) or "Draft" (default) chips |
| Action Buttons | Play (publish/start), Edit, Delete icons per row |
| Create Dialog | Modal form with fields: Quiz Title, Class, Duration (min), Total Questions, Passing Marks |
| Create Button | Top-right "Create Quiz" button opens the dialog |

---

## 10. Notifications

**Page:** `/notifications`

| Feature | Description |
|---------|-------------|
| Sent Notifications List | Each notification shows message, target audience, date, and type chip (Students/Parents) |
| Send Dialog | Modal with recipient dropdown (class-specific students or parents, all students, all parents) and message textarea |
| Recipient Options | Class 10-A/10-B/11-A Students, Class 10-A/10-B Parents, All My Students, All Parents |
| Send Button | Top-right "Send Notification" button opens the dialog |

---

## 11. Timetable

**Page:** `/timetable`

| Feature | Description |
|---------|-------------|
| Weekly Grid | Table with days (Mon-Sat) as rows and 6 period time slots as columns |
| Period Slots | Shows class + subject (e.g., "10-A Math") or "Free" |
| Visual Distinction | Assigned classes shown as blue chips, free periods as outlined gray chips |
| Time Slots | 8:00-8:45, 9:00-9:45, 10:00-10:45, 11:00-11:45, 12:00-12:45, 1:30-2:15 |

---

## 12. Leave Management

**Page:** `/leaves`

| Feature | Description |
|---------|-------------|
| Leave Balance Cards | 3 cards (Casual, Sick, Earned) showing Remaining, Used, and Pending counts |
| Leave History Table | Columns: Type, From, To, Days, Reason, Status |
| Status Indicators | "Approved" (green) or "Pending" (warning/yellow) chips |
| Apply Leave Dialog | Modal form with: Leave Type dropdown, From Date, To Date, Reason |
| Apply Button | Top-right "Apply Leave" button opens the dialog |

---

## Technical Architecture

| Layer | Technology |
|-------|-----------|
| Build Tool | Vite 5 (dev server on port 5175) |
| UI Framework | React 18 |
| Component Library | Material UI 5 (with Emotion) |
| State Management | Redux Toolkit 2 |
| Routing | React Router 6 (nested routes) |
| Forms | React Hook Form + Zod schema validation |
| Charts | Recharts 2 |
| HTTP Client | Axios with interceptors |
| Theme | Custom MUI theme (primary: #1a237e, secondary: #4fc3f7) |

---

## Current State

- All pages use **hardcoded demo data** (no live API integration for page content)
- Authentication flow is wired to the backend API (`/auth/login/`, `/auth/refresh-token/`, `/auth/logout/`)
- The app is multi-tenant aware via `X-School-Code` header
- No unit tests or E2E tests present
- No TypeScript (plain JSX)
- Version: 0.0.1 (early development)
