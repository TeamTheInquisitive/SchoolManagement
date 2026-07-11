import { useState, useMemo } from 'react';
import { useDebounceValue } from 'usehooks-ts';
import { RotateCcw, Edit2, Eye, EyeOff, Copy, Check, Download } from 'lucide-react';
import { Button, DataTable, ConfirmDialog, Tabs, SearchableSelect, SearchInput, useToast, Breadcrumb, usePagination, useTabState } from 'school-erp-ui-shared';
import { useStudents, useResetStudentPassword } from '../../services/studentService';
import { useTeachers, useResetTeacherPassword } from '../../services/teacherService';
import { useSchoolProfile } from '../../services/settingsService';
import { useClassSectionFilter } from '../../hooks/useClassSectionFilter';
import { getSchoolInfo } from '../../utils/getSchoolInfo';
import { generateCredentialsPdf } from '../../utils/credentialsPdf';
import { ENDPOINTS } from '../../config/api';

export default function CredentialsPage() {
  const toast = useToast();
  const { data: schoolProfile } = useSchoolProfile();
  const [pdfExporting, setPdfExporting] = useState(false);
  const tabs = [
    { id: 'students', label: 'Student Credentials' },
    { id: 'teachers', label: 'Teacher Credentials' },
  ];
  const [activeTab, setActiveTab] = useTabState(tabs);

  const handleDownloadPdf = async () => {
    if (pdfExporting) return;
    setPdfExporting(true);
    toast.info('Generating credentials PDF... Please wait.');
    try {
      const { fetchAllPages } = await import('../../utils/exportAllPages');
      const [allStudents, allTeachers] = await Promise.all([
        fetchAllPages(ENDPOINTS.students.list, { status: 'Active' }, 100),
        fetchAllPages(ENDPOINTS.teachers.list, {}, 100),
      ]);
      const students = allStudents.map(s => ({
        full_name: s.full_name || s.name || '',
        class_name: s.class_name || '',
        section: s.section || '',
        roll_number: s.roll_number || '',
        password_changed: s.password_changed || false,
      }));
      const teachers = allTeachers.map(t => ({
        full_name: t.user?.full_name || t.full_name || t.name || '',
        department: t.department || '',
        email: t.user?.email || t.email || '',
        password_changed: t.password_changed || false,
      }));
      generateCredentialsPdf({
        schoolInfo: getSchoolInfo(schoolProfile),
        students,
        teachers,
      });
      toast.success(`PDF generated with ${students.length} students and ${teachers.length} teachers`);
    } catch (err) {
      toast.error('Failed to generate PDF');
    }
    setPdfExporting(false);
  };

  return (
    <div className="space-y-4">
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Credential Management' }]} />
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Credential Management</h1>
        <Button variant="secondary" icon={Download} onClick={handleDownloadPdf} disabled={pdfExporting} loading={pdfExporting}>
          {pdfExporting ? 'Generating...' : 'Download PDF'}
        </Button>
      </div>
      <Tabs tabs={tabs} active={activeTab} onChange={setActiveTab} />
      {activeTab === 0 && <StudentCredentials />}
      {activeTab === 1 && <TeacherCredentials />}
    </div>
  );
}

function StudentCredentials() {
  const toast = useToast();
  const { data: schoolData } = useSchoolProfile();
  const schoolCode = schoolData?.school_code || schoolData?.code || 'school';
  const { classOptions, sectionOptions, selectedClass, selectedSection, setSelectedClass, setSelectedSection } = useClassSectionFilter();
  const [statusFilter, setStatusFilter] = useState('');
  const [genderFilter, setGenderFilter] = useState('');
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounceValue(search, 300);
  const [confirmReset, setConfirmReset] = useState(null);
  const [editModal, setEditModal] = useState(null);
  const [customPassword, setCustomPassword] = useState('');
  const [bulkResetConfirm, setBulkResetConfirm] = useState(false);
  const [visiblePasswords, setVisiblePasswords] = useState({});
  const [copied, setCopied] = useState(null);
  const togglePassword = (id) => setVisiblePasswords(p => ({ ...p, [id]: !p[id] }));
  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 1500);
  };

  const pagination = usePagination(20, 'credentials-students');

  const params = {
    ...pagination.params,
    ...(selectedClass && { class_name: selectedClass }),
    ...(selectedSection && { section: selectedSection }),
    status: statusFilter || 'Active',
    ...(genderFilter && { gender: genderFilter }),
    ...(debouncedSearch && { search: debouncedSearch }),
  };
  const { data, isLoading, isFetching } = useStudents(params);
  const resetMutation = useResetStudentPassword();

  const students = data?.results ?? (Array.isArray(data) ? data : []);

  const getUsername = (s) => s.roll_number;

  const handleReset = (student) => {
    const defaultPw = getUsername(student);
    resetMutation.mutate({ id: student.id, password: defaultPw }, {
      onSuccess: () => { toast.success(`Password reset for ${student.full_name || student.name}`); setConfirmReset(null); },
      onError: () => { toast.error('Failed to reset password'); setConfirmReset(null); },
    });
  };

  const handleEdit = () => {
    if (!customPassword) return;
    resetMutation.mutate({ id: editModal.id, password: customPassword }, {
      onSuccess: () => { toast.success('Password updated'); setEditModal(null); setCustomPassword(''); },
      onError: () => toast.error('Failed to update password'),
    });
  };

  const handleBulkReset = () => {
    students.forEach((s) => resetMutation.mutate({ id: s.id, password: getUsername(s) }));
    toast.success('Bulk reset initiated');
    setBulkResetConfirm(false);
  };

  const columns = [
    { key: 'roll_number', label: 'Roll Number', render: (r) => (
      <span className="inline-flex items-center gap-1">
        {r.roll_number}
        <button onClick={(e) => { e.stopPropagation(); copyToClipboard(r.roll_number, `sroll-${r.id}`); }} className="text-gray-400 hover:text-gray-600 ml-1">
          {copied === `sroll-${r.id}` ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
        </button>
      </span>
    )},
    { key: 'name', label: 'Name', render: (r) => r.full_name || r.name },
    { key: 'class_name', label: 'Class' },
    { key: 'section', label: 'Section' },
    { key: 'username', label: 'Login Username', render: (r) => (
      <div>
        <span className="inline-flex items-center gap-1 font-mono font-semibold text-slate-900">
          {getUsername(r)}
          <button onClick={(e) => { e.stopPropagation(); copyToClipboard(getUsername(r), `suser-${r.id}`); }} className="text-gray-400 hover:text-gray-600 ml-1">
            {copied === `suser-${r.id}` ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
          </button>
        </span>
        <p className="text-[10px] text-slate-400 mt-0.5">Student login username</p>
      </div>
    )},
    { key: 'password', label: 'Password', render: (r) => (
      r.password_changed ? (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 text-xs font-medium">🔒 Updated by user</span>
      ) : (
        <span className="flex items-center gap-1">
          {visiblePasswords[r.id] ? getUsername(r) : '••••••••'}
          <button onClick={() => togglePassword(r.id)} className="text-gray-400 hover:text-gray-600"><Eye size={14} /></button>
        </span>
      )
    )},
    { key: 'actions', label: 'Actions', render: (r) => (
      <div className="flex gap-1">
        <Button size="sm" variant="ghost" title="Reset to default" onClick={() => setConfirmReset(r)}><RotateCcw size={14} /></Button>
        <Button size="sm" variant="ghost" title="Set custom password" onClick={() => setEditModal(r)}><Edit2 size={14} /></Button>
      </div>
    )},
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[200px] max-w-xs">
          <SearchInput value={search} onChange={(v) => { setSearch(v); pagination.reset(); }} placeholder="Search by name or roll number..." />
        </div>
        <SearchableSelect label="Class" options={classOptions || []} value={selectedClass} onChange={(v) => { setSelectedClass(v); pagination.reset(); }} placeholder="All Classes" />
        <SearchableSelect label="Section" options={sectionOptions || []} value={selectedSection} onChange={(v) => { setSelectedSection(v); pagination.reset(); }} placeholder="All Sections" />
        <SearchableSelect label="Status" options={[{ label: 'All', value: '' }, { label: 'Active', value: 'Active' }, { label: 'Inactive', value: 'Inactive' }]} value={statusFilter} onChange={(v) => { setStatusFilter(v); pagination.reset(); }} placeholder="Active" />
        <SearchableSelect label="Gender" options={[{ label: 'Male', value: 'male' }, { label: 'Female', value: 'female' }]} value={genderFilter} onChange={(v) => { setGenderFilter(v); pagination.reset(); }} placeholder="All" />
        <Button variant="outline" size="sm" onClick={() => setBulkResetConfirm(true)} disabled={!students.length}>Reset All</Button>
      </div>
      <DataTable
        columns={columns}
        data={students}
        loading={isFetching}
        emptyMessage="No students found"
        page={pagination.page}
        totalPages={data?.total_pages || 1}
        totalCount={data?.count || 0}
        pageSize={pagination.pageSize}
        onPageChange={(p) => pagination.setPage(p)}
        onPageSizeChange={pagination.setPageSize}
      />
      <ConfirmDialog open={!!confirmReset} title="Reset Password" message={`Reset password for ${confirmReset?.full_name || confirmReset?.name || ''}?\nUsername: ${confirmReset ? getUsername(confirmReset) : ''}\nNew password will be set to the username.`} onConfirm={() => handleReset(confirmReset)} onClose={() => setConfirmReset(null)} loading={resetMutation.isPending} />
      <ConfirmDialog open={bulkResetConfirm} title="Bulk Reset" message={`Reset passwords for all ${students.length} filtered students to their defaults?`} onConfirm={handleBulkReset} onClose={() => setBulkResetConfirm(false)} />
      {editModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-[90vw] sm:max-w-sm space-y-4">
            <h3 className="font-semibold">Set Custom Password</h3>
            <p className="text-sm text-gray-600">For: {editModal.full_name || editModal.name}</p>
            <input type="text" className="w-full border rounded px-3 py-2" placeholder="Enter new password" value={customPassword} onChange={(e) => setCustomPassword(e.target.value)} />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" onClick={() => { setEditModal(null); setCustomPassword(''); }}>Cancel</Button>
              <Button onClick={handleEdit} disabled={!customPassword || resetMutation.isPending}>Save</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function TeacherCredentials() {
  const toast = useToast();
  const [departmentFilter, setDepartmentFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounceValue(search, 300);
  const [confirmReset, setConfirmReset] = useState(null);
  const [editModal, setEditModal] = useState(null);
  const [customPassword, setCustomPassword] = useState('');
  const [bulkResetConfirm, setBulkResetConfirm] = useState(false);
  const [visiblePasswords, setVisiblePasswords] = useState({});
  const [copied, setCopied] = useState(null);
  const togglePassword = (id) => setVisiblePasswords(p => ({ ...p, [id]: !p[id] }));
  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 1500);
  };

  const pagination = usePagination(20, 'credentials-teachers');

  const params = {
    ...pagination.params,
    ...(departmentFilter && { department: departmentFilter }),
    ...(statusFilter && { status: statusFilter }),
    ...(debouncedSearch && { search: debouncedSearch }),
  };
  const { data, isLoading, isFetching } = useTeachers(params);
  const resetMutation = useResetTeacherPassword();

  const rawTeachers = data?.results ?? (Array.isArray(data) ? data : []);
  const teachers = rawTeachers.map(t => ({ ...t, full_name: t.user?.full_name || t.full_name, email: t.user?.email || t.email }));
  const departments = useMemo(() => [...new Set(teachers.map(t => t.department).filter(Boolean))].map(d => ({ label: d, value: d })), [teachers]);

  const getUsername = (t) => t.email;

  const handleReset = (teacher) => {
    resetMutation.mutate({ id: teacher.id, password: teacher.email }, {
      onSuccess: () => { toast.success(`Password reset for ${teacher.full_name || teacher.name}`); setConfirmReset(null); },
      onError: () => { toast.error('Failed to reset password'); setConfirmReset(null); },
    });
  };

  const handleEdit = () => {
    if (!customPassword) return;
    resetMutation.mutate({ id: editModal.id, password: customPassword }, {
      onSuccess: () => { toast.success('Password updated'); setEditModal(null); setCustomPassword(''); },
      onError: () => toast.error('Failed to update password'),
    });
  };

  const handleBulkReset = () => {
    teachers.forEach((t) => resetMutation.mutate({ id: t.id, password: t.email }));
    toast.success('Bulk reset initiated');
    setBulkResetConfirm(false);
  };

  const columns = [
    { key: 'employee_id', label: 'Employee ID', render: (r) => (
      <span className="inline-flex items-center gap-1">
        {r.employee_id}
        <button onClick={(e) => { e.stopPropagation(); copyToClipboard(r.employee_id, `temp-${r.id}`); }} className="text-gray-400 hover:text-gray-600 ml-1">
          {copied === `temp-${r.id}` ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
        </button>
      </span>
    )},
    { key: 'name', label: 'Name', render: (r) => r.full_name || r.name },
    { key: 'department', label: 'Department' },
    { key: 'email', label: 'Email (Username)', render: (r) => (
      <span className="inline-flex items-center gap-1">
        {r.email}
        <button onClick={(e) => { e.stopPropagation(); copyToClipboard(r.email, `temail-${r.id}`); }} className="text-gray-400 hover:text-gray-600 ml-1">
          {copied === `temail-${r.id}` ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
        </button>
      </span>
    )},
    { key: 'password', label: 'Password', render: (r) => (
      r.password_changed ? (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 text-xs font-medium">🔒 Updated by user</span>
      ) : (
        <span className="flex items-center gap-1">
          {visiblePasswords[r.id] ? r.email : '••••••••'}
          <button onClick={() => togglePassword(r.id)} className="text-gray-400 hover:text-gray-600"><Eye size={14} /></button>
        </span>
      )
    )},
    { key: 'actions', label: 'Actions', render: (r) => (
      <div className="flex gap-1">
        <Button size="sm" variant="ghost" title="Reset to default" onClick={() => setConfirmReset(r)}><RotateCcw size={14} /></Button>
        <Button size="sm" variant="ghost" title="Set custom password" onClick={() => setEditModal(r)}><Edit2 size={14} /></Button>
      </div>
    )},
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[200px] max-w-xs">
          <SearchInput value={search} onChange={(v) => { setSearch(v); pagination.reset(); }} placeholder="Search by name or email..." />
        </div>
        <SearchableSelect label="Department" options={departments} value={departmentFilter} onChange={(v) => { setDepartmentFilter(v); pagination.reset(); }} placeholder="All Departments" />
        <SearchableSelect label="Status" options={[{ label: 'Active', value: 'active' }, { label: 'Inactive', value: 'inactive' }]} value={statusFilter} onChange={(v) => { setStatusFilter(v); pagination.reset(); }} placeholder="All" />
        <Button variant="outline" size="sm" onClick={() => setBulkResetConfirm(true)} disabled={!teachers.length}>Reset All</Button>
      </div>
      <DataTable
        columns={columns}
        data={teachers}
        loading={isFetching}
        emptyMessage="No teachers found"
        page={pagination.page}
        totalPages={data?.total_pages || 1}
        totalCount={data?.count || 0}
        pageSize={pagination.pageSize}
        onPageChange={(p) => pagination.setPage(p)}
        onPageSizeChange={pagination.setPageSize}
      />
      <ConfirmDialog open={!!confirmReset} title="Reset Password" message={`Reset password for ${confirmReset?.full_name || confirmReset?.name || ''}?\nNew password: ${confirmReset?.email || ''}`} onConfirm={() => handleReset(confirmReset)} onClose={() => setConfirmReset(null)} loading={resetMutation.isPending} />
      <ConfirmDialog open={bulkResetConfirm} title="Bulk Reset" message={`Reset passwords for all ${teachers.length} filtered teachers to their defaults?`} onConfirm={handleBulkReset} onClose={() => setBulkResetConfirm(false)} />
      {editModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-lg p-6 w-full max-w-[90vw] sm:max-w-sm space-y-4">
            <h3 className="font-semibold">Set Custom Password</h3>
            <p className="text-sm text-gray-600">For: {editModal.full_name || editModal.name}</p>
            <input type="text" className="w-full border rounded px-3 py-2" placeholder="Enter new password" value={customPassword} onChange={(e) => setCustomPassword(e.target.value)} />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" onClick={() => { setEditModal(null); setCustomPassword(''); }}>Cancel</Button>
              <Button onClick={handleEdit} disabled={!customPassword || resetMutation.isPending}>Save</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
