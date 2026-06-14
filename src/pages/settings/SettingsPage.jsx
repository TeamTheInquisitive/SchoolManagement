import { useState, useRef } from 'react';
import { Building2, Calendar, BookOpen, Layers, Save, Plus, School, Pencil, Trash2, IndianRupee, Upload, Image, CalendarCheck, ChevronDown, ChevronRight, Award, ClipboardCheck, Clock } from 'lucide-react';
import { Button, Badge, Modal, Skeleton, Tabs, DateInput, DateRangePicker, useToast, Breadcrumb, SearchableSelect, ConfirmDialog } from 'school-erp-ui-shared';
import { useTabState } from '../../hooks/useTabState';
import { useSchoolProfile, useAcademicYear, useAcademicYears, useCreateAcademicYear, useUpdateAcademicYearById, useDeleteAcademicYear, useSetCurrentAcademicYear, useClassSections, useSubjects, useUpdateSchoolProfile, useUpdateAcademicYear, useCreateClasses, useCreateSections, useDeleteClass, useDeleteClassSection, useCreateSubjects, useUpdateSubject, useDeleteSubject, useClassSubjects, useUpdateClassSubjects, useFeeStructures, useCreateFeeStructure, useUpdateFeeStructure, useDeleteFeeStructure, useUploadLogo, useIdGenerationConfig, useUpdateIdGenerationConfig, useHolidays, useUpdateHolidays, useAttendanceConfig, useUpdateAttendanceConfig, useClassSectionAssignments, useUpdateClassSectionAssignment } from '../../services/settingsService';
import { useTeachers, useAssignClass } from '../../services/teacherService';
import { useLeavePolicy, useUpdateLeavePolicy } from '../../services/leaveService';
import { useSlotTypes, useUpdateSlotTypes } from '../../services/timetableService';
import { useStaff } from '../../services/staffService';
import { useGradeSystem, useUpdateGradeSystem } from '../../services/examinationService';
import { DEPARTMENTS } from '../../constants.jsx';
import { API_BASE_URL } from '../../config/api';

export default function SettingsPage() {
  const tabs = [
    { id: 'school-profile', label: 'School Profile', icon: Building2 },
    { id: 'academic-year', label: 'Academic Year', icon: Calendar },
    { id: 'academic-structure', label: 'Academic Structure', icon: Layers },
    { id: 'teacher-mapping', label: 'Subject & Teacher Mapping', icon: BookOpen },
    { id: 'timetable', label: 'Timetable', icon: Clock },
    { id: 'grades', label: 'Grades', icon: Award },
    { id: 'fee-structure', label: 'Fee Structure', icon: IndianRupee },
    { id: 'leave-holidays', label: 'Leave & Holidays', icon: CalendarCheck },
    { id: 'attendance', label: 'Attendance', icon: ClipboardCheck },
  ];

  const [tab, setTab] = useTabState(tabs);

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Settings' }]} />
      <div className="mb-6">
        <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">Manage school configuration, academic year, and other settings</p>
      </div>

      <Tabs tabs={tabs} active={tab} onChange={setTab} className="mb-6" />

      {tab === 0 && <SchoolProfileTab />}
      {tab === 1 && <AcademicYearTab />}
      {tab === 2 && <><SubjectsTab /><div className="mt-6"><ClassSectionsTab /></div></>}
      {tab === 3 && <ClassSubjectMappingTab />}
      {tab === 4 && <TimetableSettingsTab />}
      {tab === 5 && <GradesTab />}
      {tab === 6 && <FeeStructureTab />}
      {tab === 7 && <><LeavePolicyTab /><div className="mt-6"><HolidaysTab /></div></>}
      {tab === 8 && <AttendanceModeTab />}
    </div>
  );
}

function SchoolProfileTab() {
  const toast = useToast();
  const { data: profile, isLoading } = useSchoolProfile();
  const updateMutation = useUpdateSchoolProfile();
  const uploadLogoMutation = useUploadLogo();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState(null);
  const [formErrors, setFormErrors] = useState({});
  const [logoPreview, setLogoPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const startEdit = () => {
    setForm({
      school_name: profile?.school_name || '',
      address: profile?.address || '',
      city: profile?.city || '',
      state: profile?.state || '',
      pin_code: profile?.pin_code || '',
      phone: profile?.phone || '',
      email: profile?.email || '',
      website: profile?.website || '',
      principal_name: profile?.principal_name || '',
      established_year: profile?.established_year || '',
      board: profile?.board || '',
      working_hours: profile?.working_hours || '',
      motto: profile?.motto || '',
    });
    setEditing(true);
  };

  const handleSave = () => {
    const newErrors = {};
    if (!form.school_name?.trim()) newErrors.school_name = 'School name is required';
    if (!form.principal_name?.trim()) newErrors.principal_name = 'Principal name is required';
    if (!form.board?.trim()) newErrors.board = 'Board affiliation is required';
    if (!form.established_year) newErrors.established_year = 'Established year is required';
    if (!form.phone?.trim()) newErrors.phone = 'Phone is required';
    else if (!/^[6-9]\d{9}$/.test(form.phone)) newErrors.phone = 'Phone must be 10 digits starting with 6-9';
    if (!form.email?.trim()) newErrors.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) newErrors.email = 'Invalid email format';
    if (!form.address?.trim()) newErrors.address = 'Address is required';
    if (!form.pin_code?.trim()) newErrors.pin_code = 'Pincode is required';
    else if (!/^\d{6}$/.test(form.pin_code)) newErrors.pin_code = 'Pincode must be 6 digits';
    if (!form.city?.trim()) newErrors.city = 'City is required';
    if (!form.state?.trim()) newErrors.state = 'State is required';
    if (Object.keys(newErrors).length > 0) { setFormErrors(newErrors); return; }
    setFormErrors({});
    updateMutation.mutate(form, { onSuccess: () => { setEditing(false); toast.success('Profile updated successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to update profile'); } });
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Invalid file type. Allowed: PNG, JPG, JPEG, WebP');
      return;
    }

    // Validate file size (2MB)
    if (file.size > 2 * 1024 * 1024) {
      toast.error('File too large. Maximum size is 2MB');
      return;
    }

    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = (ev) => setLogoPreview(ev.target.result);
    reader.readAsDataURL(file);
  };

  const handleUploadLogo = () => {
    if (!selectedFile) return;
    uploadLogoMutation.mutate(selectedFile, {
      onSuccess: () => {
        toast.success('Logo uploaded successfully');
        setSelectedFile(null);
        setLogoPreview(null);
      },
      onError: (err) => {
        toast.error(err.response?.data?.detail || 'Failed to upload logo');
      },
    });
  };

  const getLogoUrl = () => {
    if (profile?.logo_url) {
      // If it starts with http, use as-is; otherwise prepend API base URL
      if (profile.logo_url.startsWith('http')) return profile.logo_url;
      // Remove /api/v1 suffix from base URL to get server origin
      const baseOrigin = API_BASE_URL.replace(/\/api\/v1\/?$/, '');
      return `${baseOrigin}${profile.logo_url}`;
    }
    return null;
  };

  if (isLoading) return <div className="space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}</div>;

  const currentLogoUrl = getLogoUrl();

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center overflow-hidden">
            {currentLogoUrl ? (
              <img src={currentLogoUrl} alt="School Logo" className="w-full h-full object-cover" />
            ) : (
              <School size={28} className="text-primary-600" />
            )}
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">{profile?.school_name || 'School Name'}</h2>
            <p className="text-sm text-slate-500">Code: {profile?.school_code || '—'}</p>
          </div>
        </div>
        {!editing && <Button variant="secondary" size="sm" onClick={startEdit}>Edit Profile</Button>}
      </div>

      {/* Logo Upload Section */}
      <div className="mb-6 p-4 bg-slate-50 rounded-xl border border-slate-100">
        <h3 className="text-sm font-semibold text-slate-700 mb-3">School Logo</h3>
        <div className="flex items-center gap-4">
          <div className="w-20 h-20 rounded-xl border-2 border-dashed border-slate-300 flex items-center justify-center overflow-hidden bg-white">
            {logoPreview ? (
              <img src={logoPreview} alt="Preview" className="w-full h-full object-cover" />
            ) : currentLogoUrl ? (
              <img src={currentLogoUrl} alt="Current Logo" className="w-full h-full object-cover" />
            ) : (
              <Image size={24} className="text-slate-300" />
            )}
          </div>
          <div className="flex flex-col gap-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept="image/png,image/jpeg,image/jpg,image/webp"
              className="hidden"
            />
            <Button
              variant="secondary"
              size="sm"
              icon={Upload}
              onClick={() => fileInputRef.current?.click()}
            >
              {currentLogoUrl ? 'Change Logo' : 'Upload Logo'}
            </Button>
            {selectedFile && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">{selectedFile.name}</span>
                <Button size="sm" onClick={handleUploadLogo} loading={uploadLogoMutation.isPending}>
                  Save Logo
                </Button>
              </div>
            )}
            <p className="text-[11px] text-slate-400">PNG, JPG, or WebP. Max 2MB.</p>
          </div>
        </div>
      </div>

      {!editing ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <InfoField label="Principal" value={profile?.principal_name} />
          <InfoField label="Board" value={profile?.board} />
          <InfoField label="Established" value={profile?.established_year} />
          <InfoField label="Phone" value={profile?.phone} />
          <InfoField label="Email" value={profile?.email} />
          <InfoField label="Website" value={profile?.website} />
          <InfoField label="Address" value={profile?.address} />
          <InfoField label="City" value={profile?.city} />
          <InfoField label="State / Pin" value={[profile?.state, profile?.pin_code].filter(Boolean).join(' - ')} />
          <InfoField label="Working Hours" value={profile?.working_hours} />
          <InfoField label="Motto / Tagline" value={profile?.motto} />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField label="School Name *" value={form.school_name} onChange={v => { setForm({ ...form, school_name: v }); setFormErrors(e => ({ ...e, school_name: undefined })); }} error={formErrors.school_name} />
            <FormField label="Principal Name *" value={form.principal_name} onChange={v => { setForm({ ...form, principal_name: v }); setFormErrors(e => ({ ...e, principal_name: undefined })); }} error={formErrors.principal_name} />
            <FormField label="Board *" value={form.board} onChange={v => { setForm({ ...form, board: v }); setFormErrors(e => ({ ...e, board: undefined })); }} error={formErrors.board} />
            <FormField label="Established Year *" value={form.established_year} onChange={v => { setForm({ ...form, established_year: v }); setFormErrors(e => ({ ...e, established_year: undefined })); }} type="number" error={formErrors.established_year} />
            <FormField label="Phone" value={form.phone} onChange={v => { setForm({ ...form, phone: v }); setFormErrors(e => ({ ...e, phone: undefined })); }} error={formErrors.phone} />
            <FormField label="Email" value={form.email} onChange={v => { setForm({ ...form, email: v }); setFormErrors(e => ({ ...e, email: undefined })); }} type="email" error={formErrors.email} />
            <FormField label="Website" value={form.website} onChange={v => setForm({ ...form, website: v })} />
            <FormField label="Address *" value={form.address} onChange={v => { setForm({ ...form, address: v }); setFormErrors(e => ({ ...e, address: undefined })); }} error={formErrors.address} />
            <FormField label="City *" value={form.city} onChange={v => { setForm({ ...form, city: v }); setFormErrors(e => ({ ...e, city: undefined })); }} error={formErrors.city} />
            <FormField label="State *" value={form.state} onChange={v => { setForm({ ...form, state: v }); setFormErrors(e => ({ ...e, state: undefined })); }} error={formErrors.state} />
            <FormField label="Pin Code" value={form.pin_code} onChange={v => { setForm({ ...form, pin_code: v }); setFormErrors(e => ({ ...e, pin_code: undefined })); }} error={formErrors.pin_code} />
            <FormField label="Working Hours" value={form.working_hours} onChange={v => setForm({ ...form, working_hours: v })} placeholder="e.g., 8:00 AM - 3:30 PM" />
            <FormField label="Motto / Tagline" value={form.motto} onChange={v => setForm({ ...form, motto: v })} placeholder="e.g., Knowledge is Power" />
          </div>
          <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
            <Button variant="ghost" onClick={() => setEditing(false)}>Cancel</Button>
            <Button icon={Save} onClick={handleSave} loading={updateMutation.isPending}>Save Changes</Button>
          </div>
        </div>
      )}
      <IdGenerationSection />
    </div>
  );
}

function IdGenerationSection() {
  const toast = useToast();
  const { data: config, isLoading } = useIdGenerationConfig();
  const updateMutation = useUpdateIdGenerationConfig();
  const [form, setForm] = useState(null);

  if (isLoading) return null;

  const entities = [
    { key: 'student', label: 'Student' },
    { key: 'teacher', label: 'Teacher' },
    { key: 'staff', label: 'Staff' },
  ];

  const currentConfig = form || config || {};

  const handleToggle = (key) => {
    const updated = { ...currentConfig, [key]: { ...currentConfig[key], enabled: !currentConfig[key]?.enabled } };
    setForm(updated);
  };

  const handlePattern = (key, pattern) => {
    const updated = { ...currentConfig, [key]: { ...currentConfig[key], pattern } };
    setForm(updated);
  };

  const handleSave = () => {
    const payload = {};
    entities.forEach(({ key }) => {
      payload[key] = { enabled: !!currentConfig[key]?.enabled, pattern: currentConfig[key]?.pattern || '', next_seq: currentConfig[key]?.next_seq || 1 };
    });
    updateMutation.mutate(payload, {
      onSuccess: () => { setForm(null); toast.success('ID generation settings saved'); },
      onError: (err) => toast.error(err.response?.data?.detail || 'Failed to save'),
    });
  };

  const getPreview = (cfg) => {
    if (!cfg?.pattern) return '—';
    const year = new Date().getFullYear().toString().slice(-2);
    let preview = cfg.pattern.replace('{YY}', year).replace('{YEAR}', year);
    const match = preview.match(/\{SEQ(?::(\d+))?\}/);
    if (match) {
      const pad = match[1] ? parseInt(match[1]) : 1;
      preview = preview.replace(match[0], String(cfg.next_seq || 1).padStart(pad, '0'));
    }
    return preview;
  };

  const isDirty = form !== null;

  return (
    <div className="mt-6 bg-white border border-slate-200 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-slate-900">ID Auto-Generation</h3>
          <p className="text-xs text-slate-500 mt-0.5">Configure automatic ID patterns for students, teachers, and staff</p>
        </div>
        {isDirty && <Button size="sm" icon={Save} onClick={handleSave} loading={updateMutation.isPending}>Save</Button>}
      </div>
      <div className="space-y-3">
        {entities.map(({ key, label }) => {
          const cfg = currentConfig[key] || {};
          return (
            <div key={key} className="flex items-center gap-4 p-3 bg-slate-50 rounded-lg border border-slate-100">
              <div className="w-20 text-sm font-medium text-slate-700">{label}</div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked={cfg.enabled || false} onChange={() => handleToggle(key)} className="sr-only peer" />
                <div className="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
              <input
                type="text"
                value={cfg.pattern || ''}
                onChange={(e) => handlePattern(key, e.target.value)}
                placeholder="e.g. STU{YY}{SEQ:4}"
                className="flex-1 text-sm border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <div className="text-xs text-slate-500 min-w-[120px]">
                Preview: <span className="font-mono text-slate-700">{getPreview(cfg)}</span>
              </div>
            </div>
          );
        })}
      </div>
      <p className="text-[11px] text-slate-400 mt-3">Tokens: <code className="bg-slate-100 px-1 rounded">{'{YY}'}</code> = last 2 digits of current year (26 for 2026, 27 for 2027), <code className="bg-slate-100 px-1 rounded">{'{SEQ:4}'}</code> = zero-padded sequence number. Example: STU{'{YY}'}{'{SEQ:4}'} → STU260001</p>
    </div>
  );
}

function AcademicYearTab() {
  const toast = useToast();
  const { data, isLoading } = useAcademicYear();
  const { data: allYears, isLoading: yearsLoading } = useAcademicYears();
  const createMutation = useCreateAcademicYear();
  const updateMutation = useUpdateAcademicYearById();
  const deleteMutation = useDeleteAcademicYear();
  const setCurrentMutation = useSetCurrentAcademicYear();
  const [showCreate, setShowCreate] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [deleteYearId, setDeleteYearId] = useState(null);
  const [form, setForm] = useState({ name: '', start_date: '', end_date: '' });

  if (isLoading || yearsLoading) return <div className="space-y-4">{[1, 2].map(i => <Skeleton key={i} className="h-20 w-full" />)}</div>;

  const years = allYears?.academic_years || [];

  const handleCreate = () => {
    createMutation.mutate({ ...form, is_current: years.length === 0 }, {
      onSuccess: () => { setShowCreate(false); setForm({ name: '', start_date: '', end_date: '' }); toast.success('Academic year created'); },
      onError: (err) => { toast.error(err.response?.data?.error || 'Failed to create'); },
    });
  };

  const handleUpdate = () => {
    updateMutation.mutate({ id: editingId, ...form }, {
      onSuccess: () => { setEditingId(null); toast.success('Academic year updated'); },
      onError: (err) => { toast.error(err.response?.data?.error || 'Failed to update'); },
    });
  };

  const confirmDeleteYear = () => {
    if (!deleteYearId) return;
    deleteMutation.mutate(deleteYearId, {
      onSuccess: () => { setDeleteYearId(null); toast.success('Academic year deleted'); },
      onError: (err) => { setDeleteYearId(null); toast.error(err.response?.data?.error || 'Failed to delete'); },
    });
  };

  const handleSetCurrent = (id) => {
    setCurrentMutation.mutate(id, {
      onSuccess: () => { toast.success('Current academic year updated'); },
      onError: (err) => { toast.error(err.response?.data?.error || 'Failed to update'); },
    });
  };

  const startEdit = (year) => {
    setForm({ name: year.name, start_date: year.start_date, end_date: year.end_date });
    setEditingId(year.id);
  };

  return (
    <div className="space-y-6">
      {/* Current Year Selection */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h3 className="text-base font-semibold text-slate-900 mb-4">Current Academic Year</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div className="md:col-span-2">
            <label className="text-xs text-slate-500 mb-1.5 block">Select Academic Year</label>
            <SearchableSelect
              value={years.find(y => y.is_current)?.id || ''}
              onChange={(id) => { if (id) handleSetCurrent(id); }}
              options={years.map(y => ({ value: y.id, label: `${y.name} (${y.start_date} → ${y.end_date})` }))}
              placeholder="Select academic year..."
            />
          </div>
          <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 text-center">
            <p className="text-xs text-slate-500">Start Date</p>
            <p className="text-lg font-bold text-emerald-700">{data?.start_date || '—'}</p>
          </div>
          <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 text-center">
            <p className="text-xs text-slate-500">End Date</p>
            <p className="text-lg font-bold text-amber-700">{data?.end_date || '—'}</p>
          </div>
        </div>
      </div>

      {/* All Academic Years */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-slate-900">All Academic Years</h3>
          <Button variant="secondary" size="sm" icon={Plus} onClick={() => { setForm({ name: '', start_date: '', end_date: '' }); setShowCreate(true); }}>Add Year</Button>
        </div>
        {years.length > 0 ? (
          <div className="space-y-2">
            {years.map((year) => (
              <div key={year.id} className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-100">
                {editingId === year.id ? (
                  <div className="flex items-center gap-3 flex-1">
                    <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="border border-slate-300 rounded-lg px-2 py-1.5 text-sm w-28" />
                    <DateRangePicker
                      startValue={form.start_date}
                      endValue={form.end_date}
                      onChange={(start, end) => setForm({ ...form, start_date: start, end_date: end })}
                    />
                    <Button size="sm" onClick={handleUpdate} loading={updateMutation.isPending}>Save</Button>
                    <Button size="sm" variant="ghost" onClick={() => setEditingId(null)}>Cancel</Button>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center gap-3">
                      <p className="text-sm font-semibold text-slate-900">{year.name}</p>
                      {year.is_current && <Badge variant="success">Current</Badge>}
                      <p className="text-xs text-slate-500">{year.start_date} → {year.end_date}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {!year.is_current && (
                        <button onClick={() => handleSetCurrent(year.id)} className="text-xs text-primary-600 hover:text-primary-800 font-medium">Set Current</button>
                      )}
                      <button onClick={() => startEdit(year)} className="p-1.5 rounded-lg text-slate-400 hover:text-primary-600 hover:bg-primary-50 transition-colors" title="Edit">
                        <Pencil size={14} />
                      </button>
                      {!year.is_current && (
                        <button onClick={() => setDeleteYearId(year.id)} className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors" title="Delete">
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400 text-center py-6">No academic years configured. Create one to get started.</p>
        )}
      </div>

      {/* Create Modal */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Create Academic Year" size="lg">
        <div className="space-y-3">
          <FormField label="Name *" value={form.name} onChange={v => setForm({ ...form, name: v })} placeholder="2025-2026" />
          <DateRangePicker
            label="Academic Year Duration *"
            startValue={form.start_date}
            endValue={form.end_date}
            onChange={(start, end) => setForm({ ...form, start_date: start, end_date: end })}
          />
        </div>
        <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
          <Button variant="ghost" onClick={() => setShowCreate(false)}>Cancel</Button>
          <Button onClick={handleCreate} loading={createMutation.isPending} disabled={!form.name || !form.start_date || !form.end_date}>Create</Button>
        </div>
      </Modal>

      <ConfirmDialog open={!!deleteYearId} onClose={() => setDeleteYearId(null)} onConfirm={confirmDeleteYear} loading={deleteMutation.isPending} title="Delete Academic Year" message="Are you sure you want to delete this academic year? This action cannot be undone." />
    </div>
  );
}

function ClassSectionsTab() {
  const toast = useToast();
  const { data, isLoading } = useClassSections();
  const { data: teachersData } = useTeachers();
  const assignClass = useAssignClass();
  const createClasses = useCreateClasses();
  const createSections = useCreateSections();
  const deleteClassMutation = useDeleteClass();
  const deleteClassSectionMutation = useDeleteClassSection();
  const [showAddClass, setShowAddClass] = useState(false);
  const [addSectionForClass, setAddSectionForClass] = useState(null);
  const [newClasses, setNewClasses] = useState('');
  const [newSections, setNewSections] = useState('');
  const [deleteClassTarget, setDeleteClassTarget] = useState(null);
  const [deleteSectionTarget, setDeleteSectionTarget] = useState(null);

  if (isLoading) return <div className="space-y-4">{[1, 2].map(i => <Skeleton key={i} className="h-16 w-full" />)}</div>;

  const classes = data?.classes || [];
  const teachers = (teachersData?.results || teachersData) ?? [];

  // Build a map of section key -> current class teacher id
  const classTeacherMap = {};
  const assignedTeacherIds = new Set();
  teachers.forEach(t => {
    (t.class_assignments || []).forEach(a => {
      if (a.is_class_teacher) {
        classTeacherMap[`${a.class_name}-${a.section}`] = t.id;
        assignedTeacherIds.add(t.id);
      }
    });
  });

  const getTeacherOptions = (currentTeacherId) => {
    return teachers
      .filter(t => t.status === 'Active' && t.department === 'Teaching' && (!assignedTeacherIds.has(t.id) || t.id === currentTeacherId))
      .map(t => ({ value: t.id, label: t.user?.full_name || t.employee_id }));
  };

  const handleAssignClassTeacher = (teacherId, className, sectionName) => {
    if (!teacherId) return;
    assignClass.mutate({ id: teacherId, data: { class_name: className, section: sectionName, subject: '', is_class_teacher: true } }, {
      onSuccess: () => toast.success('Class teacher assigned'),
      onError: (err) => toast.error(err.response?.data?.detail || 'Failed to assign class teacher'),
    });
  };

  const handleAddClasses = () => {
    const items = newClasses.split(',').map(s => s.trim()).filter(Boolean);
    if (items.length) createClasses.mutate(items, { onSuccess: () => { setShowAddClass(false); setNewClasses(''); toast.success('Classes added successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to add classes'); } });
  };

  const handleAddSections = () => {
    const items = newSections.split(',').map(s => s.trim()).filter(Boolean);
    if (items.length) createSections.mutate({ sections: items, class_id: addSectionForClass.id }, { onSuccess: () => { setAddSectionForClass(null); setNewSections(''); toast.success('Sections added successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to add sections'); } });
  };

  const confirmDeleteClass = () => {
    if (!deleteClassTarget) return;
    deleteClassMutation.mutate(deleteClassTarget.id, {
      onSuccess: () => { setDeleteClassTarget(null); toast.success('Class deleted successfully'); },
      onError: (err) => { setDeleteClassTarget(null); toast.error(err.response?.data?.detail || 'Failed to delete class'); },
    });
  };

  const confirmDeleteSection = () => {
    if (!deleteSectionTarget) return;
    deleteClassSectionMutation.mutate(deleteSectionTarget.id, {
      onSuccess: () => { setDeleteSectionTarget(null); toast.success('Section removed successfully'); },
      onError: (err) => { setDeleteSectionTarget(null); toast.error(err.response?.data?.detail || 'Failed to remove section'); },
    });
  };

  const totalSections = classes.reduce((s, c) => s + (c.sections?.length || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header with stats and action */}
      <div className="bg-white border border-slate-200 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Classes & Sections</h3>
            <p className="text-xs text-slate-500 mt-0.5">Organize your school's academic structure</p>
          </div>
          <Button variant="primary" size="sm" icon={Plus} onClick={() => setShowAddClass(true)}>Add Classes</Button>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-blue-700">{classes.length}</p>
            <p className="text-[10px] text-blue-600 font-medium">Classes</p>
          </div>
          <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-emerald-700">{totalSections}</p>
            <p className="text-[10px] text-emerald-600 font-medium">Sections</p>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 text-center">
            <p className="text-xl font-bold text-purple-700">{classes.filter(c => c.sections?.length > 1).length}</p>
            <p className="text-[10px] text-purple-600 font-medium">Multi-Section</p>
          </div>
        </div>
      </div>

      {/* Class cards */}
      {classes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {classes.map((cls) => (
            <ClassCard key={cls.id} cls={cls} onAddSection={() => setAddSectionForClass(cls)} onDeleteClass={() => setDeleteClassTarget(cls)} onDeleteSection={(sec) => setDeleteSectionTarget(sec)} />
          ))}
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
          <p className="text-sm text-slate-400">No classes configured yet. Add classes to get started.</p>
        </div>
      )}

      {/* Add Classes Modal */}
      <Modal open={showAddClass} onClose={() => setShowAddClass(false)} title="Add Classes" size="sm">
        <div className="space-y-3">
          <p className="text-sm text-slate-500">Enter class names separated by commas</p>
          <FormField label="Classes" value={newClasses} onChange={setNewClasses} placeholder="LKG, UKG, 1, 2, 3" />
        </div>
        <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
          <Button variant="ghost" onClick={() => setShowAddClass(false)}>Cancel</Button>
          <Button onClick={handleAddClasses} loading={createClasses.isPending} disabled={!newClasses.trim()}>Add Classes</Button>
        </div>
      </Modal>

      {/* Add Sections Modal (per class) */}
      <Modal open={!!addSectionForClass} onClose={() => setAddSectionForClass(null)} title={`Add Sections to ${addSectionForClass?.display_name || ''}`} size="sm">
        <div className="space-y-3">
          <p className="text-sm text-slate-500">Enter section names separated by commas (e.g., A, B, C, D)</p>
          <FormField label="Sections" value={newSections} onChange={setNewSections} placeholder="A, B, C, D" />
        </div>
        <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
          <Button variant="ghost" onClick={() => setAddSectionForClass(null)}>Cancel</Button>
          <Button onClick={handleAddSections} loading={createSections.isPending} disabled={!newSections.trim()}>Add Sections</Button>
        </div>
      </Modal>

      <ConfirmDialog open={!!deleteClassTarget} onClose={() => setDeleteClassTarget(null)} onConfirm={confirmDeleteClass} loading={deleteClassMutation.isPending} title="Delete Class" message={`Are you sure you want to delete "${deleteClassTarget?.display_name || ''}"? All sections under this class will also be removed. This action cannot be undone.`} />

      <ConfirmDialog open={!!deleteSectionTarget} onClose={() => setDeleteSectionTarget(null)} onConfirm={confirmDeleteSection} loading={deleteClassSectionMutation.isPending} title="Remove Section" message={`Are you sure you want to remove "Section ${deleteSectionTarget?.section_name || ''}" from this class? This action cannot be undone.`} />
    </div>
  );
}

function SubjectsTab() {
  const toast = useToast();
  const { data, isLoading } = useSubjects();
  const { data: classSubjectData, isLoading: csLoading } = useClassSubjects();
  const createSubjects = useCreateSubjects();
  const updateSubjectMutation = useUpdateSubject();
  const deleteSubjectMutation = useDeleteSubject();
  const updateClassSubjects = useUpdateClassSubjects();
  const [showAdd, setShowAdd] = useState(false);
  const [editingSubject, setEditingSubject] = useState(null);
  const [deleteSubjectTarget, setDeleteSubjectTarget] = useState(null);
  const [newSubject, setNewSubject] = useState({ name: '', code: '' });

  const SUBJECT_COLORS = ['bg-blue-500', 'bg-emerald-500', 'bg-purple-500', 'bg-amber-500', 'bg-pink-500', 'bg-cyan-500', 'bg-indigo-500', 'bg-red-500'];

  if (isLoading || csLoading) return <div className="space-y-4">{[1, 2].map(i => <Skeleton key={i} className="h-16 w-full" />)}</div>;

  const subjects = Array.isArray(data) ? data : (data?.subjects || data?.results || []);
  const classesWithSubjects = classSubjectData?.classes || [];
  const academicYear = classSubjectData?.academic_year;

  const handleAdd = () => {
    if (!newSubject.name.trim()) return;
    createSubjects.mutate([{ name: newSubject.name, code: newSubject.code || null }], {
      onSuccess: () => { setShowAdd(false); setNewSubject({ name: '', code: '' }); toast.success('Subject added successfully'); },
      onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to add subject'); },
    });
  };

  const handleUpdate = () => {
    if (!editingSubject || !newSubject.name.trim()) return;
    updateSubjectMutation.mutate({ id: editingSubject.id, name: newSubject.name, code: newSubject.code || null }, {
      onSuccess: () => { setEditingSubject(null); setShowAdd(false); setNewSubject({ name: '', code: '' }); toast.success('Subject updated'); },
      onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to update'); },
    });
  };

  const handleDelete = (sub) => setDeleteSubjectTarget(sub);

  const confirmDeleteSubject = () => {
    if (!deleteSubjectTarget) return;
    deleteSubjectMutation.mutate(deleteSubjectTarget.id, {
      onSuccess: () => { setDeleteSubjectTarget(null); toast.success('Subject deleted'); },
      onError: (err) => { setDeleteSubjectTarget(null); toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to delete'); },
    });
  };

  const startEdit = (sub) => {
    setNewSubject({ name: sub.name || '', code: sub.code || '' });
    setEditingSubject(sub);
    setShowAdd(true);
  };

  const closeModal = () => {
    setShowAdd(false);
    setEditingSubject(null);
    setNewSubject({ name: '', code: '' });
  };

  return (
    <div className="space-y-6">
      {/* Subjects List */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-slate-900">Subjects</h3>
          <Button variant="secondary" size="sm" icon={Plus} onClick={() => { setNewSubject({ name: '', code: '' }); setEditingSubject(null); setShowAdd(true); }}>Add Subject</Button>
        </div>
        {subjects.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {subjects.map((sub, i) => {
              const name = typeof sub === 'string' ? sub : sub.name || sub.subject_name;
              const code = typeof sub === 'object' ? sub.code || sub.subject_code : null;
              const id = typeof sub === 'object' ? sub.id : null;
              return (
                <div key={id || i} className="group flex items-center gap-3 p-3.5 bg-slate-50 rounded-xl border border-slate-100 transition-all duration-150 hover:border-slate-200 hover:shadow-sm">
                  <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center shrink-0">
                    <BookOpen size={16} className="text-primary-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${SUBJECT_COLORS[i % SUBJECT_COLORS.length]} shrink-0`} />
                      <p className="text-sm font-medium text-slate-900 truncate">{name}</p>
                    </div>
                    {code && <p className="text-[11px] text-slate-400 ml-3.5">{code}</p>}
                  </div>
                  {id && (
                    <div className="flex items-center gap-0.5 shrink-0">
                      <button onClick={() => startEdit(sub)} className="p-1.5 rounded-lg text-slate-400 hover:text-primary-600 hover:bg-primary-50 transition-colors" title="Edit">
                        <Pencil size={13} />
                      </button>
                      <button onClick={() => handleDelete(sub)} className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors" title="Delete">
                        <Trash2 size={13} />
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-slate-400 text-center py-6">No subjects configured yet</p>
        )}
      </div>


      <Modal open={showAdd} onClose={closeModal} title={editingSubject ? 'Edit Subject' : 'Add Subject'} size="sm">
        <div className="space-y-3">
          <FormField label="Subject Name *" value={newSubject.name} onChange={v => setNewSubject({ ...newSubject, name: v })} placeholder="e.g., Mathematics" />
          <FormField label="Subject Code (optional)" value={newSubject.code} onChange={v => setNewSubject({ ...newSubject, code: v })} placeholder="e.g., MATH" />
        </div>
        <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
          <Button variant="ghost" onClick={closeModal}>Cancel</Button>
          <Button onClick={editingSubject ? handleUpdate : handleAdd} loading={createSubjects.isPending || updateSubjectMutation.isPending} disabled={!newSubject.name.trim()}>
            {editingSubject ? 'Update' : 'Add Subject'}
          </Button>
        </div>
      </Modal>

      <ConfirmDialog open={!!deleteSubjectTarget} onClose={() => setDeleteSubjectTarget(null)} onConfirm={confirmDeleteSubject} loading={deleteSubjectMutation.isPending} title="Delete Subject" message={`Are you sure you want to delete "${deleteSubjectTarget?.name}"? This action cannot be undone.`} />
    </div>
  );
}

function ClassSubjectMappingTab() {
  const toast = useToast();
  const { data: subjectsRaw, isLoading: subjectsLoading } = useSubjects();
  const { data: classSubjectData, isLoading: csLoading } = useClassSubjects();
  const { data: assignmentData, isLoading: assignLoading } = useClassSectionAssignments();
  const { data: teachersData } = useTeachers();
  const updateClassSubjects = useUpdateClassSubjects();
  const updateAssignment = useUpdateClassSectionAssignment();
  const [expandedClass, setExpandedClass] = useState(null);

  if (subjectsLoading || csLoading) return <div className="space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-20 w-full" />)}</div>;

  const subjects = Array.isArray(subjectsRaw) ? subjectsRaw : (subjectsRaw?.subjects || subjectsRaw?.results || []);
  const classesWithSubjects = classSubjectData?.classes || [];
  const assignmentClasses = assignmentData?.classes || [];
  const academicYear = assignmentData?.academic_year || classSubjectData?.academic_year;
  const allTeachers = Array.isArray(teachersData?.results) ? teachersData.results : [];
  const teachingStaff = allTeachers.filter(t => t.department === 'Teaching' && t.status === 'Active');

  const getTeachersForSubject = (subjectName) => {
    return teachingStaff.filter(t => {
      const primary = (t.primary_subject || '').toLowerCase();
      const subs = (t.subjects || []).map(s => s.toLowerCase());
      return primary === subjectName.toLowerCase() || subs.includes(subjectName.toLowerCase());
    });
  };

  const handleSaveSection = (classSectionId, classTeacherId, subjectTeachers) => {
    updateAssignment.mutate({ classSectionId, data: { class_teacher_id: classTeacherId || null, subject_teachers: subjectTeachers } }, {
      onSuccess: () => toast.success('Assignments saved'),
      onError: (err) => toast.error(err.response?.data?.detail || err.response?.data?.error || 'Failed to save'),
    });
  };

  // Merge assignment data into classesWithSubjects
  const getAssignmentForClass = (classId) => assignmentClasses.find(c => c.id === classId);

  if (subjects.length === 0) return (
    <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
      <p className="text-sm text-slate-500">No subjects configured yet. Add subjects in the "Classes, Sections & Subjects" tab first.</p>
    </div>
  );

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-slate-900">Class-Subject Mapping & Teacher Assignments</h3>
        <p className="text-xs text-slate-500 mt-1">Map subjects to classes, then assign class teachers and subject teachers per section. Academic Year: <span className="font-medium text-slate-700">{academicYear || '—'}</span></p>
      </div>

      {/* Teacher Workload Summary */}
      {teachingStaff.length > 0 && (
        <div className="mb-4 p-3 bg-slate-50 rounded-lg border border-slate-100">
          <p className="text-[10px] font-semibold text-slate-500 uppercase mb-2">Teacher Workload</p>
          <div className="flex flex-wrap gap-2">
            {teachingStaff.map(t => {
              const name = t.user?.full_name || t.full_name;
              const count = assignmentClasses.reduce((sum, cls) =>
                sum + cls.sections.reduce((sSum, sec) =>
                  sSum + (sec.class_teacher?.staff_id === t.id ? 1 : 0) + (sec.subject_teachers || []).filter(st => st.staff_id === t.id).length
                , 0)
              , 0);
              return (
                <span key={t.id} className={`text-[11px] px-2.5 py-1 rounded-full border font-medium ${count > 20 ? 'bg-red-50 border-red-200 text-red-700' : count > 12 ? 'bg-amber-50 border-amber-200 text-amber-700' : 'bg-slate-100 border-slate-200 text-slate-600'}`}>
                  {name.split(' ')[0]} <span className="font-bold">{count}</span>
                </span>
              );
            })}
          </div>
          {(() => {
            const overloadedCount = teachingStaff.filter(t => {
              const count = assignmentClasses.reduce((sum, cls) =>
                sum + cls.sections.reduce((sSum, sec) =>
                  sSum + (sec.class_teacher?.staff_id === t.id ? 1 : 0) + (sec.subject_teachers || []).filter(st => st.staff_id === t.id).length
                , 0)
              , 0);
              return count > 20;
            }).length;
            if (overloadedCount === 0) return null;
            return <p className="text-[11px] text-red-600 font-medium mt-2">&#9888; {overloadedCount} teacher{overloadedCount !== 1 ? 's' : ''} overloaded (&gt;20 assignments)</p>;
          })()}
        </div>
      )}

      {classesWithSubjects.length > 0 ? (
        <div className="space-y-4">
          {classesWithSubjects.map((cls) => {
            const assignmentCls = getAssignmentForClass(cls.id);
            const isExpanded = expandedClass === cls.id;
            return (
              <div key={cls.id} className="border border-slate-200 rounded-xl overflow-hidden">
                {/* Class header */}
                <button
                  onClick={() => setExpandedClass(isExpanded ? null : cls.id)}
                  className="w-full flex items-center justify-between p-4 bg-slate-50 hover:bg-slate-100 transition-colors text-left"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-primary-100 text-primary-700 flex items-center justify-center text-sm font-bold">{cls.name}</div>
                    <div>
                      <p className="text-sm font-semibold text-slate-900">Class {cls.name}</p>
                      <p className="text-[10px] text-slate-500">{cls.subjects?.length || 0} subjects • {assignmentCls?.sections?.length || 0} section{(assignmentCls?.sections?.length || 0) !== 1 ? 's' : ''}</p>
                    </div>
                  </div>
                  <ChevronRight className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`} />
                </button>

                {isExpanded && (
                  <div className="p-4 border-t border-slate-100 space-y-5">
                    {/* Subject mapping for this class */}
                    <div>
                      <p className="text-xs font-semibold text-slate-600 mb-2">Subjects</p>
                      <ClassSubjectRow cls={cls} allSubjects={subjects} updateClassSubjects={updateClassSubjects} toast={toast} />
                    </div>

                    {/* Section-level teacher assignments */}
                    {assignmentCls?.sections?.length > 0 && (
                      <div>
                        <p className="text-xs font-semibold text-slate-600 mb-2">Teacher Assignments by Section</p>
                        <div className="space-y-3">
                          {assignmentCls.sections.map((section) => (
                            <SectionAssignmentCard
                              key={section.id}
                              section={section}
                              teachingStaff={teachingStaff}
                              getTeachersForSubject={getTeachersForSubject}
                              onSave={handleSaveSection}
                              saving={updateAssignment.isPending}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                    {!assignmentCls && !assignLoading && (
                      <p className="text-xs text-slate-400 py-2">Teacher assignment data will be available after backend deployment.</p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <p className="text-sm text-slate-400 text-center py-6">No classes configured yet. Add classes in the previous tab first.</p>
      )}
    </div>
  );
}

function SectionAssignmentCard({ section, teachingStaff, getTeachersForSubject, onSave, saving }) {
  const [classTeacher, setClassTeacher] = useState(section.class_teacher?.staff_id || '');
  const [subjectTeachers, setSubjectTeachers] = useState(() =>
    Object.fromEntries((section.subject_teachers || []).map(st => [st.subject_id, st.staff_id || '']))
  );
  const [dirty, setDirty] = useState(false);
  const [collapsed, setCollapsed] = useState(true);

  const handleClassTeacherChange = (v) => { setClassTeacher(v); setDirty(true); };
  const handleSubjectTeacherChange = (subjectId, staffId) => { setSubjectTeachers(prev => ({ ...prev, [subjectId]: staffId })); setDirty(true); };

  const handleSave = () => {
    const stArr = Object.entries(subjectTeachers).map(([subject_id, staff_id]) => ({ subject_id, staff_id: staff_id || null }));
    onSave(section.id, classTeacher || null, stArr);
    setDirty(false);
  };

  const teacherOptions = teachingStaff.map(t => ({ value: t.id, label: t.user?.full_name || t.full_name }));
  const assignedCount = (section.subject_teachers || []).filter(st => subjectTeachers[st.subject_id]).length;
  const totalSubjects = (section.subject_teachers || []).length;

  return (
    <div className={`border rounded-xl overflow-hidden transition-all duration-200 ${dirty ? 'border-primary-300 shadow-sm' : 'border-slate-200'}`}>
      {/* Collapsible header */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="w-full flex items-center justify-between p-3.5 bg-white hover:bg-slate-50 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-50 to-indigo-100 flex items-center justify-center text-xs font-bold text-indigo-600">{section.section_name}</div>
          <div>
            <p className="text-sm font-semibold text-slate-800">Section {section.section_name}</p>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-[10px] text-slate-500">{section.class_teacher?.name ? `CT: ${section.class_teacher.name}` : 'No class teacher'}</span>
              <span className="text-[10px] text-slate-400">•</span>
              <span className={`text-[10px] font-medium ${assignedCount === totalSubjects && totalSubjects > 0 ? 'text-emerald-600' : 'text-amber-600'}`}>{assignedCount}/{totalSubjects} teachers assigned</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {dirty && <span className="text-[9px] bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full font-medium">Unsaved</span>}
          <ChevronRight className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${!collapsed ? 'rotate-90' : ''}`} />
        </div>
      </button>

      {!collapsed && (
        <div className="p-4 border-t border-slate-100 bg-slate-50/30 space-y-3">
          {/* Class Teacher */}
          <div className="p-3 bg-blue-50/60 rounded-lg border border-blue-100/80">
            <label className="text-[10px] font-semibold text-blue-600 uppercase mb-1.5 block">Class Teacher</label>
            <SearchableSelect
              value={classTeacher}
              onChange={handleClassTeacherChange}
              options={[{ value: '', label: 'Not Assigned' }, ...teacherOptions]}
              placeholder="Select class teacher..."
            />
          </div>

          {/* Subject Teachers */}
          {section.subject_teachers?.length > 0 && (
            <div>
              <p className="text-[10px] font-semibold text-slate-500 uppercase mb-2">Subject Teachers</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {section.subject_teachers.map((st) => {
                const matchedTeachers = getTeachersForSubject(st.subject_name);
                const options = matchedTeachers.length > 0
                  ? matchedTeachers.map(t => ({ value: t.id, label: t.user?.full_name || t.full_name }))
                  : teachingStaff.map(t => ({ value: t.id, label: `${t.user?.full_name || t.full_name} (${t.primary_subject || 'No subject'})` }));
                const isAssigned = !!subjectTeachers[st.subject_id];

                return (
                  <div key={st.subject_id} className={`flex items-center gap-2 p-2.5 rounded-lg border transition-colors ${isAssigned ? 'bg-emerald-50/40 border-emerald-100' : 'bg-white border-slate-100'}`}>
                    <div className="w-24 flex-shrink-0 flex items-center gap-1.5">
                      <span className={`w-1.5 h-1.5 rounded-full ${isAssigned ? 'bg-emerald-500' : 'bg-slate-300'}`} />
                      <span className="text-xs font-medium text-slate-700 truncate">{st.subject_name}</span>
                    </div>
                    <div className="flex-1">
                      <SearchableSelect
                        value={subjectTeachers[st.subject_id] || ''}
                        onChange={(v) => handleSubjectTeacherChange(st.subject_id, v)}
                        options={[{ value: '', label: 'Not Assigned' }, ...options]}
                        placeholder="Select teacher..."
                  />
                </div>
                {matchedTeachers.length === 0 && subjectTeachers[st.subject_id] && <span className="text-[9px] text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded flex-shrink-0" title="Assigned teacher doesn't specialize in this subject">⚠ Non-specialist</span>}
              </div>
            );
          })}
              </div>
            </div>
          )}
          {(!section.subject_teachers || section.subject_teachers.length === 0) && (
            <p className="text-xs text-slate-400 text-center py-3">No subjects mapped to this class yet. Map subjects above first.</p>
          )}

          {/* Save button */}
          {dirty && (
            <div className="flex justify-end pt-2 border-t border-slate-100">
              <Button variant="primary" size="sm" onClick={handleSave} disabled={saving}>{saving ? 'Saving...' : 'Save Changes'}</Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function LeavePolicyTab() {
  const toast = useToast();
  const { data, isLoading } = useLeavePolicy();
  const updateMutation = useUpdateLeavePolicy();
  const { data: staffData } = useStaff({ page_size: 500 });
  const [showModal, setShowModal] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);
  const [deleteIndex, setDeleteIndex] = useState(null);
  const [form, setForm] = useState({ type: '', display_name: '', total_per_year: '', applicable_to: 'all', departments: [], members: [] });
  const [expandedDepts, setExpandedDepts] = useState({});

  if (isLoading) return <div className="space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}</div>;

  const leaveTypes = data?.leave_types || [];
  const allStaff = staffData?.results || [];

  const getStaffByDept = (dept) => allStaff.filter(s => s.department === dept);

  const saveAll = (updatedTypes) => {
    const payload = updatedTypes.map(lt => ({
      type: lt.type,
      display_name: lt.display_name || null,
      total_per_year: lt.total_per_year,
      applicable_to: lt.applicable_to,
      members: lt.members || null,
      carry_forward: lt.carry_forward || false,
      requires_approval: lt.requires_approval !== false,
      half_day_allowed: lt.half_day_allowed || false,
    }));
    updateMutation.mutate({ leave_types: payload }, {
      onSuccess: () => toast.success('Leave policy updated'),
      onError: (err) => toast.error(err.response?.data?.detail || 'Failed to update'),
    });
  };

  const handleSave = () => {
    const entry = {
      type: form.type,
      display_name: form.display_name || null,
      total_per_year: parseInt(form.total_per_year) || 0,
      applicable_to: form.applicable_to === 'all' ? 'all' : form.departments,
      members: form.applicable_to === 'all' ? null : form.members,
      carry_forward: false,
      requires_approval: true,
      half_day_allowed: false,
    };
    let updated;
    if (editingIndex !== null) {
      updated = leaveTypes.map((lt, i) => i === editingIndex ? entry : lt);
    } else {
      updated = [...leaveTypes, entry];
    }
    saveAll(updated);
    setShowModal(false);
    setEditingIndex(null);
  };

  const handleDelete = () => {
    if (deleteIndex === null) return;
    saveAll(leaveTypes.filter((_, i) => i !== deleteIndex));
    setDeleteIndex(null);
  };

  const startEdit = (index) => {
    const lt = leaveTypes[index];
    const isAll = lt.applicable_to === 'all';
    setForm({
      type: lt.type,
      display_name: lt.display_name || '',
      total_per_year: String(lt.total_per_year),
      applicable_to: isAll ? 'all' : 'specific',
      departments: isAll ? [] : (Array.isArray(lt.applicable_to) ? lt.applicable_to : []),
      members: lt.members || [],
    });
    setEditingIndex(index);
    setExpandedDepts({});
    setShowModal(true);
  };

  const startAdd = () => {
    setForm({ type: '', display_name: '', total_per_year: '', applicable_to: 'all', departments: [], members: [] });
    setEditingIndex(null);
    setExpandedDepts({});
    setShowModal(true);
  };

  const toggleDept = (dept) => {
    const has = form.departments.includes(dept);
    const deptStaffIds = getStaffByDept(dept).map(s => s.id);
    if (has) {
      setForm({ ...form, departments: form.departments.filter(d => d !== dept), members: form.members.filter(id => !deptStaffIds.includes(id)) });
    } else {
      setForm({ ...form, departments: [...form.departments, dept], members: [...new Set([...form.members, ...deptStaffIds])] });
    }
  };

  const toggleMember = (memberId, dept) => {
    const has = form.members.includes(memberId);
    const newMembers = has ? form.members.filter(id => id !== memberId) : [...form.members, memberId];
    setForm({ ...form, members: newMembers });
    // If all members of dept are unchecked, remove dept
    const deptStaffIds = getStaffByDept(dept).map(s => s.id);
    const anyChecked = deptStaffIds.some(id => newMembers.includes(id));
    if (!anyChecked && form.departments.includes(dept)) {
      setForm(f => ({ ...f, departments: f.departments.filter(d => d !== dept), members: newMembers }));
    } else if (anyChecked && !form.departments.includes(dept)) {
      setForm(f => ({ ...f, departments: [...f.departments, dept], members: newMembers }));
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Leave Policy</h3>
            <p className="text-xs text-slate-400">Academic Year: {data?.academic_year || '—'}</p>
          </div>
          <Button variant="secondary" size="sm" icon={Plus} onClick={startAdd}>Add Leave Type</Button>
        </div>

        {leaveTypes.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Leave Type</th>
                  <th className="text-center py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Days/Year</th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Applicable To</th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {leaveTypes.map((lt, i) => (
                  <tr key={i} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 px-4">
                      <p className="font-medium text-slate-900">{lt.type}</p>
                      {lt.display_name && <p className="text-xs text-slate-400">{lt.display_name}</p>}
                    </td>
                    <td className="py-3 px-4 text-center"><span className="px-2.5 py-1 rounded-lg bg-primary-50 text-primary-700 font-bold text-xs">{lt.total_per_year}</span></td>
                    <td className="py-3 px-4">
                      {lt.applicable_to === 'all' ? (
                        <Badge variant="success">All Departments</Badge>
                      ) : (
                        <div className="flex flex-wrap gap-1">
                          {(Array.isArray(lt.applicable_to) ? lt.applicable_to : []).map(d => <Badge key={d} variant="default">{d}</Badge>)}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => startEdit(i)} className="p-1.5 rounded-lg text-slate-400 hover:text-primary-600 hover:bg-primary-50 transition-colors"><Pencil size={14} /></button>
                        <button onClick={() => setDeleteIndex(i)} className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"><Trash2 size={14} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <CalendarCheck size={24} className="text-slate-300 mx-auto mb-2" />
            <p className="text-sm text-slate-500">No leave types configured yet</p>
            <p className="text-xs text-slate-400 mt-1">Click "Add Leave Type" to define your leave policy</p>
          </div>
        )}
      </div>

      <Modal open={showModal} onClose={() => { setShowModal(false); setEditingIndex(null); }} title={editingIndex !== null ? 'Edit Leave Type' : 'Add Leave Type'} size="md">
        <div className="space-y-4">
          <FormField label="Leave Name *" value={form.type} onChange={v => setForm({ ...form, type: v })} placeholder="e.g., Sick Leave - Teaching" />
          <FormField label="Display Name (shown to staff) *" value={form.display_name} onChange={v => setForm({ ...form, display_name: v })} placeholder="e.g., Sick Leave" />
          <FormField label="Days Per Year *" value={form.total_per_year} onChange={v => setForm({ ...form, total_per_year: v })} type="number" placeholder="12" />
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Applicable For</label>
            <SearchableSelect
              options={[{ value: 'all', label: 'All Departments' }, { value: 'specific', label: 'Specific Departments' }]}
              value={form.applicable_to}
              onChange={v => setForm({ ...form, applicable_to: v, departments: v === 'all' ? [] : form.departments, members: v === 'all' ? [] : form.members })}
            />
          </div>

          {form.applicable_to === 'specific' && (
            <div className="border border-slate-200 rounded-lg max-h-64 overflow-y-auto">
              {DEPARTMENTS.map(dept => {
                const deptStaff = getStaffByDept(dept.value);
                const isExpanded = expandedDepts[dept.value];
                const deptChecked = form.departments.includes(dept.value);
                return (
                  <div key={dept.value} className="border-b border-slate-100 last:border-0">
                    <div className="flex items-center gap-2 px-3 py-2 hover:bg-slate-50">
                      <input type="checkbox" checked={deptChecked} onChange={() => toggleDept(dept.value)} className="w-4 h-4 rounded border-slate-300 text-primary-600" />
                      <button type="button" className="flex items-center gap-1 flex-1 text-left text-sm font-medium text-slate-700" onClick={() => setExpandedDepts({ ...expandedDepts, [dept.value]: !isExpanded })}>
                        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                        {dept.label} <span className="text-xs text-slate-400">({deptStaff.length})</span>
                      </button>
                    </div>
                    {isExpanded && deptStaff.length > 0 && (
                      <div className="pl-9 pb-2 space-y-1">
                        {deptStaff.map(s => (
                          <label key={s.id} className="flex items-center gap-2 px-2 py-1 cursor-pointer hover:bg-slate-50 rounded text-sm text-slate-600">
                            <input type="checkbox" checked={form.members.includes(s.id)} onChange={() => toggleMember(s.id, dept.value)} className="w-3.5 h-3.5 rounded border-slate-300 text-primary-600" />
                            {s.full_name || s.name}
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
        <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
          <Button variant="ghost" onClick={() => { setShowModal(false); setEditingIndex(null); }}>Cancel</Button>
          <Button onClick={handleSave} loading={updateMutation.isPending} disabled={!form.type || !form.total_per_year}>{editingIndex !== null ? 'Update' : 'Add'}</Button>
        </div>
      </Modal>

      <ConfirmDialog open={deleteIndex !== null} onClose={() => setDeleteIndex(null)} onConfirm={handleDelete} loading={updateMutation.isPending} title="Delete Leave Type" message={`Are you sure you want to delete "${leaveTypes[deleteIndex]?.type}"? This action cannot be undone.`} />
    </div>
  );
}

function HolidayCalendarGrid({ holidays }) {
  const [calMonth, setCalMonth] = useState(() => {
    const first = holidays.find(h => h.date);
    if (first) { const d = new Date(first.date); return new Date(d.getFullYear(), d.getMonth(), 1); }
    return new Date(new Date().getFullYear(), new Date().getMonth(), 1);
  });
  const [hoveredDay, setHoveredDay] = useState(null);

  const year = calMonth.getFullYear();
  const month = calMonth.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const startDay = new Date(year, month, 1).getDay();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const holidayDates = new Map();
  holidays.forEach(h => {
    const d = new Date(h.date + 'T00:00:00');
    if (d.getFullYear() === year && d.getMonth() === month) {
      holidayDates.set(d.getDate(), h);
    }
  });

  const totalThisMonth = holidayDates.size;

  return (
    <div className="mb-5 bg-white border border-slate-200 rounded-xl p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-50 to-red-100 flex items-center justify-center">
            <Calendar size={15} className="text-red-500" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900">Holiday Calendar</h4>
            <p className="text-[10px] text-slate-500">{totalThisMonth} holiday{totalThisMonth !== 1 ? 's' : ''} this month</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={() => setCalMonth(new Date(year, month - 1, 1))} className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-slate-100 text-slate-500 transition-colors">
            <ChevronRight className="w-4 h-4 rotate-180" />
          </button>
          <span className="text-sm font-semibold text-slate-800 min-w-[120px] text-center">{calMonth.toLocaleString('default', { month: 'long', year: 'numeric' })}</span>
          <button onClick={() => setCalMonth(new Date(year, month + 1, 1))} className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-slate-100 text-slate-500 transition-colors">
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Day headers */}
      <div className="grid grid-cols-7 mb-1">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
          <div key={d} className="text-center text-[10px] font-semibold text-slate-400 uppercase py-1.5">{d}</div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-1">
        {Array.from({ length: startDay }, (_, i) => <div key={`e-${i}`} />)}
        {Array.from({ length: daysInMonth }, (_, i) => {
          const day = i + 1;
          const hol = holidayDates.get(day);
          const isToday = today.getFullYear() === year && today.getMonth() === month && today.getDate() === day;
          const isSunday = new Date(year, month, day).getDay() === 0;

          return (
            <div
              key={day}
              className={`relative min-h-[38px] p-1 rounded-lg text-center transition-all duration-100 cursor-default ${
                hol ? 'bg-gradient-to-br from-red-50 to-red-100 border border-red-200' :
                isToday ? 'bg-primary-50 border border-primary-200' :
                isSunday ? 'bg-slate-50' : 'hover:bg-slate-50'
              }`}
              onMouseEnter={() => hol && setHoveredDay(day)}
              onMouseLeave={() => setHoveredDay(null)}
            >
              <span className={`text-xs font-medium ${
                hol ? 'text-red-700' :
                isToday ? 'text-primary-700' :
                isSunday ? 'text-slate-400' : 'text-slate-700'
              }`}>{day}</span>
              {hol && <div className="w-1.5 h-1.5 rounded-full bg-red-500 mx-auto mt-0.5" />}

              {/* Tooltip */}
              {hoveredDay === day && hol && (
                <div className="absolute z-20 bottom-full left-1/2 -translate-x-1/2 mb-1 bg-slate-800 text-white text-[10px] px-2.5 py-1.5 rounded-lg shadow-lg whitespace-nowrap">
                  {hol.name}
                  <div className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-slate-800" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      {totalThisMonth > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-100">
          <div className="flex flex-wrap gap-2">
            {[...holidayDates.entries()].map(([day, h]) => (
              <div key={day} className="flex items-center gap-1.5 bg-red-50 border border-red-100 rounded-lg px-2.5 py-1.5">
                <span className="text-xs font-bold text-red-700">{day}</span>
                <span className="text-xs text-red-600">{h.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function HolidaysTab() {
  const toast = useToast();
  const { data, isLoading } = useHolidays();
  const updateMutation = useUpdateHolidays();
  const [showModal, setShowModal] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);
  const [deleteIndex, setDeleteIndex] = useState(null);
  const [form, setForm] = useState({ date: '', name: '', type: 'School', description: '' });

  if (isLoading) return <div className="space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}</div>;

  const holidays = data?.holidays || [];
  const types = ['National', 'Regional', 'School', 'Optional'];
  const typeBadgeVariant = { National: 'error', Regional: 'warning', School: 'success', Optional: 'default' };

  const saveAll = (updated) => {
    updateMutation.mutate({ holidays: updated }, {
      onSuccess: () => toast.success('Holidays updated'),
      onError: (err) => toast.error(err.response?.data?.detail || 'Failed to update'),
    });
  };

  const handleSave = () => {
    const entry = { date: form.date, name: form.name, type: form.type, description: form.description };
    let updated;
    if (editingIndex !== null) {
      updated = holidays.map((h, i) => i === editingIndex ? entry : h);
    } else {
      updated = [...holidays, entry];
    }
    updated.sort((a, b) => a.date.localeCompare(b.date));
    saveAll(updated);
    setShowModal(false);
    setEditingIndex(null);
  };

  const handleDelete = () => {
    if (deleteIndex === null) return;
    saveAll(holidays.filter((_, i) => i !== deleteIndex));
    setDeleteIndex(null);
  };

  const startEdit = (index) => {
    const h = holidays[index];
    setForm({ date: h.date, name: h.name, type: h.type, description: h.description || '' });
    setEditingIndex(index);
    setShowModal(true);
  };

  const startAdd = () => {
    setForm({ date: '', name: '', type: 'School', description: '' });
    setEditingIndex(null);
    setShowModal(true);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Holidays</h3>
            <p className="text-xs text-slate-400">{holidays.length} holiday{holidays.length !== 1 ? 's' : ''} configured</p>
          </div>
          <Button variant="secondary" size="sm" icon={Plus} onClick={startAdd}>Add Holiday</Button>
        </div>

        {/* Holiday Calendar Mini Grid */}
        {holidays.length > 0 && <HolidayCalendarGrid holidays={holidays} />}

        {holidays.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Date</th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Holiday Name</th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Type</th>
                  <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Description</th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {holidays.map((h, i) => (
                  <tr key={i} className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 px-4 font-medium text-slate-900 whitespace-nowrap">{h.date}</td>
                    <td className="py-3 px-4 text-slate-800">{h.name}</td>
                    <td className="py-3 px-4"><Badge variant={typeBadgeVariant[h.type] || 'default'}>{h.type}</Badge></td>
                    <td className="py-3 px-4 text-slate-500 text-xs max-w-[200px] truncate">{h.description || '—'}</td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => startEdit(i)} className="p-1.5 rounded-lg text-slate-400 hover:text-primary-600 hover:bg-primary-50 transition-colors"><Pencil size={14} /></button>
                        <button onClick={() => setDeleteIndex(i)} className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"><Trash2 size={14} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <Calendar size={24} className="text-slate-300 mx-auto mb-2" />
            <p className="text-sm text-slate-500">No holidays configured yet</p>
            <p className="text-xs text-slate-400 mt-1">Click "Add Holiday" to mark holidays for the academic year</p>
          </div>
        )}
      </div>

      <Modal open={showModal} onClose={() => { setShowModal(false); setEditingIndex(null); }} title={editingIndex !== null ? 'Edit Holiday' : 'Add Holiday'} size="sm">
        <div className="space-y-3">
          <FormField label="Date *" value={form.date} onChange={v => setForm({ ...form, date: v })} type="date" />
          <FormField label="Holiday Name *" value={form.name} onChange={v => setForm({ ...form, name: v })} placeholder="e.g., Republic Day" />
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Type *</label>
            <select value={form.type} onChange={e => setForm({ ...form, type: e.target.value })} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
              {types.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <FormField label="Description" value={form.description} onChange={v => setForm({ ...form, description: v })} placeholder="Optional description" />
        </div>
        <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
          <Button variant="ghost" onClick={() => { setShowModal(false); setEditingIndex(null); }}>Cancel</Button>
          <Button onClick={handleSave} loading={updateMutation.isPending} disabled={!form.date || !form.name}>{editingIndex !== null ? 'Update' : 'Add'}</Button>
        </div>
      </Modal>

      <ConfirmDialog open={deleteIndex !== null} onClose={() => setDeleteIndex(null)} onConfirm={handleDelete} loading={updateMutation.isPending} title="Delete Holiday" message={`Are you sure you want to delete "${holidays[deleteIndex]?.name}"? This action cannot be undone.`} />
    </div>
  );
}

function AttendanceModeTab() {
  const toast = useToast();
  const { data: config, isLoading } = useAttendanceConfig();
  const updateMutation = useUpdateAttendanceConfig();
  const [selectedMode, setSelectedMode] = useState(null);

  if (isLoading) return <div className="space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-24 w-full" />)}</div>;

  const currentMode = selectedMode || config?.attendance_mode || 'daily';
  const isDirty = selectedMode !== null && selectedMode !== (config?.attendance_mode || 'daily');

  const modes = [
    {
      id: 'daily',
      label: 'Daily',
      description: 'Take attendance once per day for each class/section',
      enabled: true,
    },
    {
      id: 'subject_wise',
      label: 'Subject-wise',
      description: 'Take attendance per subject/period throughout the day',
      enabled: true,
    },
    {
      id: 'twice_daily',
      label: 'Twice (Morning & Afternoon)',
      description: 'Take attendance twice a day — morning and afternoon sessions',
      enabled: false,
    },
  ];

  const handleSave = () => {
    const payload = {
      threshold: config?.threshold || 75,
      min_days: config?.min_days || 30,
      attendance_mode: selectedMode,
    };
    updateMutation.mutate(payload, {
      onSuccess: () => { setSelectedMode(null); toast.success('Attendance mode updated'); },
      onError: (err) => { toast.error(err.response?.data?.detail || 'Failed to update attendance mode'); },
    });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Attendance Mode</h3>
            <p className="text-xs text-slate-400 mt-0.5">Choose how attendance is recorded for your school</p>
          </div>
          {isDirty && <Button size="sm" icon={Save} onClick={handleSave} loading={updateMutation.isPending}>Save</Button>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {modes.map((mode) => {
            const isSelected = currentMode === mode.id;
            const isDisabled = !mode.enabled;

            return (
              <button
                key={mode.id}
                type="button"
                disabled={isDisabled}
                onClick={() => { if (mode.enabled) setSelectedMode(mode.id); }}
                className={`relative text-left p-5 rounded-xl border-2 transition-all duration-200 ${
                  isDisabled
                    ? 'border-slate-100 bg-slate-50 cursor-not-allowed opacity-60'
                    : isSelected
                    ? 'border-primary-500 bg-primary-50/50 shadow-sm'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm cursor-pointer'
                }`}
              >
                {/* Radio indicator */}
                <div className="flex items-start gap-3">
                  <div className={`mt-0.5 w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${
                    isDisabled
                      ? 'border-slate-200 bg-slate-100'
                      : isSelected
                      ? 'border-primary-500 bg-primary-500'
                      : 'border-slate-300 bg-white'
                  }`}>
                    {isSelected && !isDisabled && (
                      <div className="w-2 h-2 rounded-full bg-white" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className={`text-sm font-semibold ${isDisabled ? 'text-slate-400' : isSelected ? 'text-primary-900' : 'text-slate-800'}`}>
                        {mode.label}
                      </p>
                      {!mode.enabled && (
                        <span className="inline-flex px-2 py-0.5 rounded-full bg-amber-100 text-[10px] font-semibold text-amber-700 uppercase tracking-wider">
                          Coming Soon
                        </span>
                      )}
                    </div>
                    <p className={`text-xs mt-1 ${isDisabled ? 'text-slate-300' : isSelected ? 'text-primary-700' : 'text-slate-500'}`}>
                      {mode.description}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        <div className="mt-5 px-4 py-3 rounded-lg bg-blue-50 border border-blue-100">
          <p className="text-xs text-blue-700">
            <span className="font-semibold">Current mode:</span> {modes.find(m => m.id === (config?.attendance_mode || 'daily'))?.label || 'Daily'}.
            {' '}Attendance is taken once per day for each class and section.
          </p>
        </div>
      </div>

      {/* Working Days Section */}
      <WorkingDaysSection config={config} />
    </div>
  );
}

function WorkingDaysSection({ config }) {
  const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const defaultWorkingDays = config?.working_days || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
  const [workingDays, setWorkingDays] = useState(defaultWorkingDays);

  const toggleDay = (day) => {
    setWorkingDays(prev => prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-slate-900">Working Days</h3>
        <p className="text-xs text-slate-400 mt-0.5">Select which days of the week the school operates</p>
      </div>
      <div className="flex flex-wrap gap-3">
        {DAYS.map(day => {
          const isActive = workingDays.includes(day);
          return (
            <button
              key={day}
              type="button"
              onClick={() => toggleDay(day)}
              className={`px-4 py-2.5 rounded-xl border-2 text-sm font-semibold transition-all duration-200 ${
                isActive
                  ? 'border-primary-500 bg-primary-50 text-primary-700 shadow-sm'
                  : 'border-slate-200 bg-white text-slate-400 hover:border-slate-300'
              }`}
            >
              {day}
            </button>
          );
        })}
      </div>
      <p className="text-[11px] text-slate-400 mt-3">{workingDays.length} working day{workingDays.length !== 1 ? 's' : ''} per week</p>
    </div>
  );
}

function GradesTab() {
  const toast = useToast();
  const { data, isLoading, isError } = useGradeSystem();
  const updateMutation = useUpdateGradeSystem();
  const [showModal, setShowModal] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);
  const [deleteIndex, setDeleteIndex] = useState(null);
  const [form, setForm] = useState({ grade: '', min_percentage: '', max_percentage: '', grade_point: '' });

  if (isLoading) return <div className="space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}</div>;

  const grades = data?.grades || [];

  const saveGrades = (updatedGrades) => {
    updateMutation.mutate({ name: data?.name || 'Default Grade System', grades: updatedGrades }, {
      onSuccess: () => toast.success('Grade system updated'),
      onError: (err) => toast.error(err.response?.data?.detail || 'Failed to update'),
    });
  };

  const handleSave = () => {
    const entry = {
      grade: form.grade,
      min_percentage: parseFloat(form.min_percentage),
      max_percentage: parseFloat(form.max_percentage),
      grade_point: form.grade_point ? parseFloat(form.grade_point) : null,
      description: null,
    };

    if (entry.min_percentage >= entry.max_percentage) {
      toast.error('Min percentage must be less than max percentage');
      return;
    }

    let updated;
    if (editingIndex !== null) {
      updated = grades.map((g, i) => i === editingIndex ? entry : g);
    } else {
      updated = [...grades, entry];
    }

    const sorted = [...updated].sort((a, b) => a.min_percentage - b.min_percentage);
    for (let i = 0; i < sorted.length - 1; i++) {
      if (sorted[i].max_percentage > sorted[i + 1].min_percentage) {
        toast.error(`Grade ranges overlap: "${sorted[i].grade}" (${sorted[i].min_percentage}%-${sorted[i].max_percentage}%) overlaps with "${sorted[i + 1].grade}" (${sorted[i + 1].min_percentage}%-${sorted[i + 1].max_percentage}%)`);
        return;
      }
    }

    saveGrades(updated);
    setShowModal(false);
    setEditingIndex(null);
  };

  const handleDelete = () => {
    if (deleteIndex === null) return;
    saveGrades(grades.filter((_, i) => i !== deleteIndex));
    setDeleteIndex(null);
  };

  const startEdit = (index) => {
    const g = grades[index];
    setForm({
      grade: g.grade,
      min_percentage: String(g.min_percentage),
      max_percentage: String(g.max_percentage),
      grade_point: g.grade_point != null ? String(g.grade_point) : '',
    });
    setEditingIndex(index);
    setShowModal(true);
  };

  const startAdd = () => {
    setForm({ grade: '', min_percentage: '', max_percentage: '', grade_point: '' });
    setEditingIndex(null);
    setShowModal(true);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Grade System</h3>
            <p className="text-xs text-slate-400">{data?.name || 'Not configured'} • Academic Year: {data?.academic_year || '—'}</p>
          </div>
          <Button variant="secondary" size="sm" icon={Plus} onClick={startAdd}>Add Grade</Button>
        </div>
        <div className="mb-4 px-3 py-2 rounded-lg bg-blue-50 border border-blue-100 text-xs text-blue-700">
          <span className="font-semibold">How ranges work:</span> Min % is inclusive, Max % is exclusive. Example: Grade A (90–100) means 90% ≤ score &lt; 100%. A student scoring exactly 90% gets Grade A. The highest grade should have Max = 100 (which is inclusive for the top grade).
        </div>

        {isError && !data ? (
          <div className="text-center py-12">
            <Award size={24} className="text-slate-300 mx-auto mb-2" />
            <p className="text-sm text-slate-500">No grade system configured yet</p>
            <p className="text-xs text-slate-400 mt-1">Click "Add Grade" to define your grading scale</p>
          </div>
        ) : grades.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Grade</th>
                  <th className="text-center py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Range</th>
                  <th className="text-center py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Grade Point</th>
                  <th className="text-right py-3 px-4 text-xs font-semibold text-slate-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {grades.map((g, i) => {
                  const isLowestGrade = grades.length > 0 && g.min_percentage === Math.min(...grades.map(gr => gr.min_percentage));
                  return (
                  <tr key={i} className={`transition-colors ${isLowestGrade ? 'bg-amber-50/60 hover:bg-amber-50' : 'hover:bg-slate-50/50'}`}>
                    <td className="py-3 px-4 font-semibold text-slate-900">
                      <span className="flex items-center gap-1.5">
                        {g.grade}
                        {isLowestGrade && <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-700 font-medium">Min Passing</span>}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center"><span className="px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 text-xs font-medium">{g.min_percentage}% – {g.max_percentage}%</span></td>
                    <td className="py-3 px-4 text-center"><span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 text-xs font-bold">{g.grade_point != null ? g.grade_point : '—'}</span></td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => startEdit(i)} className="p-1.5 rounded-lg text-slate-400 hover:text-primary-600 hover:bg-primary-50 transition-colors"><Pencil size={14} /></button>
                        <button onClick={() => setDeleteIndex(i)} className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"><Trash2 size={14} /></button>
                      </div>
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <Award size={24} className="text-slate-300 mx-auto mb-2" />
            <p className="text-sm text-slate-500">No grades defined yet</p>
            <p className="text-xs text-slate-400 mt-1">Click "Add Grade" to get started</p>
          </div>
        )}

        {grades.length > 0 && (() => {
          const sorted = [...grades].sort((a, b) => a.min_percentage - b.min_percentage);
          const gaps = [];
          if (sorted[0].min_percentage > 0) gaps.push(`0% – ${sorted[0].min_percentage}%`);
          for (let i = 0; i < sorted.length - 1; i++) {
            if (sorted[i].max_percentage < sorted[i + 1].min_percentage) {
              gaps.push(`${sorted[i].max_percentage}% – ${sorted[i + 1].min_percentage}%`);
            }
          }
          if (sorted[sorted.length - 1].max_percentage < 100) gaps.push(`${sorted[sorted.length - 1].max_percentage}% – 100%`);
          if (gaps.length === 0) return null;
          return (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-xs font-semibold text-red-700 mb-1">Coverage gaps detected — the following ranges are not assigned to any grade:</p>
              <div className="flex flex-wrap gap-1.5">
                {gaps.map((gap, i) => <span key={i} className="px-2 py-0.5 rounded bg-red-100 text-red-700 text-xs font-medium">{gap}</span>)}
              </div>
            </div>
          );
        })()}
      </div>

      {/* Grade Preview Calculator */}
      {grades.length > 0 && <GradePreviewCalculator grades={grades} />}

      <Modal open={showModal} onClose={() => { setShowModal(false); setEditingIndex(null); }} title={editingIndex !== null ? 'Edit Grade' : 'Add Grade'} size="sm">
        <div className="space-y-4">
          <FormField label="Grade Name *" value={form.grade} onChange={v => setForm({ ...form, grade: v })} placeholder="e.g., A+, A, B+" />
          <div className="grid grid-cols-3 gap-4">
            <FormField label="Min % (inclusive) *" value={form.min_percentage} onChange={v => setForm({ ...form, min_percentage: v })} type="number" placeholder="90" />
            <FormField label="Max % (exclusive) *" value={form.max_percentage} onChange={v => setForm({ ...form, max_percentage: v })} type="number" placeholder="100" />
            <FormField label="Grade Point" value={form.grade_point} onChange={v => setForm({ ...form, grade_point: v })} type="number" placeholder="10" />
          </div>
          <p className="text-[11px] text-slate-400">A score of exactly the boundary value (e.g., 90%) belongs to the grade starting at that value, not the one ending at it.</p>
        </div>
        <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
          <Button variant="ghost" onClick={() => { setShowModal(false); setEditingIndex(null); }}>Cancel</Button>
          <Button onClick={handleSave} loading={updateMutation.isPending} disabled={!form.grade || !form.min_percentage || !form.max_percentage}>{editingIndex !== null ? 'Update' : 'Add'}</Button>
        </div>
      </Modal>

      <ConfirmDialog open={deleteIndex !== null} onClose={() => setDeleteIndex(null)} onConfirm={handleDelete} loading={updateMutation.isPending} title="Delete Grade" message={`Are you sure you want to delete "${grades[deleteIndex]?.grade}"? This action cannot be undone.`} />
    </div>
  );
}

function GradePreviewCalculator({ grades }) {
  const [testPercent, setTestPercent] = useState('');

  const getGradeForPercent = (pct) => {
    const num = parseFloat(pct);
    if (isNaN(num) || num < 0 || num > 100) return null;
    const sorted = [...grades].sort((a, b) => b.min_percentage - a.min_percentage);
    for (const g of sorted) {
      if (num >= g.min_percentage && num < g.max_percentage) return g;
      // Top grade: max_percentage is inclusive
      if (g.max_percentage === 100 && num === 100 && num >= g.min_percentage) return g;
    }
    return null;
  };

  const result = testPercent ? getGradeForPercent(testPercent) : null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5">
      <h4 className="text-sm font-semibold text-slate-900 mb-3">Grade Preview Calculator</h4>
      <div className="flex items-center gap-3">
        <div className="flex-1 max-w-[200px]">
          <input
            type="number"
            value={testPercent}
            onChange={e => setTestPercent(e.target.value)}
            placeholder="Enter percentage (0-100)"
            min="0"
            max="100"
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        {testPercent && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-500">{testPercent}%</span>
            <span className="text-slate-400">→</span>
            {result ? (
              <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200">
                <span className="text-sm font-bold text-emerald-800">Grade: {result.grade}</span>
                {result.grade_point != null && <span className="text-xs text-emerald-600">(GP: {result.grade_point})</span>}
              </span>
            ) : (
              <span className="inline-flex px-3 py-1.5 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">No matching grade</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function InfoField({ label, value }) {
  return (
    <div className="p-3 bg-slate-50 rounded-xl">
      <p className="text-[11px] text-slate-400 mb-0.5">{label}</p>
      <p className="text-sm font-medium text-slate-900">{value || '—'}</p>
    </div>
  );
}

function FeeStructureTab() {
  const toast = useToast();
  const { data, isLoading } = useFeeStructures();
  const createMutation = useCreateFeeStructure();
  const updateMutation = useUpdateFeeStructure();
  const deleteMutation = useDeleteFeeStructure();
  const [showAdd, setShowAdd] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [deleteFeeId, setDeleteFeeId] = useState(null);
  const [form, setForm] = useState({ fee_type: '', amount: '', frequency: 'yearly', fee_category: 'tuition', class_id: '', class_section_id: '' });
  const [allClasses, setAllClasses] = useState(false);
  const [selectedClasses, setSelectedClasses] = useState([]);
  const defaultCategories = [
    { value: 'tuition', label: 'Tuition Fee' },
    { value: 'hostel', label: 'Hostel Fee' },
    { value: 'transport', label: 'Transport Fee' },
    { value: 'lab', label: 'Lab Fee' },
    { value: 'library', label: 'Library Fee' },
    { value: 'other', label: 'Other' },
  ];
  const [customCategories, setCustomCategories] = useState(defaultCategories);
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');

  if (isLoading) return <div className="space-y-4">{[1, 2].map(i => <Skeleton key={i} className="h-16 w-full" />)}</div>;

  const structures = data?.structures || [];
  const classes = data?.classes || [];
  const classSections = data?.class_sections || [];
  const categories = customCategories;
  const frequencies = [
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' },
    { value: 'half-yearly', label: 'Half-Yearly' },
    { value: 'yearly', label: 'Yearly' },
    { value: 'one-time', label: 'One-Time' },
  ];

  const handleCreate = async () => {
    if (!form.fee_type || !form.amount) return;
    const basePayload = { fee_type: form.fee_type, amount: parseFloat(form.amount), frequency: form.frequency, fee_category: form.fee_category };

    const entries = [];
    if (allClasses || selectedClasses.length === 0) {
      entries.push({ ...basePayload, class_id: null, class_section_id: null });
    } else {
      for (const sc of selectedClasses) {
        if (sc.allSections) {
          entries.push({ ...basePayload, class_id: sc.classId, class_section_id: null });
        } else {
          for (const secId of sc.sections) {
            entries.push({ ...basePayload, class_id: sc.classId, class_section_id: secId });
          }
          if (sc.sections.length === 0) {
            entries.push({ ...basePayload, class_id: sc.classId, class_section_id: null });
          }
        }
      }
    }

    try {
      for (const entry of entries) {
        await createMutation.mutateAsync(entry);
      }
      setShowAdd(false); resetForm(); toast.success(`${entries.length} fee structure(s) created`);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to create');
    }
  };

  const handleUpdate = () => {
    updateMutation.mutate({ id: editingId, ...form, amount: parseFloat(form.amount), class_id: form.class_id || null, class_section_id: form.class_section_id || null }, {
      onSuccess: () => { setEditingId(null); setShowAdd(false); resetForm(); toast.success('Fee structure updated'); },
      onError: (err) => { toast.error(err.response?.data?.error || 'Failed to update'); },
    });
  };

  const handleDelete = (id) => setDeleteFeeId(id);

  const confirmDeleteFee = () => {
    if (!deleteFeeId) return;
    deleteMutation.mutate(deleteFeeId, {
      onSuccess: () => { setDeleteFeeId(null); toast.success('Fee structure deleted'); },
      onError: (err) => { setDeleteFeeId(null); toast.error(err.response?.data?.error || 'Failed to delete'); },
    });
  };

  const startEdit = (fs) => {
    setForm({ fee_type: fs.fee_type, amount: String(fs.amount), frequency: fs.frequency, fee_category: fs.fee_category, class_id: fs.class_id || '', class_section_id: fs.class_section_id || '' });
    setEditingId(fs.id);
    setShowAdd(true);
  };

  const resetForm = () => { setForm({ fee_type: '', amount: '', frequency: 'yearly', fee_category: 'tuition', class_id: '', class_section_id: '' }); setAllClasses(false); setSelectedClasses([]); };

  const getClassName = (classId) => {
    const cls = classes.find(c => c.id === classId);
    return cls ? cls.display_name : 'All Classes';
  };

  const getCategoryLabel = (val) => categories.find(c => c.value === val)?.label || val;

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-slate-900">Fee Structure</h3>
            <p className="text-xs text-slate-400">Academic Year: {data?.academic_year || '—'}</p>
          </div>
          <Button variant="secondary" size="sm" icon={Plus} onClick={() => { resetForm(); setEditingId(null); setShowAdd(true); }}>Add Fee</Button>
        </div>
        <div className="mb-4 px-3 py-2 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-700">
          <span className="font-semibold">Note:</span> Editing fees here only applies to new students enrolled after the change. Existing students' fee records remain unchanged — use Fee Management to modify individual student fees.
        </div>

        {/* Fee Summary by Class - Annual Total */}
        {structures.length > 0 && classes.length > 0 && (() => {
          const freqMultiplier = (freq) => ({ monthly: 12, quarterly: 4, 'half-yearly': 2, yearly: 1, 'one-time': 1 }[freq] || 1);
          const classTotals = classes.map(cls => {
            const generalFees = structures.filter(fs => !fs.class_id && !fs.class_section_id);
            const classFees = structures.filter(fs => fs.class_id === cls.id && !fs.class_section_id);
            return { cls, annualTotal: [...generalFees, ...classFees].reduce((sum, fs) => sum + Number(fs.amount) * freqMultiplier(fs.frequency), 0) };
          });
          const nonZeroTotals = classTotals.filter(ct => ct.annualTotal > 0);
          const highestTotal = nonZeroTotals.length > 0 ? Math.max(...nonZeroTotals.map(ct => ct.annualTotal)) : 0;
          const lowestTotal = nonZeroTotals.length > 0 ? Math.min(...nonZeroTotals.map(ct => ct.annualTotal)) : 0;
          return (
          <div className="mb-4 grid grid-cols-2 md:grid-cols-5 gap-2">
            {classTotals.map(({ cls, annualTotal }) => {
              const isHighest = annualTotal > 0 && annualTotal === highestTotal && highestTotal !== lowestTotal;
              const isLowest = annualTotal > 0 && annualTotal === lowestTotal && highestTotal !== lowestTotal;
              return (
                <div key={cls.id} className={`px-3 py-2 rounded-lg border text-center ${isHighest ? 'bg-red-50 border-red-200' : isLowest ? 'bg-emerald-50 border-emerald-200' : 'bg-slate-50 border-slate-100'}`}>
                  <p className="text-[10px] font-semibold text-slate-500 uppercase truncate">{cls.display_name || `Class ${cls.name}`}</p>
                  <p className="text-sm font-bold text-slate-800 mt-0.5">{annualTotal > 0 ? `₹${annualTotal.toLocaleString()}` : '—'}</p>
                  <p className="text-[9px] text-slate-400">per year</p>
                  {isHighest && <p className="text-[9px] font-semibold text-red-600 mt-0.5">Highest</p>}
                  {isLowest && <p className="text-[9px] font-semibold text-emerald-600 mt-0.5">Lowest</p>}
                </div>
              );
            })}
          </div>
          );
        })()}

        {structures.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 items-start max-h-[70vh] overflow-y-auto">
            {/* General fees (no class assigned) */}
            {(() => {
              const generalFees = structures.filter(fs => !fs.class_id && !fs.class_section_id);
              const generalTotal = generalFees.reduce((sum, fs) => sum + Number(fs.amount), 0);
              if (generalFees.length === 0) return null;
              return (
                <div className="bg-white border border-slate-200 border-l-4 border-l-slate-500 rounded-xl p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300 lg:col-span-2">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center">
                        <Layers size={18} className="text-slate-600" />
                      </div>
                      <div>
                        <p className="text-base font-bold text-slate-900">All Classes (General)</p>
                        <p className="text-xs text-slate-500">{generalFees.length} fee type{generalFees.length !== 1 ? 's' : ''}</p>
                      </div>
                    </div>
                    <div className="px-4 py-2 rounded-xl bg-gradient-to-br from-emerald-50 to-emerald-100 border border-emerald-200 text-center min-w-[90px]">
                      <p className="text-xs text-emerald-600 font-medium uppercase">Total</p>
                      <p className="text-base font-bold text-emerald-700">₹{generalTotal.toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="mb-4 px-3 py-2 rounded-lg bg-blue-50 border border-blue-100 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4 text-blue-500 shrink-0"><path fillRule="evenodd" d="M15 8A7 7 0 1 1 1 8a7 7 0 0 1 14 0Zm-6 3.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM7.293 5.293a1 1 0 1 1 .99 1.667l-.012.008a.75.75 0 0 0-.386.631V8a.75.75 0 0 0 1.5 0v-.166c0-.03.009-.056.024-.076A2.5 2.5 0 1 0 5.5 6.25a.75.75 0 0 0 1.5 0 1 1 0 0 1 .293-.957Z" clipRule="evenodd" /></svg>
                    <p className="text-xs text-blue-700">These fees are applied to <span className="font-semibold">every class</span> in addition to their class-specific fees.</p>
                  </div>
                  <div className="rounded-lg border border-slate-100 overflow-hidden divide-y divide-slate-100 bg-slate-50/30">
                    {generalFees.map((fs) => (
                      <FeeRow key={fs.id} fs={fs} getCategoryLabel={getCategoryLabel} onEdit={startEdit} onDelete={handleDelete} />
                    ))}
                  </div>
                </div>
              );
            })()}
            {/* Grouped by class */}
            {(() => {
              const generalFees = structures.filter(fs => !fs.class_id && !fs.class_section_id);
              const generalTotal = generalFees.reduce((sum, fs) => sum + Number(fs.amount), 0);
              return classes.map((cls, i) => {
              const classFees = structures.filter(fs => fs.class_id === cls.id && !fs.class_section_id);
              const sectionFees = structures.filter(fs => fs.class_id === cls.id && fs.class_section_id);
              const classTotal = classFees.reduce((sum, fs) => sum + Number(fs.amount), 0);
              const baseTotal = classTotal + generalTotal;
              const sectionGroups = Object.values(sectionFees.reduce((groups, fs) => { const key = fs.class_section_id; (groups[key] = groups[key] || []).push(fs); return groups; }, {}));
              const sectionTotals = sectionGroups.map(fees => fees.reduce((sum, fs) => sum + Number(fs.amount), 0) + baseTotal);
              const minTotal = sectionTotals.length > 0 ? Math.min(...sectionTotals) : baseTotal;
              const maxTotal = sectionTotals.length > 0 ? Math.max(...sectionTotals) : baseTotal;
              const effectiveTotal = sectionFees.length === 0 ? baseTotal : null;
              const colors = ['border-l-blue-500', 'border-l-purple-500', 'border-l-emerald-500', 'border-l-amber-500', 'border-l-pink-500', 'border-l-indigo-500'];
              const iconBgs = ['from-blue-50 to-blue-100', 'from-purple-50 to-purple-100', 'from-emerald-50 to-emerald-100', 'from-amber-50 to-amber-100', 'from-pink-50 to-pink-100', 'from-indigo-50 to-indigo-100'];
              const iconTexts = ['text-blue-700', 'text-purple-700', 'text-emerald-700', 'text-amber-700', 'text-pink-700', 'text-indigo-700'];
              const leftColor = colors[i % colors.length];
              const iconBg = iconBgs[i % iconBgs.length];
              const iconText = iconTexts[i % iconTexts.length];
              const hasFees = classFees.length > 0 || sectionFees.length > 0;
              return (
                <div key={cls.id} className={`bg-white border border-slate-200 ${leftColor} border-l-4 rounded-xl p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300`}>
                  {/* Header */}
                  <div className={`flex items-center justify-between ${(hasFees || generalFees.length > 0) ? 'mb-4' : ''}`}>
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${iconBg} flex items-center justify-center`}>
                        <span className={`text-xs font-bold ${iconText}`}>{cls.name}</span>
                      </div>
                      <div>
                        <p className="text-base font-bold text-slate-900">{cls.display_name}</p>
                        <p className="text-xs text-slate-500">
                          {hasFees ? `${classFees.length + sectionFees.length} class-specific fee${(classFees.length + sectionFees.length) !== 1 ? 's' : ''}` : 'No class-specific fees'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {(hasFees || generalFees.length > 0) && (
                        <div className="px-4 py-2 rounded-xl bg-gradient-to-br from-emerald-50 to-emerald-100 border border-emerald-200 text-center min-w-[90px]">
                          <p className="text-xs text-emerald-600 font-medium uppercase">{effectiveTotal !== null ? 'Effective Total' : 'Range'}</p>
                          <p className="text-base font-bold text-emerald-700">{effectiveTotal !== null ? `₹${effectiveTotal.toLocaleString()}` : minTotal === maxTotal ? `₹${minTotal.toLocaleString()}` : `₹${minTotal.toLocaleString()} – ₹${maxTotal.toLocaleString()}`}</p>
                        </div>
                      )}
                      <button onClick={() => { resetForm(); setSelectedClasses([{ classId: cls.id, allSections: true, sections: [] }]); setAllClasses(false); setEditingId(null); setShowAdd(true); }} className="w-8 h-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-400 hover:bg-primary-50 hover:text-primary-600 hover:border-primary-200 transition-colors" title="Add Fee">
                        <Plus size={14} />
                      </button>
                    </div>
                  </div>
                  {/* Fee rows */}
                  {(hasFees || generalFees.length > 0) && (
                    <>
                      {classFees.length > 0 && (
                        <div className="rounded-lg border border-slate-100 overflow-hidden divide-y divide-slate-100 bg-slate-50/30">
                          {classFees.map((fs) => (
                            <FeeRow key={fs.id} fs={fs} getCategoryLabel={getCategoryLabel} onEdit={startEdit} onDelete={handleDelete} />
                          ))}
                        </div>
                      )}
                      {sectionFees.length > 0 && (
                        <div className={`${classFees.length > 0 ? 'mt-3' : ''} rounded-lg border border-amber-100 overflow-hidden`}>
                          <p className="px-4 py-2 text-xs font-semibold text-amber-700 uppercase tracking-wider bg-amber-50/60 border-b border-amber-100">Section-specific</p>
                          <div className="divide-y divide-amber-100/60 bg-amber-50/20">
                            {Object.entries(sectionFees.reduce((groups, fs) => {
                              const sec = classSections.find(cs => cs.id === fs.class_section_id);
                              const label = sec?.display_name || 'Unknown Section';
                              (groups[label] = groups[label] || []).push(fs);
                              return groups;
                            }, {})).map(([secName, fees]) => {
                              const sectionTotal = fees.reduce((sum, fs) => sum + Number(fs.amount), 0) + classTotal + generalTotal;
                              return (
                              <div key={secName}>
                                <div className="flex items-center justify-between px-5 py-1.5 bg-amber-50/80">
                                  <p className="text-[11px] font-semibold text-amber-800">{secName}</p>
                                  <p className="text-[11px] font-bold text-amber-700">Total: ₹{sectionTotal.toLocaleString()}</p>
                                </div>
                                {fees.map((fs) => (
                                  <FeeRow key={fs.id} fs={fs} getCategoryLabel={getCategoryLabel} onEdit={startEdit} onDelete={handleDelete} />
                                ))}
                              </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                      {generalFees.length > 0 && (
                        <div className={`${hasFees ? 'mt-3' : ''} rounded-lg border border-slate-200 overflow-hidden bg-slate-50/50`}>
                          <p className="px-4 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider bg-slate-100/80 border-b border-slate-200">General (applies to all classes)</p>
                          <div className="divide-y divide-slate-100">
                            {generalFees.map((fs) => (
                              <div key={fs.id} className="flex items-center justify-between px-5 py-3 opacity-70">
                                <div className="flex items-center gap-3 min-w-0 flex-1">
                                  <div className="w-2 h-2 rounded-full bg-slate-300 shrink-0" />
                                  <p className="text-sm font-medium text-slate-600 truncate">{fs.fee_type}</p>
                                  <span className="hidden sm:inline-flex px-2 py-0.5 rounded-md bg-slate-100 text-[10px] font-medium text-slate-400 shrink-0">{getCategoryLabel(fs.fee_category)}</span>
                                  <span className="hidden sm:inline-flex px-2 py-0.5 rounded-md bg-slate-100 text-[10px] font-medium text-slate-400 shrink-0 capitalize">{fs.frequency}</span>
                                </div>
                                <p className="text-sm font-bold text-slate-500 tabular-nums shrink-0 ml-3">₹{Number(fs.amount).toLocaleString()}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              );
            });
            })()}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-3">
              <IndianRupee size={24} className="text-slate-300" />
            </div>
            <p className="text-sm font-medium text-slate-500">No fee structures configured yet</p>
            <p className="text-xs text-slate-400 mt-1">Click "Add Fee" to get started</p>
          </div>
        )}
      </div>

      {/* Add/Edit Modal */}
      <Modal open={showAdd} onClose={() => { setShowAdd(false); setEditingId(null); resetForm(); }} title={editingId ? 'Edit Fee Structure' : 'Add Fee Structure'} size="md">
        <div className="space-y-4">
          <div className="px-3 py-2 rounded-lg bg-amber-50 border border-amber-100 text-xs text-amber-700">
            <strong>Note:</strong> Hostel fee applies only to hostellers. Transport fee applies only to day scholars.
          </div>
          <FormField label="Fee Name *" value={form.fee_type} onChange={v => setForm({ ...form, fee_type: v })} placeholder="e.g., Tuition Fee, Hostel Fee" />
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Amount (₹) *" value={form.amount} onChange={v => setForm({ ...form, amount: v })} type="number" placeholder="5000" />
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Frequency</label>
              <SearchableSelect
                value={form.frequency}
                onChange={(val) => setForm({ ...form, frequency: val })}
                options={frequencies}
                placeholder="Select frequency"
              />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <label className="text-sm font-medium text-slate-700">Category</label>
              <button type="button" onClick={() => setShowAddCategory(true)} className="text-xs text-primary-600 hover:text-primary-700 font-medium">+ Add Category</button>
            </div>
            {showAddCategory && (
              <div className="flex items-center gap-2 mb-2">
                <input
                  type="text" value={newCategoryName} onChange={e => setNewCategoryName(e.target.value)}
                  placeholder="Category name" className="flex-1 border border-slate-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <Button size="sm" onClick={() => {
                  if (newCategoryName.trim()) {
                    const val = newCategoryName.trim().toLowerCase().replace(/\s+/g, '_');
                    setCustomCategories(prev => [...prev, { value: val, label: newCategoryName.trim() }]);
                    setForm(f => ({ ...f, fee_category: val }));
                    setNewCategoryName(''); setShowAddCategory(false);
                  }
                }}>Add</Button>
                <Button size="sm" variant="ghost" onClick={() => { setShowAddCategory(false); setNewCategoryName(''); }}>Cancel</Button>
              </div>
            )}
            <SearchableSelect
              value={form.fee_category}
              onChange={(val) => setForm({ ...form, fee_category: val })}
              options={categories}
              placeholder="Select category"
            />
            {form.fee_category === 'hostel' && (
              <span className="inline-flex mt-1.5 px-2 py-0.5 rounded-md bg-blue-50 text-[11px] font-medium text-blue-700 border border-blue-100">Applies to: Hostellers only</span>
            )}
            {form.fee_category === 'transport' && (
              <span className="inline-flex mt-1.5 px-2 py-0.5 rounded-md bg-green-50 text-[11px] font-medium text-green-700 border border-green-100">Applies to: Day Scholars only</span>
            )}
          </div>

          {/* Class selection - multiselect */}
          {!editingId && (
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Classes</label>
              <label className="flex items-center gap-2 cursor-pointer mb-2">
                <input type="checkbox" checked={allClasses} onChange={e => { setAllClasses(e.target.checked); if (e.target.checked) setSelectedClasses([]); }} className="w-4 h-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
                <span className="text-sm text-slate-700">All Classes (General fee)</span>
              </label>
              {!allClasses && (
                <>
                  {/* Selected classes pill tags */}
                  {selectedClasses.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-2">
                      {selectedClasses.map(sc => {
                        const cls = classes.find(c => c.id === sc.classId);
                        if (!cls) return null;
                        const sectionLabel = sc.allSections ? 'All sections' : sc.sections.length > 0 ? `${sc.sections.length} section(s)` : 'All sections';
                        return (
                          <span key={sc.classId} className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-indigo-50 border border-indigo-200 rounded-full text-xs font-medium text-indigo-700">
                            {cls.display_name} <span className="text-indigo-400 font-normal">· {sectionLabel}</span>
                            <button type="button" onClick={() => setSelectedClasses(prev => prev.filter(s => s.classId !== sc.classId))} className="ml-0.5 text-indigo-400 hover:text-red-500 transition-colors font-bold">×</button>
                          </span>
                        );
                      })}
                    </div>
                  )}
                  <div className="border border-slate-200 rounded-lg p-3 max-h-52 overflow-y-auto space-y-2">
                    {classes.map(cls => {
                      const sel = selectedClasses.find(sc => sc.classId === cls.id);
                      const isChecked = !!sel;
                      return (
                        <div key={cls.id} className={`space-y-1 rounded-lg p-2 transition-colors ${isChecked ? 'bg-indigo-50/50 border border-indigo-100' : 'hover:bg-slate-50'}`}>
                          <label className="flex items-center gap-2 cursor-pointer">
                            <input type="checkbox" checked={isChecked} onChange={e => {
                              if (e.target.checked) setSelectedClasses(prev => [...prev, { classId: cls.id, allSections: true, sections: [] }]);
                              else setSelectedClasses(prev => prev.filter(sc => sc.classId !== cls.id));
                            }} className="w-4 h-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
                            <span className={`text-sm font-medium ${isChecked ? 'text-indigo-700' : 'text-slate-800'}`}>{cls.display_name}</span>
                            {isChecked && <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-600 font-medium">Selected</span>}
                          </label>
                          {isChecked && (
                            <div className="ml-6 pl-3 border-l-2 border-indigo-200 space-y-1 mt-1">
                              <label className="flex items-center gap-2 cursor-pointer">
                                <input type="checkbox" checked={sel.allSections} onChange={e => {
                                  setSelectedClasses(prev => prev.map(sc => sc.classId === cls.id ? { ...sc, allSections: e.target.checked, sections: [] } : sc));
                                }} className="w-3.5 h-3.5 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500" />
                                <span className="text-xs text-emerald-700 font-medium">Same for all sections</span>
                              </label>
                              {!sel.allSections && (
                                <div className="ml-4 space-y-0.5">
                                  {classSections.filter(cs => cs.class_id === cls.id).map(cs => (
                                    <label key={cs.id} className="flex items-center gap-2 cursor-pointer">
                                      <input type="checkbox" checked={sel.sections.includes(cs.id)} onChange={e => {
                                        setSelectedClasses(prev => prev.map(sc => sc.classId === cls.id ? { ...sc, sections: e.target.checked ? [...sc.sections, cs.id] : sc.sections.filter(s => s !== cs.id) } : sc));
                                      }} className="w-3.5 h-3.5 rounded border-slate-300 text-amber-600 focus:ring-amber-500" />
                                      <span className="text-xs text-amber-700">{cs.display_name}</span>
                                    </label>
                                  ))}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                  {/* Selection summary */}
                  {selectedClasses.length > 0 && (
                    <div className="mt-2 px-3 py-2 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600">
                      <span className="font-medium text-slate-700">Summary:</span> Fee applies to{' '}
                      <span className="font-semibold text-indigo-700">{selectedClasses.length} class{selectedClasses.length !== 1 ? 'es' : ''}</span>
                      {selectedClasses.some(sc => !sc.allSections && sc.sections.length > 0) && (
                        <> with <span className="font-semibold text-amber-700">{selectedClasses.reduce((sum, sc) => sum + (!sc.allSections ? sc.sections.length : 0), 0)} specific section(s)</span></>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {/* Edit mode - single class/section (keep simple) */}
          {editingId && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-700 mb-1.5 block">Class</label>
                <SearchableSelect
                  value={form.class_id}
                  onChange={(val) => setForm({ ...form, class_id: val, class_section_id: '' })}
                  options={[{ value: '', label: 'All Classes' }, ...classes.map(c => ({ value: c.id, label: c.display_name }))]}
                  placeholder="Select class"
                />
              </div>
              {form.class_id && (
                <div>
                  <label className="text-sm font-medium text-slate-700 mb-1.5 block">Section</label>
                  <SearchableSelect
                    value={form.class_section_id}
                    onChange={(val) => setForm({ ...form, class_section_id: val })}
                    options={[{ value: '', label: 'All Sections' }, ...classSections.filter(cs => cs.class_id === form.class_id).map(cs => ({ value: cs.id, label: cs.display_name }))]}
                    placeholder="Select section"
                  />
                </div>
              )}
            </div>
          )}
        </div>
        <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
          <Button variant="ghost" onClick={() => { setShowAdd(false); setEditingId(null); resetForm(); }}>Cancel</Button>
          <Button onClick={editingId ? handleUpdate : handleCreate} loading={createMutation.isPending || updateMutation.isPending} disabled={!form.fee_type || !form.amount}>
            {editingId ? 'Update' : 'Create'}
          </Button>
        </div>
      </Modal>

      <ConfirmDialog open={!!deleteFeeId} onClose={() => setDeleteFeeId(null)} onConfirm={confirmDeleteFee} loading={deleteMutation.isPending} title="Delete Fee Structure" message="Are you sure you want to delete this fee structure? This action cannot be undone." />
    </div>
  );
}

function FeeRow({ fs, getCategoryLabel, onEdit, onDelete }) {
  return (
    <div className="group flex items-center justify-between px-5 py-3.5 hover:bg-slate-50/80 transition-colors">
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <div className="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
        <p className="text-sm font-medium text-slate-800 truncate">{fs.fee_type}</p>
        <span className="hidden sm:inline-flex px-2 py-0.5 rounded-md bg-slate-100 text-[10px] font-medium text-slate-500 shrink-0">{getCategoryLabel(fs.fee_category)}</span>
        <span className="hidden sm:inline-flex px-2 py-0.5 rounded-md bg-slate-100 text-[10px] font-medium text-slate-500 shrink-0 capitalize">{fs.frequency}</span>
      </div>
      <div className="flex items-center gap-2 shrink-0 ml-3">
        <p className="text-sm font-bold text-slate-800 tabular-nums">₹{Number(fs.amount).toLocaleString()}</p>
        <div className="flex items-center gap-0.5">
          <button onClick={() => onEdit(fs)} className="p-1.5 rounded-lg text-slate-400 hover:text-primary-600 hover:bg-primary-50 transition-colors" title="Edit">
            <Pencil size={13} />
          </button>
          <button onClick={() => onDelete(fs.id)} className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors" title="Delete">
            <Trash2 size={13} />
          </button>
        </div>
      </div>
    </div>
  );
}

function FormField({ label, value, onChange, type = 'text', placeholder, error }) {
  if (type === 'date') {
    return <DateInput label={label} value={value} onChange={onChange} />;
  }
  return (
    <div>
      <label className="text-sm font-medium text-slate-700 mb-1.5 block">{label}</label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${error ? 'border-red-400' : 'border-slate-300'}`}
      />
      {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
    </div>
  );
}

function ClassSubjectRow({ cls, allSubjects, updateClassSubjects, toast }) {
  const assignedIds = cls.subjects.map(s => s.id);
  const unassignedOptions = allSubjects.filter(s => !assignedIds.includes(s.id)).map(s => ({ value: s.id, label: s.name }));

  const handleAdd = (subjectId) => {
    if (!subjectId) return;
    const updated = [...assignedIds, subjectId];
    updateClassSubjects.mutate({ classId: cls.id, subject_ids: updated }, {
      onSuccess: () => { toast.success(`Subject added to ${cls.display_name}`); },
      onError: (err) => { toast.error(err.response?.data?.error || 'Failed to update'); },
    });
  };

  const handleRemove = (subjectId) => {
    const updated = assignedIds.filter(id => id !== subjectId);
    updateClassSubjects.mutate({ classId: cls.id, subject_ids: updated }, {
      onSuccess: () => { toast.success('Subject removed'); },
      onError: (err) => { toast.error(err.response?.data?.error || 'Failed to update'); },
    });
  };

  return (
    <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
      <div className="flex items-center justify-between mb-2.5">
        <p className="text-sm font-semibold text-slate-800">{cls.display_name}</p>
        <div className="w-48">
          <SearchableSelect
            value=""
            onChange={handleAdd}
            options={unassignedOptions}
            placeholder="+ Add subject"
            showSearch
          />
        </div>
      </div>
      {cls.subjects.length > 0 ? (
        <div className="flex flex-wrap gap-1.5">
          {cls.subjects.map(sub => (
            <span key={sub.id} className="inline-flex items-center gap-1 px-2.5 py-1 bg-indigo-50 border border-indigo-200 rounded-md text-xs font-medium text-indigo-700">
              {sub.name}
              <button onClick={() => handleRemove(sub.id)} className="ml-0.5 text-indigo-400 hover:text-red-500 transition-colors">×</button>
            </span>
          ))}
        </div>
      ) : (
        <p className="text-xs text-slate-400 italic">No subjects assigned</p>
      )}
    </div>
  );
}

function ClassCard({ cls, onAddSection, onDeleteClass, onDeleteSection }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white border border-slate-200 rounded-xl transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-sm">
            <span className="text-sm font-black text-white">{cls.name}</span>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-900">{cls.display_name || `Class ${cls.name}`}</h4>
            <div className="flex items-center gap-1.5 mt-0.5">
              {cls.sections.length > 0 ? (
                <div className="flex gap-1">
                  {[...cls.sections].sort((a, b) => a.section_name.localeCompare(b.section_name)).map(sec => (
                    <span key={sec.id} className="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 px-1.5 py-0.5 rounded font-medium">{sec.section_name}</span>
                  ))}
                </div>
              ) : (
                <span className="text-[10px] text-slate-400">No sections</span>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button onClick={(e) => { e.stopPropagation(); onAddSection(); }} className="p-1.5 rounded-lg text-slate-400 hover:text-primary-600 hover:bg-primary-50 transition-colors" title="Add Section">
            <Plus size={14} />
          </button>
          <button onClick={(e) => { e.stopPropagation(); onDeleteClass(); }} className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors" title="Delete Class">
            <Trash2 size={14} />
          </button>
          <ChevronDown size={14} className={`text-slate-400 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`} />
        </div>
      </div>

      {/* Sections list - expandable */}
      {expanded && cls.sections.length > 0 && (
        <div className="border-t border-slate-100 px-4 py-2 bg-slate-50/50">
          <div className="flex flex-wrap gap-2">
            {[...cls.sections].sort((a, b) => a.section_name.localeCompare(b.section_name)).map((sec) => (
              <div key={sec.id} className="flex items-center gap-1.5 bg-white border border-slate-200 rounded-lg px-3 py-1.5 group">
                <span className="text-xs font-medium text-slate-700">Section {sec.section_name}</span>
                <button onClick={() => onDeleteSection(sec)} className="text-slate-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100">
                  <Trash2 size={11} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {expanded && cls.sections.length === 0 && (
        <div className="border-t border-slate-100 px-5 py-4 text-center">
          <p className="text-xs text-slate-400">No sections yet. Click "Add Section" to create one.</p>
        </div>
      )}
    </div>
  );
}

function TimetableSettingsTab() {
  const toast = useToast();
  const { data: slotTypesData, isLoading } = useSlotTypes();
  const updateSlotTypes = useUpdateSlotTypes();
  const [types, setTypes] = useState([]);
  const [newType, setNewType] = useState('');
  const [initialized, setInitialized] = useState(false);

  const defaultTypes = ['Subject', 'Sports', 'Special Class', 'Library', 'Other'];

  if (!initialized && slotTypesData) {
    const existing = (slotTypesData.values || []).map(v => v.value || v.code || v);
    setTypes(existing.length > 0 ? existing : defaultTypes);
    setInitialized(true);
  }

  const addType = () => {
    const val = newType.trim();
    if (!val || types.includes(val)) return;
    const updated = [...types, val];
    setTypes(updated);
    setNewType('');
    saveTypes(updated);
  };

  const removeType = (idx) => {
    if (types[idx] === 'Subject') return;
    const updated = types.filter((_, i) => i !== idx);
    setTypes(updated);
    saveTypes(updated);
  };

  const saveTypes = (values) => {
    updateSlotTypes.mutate(values.map((v, i) => ({ value: v, label: v, sort_order: i })), {
      onSuccess: () => toast.success('Slot types updated'),
      onError: () => toast.error('Failed to update slot types'),
    });
  };

  if (isLoading) return <div className="animate-pulse text-slate-400 py-8 text-center">Loading...</div>;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="mb-5">
        <h3 className="text-base font-semibold text-slate-900">Timetable Slot Types</h3>
        <p className="text-xs text-slate-500 mt-1">Configure what types of periods can be scheduled (e.g., Subject, Sports, Special Class). "Subject" is the default and uses subject + conflict-checked teacher assignment.</p>
      </div>

      <div className="flex gap-2 mb-4">
        <input
          value={newType}
          onChange={e => setNewType(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') addType(); }}
          placeholder="Add new slot type (e.g. Lab, Assembly, Yoga)"
          className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        <Button variant="primary" size="sm" icon={Plus} onClick={addType} disabled={!newType.trim()}>Add</Button>
      </div>

      {/* Visual slot type chips */}
      <div className="flex flex-wrap gap-2 mb-4">
        {types.map((type, idx) => {
          const chipColors = ['bg-blue-50 border-blue-200 text-blue-700', 'bg-purple-50 border-purple-200 text-purple-700', 'bg-emerald-50 border-emerald-200 text-emerald-700', 'bg-amber-50 border-amber-200 text-amber-700', 'bg-pink-50 border-pink-200 text-pink-700', 'bg-indigo-50 border-indigo-200 text-indigo-700'];
          const color = type === 'Subject' ? 'bg-primary-50 border-primary-200 text-primary-700' : chipColors[idx % chipColors.length];
          return (
            <div key={idx} className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-medium ${color}`}>
              <span>{type}</span>
              {type === 'Subject' && <span className="text-[9px] opacity-70">(default)</span>}
              {type !== 'Subject' && (
                <button onClick={() => removeType(idx)} className="ml-0.5 p-0.5 rounded-full hover:bg-black/5 transition-colors">
                  <Trash2 size={10} />
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Slot types list (detailed view) */}
      <div className="space-y-2">
        {types.map((type, idx) => (
          <div key={idx} className="flex items-center justify-between px-4 py-2.5 bg-slate-50 rounded-lg border border-slate-100">
            <div className="flex items-center gap-3">
              <span className="w-6 h-6 rounded-md bg-primary-100 text-primary-700 flex items-center justify-center text-[10px] font-bold">{idx + 1}</span>
              <span className="text-sm font-medium text-slate-800">{type}</span>
              {type === 'Subject' && <span className="text-[10px] bg-primary-50 text-primary-600 px-2 py-0.5 rounded font-medium">Default</span>}
            </div>
            {type !== 'Subject' && (
              <button onClick={() => removeType(idx)} className="p-1.5 rounded hover:bg-red-50 text-slate-400 hover:text-red-500 transition-colors">
                <Trash2 size={14} />
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Link to Timetable Builder */}
      <div className="mt-5 p-3 bg-blue-50 border border-blue-100 rounded-lg flex items-center gap-2">
        <Clock size={14} className="text-blue-500 shrink-0" />
        <p className="text-xs text-blue-700">
          Configure period timings and class-specific timetables in the{' '}
          <a href="/admin/timetable" className="font-semibold underline underline-offset-2 hover:text-blue-900">Timetable Builder</a>.
        </p>
      </div>
    </div>
  );
}
