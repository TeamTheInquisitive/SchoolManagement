# School ERP Student Portal - Comprehensive Features Documentation

## 1. Project Overview

### Tech Stack
- **Frontend Framework:** React (with Vite build tool - `import.meta.env`)
- **UI Library:** Material UI (MUI) v5+ (`@mui/material`, `@mui/icons-material`)
- **State Management:** Redux Toolkit (`@reduxjs/toolkit`, `react-redux`)
- **Routing:** React Router v6 (`react-router-dom`)
- **Form Handling:** React Hook Form with Zod validation (`react-hook-form`, `@hookform/resolvers/zod`, `zod`)
- **HTTP Client:** Axios
- **Charting:** Recharts (`recharts`)
- **Font:** Roboto

### Architecture
- **Pattern:** Single Page Application (SPA) with role-based routing
- **State:** Centralized Redux store with async thunks for API calls
- **Layout:** Persistent sidebar navigation with top app bar (Shell layout via `PortalLayout`)
- **API:** RESTful backend at `http://localhost:8000/api/v1` with cookie-based auth and automatic token refresh
- **Styling:** MUI theme customization with custom color palette (primary: #5c6bc0, secondary: #4fc3f7)

### Theme Configuration
- Primary color: Indigo (#5c6bc0)
- Secondary color: Light blue (#4fc3f7)
- Background: Light gray (#f5f7fa) with white paper
- Buttons: No text-transform, border-radius 8px
- Cards: Border-radius 12px with subtle box shadow

---

## 2. Routing Structure

| Path | Component | Role Required |
|------|-----------|---------------|
| `/login` | LoginPage | None (public) |
| `/student` | Redirects to `/student/dashboard` | student |
| `/student/dashboard` | StudentDashboard | student |
| `/student/timetable` | TimetablePage | student |
| `/student/attendance` | AttendancePage | student |
| `/student/results` | ResultsPage | student |
| `/student/assignments` | AssignmentsPage | student |
| `/student/exams` | ExamsPage | student |
| `/student/library` | LibraryPage | student |
| `/student/messages` | MessagesPage | student |
| `/student/profile` | MyProfilePage | student |
| `/student/fees` | FeePaymentPage | student |
| `/student/quiz` | QuizPortalPage | student |
| `/teacher` | Redirects to `/teacher/dashboard` | teacher |
| `/teacher/dashboard` | TeacherDashboard | teacher |
| `*` (catch-all) | Redirects to `/login` | - |

---

## 3. Authentication & Authorization

### Authentication Flow
1. User submits email/password on LoginPage
2. Credentials sent to `POST /auth/login/`
3. On success, user object stored in Redux state and localStorage
4. Role-based redirect: `teacher` -> `/teacher/dashboard`, `student` -> `/student/dashboard`
5. On failure, error message displayed via Alert component

### Authorization
- `ProtectedRoute` component wraps all authenticated routes
- Checks `user` in Redux state; redirects to `/login` if absent
- Checks `allowedRoles` array; redirects to `/login` if role mismatch
- Supports `student` and `teacher` roles

### Token Management
- Cookie-based authentication (`withCredentials: true`)
- Automatic token refresh on 401 responses via Axios interceptor (`POST /auth/refresh-token/`)
- Multi-tenant support via `X-School-Code` header from localStorage
- Logout clears localStorage and calls `POST /auth/logout/`

### Session Persistence
- User data persisted in localStorage (`user` key)
- On app load, user hydrated from localStorage into Redux state
- `fetchMe` thunk available for session validation via `GET /auth/me/`

---

## 4. Portal Layout (Shell)

### Sidebar Navigation (Permanent Drawer - 240px width)
- **Header:** "ERP Portal" title with role subtitle (Student/Teacher)
- **User Profile Section:** Avatar (gradient background with initials), full name, email
- **Navigation Menu (Student):**
  - Dashboard
  - Timetable
  - Assignments
  - Attendance
  - Results
  - Exams
  - Library
  - Messages
  - Fee Payment
  - Quiz Portal
  - My Profile
- **Navigation Menu (Teacher):**
  - Dashboard
  - My Classes
  - Attendance
  - Assignments
  - Exams & Quizzes
  - Messages
- **Logout Button:** Dispatches logout action and navigates to login
- **Active State:** Selected item highlighted with indigo (#6366f1) background
- **Dark Theme Sidebar:** Background #0f172a with white/gray text

### Top App Bar
- Sticky positioned, white background with bottom border
- Left: Welcome message with user's first name
- Right: Notification bell icon with badge (count: 2), user avatar

### Content Area
- Light gray background (#f8fafc)
- 24px padding
- Renders child routes via `<Outlet />`

---

## 5. Page Features (Student Portal)

### 5.1 Login Page (`/login`)

**Visual Design:**
- Full-screen gradient background (purple to indigo: #667eea -> #764ba2)
- Centered white card (420px width)
- School icon in circular badge at top

**Form Fields:**
- Email Address (with email icon adornment, validated as valid email)
- Password (with lock icon adornment, type="password", required)

**Interactive Elements:**
- "Sign In" button (full width, contained variant, loading state shows "Signing in...")
- Form validation via Zod schema (email format, password required)
- Error Alert displayed on failed login

**Functionality:**
- Validates input before submission
- Dispatches Redux `login` thunk
- Role-based redirect on success
- Clears previous errors on new submission

---

### 5.2 Student Dashboard (`/student/dashboard`)

**KPI Cards (4 cards in a row):**
| Card | Value | Subtitle | Icon | Color |
|------|-------|----------|------|-------|
| Attendance | 92% | 55/60 days | CheckCircle | Green |
| Overall Grade | 85% | Grade A | TrendingUp | Blue |
| Assignments | 12/14 | 2 pending | Assignment | Amber |
| Fee Status | 0 (INR) | All paid | AttachMoney | Purple |

**Quick Actions (4 buttons):**
- Timetable (blue, CalendarMonth icon)
- Assignments (amber, Assignment icon)
- Exams (red, Quiz icon)
- Library (green, MenuBook icon)

**Today's Schedule Card:**
- Header with "Thursday" chip
- List of 5 periods with time, subject, teacher, and room
  - 8:00-8:45: Mathematics, Dr. Jane Smith, Room 101
  - 9:00-9:45: English, Ms. Emily Davis, Room 102
  - 10:00-10:45: Physics, Prof. Robert Johnson, Lab 1
  - 11:00-11:45: Chemistry, Mr. William Anderson, Lab 2
  - 12:00-12:45: Hindi, Mrs. Priya Sharma, Room 103

**Pending Assignments Card:**
- List with assignment title, subject, due date
- Color-coded "days left" chips (error for <=1 day, warning otherwise)

**Upcoming Exams Card:**
- Exam name, date, and type chip (outlined)

**Subject Attendance Card:**
- Per-subject progress bars with percentage
- Color-coded: green >= 75%, red < 75%
- Subjects: Mathematics (95%), English (88%), Physics (80%), Chemistry (92%), Biology (72%)

**Recent Results Card:**
- Exam name, marks, grade chip, date
- 3 most recent results displayed

**Announcements Card:**
- Title, date, and source (Admin/Library)
- 3 recent announcements

---

### 5.3 Assignments Page (`/student/assignments`)

**Summary Cards (4 across):**
- Total assignments count
- Pending count (amber)
- Submitted count (blue)
- Graded count (green)

**Tabbed Interface:**
- Tab 1: "All" - shows all assignments
- Tab 2: "Pending" - filters to pending only
- Tab 3: "Graded" - filters to graded only

**Assignments Table:**
| Column | Description |
|--------|-------------|
| Assignment | Title of assignment |
| Subject | Subject name |
| Due Date | Date string |
| Marks | Scored/Maximum marks |
| Status | Chip (Pending/Submitted/Graded/Late with color coding) |
| Action | "Submit" button for pending assignments |

**Submit Assignment Dialog:**
- Dialog title: "Submit Assignment"
- Assignment title displayed
- Comments text field (optional, multiline, 2 rows)
- File upload button (accepts PDF, Image, Doc)
- File constraints: Max 10MB per file, up to 5 files
- Cancel and Submit buttons

**Status Configuration:**
- Pending: warning color, Schedule icon
- Submitted: primary color, CheckCircle icon
- Graded: success color, CheckCircle icon
- Late: error color, Warning icon

---

### 5.4 Attendance Page (`/student/attendance`)

**Overall Attendance Card:**
- Large percentage display (green if >= 75%, red otherwise)
- "Overall Attendance" label
- Days ratio (e.g., 45/60 days)
- Warning chip if below 75% threshold

**Subject-wise Attendance Card:**
- Month filter dropdown (May, April, March)
- Per-subject progress bars with:
  - Subject name
  - Percentage and ratio (e.g., 90% 18/20)
  - Color-coded bars (green >= 75%, red < 75%)
- Subjects tracked: Mathematics, English, Physics, Chemistry, Biology

**Recent Attendance Table:**
| Column | Description |
|--------|-------------|
| Date | Date of class |
| Subject | Subject name |
| Status | Chip - "present" (green) or "absent" (red) |

---

### 5.5 Exams Page (`/student/exams`)

**Tabbed Interface (3 tabs):**

**Tab 1: Upcoming Exams**
- Grid of exam cards (2 per row on medium screens) with:
  - Exam name and type chip (Mid-term/Unit Test/Final)
  - Date and time
  - Venue and duration
  - "Download Hall Ticket" button with Download icon

**Tab 2: Online Quizzes**
- Table with columns: Quiz, Subject, Questions, Duration, Attempts, Action
- Action column: "Take Quiz" button (contained, with PlayArrow icon) or "Completed" chip
- Tracks attempts used vs allowed (e.g., 1/3, 2/3, 3/3)

**Tab 3: Past Results**
- Table with columns: Exam, Date, Marks, Grade, Rank
- Grade displayed as outlined chip
- Rank displayed with # prefix

---

### 5.6 Fee Payment Page (`/student/fees`)

**Fee Summary Cards (4 across):**
- Total Fees (in INR)
- Paid amount (green)
- Due amount (amber/warning)
- Overdue amount (red)

**Tabbed Interface (2 tabs):**

**Tab 1: Current Dues**
- Table columns: Fee Type, Amount (INR), Due Date, Status, Action
- Status: "Overdue" (red chip) or "Pending" (warning chip)
- Action: "Pay Now" button (contained variant)

**Tab 2: Payment History**
- Table columns: Fee Type, Amount (INR), Paid Date, Method, Receipt
- Method displayed as outlined chip (UPI, Cash, Bank Transfer)
- Receipt: Clickable button with Download icon showing receipt ID (e.g., RCP-2024-001)

---

### 5.7 Library Page (`/student/library`)

**Summary Cards (4 across):**
- Books Borrowed (with MenuBook icon in blue badge)
- Overdue count (red)
- Max Allowed (limit: 3)
- Total Fines (INR, amber)

**Tabbed Interface (3 tabs):**

**Tab 1: My Books**
- Table columns: Book, Author, Issue Date, Due Date, Status
- Status: "Issued" (primary chip) or "Overdue" (error chip)

**Tab 2: Browse Catalog**
- Search text field with search icon (filters by title or author)
- Table columns: Title, Author, Category, Available
- Availability: Green chip with copy count or red "Unavailable" chip
- Categories include: Computer Science, Physics, Chemistry, Mathematics, English

**Tab 3: History**
- Table columns: Book, Issue Date, Return Date, Fine
- Fine displayed as INR amount or "-" if none

---

### 5.8 Messages Page (`/student/messages`)

**Tabbed Interface (2 tabs):**

**Tab 1: Chat with Teachers**
- Split-pane layout (280px sidebar + chat area, 500px height)
- **Teacher List (Left Panel):**
  - List of teachers with avatar (gradient), name, last message (truncated), time ago
  - Selected teacher highlighted
- **Chat Area (Right Panel):**
  - Header: Teacher name and subject
  - Message bubbles:
    - Student messages: right-aligned, indigo background, white text
    - Teacher messages: left-aligned, white background with border
    - Timestamps on each message
  - Message input: TextField with "Type a message..." placeholder
  - Send button (contained, indigo, with Send icon)

**Tab 2: Announcements**
- List of announcement cards with:
  - Title (bold)
  - Source chip (Admin/Library, outlined)
  - Content text
  - Date

---

### 5.9 My Profile Page (`/student/profile`)

**Profile Header Card:**
- Large avatar (80px, gradient with initials)
- Full name, roll number, class and section
- Email chip, phone chip, student type chip (Day Scholar)
- "Edit Profile" button (outlined, with Edit icon)

**Personal Information Card:**
- Date of Birth, Gender, Admission Date
- Blood Group, Religion, Student Type
- Full address

**Parent/Guardian Information Card:**
- Name, Relationship, Phone
- Email, Occupation, Emergency Contact

**Medical Information Card:**
- Blood Group
- Medical Conditions
- Allergies
- Indicated with heart icon (red)

**Transport Information Card:**
- Enrollment status
- Route name (e.g., Route 5 - Downtown)
- Bus number (e.g., BUS-005)
- Pickup point
- Indicated with bus icon (blue)

**Mentor Details Card:**
- Mentor name
- Subject
- Contact number
- Indicated with school icon (indigo)

---

### 5.10 Quiz Portal Page (`/student/quiz`)

**Summary Cards (4 across):**
- Available quizzes count
- Completed quizzes count
- Average Score (88%, green)
- Average Rank (#4, with trophy icon in amber badge)

**Available Quizzes Table:**
- Columns: Quiz, Subject, Questions, Duration (min), Attempts, Best Score, Action
- Action: "Start" button (contained, with PlayArrow icon) or "Completed" chip
- Tracks attempt usage (e.g., 0/3, 1/3, 3/3)

**Completed Quizzes Table:**
- Columns: Quiz, Subject, Score, Percentage (green chip), Rank (#N), Date

**Quiz Taking Dialog (Full-width, max-width md):**
- Title bar with quiz name and countdown timer chip (e.g., "29:45" in red)
- Progress bar (indigo, determinate based on question number)
- Question counter ("Question X of Y")
- Question text
- Radio button options (styled with border and padding)
- Navigation: "Previous" button (disabled on first question), "Next" button, "Submit Quiz" button (green, on last question)

**Result Dialog:**
- Success icon (green checkmark, 64px)
- "Quiz Completed!" heading
- Score display (e.g., "2/3" in large indigo text)
- Percentage text
- "Back to Quizzes" button

---

### 5.11 Results Page (`/student/results`)

**Summary Cards (4 across):**
- Overall Percentage (82%, blue)
- Class Rank (5th / 45 students)
- Percentile (89th)
- Grade (A)

**Performance Trend Chart (Line Chart - Recharts):**
- X-axis: Exam names (Unit 1, Mid-term, Unit 2, Quarterly)
- Y-axis: Percentage (0-100)
- Line color: Indigo (#6366f1)
- Grid with dashed lines
- Tooltip enabled

**Subject Comparison Chart (Bar Chart - Recharts):**
- Grouped bar chart comparing student marks vs class average
- X-axis: Subject names
- Y-axis: Marks (0-100)
- Student bars: Indigo (#6366f1)
- Class average bars: Gray (#e2e8f0)
- Tooltip enabled

**Subject-wise Results Table:**
- Exam filter dropdown (Unit Test 1, Mid-term, Unit Test 2, Quarterly)
- Table columns: Subject, Marks (scored/total), Grade (outlined chip), Class Avg (%), Status
- Status: "Pass" (green chip) or "Fail" (red chip), threshold at 40 marks

---

### 5.12 Timetable Page (`/student/timetable`)

**Header:**
- Page title: "My Timetable"
- Subtitle: "Class 10-A - Academic Year 2025-2026"

**Weekly Timetable Table:**
- Rows: Monday through Saturday (6 days)
- Columns: Day + 6 time periods (8:00-8:45, 9:00-9:45, 10:00-10:45, 11:00-11:45, 12:00-12:45, 1:30-2:15)
- Cell content as chips:
  - Regular subjects: Outlined chip with subject name
  - Break: Gray background chip
  - Free: Outlined chip with muted text
- Subjects covered: Mathematics, English, Physics, Chemistry, Biology, Hindi, PE, Computer, Art, Library

---

## 6. Page Features (Teacher Portal)

### 6.1 Teacher Dashboard (`/teacher/dashboard`)

**KPI Cards (4 across):**
| Card | Value | Icon | Color |
|------|-------|------|-------|
| Total Classes | 6 | People | Indigo |
| Students | 145 | People | Green |
| Assignments | 12 | Assignment | Orange |
| Avg Rating | 4.8/5 | Star | Purple |

**Note:** The teacher portal currently only has the dashboard page implemented. The sidebar menu shows additional planned pages (My Classes, Attendance, Assignments, Exams & Quizzes, Messages) but their routes are not yet defined.

---

## 7. API Service Configuration

### Base Configuration
- Base URL: `VITE_API_URL` env variable or `http://localhost:8000/api/v1`
- Content-Type: `application/json`
- Credentials: Included (cookies)

### Request Interceptor
- Attaches `X-School-Code` header from localStorage on every request (multi-tenant support)

### Response Interceptor
- On 401 response: Attempts token refresh via `POST /auth/refresh-token/`
- On refresh success: Retries original request
- On refresh failure: Redirects to `/login`
- Prevents infinite retry loops with `_retry` flag

### API Endpoints Used
- `POST /auth/login/` - User authentication
- `POST /auth/logout/` - Session termination
- `POST /auth/refresh-token/` - Token refresh
- `GET /auth/me/` - Current user info

---

## 8. State Management (Redux)

### Auth Slice
**State Shape:**
```
{
  user: { role, full_name, email, ... } | null,
  loading: boolean,
  error: string | null
}
```

**Actions:**
- `login` (async thunk) - Authenticates user, stores in localStorage
- `fetchMe` (async thunk) - Validates session, updates user data
- `logout` (reducer) - Clears state and localStorage, calls logout API
- `clearError` (reducer) - Resets error state

---

## 9. Data Characteristics

**Note:** The current implementation uses hardcoded/mock data within components. All data displayed (assignments, attendance records, exam schedules, fee records, library books, messages, quiz questions, results, and timetable) is static and defined directly in the component files. The API integration layer is set up but the page components do not yet fetch data from the backend - they render predefined arrays.

### Currency
- Indian Rupee (INR) used throughout (fee payments, library fines)

### Academic Context
- Class 10, Section A
- Academic Year 2025-2026
- Subjects: Mathematics, English, Physics, Chemistry, Biology, Hindi, Computer, Art, PE
- Grading: A+, A, B+, B, etc.
- Attendance threshold: 75%

---

## 10. UI/UX Patterns

### Design System
- Card-based layout with subtle borders (#e2e8f0) and no box shadow (flat design)
- Color-coded status indicators (green=success, amber=warning, red=error, blue=info)
- Consistent typography scale (1.5rem headings, 0.875rem body, 0.75rem captions)
- Slate color palette for text (#1e293b dark, #475569 medium, #64748b light, #94a3b8 muted)

### Interactive Patterns
- Tabbed navigation for multi-view pages
- Dialog modals for actions (submit assignment, take quiz)
- Filter dropdowns for data views (month, exam type)
- Search fields with real-time filtering
- Progress bars for percentage data
- Status chips with color coding

### Responsive Grid
- Uses MUI Grid with breakpoints: xs (12), sm (6), md (3/4/6) depending on content
- Mobile-first approach with responsive column sizing
