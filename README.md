# School Management Portal - Admin Portal

React-based admin dashboard for school administrators to manage all school operations.

## Tech Stack
- React 18, Vite 5
- Material UI (MUI) v5
- Redux Toolkit (state management)
- React Router v6
- React Hook Form + Zod (form validation)
- Recharts (analytics/charts)
- Axios (HTTP client with httpOnly cookie auth)

## Setup

```bash
# Enter directory
cd admin-portal

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# Run development server
npm run dev
```

App runs at `http://localhost:5173`

## Build for Production
```bash
npm run build
# Output in dist/ folder
```

## Project Structure
```
admin-portal/src/
├── components/
│   ├── layout/        # AdminLayout, Sidebar, Header
│   └── ProtectedRoute.jsx
├── pages/
│   ├── auth/          # LoginPage
│   ├── dashboard/     # DashboardPage (KPIs, charts)
│   ├── students/      # StudentsPage, StudentDetailsPage
│   ├── teachers/      # TeachersPage, TeacherPrivilegesPage
│   ├── leaves/        # LeaveManagementPage
│   ├── examinations/  # ExaminationsPage
│   ├── library/       # LibraryPage
│   ├── fees/          # FeeManagementPage
│   ├── transport/     # TransportPage
│   ├── payroll/       # PayrollPage
│   ├── staff/         # StaffPage
│   └── ComingSoon.jsx
├── store/             # Redux store + authSlice
├── services/          # Axios API client
└── theme/             # MUI theme customization
```

## Authentication
Uses httpOnly cookies (set by backend). No tokens stored in localStorage. Only user profile data (name, role) is cached locally for UI display.

## Environment Variables
```
VITE_API_URL=http://localhost:8000/api/v1
```
