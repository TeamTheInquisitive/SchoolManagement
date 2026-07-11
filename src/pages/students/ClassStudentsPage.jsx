import { useState, useMemo, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Badge, SearchableSelect, Breadcrumb, useToast, ResetPasswordModal, StudentDetailView, Button, Modal, DateInput, ConfirmDialog } from 'school-erp-ui-shared';
import { useStudents, useStudentExamResults, useStudentParentMeetings, useStudentActivities, useStudentFeeHistory, useStudentDisciplinaryRecords, useUpdateStudent, useCreateAward, useUpdateAward, useDeleteAward, useCreateActivity, useUpdateActivity, useDeleteActivity, useCreateParentMeeting, useUpdateParentMeeting, useDeleteParentMeeting, useCreateDisciplinaryRecord, useUpdateDisciplinaryRecord, useDeleteDisciplinaryRecord, useResetStudentPassword } from '../../services/studentService';
import { useClassSectionFilter } from '../../hooks/useClassSectionFilter';
import { useHolidays } from '../../services/settingsService';
import { PieChart, Pie, Cell, Legend as RLegend, ResponsiveContainer } from 'recharts';
import { Users, Search } from 'lucide-react';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';

export default function ClassStudentsPage() {
  const { className: urlClassName, sectionName: urlSectionName, studentId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();

  const { classOptions: rawClassOptions, sectionOptions: rawSectionOptions, classes: allClasses, setSelectedClass: setFilterClass, setSelectedSection: setFilterSection } = useClassSectionFilter();

  const uniqueClassNames = useMemo(() => {
    if (!allClasses) return [];
    return [...new Set(allClasses.map(c => c.name))].sort();
  }, [allClasses]);

  const classOptions = [
    ...uniqueClassNames.map(c => ({ value: c, label: `Class ${c}` }))
  ];

  const [selectedClassName, setSelectedClassName] = useState(urlClassName || '');
  const [selectedSectionName, setSelectedSectionName] = useState(urlSectionName || '');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 30;

  useEffect(() => {
    if (urlClassName) setSelectedClassName(urlClassName);
    if (urlSectionName) setSelectedSectionName(urlSectionName);
  }, [urlClassName, urlSectionName]);

  const activeClassName = selectedClassName;
  const activeSectionName = selectedSectionName;

  const sectionOptions = useMemo(() => {
    if (!activeClassName || !allClasses) return [];
    const cls = allClasses.find(c => c.name === activeClassName);
    if (!cls || !cls.sections) return [];
    return cls.sections.map(s => ({ value: s.section_name, label: s.section_name }));
  }, [activeClassName, allClasses]);

  // Fetch students for selected class/section
  const { data: studentsData, isLoading: studentsLoading } = useStudents({
    class_name: activeClassName || undefined,
    section: activeSectionName || undefined,
    search: search || undefined,
    page,
    page_size: pageSize,
    status: 'Active',
  });

  const students = studentsData?.results || [];
  const totalPages = studentsData?.total_pages || 1;

  // Fetch student detail if studentId is in URL
  const { data: studentData, isLoading: detailLoading } = useQuery({
    queryKey: ['students', 'detail', studentId],
    queryFn: () => api.get(`/admin/students/${studentId}`).then(r => r.data),
    enabled: !!studentId,
    placeholderData: (prev) => prev,
  });
  const { data: examResultsData } = useStudentExamResults(studentId);
  const { data: meetingsData } = useStudentParentMeetings(studentId);
  const { data: activitiesData } = useStudentActivities(studentId);
  const { data: feeHistoryData } = useStudentFeeHistory(studentId);
  const { data: disciplinaryData } = useStudentDisciplinaryRecords(studentId);

  const updateStudent = useUpdateStudent();
  const createAward = useCreateAward();
  const updateAward = useUpdateAward();
  const deleteAward = useDeleteAward();
  const createActivity = useCreateActivity();
  const updateActivity = useUpdateActivity();
  const deleteActivity = useDeleteActivity();
  const createParentMeeting = useCreateParentMeeting();
  const updateParentMeeting = useUpdateParentMeeting();
  const deleteParentMeeting = useDeleteParentMeeting();
  const createDisciplinary = useCreateDisciplinaryRecord();
  const updateDisciplinary = useUpdateDisciplinaryRecord();
  const deleteDisciplinary = useDeleteDisciplinaryRecord();
  const resetPassword = useResetStudentPassword();

  const [editingSection, setEditingSection] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [resetPwOpen, setResetPwOpen] = useState(false);
  const [resetPwLoading, setResetPwLoading] = useState(false);

  // Modal states
  const [awardModalOpen, setAwardModalOpen] = useState(false);
  const [editingAward, setEditingAward] = useState(null);
  const [awardForm, setAwardForm] = useState({ title: '', category: '', description: '', awarded_date: '', awarded_by: '', level: '' });
  const [activityModalOpen, setActivityModalOpen] = useState(false);
  const [editingActivity, setEditingActivity] = useState(null);
  const [activityForm, setActivityForm] = useState({ name: '', activity_type: '', description: '', role: '', start_date: '', end_date: '', achievement: '' });
  const [meetingModalOpen, setMeetingModalOpen] = useState(false);
  const [editingMeeting, setEditingMeeting] = useState(null);
  const [meetingForm, setMeetingForm] = useState({ meeting_date: '', meeting_type: '', agenda: '', discussion_notes: '', remarks: '', follow_up_required: false, parent_attended: true, next_meeting_date: '' });
  const [disciplinaryModalOpen, setDisciplinaryModalOpen] = useState(false);
  const [editingDisciplinary, setEditingDisciplinary] = useState(null);
  const [disciplinaryForm, setDisciplinaryForm] = useState({ incident_date: '', category: '', severity: '', description: '', action_taken: '', parent_notified: false, status: 'Open' });
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Class/section change handlers
  const handleClassChange = (val) => {
    setSearch('');
    setPage(1);
    setSelectedClassName(val);
    if (val && allClasses) {
      const cls = allClasses.find(c => c.name === val);
      const firstSection = cls?.sections?.[0]?.section_name || '';
      setSelectedSectionName(firstSection);
      if (firstSection) {
        navigate(`/admin/students/${val}/${firstSection}`, { replace: true });
      }
    }
  };

  const handleSectionChange = (val) => {
    setSelectedSectionName(val);
    setSearch('');
    setPage(1);
    if (val) {
      navigate(`/admin/students/${activeClassName}/${val}`, { replace: true });
    }
  };

  const handleStudentClick = (sid) => {
    navigate(`/admin/students/${activeClassName}/${activeSectionName}/${sid}`);
  };

  // Build student detail
  const raw = studentData ?? {};
  const studentDetail = {
    name: raw.full_name || '', roll: raw.roll_number || '', class: raw.class_name ? `${raw.class_name}-${raw.section || ''}` : '', email: raw.email || '', phone: raw.phone || '', type: raw.type || '',
    personal: { dob: raw.date_of_birth || '', admissionDate: raw.admission_date || '', address: raw.address || '' },
    parent: { name: raw.parent?.name || '', phone: raw.parent?.phone || '', email: raw.parent?.email || '', emergency: raw.parent?.emergency_contact || '', relationship: raw.parent?.relationship || '' },
    parents: raw.parents || [],
    medical: { bloodGroup: raw.medical?.blood_group || '', gender: raw.gender || '', religion: raw.medical?.religion || '', conditions: raw.medical?.conditions || '' },
    mentor: { name: raw.mentor?.name || '', subject: raw.mentor?.subject || '', qualification: raw.mentor?.qualification || '', email: raw.mentor?.email || '', phone: raw.mentor?.phone || '' },
    class_teacher: raw.class_teacher || null,
    stats: raw.stats || {},
    transport: raw.transport || { enrolled: false },
  };
  const examData = Array.isArray(examResultsData?.exams) ? examResultsData.exams : Array.isArray(examResultsData) ? examResultsData : [];
  const meetings = Array.isArray(meetingsData?.meetings) ? meetingsData.meetings : Array.isArray(meetingsData) ? meetingsData : [];
  const activitiesObj = { activities: Array.isArray(activitiesData?.extra_curricular) ? activitiesData.extra_curricular : [], awards: Array.isArray(activitiesData?.awards) ? activitiesData.awards : [] };
  const feeHistoryObj = { structure: Array.isArray(feeHistoryData?.fee_structure) ? feeHistoryData.fee_structure : Array.isArray(feeHistoryData?.structure) ? feeHistoryData.structure : [], payments: Array.isArray(feeHistoryData?.payments) ? feeHistoryData.payments : [] };
  const disciplinary = Array.isArray(disciplinaryData?.records) ? disciplinaryData.records : Array.isArray(disciplinaryData) ? disciplinaryData : [];

  // Award modal handlers
  const handleOpenAwardModal = (award = null) => {
    if (award) {
      setEditingAward(award);
      setAwardForm({ title: award.title || award.name || '', category: award.category || '', description: award.description || '', awarded_date: award.awarded_date || '', awarded_by: award.awarded_by || '', level: award.level || '' });
    } else {
      setEditingAward(null);
      setAwardForm({ title: '', category: '', description: '', awarded_date: '', awarded_by: '', level: '' });
    }
    setAwardModalOpen(true);
  };

  const handleSaveAward = () => {
    const data = Object.fromEntries(Object.entries(awardForm).filter(([, v]) => v));
    if (editingAward) {
      updateAward.mutate({ studentId, awardId: editingAward.id, data }, { onSuccess: () => { setAwardModalOpen(false); toast.success('Award updated'); } });
    } else {
      createAward.mutate({ studentId, data }, { onSuccess: () => { setAwardModalOpen(false); toast.success('Award added'); } });
    }
  };

  // Activity modal handlers
  const handleOpenActivityModal = (activity = null) => {
    if (activity) {
      setEditingActivity(activity);
      setActivityForm({ name: activity.name || activity.activity_name || '', activity_type: activity.activity_type || '', description: activity.description || '', role: activity.role || '', start_date: activity.start_date || '', end_date: activity.end_date || '', achievement: activity.achievement || '' });
    } else {
      setEditingActivity(null);
      setActivityForm({ name: '', activity_type: '', description: '', role: '', start_date: '', end_date: '', achievement: '' });
    }
    setActivityModalOpen(true);
  };

  const handleSaveActivity = () => {
    const data = Object.fromEntries(Object.entries(activityForm).filter(([, v]) => v));
    if (editingActivity) {
      updateActivity.mutate({ studentId, activityId: editingActivity.id, data }, { onSuccess: () => { setActivityModalOpen(false); toast.success('Activity updated'); } });
    } else {
      createActivity.mutate({ studentId, data }, { onSuccess: () => { setActivityModalOpen(false); toast.success('Activity added'); } });
    }
  };

  // Meeting modal handlers
  const handleOpenMeetingModal = (meeting = null) => {
    if (meeting) {
      setEditingMeeting(meeting);
      setMeetingForm({ meeting_date: meeting.meeting_date || '', meeting_type: meeting.meeting_type || '', agenda: meeting.agenda || '', discussion_notes: meeting.discussion_notes || '', remarks: meeting.remarks || '', follow_up_required: meeting.follow_up_required || false, parent_attended: meeting.parent_attended !== false, next_meeting_date: meeting.next_meeting_date || '' });
    } else {
      setEditingMeeting(null);
      setMeetingForm({ meeting_date: '', meeting_type: '', agenda: '', discussion_notes: '', remarks: '', follow_up_required: false, parent_attended: true, next_meeting_date: '' });
    }
    setMeetingModalOpen(true);
  };

  const handleSaveMeeting = () => {
    const data = Object.fromEntries(Object.entries(meetingForm).filter(([, v]) => v !== '' && v !== undefined && v !== null));
    if (editingMeeting) {
      updateParentMeeting.mutate({ studentId, meetingId: editingMeeting.id, data }, { onSuccess: () => { setMeetingModalOpen(false); toast.success('Meeting updated'); } });
    } else {
      createParentMeeting.mutate({ studentId, data }, { onSuccess: () => { setMeetingModalOpen(false); toast.success('Meeting added'); } });
    }
  };

  // Disciplinary modal handlers
  const handleOpenDisciplinaryModal = (record = null) => {
    if (record) {
      setEditingDisciplinary(record);
      setDisciplinaryForm({ incident_date: record.incident_date || '', category: record.category || '', severity: record.severity || '', description: record.description || '', action_taken: record.action_taken || '', parent_notified: record.parent_notified || false, status: record.status || 'Open' });
    } else {
      setEditingDisciplinary(null);
      setDisciplinaryForm({ incident_date: '', category: '', severity: '', description: '', action_taken: '', parent_notified: false, status: 'Open' });
    }
    setDisciplinaryModalOpen(true);
  };

  const handleSaveDisciplinary = () => {
    const data = Object.fromEntries(Object.entries(disciplinaryForm).filter(([, v]) => v !== '' && v !== undefined && v !== null));
    if (editingDisciplinary) {
      updateDisciplinary.mutate({ studentId, recordId: editingDisciplinary.id, data }, { onSuccess: () => { setDisciplinaryModalOpen(false); toast.success('Record updated'); } });
    } else {
      createDisciplinary.mutate({ studentId, data }, { onSuccess: () => { setDisciplinaryModalOpen(false); toast.success('Record added'); } });
    }
  };

  const handleDeleteConfirm = () => {
    if (!deleteConfirm) return;
    const { type, id: itemId } = deleteConfirm;
    if (type === 'award') deleteAward.mutate({ studentId, awardId: itemId }, { onSuccess: () => { setDeleteConfirm(null); toast.success('Award deleted'); } });
    else if (type === 'activity') deleteActivity.mutate({ studentId, activityId: itemId }, { onSuccess: () => { setDeleteConfirm(null); toast.success('Activity deleted'); } });
    else if (type === 'meeting') deleteParentMeeting.mutate({ studentId, meetingId: itemId }, { onSuccess: () => { setDeleteConfirm(null); toast.success('Meeting deleted'); } });
    else if (type === 'disciplinary') deleteDisciplinary.mutate({ studentId, recordId: itemId }, { onSuccess: () => { setDeleteConfirm(null); toast.success('Record deleted'); } });
  };

  const handleResetPassword = async (newPassword) => {
    setResetPwLoading(true);
    try {
      await api.post(ENDPOINTS.students.resetPassword(studentId), { new_password: newPassword });
      toast.success('Password reset successful');
      setResetPwOpen(false);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to reset password');
    }
    setResetPwLoading(false);
  };

  // Sidebar student list
  const studentsList = students.map(s => ({
    id: s.id,
    name: s.full_name || s.name || '',
    roll: s.roll_number || s.roll || '',
    class: s.class_name ? `${s.class_name}-${s.section || ''}` : '',
    avatar: (s.full_name || s.name || '??').slice(0, 2).toUpperCase(),
  }));

  const breadcrumbItems = studentId
    ? [
        { label: 'Dashboard', href: '/admin/dashboard' },
        { label: 'Students', href: '/admin/students' },
        { label: `Class ${activeClassName}-${activeSectionName}`, href: `/admin/students/${activeClassName}/${activeSectionName}` },
        { label: raw.full_name || 'Student Details' },
      ]
    : [
        { label: 'Dashboard', href: '/admin/dashboard' },
        { label: 'Students', href: '/admin/students' },
        { label: `Class ${activeClassName}-${activeSectionName}` },
      ];


  // Student Detail View
  if (studentId && studentData) {
    return (
      <>
        <StudentDetailView
          student={studentDetail}
          examResults={examData}
          meetings={meetings}
          activities={activitiesObj}
          feeHistory={feeHistoryObj}
          disciplinaryRecords={disciplinary}
          students={studentsList}
          selectedStudentId={studentId}
          onSelectStudent={(sid) => handleStudentClick(sid)}
          classFilter={activeClassName}
          setClassFilter={handleClassChange}
          classOptions={classOptions}
          sectionFilter={activeSectionName}
          setSectionFilter={(val) => { if (val) navigate(`/admin/students/${activeClassName}/${val}`); }}
          sectionOptions={sectionOptions}
          searchName={search}
          setSearchName={setSearch}
          breadcrumbItems={breadcrumbItems}
          onPrint={() => window.print()}
          onExportPdf={() => window.print()}
          editingSection={editingSection}
          onEditSection={(section) => {
            const formData = {
              academic: { full_name: raw.full_name || '', email: raw.email || '', phone: raw.phone || '', class_name: raw.class_name || '', section: raw.section || '' },
              personal: { phone: raw.phone || '', email: raw.email || '', date_of_birth: raw.date_of_birth || '', admission_date: raw.admission_date || '', student_type: raw.type || '', address: raw.address || '' },
              parent: { parents: (raw.parents && raw.parents.length ? raw.parents.map(p => ({ name: p.name || '', relationship: p.relationship || '', phone: p.phone || '', email: p.email || '' })) : [{ name: raw.parent?.name || '', relationship: raw.parent?.relationship || 'Father', phone: raw.parent?.phone || '', email: raw.parent?.email || '' }]) },
              medical: { blood_group: raw.medical?.blood_group || '', gender: raw.gender || '', religion: raw.medical?.religion || '', medical_conditions: raw.medical?.conditions || '' },
            };
            setEditForm(formData[section] || {});
            setEditingSection(section);
          }}
          onSaveSection={() => {
            let payload;
            if (Array.isArray(editForm.parents)) {
              const parents = editForm.parents.filter(p => (p.name || '').trim()).map(p => ({ name: p.name.trim(), relationship: p.relationship || 'Parent/Guardian', phone: p.phone || null, email: p.email || null }));
              if (parents.length === 0) { toast.error('At least one parent/guardian is required'); return; }
              const rels = parents.map(p => (p.relationship || '').toLowerCase());
              if (new Set(rels).size !== rels.length) { toast.error('Each parent/guardian must have a unique relationship'); return; }
              payload = { parents };
            } else {
              const allowedFields = ['full_name', 'email', 'phone', 'date_of_birth', 'admission_date', 'gender', 'student_type', 'blood_group', 'religion', 'address', 'parent_name', 'parent_phone', 'parent_email', 'parent_relationship', 'parent_emergency', 'medical_conditions'];
              payload = Object.fromEntries(Object.entries(editForm).filter(([k, v]) => v !== undefined && v !== '' && allowedFields.includes(k)));
            }
            updateStudent.mutate({ id: studentId, data: payload }, { onSuccess: () => { setEditingSection(null); toast.success('Student updated'); } });
          }}
          onFieldChange={(field, value) => setEditForm(prev => ({ ...prev, [field]: value }))}
          editForm={editForm}
          isSaving={updateStudent.isPending}
          onCancelEdit={() => setEditingSection(null)}
          onResetPassword={() => setResetPwOpen(true)}
          onMeetingAdd={() => handleOpenMeetingModal()}
          onMeetingEdit={(m) => handleOpenMeetingModal(m)}
          onMeetingDelete={(m) => setDeleteConfirm({ type: 'meeting', id: m.id, message: 'Delete this meeting?' })}
          onActivityAdd={() => handleOpenActivityModal()}
          onActivityEdit={(a) => handleOpenActivityModal(a)}
          onActivityDelete={(a) => setDeleteConfirm({ type: 'activity', id: a.id, message: 'Delete this activity?' })}
          onAwardAdd={() => handleOpenAwardModal()}
          onAwardEdit={(a) => handleOpenAwardModal(a)}
          onAwardDelete={(a) => setDeleteConfirm({ type: 'award', id: a.id, message: 'Delete this award?' })}
          onDisciplinaryAdd={() => handleOpenDisciplinaryModal()}
          onDisciplinaryEdit={(d) => handleOpenDisciplinaryModal(d)}
          onDisciplinaryDelete={(d) => setDeleteConfirm({ type: 'disciplinary', id: d.id, message: 'Delete this record?' })}
        />

        <AttendanceCalendarSection studentId={studentId} />

        <ResetPasswordModal open={resetPwOpen} onClose={() => setResetPwOpen(false)} onSubmit={handleResetPassword} loading={resetPwLoading} userName={raw.full_name || ''} />

        <ConfirmDialog open={!!deleteConfirm} onClose={() => setDeleteConfirm(null)} onConfirm={handleDeleteConfirm} title="Confirm Delete" message={deleteConfirm?.message || 'Are you sure?'} confirmLabel="Delete" variant="danger" />

        {/* Award Modal */}
        <Modal open={awardModalOpen} onClose={() => setAwardModalOpen(false)} title={editingAward ? 'Edit Award' : 'Add Award'} size="md">
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Title *</label><input value={awardForm.title} onChange={e => setAwardForm({...awardForm, title: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Category</label><SearchableSelect value={awardForm.category} onChange={v => setAwardForm({...awardForm, category: v})} options={[{value:'Academic',label:'Academic'},{value:'Sports',label:'Sports'},{value:'Arts',label:'Arts'},{value:'Leadership',label:'Leadership'},{value:'Co-curricular',label:'Co-curricular'}]} placeholder="Select..." /></div>
            </div>
            <div><label className="text-xs font-medium text-slate-600 mb-1 block">Date</label><DateInput value={awardForm.awarded_date} onChange={(v) => setAwardForm({...awardForm, awarded_date: v})} /></div>
            <div><label className="text-xs font-medium text-slate-600 mb-1 block">Description</label><textarea value={awardForm.description} onChange={e => setAwardForm({...awardForm, description: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
          </div>
          <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
            <Button variant="ghost" onClick={() => setAwardModalOpen(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleSaveAward}>{editingAward ? 'Update' : 'Add'}</Button>
          </div>
        </Modal>

        {/* Activity Modal */}
        <Modal open={activityModalOpen} onClose={() => setActivityModalOpen(false)} title={editingActivity ? 'Edit Activity' : 'Add Activity'} size="md">
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Activity Name *</label><input value={activityForm.name} onChange={e => setActivityForm({...activityForm, name: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Type</label><SearchableSelect value={activityForm.activity_type} onChange={v => setActivityForm({...activityForm, activity_type: v})} options={[{value:'Sports',label:'Sports'},{value:'Arts',label:'Arts'},{value:'Club',label:'Club'},{value:'Cultural',label:'Cultural'},{value:'Academic',label:'Academic'}]} placeholder="Select..." /></div>
            </div>
            <div><label className="text-xs font-medium text-slate-600 mb-1 block">Description</label><textarea value={activityForm.description} onChange={e => setActivityForm({...activityForm, description: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
          </div>
          <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
            <Button variant="ghost" onClick={() => setActivityModalOpen(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleSaveActivity}>{editingActivity ? 'Update' : 'Add'}</Button>
          </div>
        </Modal>

        {/* Meeting Modal */}
        <Modal open={meetingModalOpen} onClose={() => setMeetingModalOpen(false)} title={editingMeeting ? 'Edit Meeting' : 'Add Meeting'} size="md">
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Meeting Date *</label><DateInput value={meetingForm.meeting_date} onChange={(v) => setMeetingForm({...meetingForm, meeting_date: v})} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Meeting Type</label><SearchableSelect value={meetingForm.meeting_type} onChange={v => setMeetingForm({...meetingForm, meeting_type: v})} options={[{value:'Regular',label:'Regular'},{value:'Behavioral',label:'Behavioral'},{value:'Academic',label:'Academic'},{value:'Emergency',label:'Emergency'},{value:'Other',label:'Other'}]} placeholder="Select..." /></div>
            </div>
            <div><label className="text-xs font-medium text-slate-600 mb-1 block">Agenda</label><textarea value={meetingForm.agenda} onChange={e => setMeetingForm({...meetingForm, agenda: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
            <div><label className="text-xs font-medium text-slate-600 mb-1 block">Discussion Notes</label><textarea value={meetingForm.discussion_notes} onChange={e => setMeetingForm({...meetingForm, discussion_notes: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
          </div>
          <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
            <Button variant="ghost" onClick={() => setMeetingModalOpen(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleSaveMeeting}>{editingMeeting ? 'Update' : 'Add'}</Button>
          </div>
        </Modal>

        {/* Disciplinary Modal */}
        <Modal open={disciplinaryModalOpen} onClose={() => setDisciplinaryModalOpen(false)} title={editingDisciplinary ? 'Edit Record' : 'Add Record'} size="md">
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Incident Date *</label><DateInput value={disciplinaryForm.incident_date} onChange={(v) => setDisciplinaryForm({...disciplinaryForm, incident_date: v})} /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Category *</label><SearchableSelect value={disciplinaryForm.category} onChange={v => setDisciplinaryForm({...disciplinaryForm, category: v})} options={[{value:'Behavioral',label:'Behavioral'},{value:'Academic',label:'Academic'},{value:'Attendance',label:'Attendance'},{value:'Bullying',label:'Bullying'},{value:'Other',label:'Other'}]} placeholder="Select..." /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Severity *</label><SearchableSelect value={disciplinaryForm.severity} onChange={v => setDisciplinaryForm({...disciplinaryForm, severity: v})} options={[{value:'Low',label:'Low'},{value:'Medium',label:'Medium'},{value:'High',label:'High'}]} placeholder="Select..." /></div>
              <div><label className="text-xs font-medium text-slate-600 mb-1 block">Status</label><SearchableSelect value={disciplinaryForm.status} onChange={v => setDisciplinaryForm({...disciplinaryForm, status: v})} options={[{value:'Open',label:'Open'},{value:'Resolved',label:'Resolved'},{value:'Closed',label:'Closed'}]} placeholder="Select..." /></div>
            </div>
            <div><label className="text-xs font-medium text-slate-600 mb-1 block">Description *</label><textarea value={disciplinaryForm.description} onChange={e => setDisciplinaryForm({...disciplinaryForm, description: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
            <div><label className="text-xs font-medium text-slate-600 mb-1 block">Action Taken</label><textarea value={disciplinaryForm.action_taken} onChange={e => setDisciplinaryForm({...disciplinaryForm, action_taken: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
          </div>
          <div className="flex justify-end gap-2 mt-4 pt-3 border-t border-slate-100">
            <Button variant="ghost" onClick={() => setDisciplinaryModalOpen(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleSaveDisciplinary}>{editingDisciplinary ? 'Update' : 'Add'}</Button>
          </div>
        </Modal>
      </>
    );
  }

  // Student List View (no studentId selected)
  return (
    <div>
      <Breadcrumb items={breadcrumbItems} />

      <div className="mb-6">
        <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Class {activeClassName}-{activeSectionName} Students</h1>
        <p className="text-sm text-slate-500 mt-1">View and manage students in this class section</p>
      </div>

      {/* Class/Section selector */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 mb-5">
        <div className="flex flex-col md:flex-row md:items-center gap-3">
          <div className="w-48">
            <SearchableSelect
              value={activeClassName}
              onChange={handleClassChange}
              options={classOptions}
              placeholder="Select Class"
            />
          </div>
          <div className="w-48">
            <SearchableSelect
              value={activeSectionName}
              onChange={handleSectionChange}
              options={sectionOptions}
              placeholder="Select Section"
            />
          </div>
          <div className="flex-1">
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                placeholder="Search students by name..."
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Students List */}
      {!activeClassName || !activeSectionName ? (
        <div className="text-center py-16 bg-white border border-slate-200 rounded-xl">
          <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-4">
            <Users size={28} className="text-slate-400" />
          </div>
          <p className="text-base font-medium text-slate-600">Select a class and section to view students</p>
        </div>
      ) : studentsLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-slate-500">Loading students...</p>
          </div>
        </div>
      ) : students.length > 0 ? (
        <div>
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-semibold text-slate-900">
              {studentsData?.count || students.length} Students
            </p>
            {totalPages > 1 && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Page {page} of {totalPages}</span>
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1} className="px-2 py-1 text-xs rounded-md bg-slate-100 text-slate-600 hover:bg-slate-200 disabled:opacity-40">Prev</button>
                <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page >= totalPages} className="px-2 py-1 text-xs rounded-md bg-slate-100 text-slate-600 hover:bg-slate-200 disabled:opacity-40">Next</button>
              </div>
            )}
          </div>

          <div className="space-y-2">
            {students.map(s => (
              <div
                key={s.id}
                onClick={() => handleStudentClick(s.id)}
                className="bg-white border border-slate-200 rounded-xl p-4 cursor-pointer transition-all duration-200 hover:border-slate-300 hover:shadow-sm"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {(s.full_name || '').slice(0, 2).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-900 truncate">{s.full_name}</p>
                    <p className="text-xs text-slate-500">{s.roll_number} | {s.email || ''}</p>
                  </div>
                  <Badge variant={s.status === 'Active' ? 'success' : 'warning'}>{s.status || 'Active'}</Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-14 bg-white border border-slate-200 rounded-xl">
          <div className="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3">
            <Users size={24} className="text-slate-400" />
          </div>
          <p className="text-sm font-medium text-slate-600">No students found</p>
          <p className="text-xs text-slate-400 mt-1">Try a different search or select another class/section</p>
        </div>
      )}
    </div>
  );
}

function AttendanceCalendarSection({ studentId }) {
  const now = new Date();
  const [month, setMonth] = useState(String(now.getMonth() + 1));
  const [year, setYear] = useState(String(now.getFullYear()));
  const [expanded, setExpanded] = useState(false);

  const { data: attendanceData } = useQuery({
    queryKey: ['students', studentId, 'attendance', month, year],
    queryFn: () => api.get(`/admin/students/${studentId}/attendance`, { params: { month: +month, year: +year } }).then(r => r.data),
    enabled: !!studentId && expanded,
  });

  const { data: holidaysData } = useHolidays();

  const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const monthOptions = MONTHS.map((m, i) => ({ value: String(i + 1), label: m }));
  const yearOptions = Array.from({ length: 3 }, (_, i) => ({ value: String(now.getFullYear() - i), label: String(now.getFullYear() - i) }));

  const calendarData = useMemo(() => {
    const m = +month, y = +year;
    const daysInMonth = new Date(y, m, 0).getDate();
    const firstDay = new Date(y, m - 1, 1).getDay();
    const today = new Date();

    const holidays = (holidaysData?.holidays || [])
      .filter(h => { const d = new Date(h.date); return d.getMonth() + 1 === m && d.getFullYear() === y; })
      .map(h => h.date);

    const records = (attendanceData?.records || []).reduce((acc, r) => { acc[r.date] = r.status; return acc; }, {});

    const days = [];
    for (let i = 0; i < firstDay; i++) days.push(null);
    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      const dayOfWeek = new Date(y, m - 1, d).getDay();
      const isFuture = new Date(y, m - 1, d) > today;
      const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
      const isHoliday = holidays.includes(dateStr);
      const status = records[dateStr];
      days.push({ day: d, dateStr, isWeekend, isHoliday, isFuture, status });
    }

    const presentCount = Object.values(records).filter(s => s === 'Present' || s === 'Late').length;
    const absentCount = Object.values(records).filter(s => s === 'Absent').length;
    const holidayCount = holidays.length;
    const weekends = Array.from({ length: daysInMonth }, (_, i) => new Date(y, m - 1, i + 1).getDay()).filter(d => d === 0 || d === 6).length;
    const workingDays = daysInMonth - weekends - holidayCount;

    return { days, presentCount, absentCount, holidayCount, workingDays };
  }, [attendanceData, holidaysData, month, year]);

  const pieData = [
    { name: 'Present', value: calendarData.presentCount, color: '#22c55e' },
    { name: 'Absent', value: calendarData.absentCount, color: '#ef4444' },
    { name: 'Holidays', value: calendarData.holidayCount, color: '#94a3b8' },
  ].filter(d => d.value > 0);

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden mt-4">
      <button onClick={() => setExpanded(!expanded)} className="w-full flex items-center justify-between px-5 py-4 hover:bg-slate-50 transition-colors">
        <div className="flex items-center gap-2">
          <span className="text-base font-semibold text-slate-800">Attendance Overview</span>
          <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium">{MONTHS[+month - 1]} {year}</span>
        </div>
        <svg className={`w-5 h-5 text-slate-400 transition-transform ${expanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
      </button>

      {expanded && (
        <div className="px-5 pb-5 border-t border-slate-100">
          <div className="flex gap-3 py-4">
            <div className="w-40"><SearchableSelect value={month} onChange={setMonth} options={monthOptions} placeholder="Month" /></div>
            <div className="w-28"><SearchableSelect value={year} onChange={setYear} options={yearOptions} placeholder="Year" /></div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            <div className="lg:col-span-2">
              <div className="border border-slate-200 rounded-lg overflow-hidden">
                <div className="grid grid-cols-7 bg-slate-50 border-b border-slate-200">
                  {['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map(d => (
                    <div key={d} className="text-center text-[11px] font-semibold text-slate-500 uppercase tracking-wide py-2">{d}</div>
                  ))}
                </div>
                <div className="grid grid-cols-7 gap-1 p-3">
                  {calendarData.days.map((cell, i) => (
                    <div key={i} className="flex items-center justify-center py-1">
                      {cell && (
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${cell.isFuture ? 'text-slate-300' : cell.isHoliday ? 'bg-slate-200 text-slate-500' : cell.isWeekend ? 'text-slate-400' : cell.status === 'Present' || cell.status === 'Late' ? 'bg-green-100 text-green-700 ring-1 ring-green-300' : cell.status === 'Absent' ? 'bg-red-100 text-red-700 ring-1 ring-red-300' : 'text-slate-600'}`}>
                          {cell.day}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex flex-wrap gap-4 mt-3 text-xs text-slate-600">
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-green-50 border border-green-200"></span>Present</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-red-50 border border-red-200"></span>Absent</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-slate-100 border border-slate-300"></span>Holiday</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-slate-50 border border-slate-200"></span>Weekend</span>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-green-50 border border-green-100 rounded-lg p-3 text-center"><div className="text-xl font-bold text-green-700">{calendarData.presentCount}</div><div className="text-[10px] text-green-600 font-medium">Present</div></div>
                <div className="bg-red-50 border border-red-100 rounded-lg p-3 text-center"><div className="text-xl font-bold text-red-700">{calendarData.absentCount}</div><div className="text-[10px] text-red-600 font-medium">Absent</div></div>
                <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 text-center"><div className="text-xl font-bold text-blue-700">{calendarData.workingDays}</div><div className="text-[10px] text-blue-600 font-medium">Working Days</div></div>
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center"><div className="text-xl font-bold text-slate-600">{calendarData.holidayCount}</div><div className="text-[10px] text-slate-500 font-medium">Holidays</div></div>
              </div>

              {pieData.length > 0 && (
                <div className="h-44">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={30} outerRadius={55} paddingAngle={2}>
                        {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                      </Pie>
                      <RLegend iconSize={8} wrapperStyle={{ fontSize: '11px' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
