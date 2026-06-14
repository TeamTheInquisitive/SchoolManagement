import { useState, useEffect } from 'react';
import { useDebounceValue } from 'usehooks-ts';
import { useQueryClient } from '@tanstack/react-query';
import { Plus, Eye, Pencil, Trash2, Download, Upload, Users, CheckCircle, GraduationCap, Filter, FileSpreadsheet, X } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { useStudents, useCreateStudent, useDeleteStudent, useUpdateStudent, useStudentFeeHistory } from '../../services/studentService';
import { useFeeStructures, useSchoolProfile } from '../../services/settingsService';
import { fetchNextId } from '../../services/settingsService';
import { useClassSectionFilter } from '../../hooks/useClassSectionFilter';
import { Button, Badge, Modal, ConfirmDialog, SearchableSelect, useToast, exportToCsv, exportToExcel, useSortableData, Breadcrumb, usePagination, DataTable, DatePicker , AnimatedNumber } from 'school-erp-ui-shared';
import { GENDER_OPTIONS } from '../../constants.jsx';
import { downloadBulkTemplate } from '../../utils/bulkTemplateExport';
import BulkImportModal from '../../components/BulkImportModal';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';

const phoneRegex = /^[6-9]\d{9}$/;

const studentSchema = z.object({
  roll_number: z.string().min(1, 'Required').refine(v => v.trim().length > 0, 'Roll number cannot be empty'),
  full_name: z.string().min(1, 'Required').refine(v => v.trim().length > 0, 'Name cannot be empty'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  phone: z.string().regex(phoneRegex, '10 digits starting with 6-9').optional().or(z.literal('')),
  class_name: z.string().min(1, 'Required'),
  section: z.string().min(1, 'Required'),
  date_of_birth: z.string().optional().refine(val => {
    if (!val) return true;
    return val <= new Date().toISOString().split('T')[0];
  }, { message: 'Date of birth must be in the past' }),
  admission_date: z.string().optional().refine(val => {
    if (!val) return true;
    return val <= new Date().toISOString().split('T')[0];
  }, { message: 'Admission date cannot be in the future' }),
  gender: z.string().optional(),
  student_type: z.string().optional(),
  blood_group: z.string().optional(),
  religion: z.string().optional(),
  address: z.string().optional(),
  parent_name: z.string().optional(),
  parent_phone: z.string().regex(phoneRegex, '10 digits starting with 6-9').optional().or(z.literal('')),
  parent_email: z.string().email('Invalid email').optional().or(z.literal('')),
  parent_relationship: z.string().optional(),
});

export default function StudentsPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounceValue(search, 300);
  const { selectedClass: filterClass, selectedSection: filterSection, setSelectedClass: setFilterClass, setSelectedSection: setFilterSection, classOptions, sectionOptions, sectionsLoading, classes: allClasses } = useClassSectionFilter();
  const { data: schoolProfile } = useSchoolProfile();
  const [filterStatus, setFilterStatus] = useState('Active');
  const [filterGender, setFilterGender] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  const [deleteId, setDeleteId] = useState(null);
  const [formStep, setFormStep] = useState(0);
  const [passOutDialog, setPassOutDialog] = useState(false);
  const [bulkImportOpen, setBulkImportOpen] = useState(false);
  const [passOutClass, setPassOutClass] = useState('');
  const [passOutYear, setPassOutYear] = useState(new Date().getFullYear().toString());
  const [confirmGraduate, setConfirmGraduate] = useState(false);
  const pagination = usePagination(20, 'admin-students');
  const { register, handleSubmit, reset, watch, setValue, trigger, formState: { errors } } = useForm({ resolver: zodResolver(studentSchema) });

  const { data: studentsData, isLoading, isFetching } = useStudents({
    ...pagination.params,
    search: debouncedSearch || undefined,
    class_name: filterClass || undefined,
    section: filterSection || undefined,
    status: filterStatus || undefined,
    gender: filterGender || undefined,
  });

  const createMutation = useCreateStudent();
  const updateMutation = useUpdateStudent();
  const deleteMutation = useDeleteStudent();

  const students = studentsData?.results ?? [];

  const [studentConcessions, setStudentConcessions] = useState({});
  const [studentCustomFees, setStudentCustomFees] = useState([]);
  const [studentExcludedFees, setStudentExcludedFees] = useState([]);
  const onSubmit = (data) => {
    const payload = Object.fromEntries(Object.entries(data).filter(([, v]) => v !== '' && v !== undefined));
    const nonZeroConcessions = Object.fromEntries(Object.entries(studentConcessions).filter(([, v]) => Number(v) > 0));
    if (Object.keys(nonZeroConcessions).length > 0) payload.concessions = nonZeroConcessions;
    if (studentCustomFees.length > 0) payload.custom_fees = studentCustomFees;
    if (studentExcludedFees.length > 0) payload.excluded_fee_ids = studentExcludedFees;
    if (editingStudent) {
      updateMutation.mutate({ id: editingStudent.id, data: payload }, {
        onSuccess: () => { setDialogOpen(false); setEditingStudent(null); reset(); toast.success('Student updated successfully'); },
        onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to update student'); },
      });
    } else {
      createMutation.mutate(payload, {
        onSuccess: () => { setDialogOpen(false); reset(); setFormStep(0); setStudentConcessions({}); setStudentCustomFees([]); setStudentExcludedFees([]); toast.success('Student added successfully'); },
        onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to add student'); },
      });
    }
  };

  const handleDownloadTemplate = async () => {
    const classNames = allClasses.map(c => c.name);
    const sectionNames = [...new Set(allClasses.flatMap(c => (c.sections || []).map(s => s.section_name)))];
    await downloadBulkTemplate({
      filename: 'Bulk_Student_Upload',
      schoolName: schoolProfile?.school_name || '',
      schoolCode: schoolProfile?.school_code || '',
      sheetName: 'Student Data',
      classSectionMap: allClasses,
      columns: [
        { header: 'Roll Number', key: 'roll_number', mandatory: true, description: 'Unique roll number for the student' },
        { header: 'Full Name', key: 'full_name', mandatory: true, description: 'Student full name' },
        { header: 'Email', key: 'email', description: 'Student email address' },
        { header: 'Phone', key: 'phone', description: '10-digit mobile number' },
        { header: 'Class', key: 'class_name', mandatory: true, dropdown: classNames, description: 'Class name' },
        { header: 'Section', key: 'section', mandatory: true, dropdown: sectionNames, description: 'Section name' },
        { header: 'Date of Birth', key: 'date_of_birth', description: 'Format: YYYY-MM-DD' },
        { header: 'Admission Date', key: 'admission_date', description: 'Format: YYYY-MM-DD' },
        { header: 'Gender', key: 'gender', dropdown: ['Male', 'Female', 'Other'], description: 'Gender' },
        { header: 'Student Type', key: 'student_type', dropdown: ['Day Scholar', 'Hosteller'], description: 'Day Scholar or Hosteller' },
        { header: 'Blood Group', key: 'blood_group', dropdown: ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'], description: 'Blood group' },
        { header: 'Religion', key: 'religion', description: 'Religion' },
        { header: 'Address', key: 'address', description: 'Full address' },
        { header: 'Parent Name', key: 'parent_name', description: 'Parent/Guardian name' },
        { header: 'Parent Phone', key: 'parent_phone', description: '10-digit mobile number' },
        { header: 'Parent Email', key: 'parent_email', description: 'Parent email address' },
        { header: 'Parent Relationship', key: 'parent_relationship', dropdown: ['Father', 'Mother', 'Guardian'], description: 'Relationship to student' },
      ],
    });
    toast.success('Template downloaded successfully');
  };

  const handleExportCsv = () => {
    const headers = ['Roll No', 'Name', 'Class', 'Section', 'Status', 'Phone', 'Email'];
    const rows = students.map(s => [s.roll_number, s.full_name, s.class_name, s.section, s.status, s.phone, s.email]);
    exportToCsv('students', headers, rows);
    toast.success('CSV exported successfully');
  };

  const { sortedData, sortConfig, requestSort } = useSortableData(students);

  const summary = studentsData?.summary || {};
  const totalStudents = summary.total || studentsData?.count || 0;
  const activeStudents = summary.active || 0;
  const inactiveStudents = summary.inactive || 0;


  const kpis = [
    { label: 'Total Students', value: totalStudents, icon: Users, color: 'text-blue-600', bg: 'bg-gradient-to-br from-blue-50 to-blue-100', border: 'border-blue-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(59,130,246,0.3)]' },
    { label: 'Active Students', value: activeStudents, icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-gradient-to-br from-emerald-50 to-emerald-100', border: 'border-emerald-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(16,185,129,0.3)]' },
    { label: 'Inactive/Alumni', value: inactiveStudents, icon: GraduationCap, color: 'text-amber-600', bg: 'bg-gradient-to-br from-amber-50 to-amber-100', border: 'border-amber-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(245,158,11,0.3)]' },
    { label: 'On This Page', value: students.length, icon: Filter, color: 'text-purple-600', bg: 'bg-gradient-to-br from-purple-50 to-purple-100', border: 'border-purple-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(147,51,234,0.3)]' },
  ];

  const inp = (err) => `w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${err ? 'border-red-400' : 'border-slate-300'}`;

  const columns = [
    { key: 'roll_number', label: 'Roll No.', sortable: true },
    {
      key: 'full_name', label: 'Name', sortable: true,
      render: (s) => (
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate(`/admin/students/${s.id}`)}>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-xs font-semibold shadow-sm">{(s.full_name || '').slice(0, 2).toUpperCase()}</div>
          <span className="font-semibold text-purple-600 hover:underline">{s.full_name}</span>
        </div>
      ),
    },
    { key: 'class_name', label: 'Class', sortable: true, render: (s) => <span className="text-slate-500">{s.class_name}</span> },
    { key: 'section', label: 'Section', render: (s) => <span className="text-slate-500">{s.section}</span> },
    { key: 'status', label: 'Status', sortable: true, render: (s) => <Badge status={s.status} /> },
    { key: 'phone', label: 'Phone', render: (s) => <span className="text-slate-500">{s.phone}</span> },
    {
      key: 'actions', label: 'Actions',
      render: (s) => (
        <div className="flex gap-1">
          <button onClick={(e) => { e.stopPropagation(); navigate(`/admin/students/${s.id}`); }} className="p-1.5 hover:bg-slate-100 rounded-lg transition-all duration-150 active:scale-[0.97]"><Eye className="w-4 h-4 text-slate-500" /></button>
          <button onClick={(e) => { e.stopPropagation(); setEditingStudent(s); reset({ roll_number: s.roll_number || '', full_name: s.full_name || '', email: s.email || '', phone: s.phone || '', class_name: s.class_name || '', section: s.section || '', date_of_birth: s.date_of_birth || '', admission_date: s.admission_date || '', gender: s.gender || '', student_type: s.student_type || '', blood_group: s.blood_group || '', religion: s.religion || '', address: s.address || '', parent_name: s.parent_name || '', parent_phone: s.parent_phone || '', parent_email: s.parent_email || '', parent_relationship: s.parent_relationship || '' }); setDialogOpen(true); }} className="p-1.5 hover:bg-slate-100 rounded-lg transition-all duration-150 active:scale-[0.97]"><Pencil className="w-4 h-4 text-slate-500" /></button>
          <button onClick={(e) => { e.stopPropagation(); setDeleteId(s.id); }} className="p-1.5 hover:bg-red-50 rounded-lg transition-all duration-150 active:scale-[0.97]"><Trash2 className="w-4 h-4 text-red-500" /></button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Students' }]} />
      <div className="flex justify-between items-center mb-6">
        <div><h1 className="text-2xl md:text-3xl font-bold text-slate-900">Students Management</h1><p className="text-sm text-slate-500 mt-1">Manage student records and alumni information</p></div>
        <div className="flex gap-2">
          <Button variant="secondary" icon={GraduationCap} disabled title="Coming Soon">Pass Out</Button>
          <Button variant="secondary" icon={Download} onClick={handleDownloadTemplate}>Download Template</Button>
          <Button variant="secondary" icon={Upload} onClick={() => setBulkImportOpen(true)}>Bulk Import</Button>
          <Button variant="primary" icon={Plus} onClick={async () => { reset({ roll_number: '', full_name: '', email: '', phone: '', class_name: '', section: '', date_of_birth: '', admission_date: '', gender: '', student_type: '', blood_group: '', religion: '', address: '', parent_name: '', parent_phone: '', parent_email: '', parent_relationship: '' }); setFormStep(0); setStudentConcessions({}); setStudentCustomFees([]); setStudentExcludedFees([]); setEditingStudent(null); try { const res = await fetchNextId('student'); if (res.enabled && res.id) setValue('roll_number', res.id); } catch {} setDialogOpen(true); }}>Add Student</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
        {kpis.map(k => (
          <div key={k.label} className={`bg-white border ${k.border} rounded-xl p-4 md:p-5 flex items-center gap-3 md:gap-4 transition-all duration-200 hover:-translate-y-1 ${k.glow} cursor-default group`}>
            <div className={`${k.bg} p-2.5 md:p-3 rounded-xl transition-transform duration-200 group-hover:scale-110`}><k.icon className={`w-5 h-5 ${k.color}`} /></div>
            <div><p className="text-xs text-slate-500 font-medium">{k.label}</p><p className="text-xl md:text-2xl font-bold text-slate-900 mt-0.5"><AnimatedNumber value={k.value} id={k.label} /></p></div>
          </div>
        ))}
      </div>

      <DataTable
        columns={columns}
        data={sortedData}
        loading={isFetching}
        emptyMessage={search ? 'No students found. Try adjusting your search or filters.' : 'No students yet. Add your first student to get started.'}
        emptyIcon={Users}
        headerTitle="All Students"
        headerCount={studentsData?.count || 0}
        headerExtra={
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" icon={Download} onClick={handleExportCsv}>Export CSV</Button>
            <Button variant="secondary" size="sm" icon={FileSpreadsheet} onClick={() => { const headers = ['Roll No', 'Name', 'Class', 'Section', 'Status', 'Phone', 'Email']; const rows = students.map(s => [s.roll_number, s.full_name, s.class_name, s.section, s.status, s.phone, s.email]); exportToExcel('students', headers, rows); toast.success('Excel exported successfully'); }}>Export Excel</Button>
          </div>
        }
        search={{ value: search, onChange: (v) => { setSearch(v); pagination.reset(); }, placeholder: 'Search students...' }}
        filters={[
          { key: 'class', value: filterClass, onChange: (v) => { setFilterClass(v); pagination.reset(); }, options: classOptions },
          { key: 'section', value: filterSection, onChange: (v) => { setFilterSection(v); pagination.reset(); }, options: sectionOptions, loading: sectionsLoading },
          { key: 'status', value: filterStatus, onChange: (v) => { setFilterStatus(v); pagination.reset(); }, options: [{ value: '', label: 'All Status' }, { value: 'Active', label: 'Active' }, { value: 'Inactive', label: 'Inactive' }] },
          { key: 'gender', value: filterGender, onChange: (v) => { setFilterGender(v); pagination.reset(); }, options: [{ value: '', label: 'All Gender' }, { value: 'Male', label: 'Male' }, { value: 'Female', label: 'Female' }] },
        ]}
        sortConfig={sortConfig}
        onSort={requestSort}
        page={pagination.page}
        totalPages={studentsData?.total_pages || 1}
        totalCount={studentsData?.count || 0}
        pageSize={pagination.pageSize}
        onPageChange={(p) => pagination.setPage(p)}
        onPageSizeChange={pagination.setPageSize}
        onRowClick={(s) => navigate(`/admin/students/${s.id}`)}
      />

      {/* Add/Edit Student Modal */}
      <Modal open={dialogOpen} onClose={() => { setDialogOpen(false); setEditingStudent(null); setFormStep(0); }} title={editingStudent ? 'Edit Student' : 'Add New Student'} size="3xl">
        <StudentFormWizard
          key={`${dialogOpen ? 'open' : 'closed'}-${editingStudent?.id ?? 'new'}`}
          register={register}
          errors={errors}
          watch={watch}
          setValue={setValue}
          trigger={trigger}
          inp={inp}
          classOptions={classOptions}
          allClasses={allClasses}
          formStep={formStep}
          setFormStep={setFormStep}
          onSubmit={handleSubmit(onSubmit)}
          onCancel={() => { setDialogOpen(false); setEditingStudent(null); setFormStep(0); }}
          isSubmitting={createMutation.isPending || updateMutation.isPending}
          isEditing={!!editingStudent}
          editingStudent={editingStudent}
          submitError={createMutation.isError ? (createMutation.error?.response?.data?.error || createMutation.error?.response?.data?.detail || 'Failed to add student') : null}
          onConcessionChange={setStudentConcessions}
          onCustomFeesChange={setStudentCustomFees}
          onExcludedFeesChange={setStudentExcludedFees}
          toast={toast}
        />
      </Modal>

      <ConfirmDialog open={!!deleteId} onClose={() => setDeleteId(null)} onConfirm={() => { const id = deleteId; setDeleteId(null); toast.undoable('Student deleted', () => deleteMutation.mutate(id, { onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to delete student'); } }), () => toast.info('Delete cancelled')); }} loading={deleteMutation.isPending} message="Are you sure you want to delete this student? You will have a few seconds to undo." />

      <BulkImportModal
        open={bulkImportOpen}
        onClose={() => setBulkImportOpen(false)}
        title="Bulk Import Students"
        columns={[
          { key: 'roll_number', header: 'Roll Number', mandatory: true },
          { key: 'full_name', header: 'Full Name', mandatory: true },
          { key: 'email', header: 'Email' },
          { key: 'phone', header: 'Phone' },
          { key: 'class_name', header: 'Class', mandatory: true },
          { key: 'section', header: 'Section', mandatory: true },
          { key: 'date_of_birth', header: 'Date of Birth' },
          { key: 'admission_date', header: 'Admission Date' },
          { key: 'gender', header: 'Gender' },
          { key: 'student_type', header: 'Student Type' },
          { key: 'blood_group', header: 'Blood Group' },
          { key: 'religion', header: 'Religion' },
          { key: 'address', header: 'Address' },
          { key: 'parent_name', header: 'Parent Name' },
          { key: 'parent_phone', header: 'Parent Phone' },
          { key: 'parent_email', header: 'Parent Email' },
          { key: 'parent_relationship', header: 'Parent Relationship' },
        ]}
        onImport={async (rows) => {
          const cleaned = rows.map(r => Object.fromEntries(Object.entries(r).filter(([, v]) => v !== '')));
          const res = await api.post(ENDPOINTS.students.bulkImport, { students: cleaned });
          queryClient.invalidateQueries({ queryKey: ['students'] });
          return res.data;
        }}
      />

      {/* Pass Out Modal */}
      <Modal open={passOutDialog} onClose={() => setPassOutDialog(false)} title="Graduate / Pass Out Students">
        <div className="space-y-5">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
            <GraduationCap size={20} className="text-amber-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-amber-800">Mark students as passed out</p>
              <p className="text-xs text-amber-600 mt-0.5">This will change their status from Active to Alumni. Select the class to graduate and the passing year.</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Class to Graduate *</label>
              <SearchableSelect
                value={passOutClass}
                onChange={setPassOutClass}
                options={[...new Set(students.filter(s => s.status === 'Active').map(s => s.class_name))].map(c => ({ value: c, label: `Class ${c}` }))}
                placeholder="Select Class..."
              />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Passing Year *</label>
              <input
                type="number"
                value={passOutYear}
                onChange={e => setPassOutYear(e.target.value)}
                min="2020"
                max="2030"
                className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400"
              />
            </div>
          </div>

          {passOutClass && (
            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-sm text-slate-700">
                <span className="font-semibold">{students.filter(s => s.class_name === passOutClass && s.status === 'Active').length}</span> active students in Class {passOutClass} will be marked as <span className="font-semibold text-amber-700">Alumni (Passed Out {passOutYear})</span>
              </p>
            </div>
          )}
        </div>

        {/* Confirmation Step */}
        {confirmGraduate && passOutClass && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mt-4">
            <p className="text-sm font-medium text-red-800">
              This will mark {students.filter(s => s.class_name === passOutClass && s.status === 'Active').length} active students in Class {passOutClass} as Alumni (Passed Out {passOutYear}). This action cannot be undone easily.
            </p>
          </div>
        )}

        <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-slate-100">
          <Button variant="ghost" onClick={() => { setPassOutDialog(false); setConfirmGraduate(false); }}>Cancel</Button>
          {!confirmGraduate ? (
            <Button
              icon={GraduationCap}
              disabled={!passOutClass || !passOutYear}
              onClick={() => setConfirmGraduate(true)}
            >
              Graduate {passOutClass ? `Class ${passOutClass}` : 'Students'}
            </Button>
          ) : (
            <Button
              icon={GraduationCap}
              className="!bg-red-600 hover:!bg-red-700"
              onClick={() => {
                const studentIds = students.filter(s => s.class_name === passOutClass && s.status === 'Active').map(s => s.id);
                if (studentIds.length === 0) return;
                // API call to mark students as passed out
                Promise.all(studentIds.map(id =>
                  import('../../services/api').then(m => m.default.patch(`/admin/students/${id}/`, { status: 'Inactive', pass_out_year: passOutYear }))
                )).then(() => {
                  setPassOutDialog(false);
                  setPassOutClass('');
                  setConfirmGraduate(false);
                  window.location.reload();
                });
              }}
            >
              Confirm
            </Button>
          )}
        </div>
      </Modal>
    </div>
  );
}

const STEPS_CREATE = [
  { id: 'personal', label: 'Personal Details', icon: '1' },
  { id: 'parent', label: 'Parent / Guardian', icon: '2' },
  { id: 'fees', label: 'Fee Structure', icon: '3' },
];

const STEPS_EDIT = [
  { id: 'personal', label: 'Personal Details', icon: '1' },
  { id: 'parent', label: 'Parent / Guardian', icon: '2' },
];

function StudentFormWizard({ register, errors, watch, setValue, trigger, inp, classOptions, allClasses, formStep, setFormStep, onSubmit, onCancel, isSubmitting, isEditing, editingStudent, submitError, onConcessionChange, onCustomFeesChange, onExcludedFeesChange, toast }) {
  const { data: feeData } = useFeeStructures();
  const { data: feeHistory } = useStudentFeeHistory(editingStudent?.id);
  const [concessions, setConcessions] = useState({});
  const [concessionsLoaded, setConcessionsLoaded] = useState(false);
  const [customFees, setCustomFees] = useState([]);
  const [excludedFees, setExcludedFees] = useState([]);
  const [showAddFee, setShowAddFee] = useState(false);
  const [newFeeType, setNewFeeType] = useState('');
  const [newFeeAmount, setNewFeeAmount] = useState('');

  useEffect(() => {
    setConcessionsLoaded(false);
    setConcessions({});
  }, [editingStudent?.id]);

  useEffect(() => {
    if (!isEditing || !feeHistory || !feeData?.structures?.length || concessionsLoaded) return;
    const feeRecords = feeHistory?.fee_structure || [];
    const existing = {};
    feeRecords.forEach((record) => {
      if (record.concession > 0) {
        const matchedFee = feeData.structures.find(fs => fs.fee_type === record.component);
        if (matchedFee) existing[matchedFee.id] = String(record.concession);
      }
    });
    if (Object.keys(existing).length > 0) {
      setConcessions(existing);
      if (onConcessionChange) onConcessionChange(existing);
    }
    setConcessionsLoaded(true);
  }, [isEditing, feeHistory, feeData, concessionsLoaded]);

  const structures = feeData?.structures || [];
  const classSections = feeData?.class_sections || [];
  const selectedClass = watch('class_name');
  const selectedSection = watch('section');
  const matchedClass = allClasses.find(c => c.name === selectedClass);
  const matchedClassSection = classSections.find(cs => cs.class_id === matchedClass?.id && cs.display_name?.endsWith(`- ${selectedSection}`));
  const generalFees = structures.filter(fs => !fs.class_id && !fs.class_section_id);
  const classWideFees = structures.filter(fs => fs.class_id === matchedClass?.id && !fs.class_section_id);
  const sectionFees = matchedClassSection ? structures.filter(fs => fs.class_section_id === matchedClassSection.id) : [];
  const applicableFees = [...generalFees, ...classWideFees, ...sectionFees];
  const displayedFees = applicableFees.filter(f => !excludedFees.includes(f.id));

  const handleConcessionChange = (feeId, value) => {
    const updated = { ...concessions, [feeId]: value };
    setConcessions(updated);
    if (onConcessionChange) onConcessionChange(updated);
  };

  const totalAfterConcession = displayedFees.reduce((sum, f) => {
    const amt = Number(f.amount) || 0;
    const disc = Number(concessions[f.id]) || 0;
    return sum + Math.max(0, amt - disc);
  }, 0);

  const addCustomFee = () => {
    if (!newFeeType.trim() || !newFeeAmount) return;
    const fee = { fee_type: newFeeType.trim(), amount: Number(newFeeAmount), frequency: 'yearly', fee_category: 'other' };
    const updated = [...customFees, fee];
    setCustomFees(updated);
    if (onCustomFeesChange) onCustomFeesChange(updated);
    setNewFeeType(''); setNewFeeAmount(''); setShowAddFee(false);
  };

  const removeCustomFee = (index) => {
    const updated = customFees.filter((_, i) => i !== index);
    setCustomFees(updated);
    if (onCustomFeesChange) onCustomFeesChange(updated);
  };

  const steps = isEditing ? STEPS_EDIT : STEPS_CREATE;

  const handleNext = async () => {
    if (formStep === 0) {
      const valid = await trigger(['roll_number', 'full_name', 'class_name', 'section']);
      if (!valid) return;
    }
    setFormStep(formStep + 1);
  };

  return (
    <div>
      {/* Stepper */}
      <div className="flex items-center justify-between mb-6 px-2">
        {steps.map((step, i) => (
          <div key={step.id} className="flex items-center flex-1">
            <div className="flex items-center gap-2.5">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-200 ${
                i < formStep ? 'bg-emerald-500 text-white' :
                i === formStep ? 'bg-primary-600 text-white shadow-md shadow-primary-200' :
                'bg-slate-100 text-slate-400'
              }`}>
                {i < formStep ? '✓' : step.icon}
              </div>
              <span className={`text-xs font-medium hidden sm:inline ${i === formStep ? 'text-primary-700' : i < formStep ? 'text-emerald-600' : 'text-slate-400'}`}>{step.label}</span>
            </div>
            {i < steps.length - 1 && <div className={`flex-1 h-0.5 mx-3 rounded ${i < formStep ? 'bg-emerald-300' : 'bg-slate-200'}`} />}
          </div>
        ))}
      </div>

      <div>
        {/* Step 1: Personal Details */}
        {formStep === 0 && (
          <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 pb-4">
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Roll Number *</label><input {...register('roll_number')} className={inp(errors.roll_number)} />{errors.roll_number && <p className="text-xs text-red-500 mt-0.5">{errors.roll_number.message}</p>}</div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Full Name *</label><input {...register('full_name')} className={inp(errors.full_name)} />{errors.full_name && <p className="text-xs text-red-500 mt-0.5">{errors.full_name.message}</p>}</div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Email</label><input {...register('email')} className={inp(errors.email)} />{errors.email && <p className="text-xs text-red-500 mt-0.5">{errors.email.message}</p>}</div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Phone</label><input {...register('phone')} maxLength={10} placeholder="9876543210" className={inp(errors.phone)} />{errors.phone && <p className="text-xs text-red-500 mt-0.5">{errors.phone.message}</p>}</div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Class *</label><SearchableSelect value={watch('class_name')} onChange={(val) => { setValue('class_name', val, { shouldValidate: true }); setValue('section', ''); }} options={classOptions.filter(o => o.value)} placeholder="Select Class..." />{errors.class_name && <p className="text-xs text-red-500 mt-0.5">{errors.class_name.message}</p>}</div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Section *</label><SearchableSelect value={watch('section')} onChange={(val) => setValue('section', val, { shouldValidate: true })} options={(() => { const cls = allClasses.find(c => c.name === watch('class_name')); return cls?.sections?.length ? cls.sections.map(s => ({ value: s.section_name, label: s.section_name })) : []; })()} placeholder="Select Section..." />{errors.section && <p className="text-xs text-red-500 mt-0.5">{errors.section.message}</p>}</div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Date of Birth</label><DatePicker value={watch('date_of_birth')} onChange={(v) => setValue('date_of_birth', v, { shouldDirty: true })} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Admission Date</label><DatePicker value={watch('admission_date')} onChange={(v) => setValue('admission_date', v, { shouldDirty: true })} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Gender</label><SearchableSelect value={watch('gender')} onChange={(val) => setValue('gender', val)} options={[{ value: '', label: 'Select' }, ...GENDER_OPTIONS]} placeholder="Select..." /></div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Student Type</label><SearchableSelect value={watch('student_type')} onChange={(val) => setValue('student_type', val)} options={[{ value: '', label: 'Select' }, { value: 'Day Scholar', label: 'Day Scholar' }, { value: 'Hosteller', label: 'Hosteller' }]} placeholder="Select..." /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Blood Group</label><SearchableSelect value={watch('blood_group')} onChange={(val) => setValue('blood_group', val)} options={['A+','A-','B+','B-','O+','O-','AB+','AB-'].map(b => ({ value: b, label: b }))} placeholder="Select..." /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Religion</label><input {...register('religion')} className={inp()} /></div>
            </div>
            <div><label className="text-xs font-medium text-slate-600 mb-1 block">Address</label><input {...register('address')} className={inp()} placeholder="Full address..." /></div>
          </div>
        )}

        {/* Step 2: Parent Details */}
        {formStep === 1 && (
          <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 pb-4">
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mb-2">
              <p className="text-xs text-slate-500">Enter the parent or guardian details for this student. This information will be used for communication and emergency contacts.</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Parent/Guardian Name</label><input {...register('parent_name')} className={inp()} placeholder="Full name" /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Relationship</label><SearchableSelect value={watch('parent_relationship')} onChange={(val) => setValue('parent_relationship', val)} options={[{ value: 'Father', label: 'Father' }, { value: 'Mother', label: 'Mother' }, { value: 'Guardian', label: 'Guardian' }, { value: 'Parent/Guardian', label: 'Parent/Guardian' }]} placeholder="Select..." /></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Phone</label><input {...register('parent_phone')} maxLength={10} placeholder="9876543210" className={inp(errors.parent_phone)} />{errors.parent_phone && <p className="text-xs text-red-500 mt-0.5">{errors.parent_phone.message}</p>}</div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Email</label><input {...register('parent_email')} className={inp(errors.parent_email)} placeholder="parent@email.com" />{errors.parent_email && <p className="text-xs text-red-500 mt-0.5">{errors.parent_email.message}</p>}</div>
            </div>
          </div>
        )}

        {/* Step 3: Fee Structure (only for new students) */}
        {!isEditing && formStep === 2 && (
          <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 pb-4">
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-100 mb-2">
              <p className="text-xs text-blue-700">The following fees will be applicable based on the selected class. This is for your reference — fees are auto-assigned on enrollment.</p>
            </div>
            {isEditing && (
              <div className="bg-amber-50 rounded-xl p-4 border border-amber-200 mb-2">
                <p className="text-xs text-amber-700 font-medium">Existing concessions are preserved. Modify fee concessions from the student details page.</p>
              </div>
            )}
            {displayedFees.length > 0 ? (
              <div className="rounded-xl border border-slate-200 overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200">
                      <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase">Fee Type</th>
                      <th className="text-left px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase">Frequency</th>
                      <th className="text-right px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase">Amount</th>
                      <th className="text-right px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase">Concession</th>
                      <th className="text-right px-4 py-2.5 text-xs font-semibold text-slate-500 uppercase">Net Amount</th>
                      <th className="text-center px-2 py-2.5 text-xs font-semibold text-slate-500 uppercase w-10"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {displayedFees.map((f, i) => {
                      const amt = Number(f.amount) || 0;
                      const disc = Number(concessions[f.id]) || 0;
                      const net = Math.max(0, amt - disc);
                      return (
                        <tr key={f.id || i} className="hover:bg-slate-50/50">
                          <td className="px-4 py-3">
                            <p className="font-medium text-slate-800">{f.fee_type}</p>
                            <p className="text-[11px] text-slate-400 capitalize">{f.fee_category}</p>
                          </td>
                          <td className="px-4 py-3 text-slate-500 capitalize">{f.frequency}</td>
                          <td className="px-4 py-3 text-right font-medium text-slate-700">₹{amt.toLocaleString()}</td>
                          <td className="px-4 py-3 text-right">
                            <input
                              type="number"
                              min="0"
                              max={amt}
                              value={concessions[f.id] || ''}
                              onChange={(e) => handleConcessionChange(f.id, e.target.value)}
                              placeholder="0"
                              className="w-24 text-right border border-slate-200 rounded-lg px-2.5 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent hover:border-slate-300 transition-colors"
                            />
                          </td>
                          <td className="px-4 py-3 text-right font-bold text-emerald-700">₹{net.toLocaleString()}</td>
                          <td className="px-2 py-3 text-center">
                            <button type="button" onClick={() => { const updated = [...excludedFees, f.id]; setExcludedFees(updated); if (onExcludedFeesChange) onExcludedFeesChange(updated); }} className="p-1 hover:bg-red-50 rounded text-red-400 hover:text-red-600 transition-colors" title="Remove fee"><Trash2 className="w-4 h-4" /></button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                  <tfoot>
                    <tr className="bg-emerald-50 border-t border-emerald-200">
                      <td colSpan={2} className="px-4 py-3 text-sm font-semibold text-slate-700">Total</td>
                      <td className="px-4 py-3 text-right text-sm font-semibold text-slate-500">₹{displayedFees.reduce((s, f) => s + Number(f.amount), 0).toLocaleString()}</td>
                      <td className="px-4 py-3 text-right text-sm font-semibold text-red-500">-₹{Object.entries(concessions).filter(([id]) => displayedFees.some(f => f.id === id)).reduce((s, [, v]) => s + (Number(v) || 0), 0).toLocaleString()}</td>
                      <td className="px-4 py-3 text-right text-base font-bold text-emerald-700">₹{totalAfterConcession.toLocaleString()}</td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400">
                <p className="text-sm">{selectedClass ? 'No fee structure configured for this class' : 'Select a class in Step 1 to see applicable fees'}</p>
              </div>
            )}

            {/* Custom Fees for this student */}
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-semibold text-slate-700">Custom Fee Components</h4>
                <button type="button" onClick={() => setShowAddFee(!showAddFee)} className="text-xs text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1">
                  <Plus className="w-3.5 h-3.5" /> Add Fee Component
                </button>
              </div>
              {showAddFee && (
                <div className="flex items-end gap-2 mb-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div className="flex-1">
                    <label className="text-xs font-medium text-slate-600 mb-1 block">Fee Type</label>
                    <input value={newFeeType} onChange={(e) => setNewFeeType(e.target.value)} placeholder="e.g. Lab Fee" className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                  </div>
                  <div className="w-32">
                    <label className="text-xs font-medium text-slate-600 mb-1 block">Amount (₹)</label>
                    <input type="number" value={newFeeAmount} onChange={(e) => setNewFeeAmount(e.target.value)} placeholder="0" className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                  </div>
                  <button type="button" onClick={addCustomFee} disabled={!newFeeType.trim() || !newFeeAmount} className="px-3 py-1.5 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed">Add</button>
                </div>
              )}
              {customFees.length > 0 && (
                <div className="rounded-lg border border-slate-200 overflow-hidden">
                  <table className="w-full text-sm">
                    <tbody className="divide-y divide-slate-100">
                      {customFees.map((f, i) => (
                        <tr key={i} className="hover:bg-slate-50/50">
                          <td className="px-4 py-2.5 font-medium text-slate-800">{f.fee_type}</td>
                          <td className="px-4 py-2.5 text-slate-500 capitalize">{f.frequency}</td>
                          <td className="px-4 py-2.5 text-right font-medium text-slate-700">₹{Number(f.amount).toLocaleString()}</td>
                          <td className="px-4 py-2.5 text-right w-10">
                            <button type="button" onClick={() => removeCustomFee(i)} className="p-1 hover:bg-red-50 rounded text-red-500 hover:text-red-700"><Trash2 className="w-4 h-4" /></button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Error */}
        {submitError && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg mt-3">{submitError}</p>}

        {/* Navigation */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-100">
          <Button variant="ghost" onClick={onCancel}>Cancel</Button>
          <div className="flex items-center gap-2">
            {formStep > 0 && (
              <Button variant="secondary" onClick={() => setFormStep(formStep - 1)}>← Previous</Button>
            )}
            {formStep < steps.length - 1 ? (
              <Button type="button" variant="primary" onClick={handleNext}>Next →</Button>
            ) : (
              <Button variant="primary" onClick={async () => { const valid = await trigger(); if (!valid) { toast.error('Please fill all required fields in previous sections'); return; } onSubmit(); }} disabled={isSubmitting}>
                {isSubmitting ? 'Saving...' : isEditing ? 'Update Student' : 'Add Student'}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
