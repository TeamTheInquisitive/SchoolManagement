import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useStudents, useStudent, useUpdateStudent, useStudentExamResults, useStudentParentMeetings, useStudentActivities, useStudentFeeHistory, useStudentDisciplinaryRecords, useCreateAward, useUpdateAward, useDeleteAward, useCreateActivity, useUpdateActivity, useDeleteActivity, useCreateParentMeeting, useUpdateParentMeeting, useDeleteParentMeeting, useCreateDisciplinaryRecord, useUpdateDisciplinaryRecord, useDeleteDisciplinaryRecord } from '../../services/studentService';
import { Button, Modal, SearchableSelect, DateInput, useRecentlyViewed, useToast, ResetPasswordModal, StudentDetailView, PrintHeader, ConfirmDialog } from 'school-erp-ui-shared';
import { useClassSectionFilter } from '../../hooks/useClassSectionFilter';
import { useHolidays, useSchoolProfile } from '../../services/settingsService';
import { useQuery } from '@tanstack/react-query';
import { PieChart, Pie, Cell, Legend as RLegend, ResponsiveContainer } from 'recharts';
import api from '../../services/api';

export default function StudentDetailsPage() {
  const { id: urlStudentId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const { selectedClass: classFilter, setSelectedClass: setClassFilter, classOptions } = useClassSectionFilter();
  const [searchName, setSearchName] = useState('');
  const [selectedStudentId, setSelectedStudentId] = useState(urlStudentId || null);
  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [showPrintModal, setShowPrintModal] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null); // { type, id, message }
  const [printSections, setPrintSections] = useState({ academic: true, personal: true, parent: true, examinations: true, performance: false, awards: true, activities: true, disciplinary: true, meetings: true, attendance: false, fees: true });
  const { data: schoolProfile } = useSchoolProfile();
  const [editingSection, setEditingSection] = useState(null);
  const [resetPwOpen, setResetPwOpen] = useState(false);
  const [resetPwLoading, setResetPwLoading] = useState(false);
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

  const { data: studentsListData } = useStudents({ page_size: 100, status: 'Active' });

  useEffect(() => {
    if (urlStudentId) {
      setSelectedStudentId(urlStudentId);
    } else if (!selectedStudentId && studentsListData?.results?.length > 0) {
      setSelectedStudentId(studentsListData.results[0].id);
    }
  }, [urlStudentId, studentsListData]);

  const { data: studentData } = useStudent(selectedStudentId);
  const { data: examResultsData } = useStudentExamResults(selectedStudentId);
  const { data: meetingsData } = useStudentParentMeetings(selectedStudentId);
  const { data: activitiesData } = useStudentActivities(selectedStudentId);
  const { data: feeHistoryData } = useStudentFeeHistory(selectedStudentId);
  const { data: disciplinaryData } = useStudentDisciplinaryRecords(selectedStudentId);

  const { addItem } = useRecentlyViewed();

  useEffect(() => {
    if (studentData && selectedStudentId) {
      addItem({ id: selectedStudentId, name: studentData.full_name, type: 'student', path: '/admin/students/' + selectedStudentId, subtitle: 'Class ' + (studentData.class_name ? `${studentData.class_name}-${studentData.section || ''}` : '') });
    }
  }, [studentData, selectedStudentId]);

  const students = (studentsListData?.results ?? []).map(s => ({ id: s.id, name: s.full_name || s.name || '', roll: s.roll_number || s.roll || '', class: s.class_name ? `${s.class_name}-${s.section || ''}` : (s.class || ''), avatar: (s.full_name || s.name || '??').slice(0, 2).toUpperCase() }));
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
    const payload = Object.fromEntries(Object.entries(awardForm).filter(([, v]) => v !== '' && v !== undefined));
    if (editingAward) {
      updateAward.mutate({ studentId: selectedStudentId, awardId: editingAward.id, data: payload }, {
        onSuccess: () => { setAwardModalOpen(false); toast.success('Award updated'); },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to update award'),
      });
    } else {
      createAward.mutate({ studentId: selectedStudentId, data: payload }, {
        onSuccess: () => { setAwardModalOpen(false); toast.success('Award added'); },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to add award'),
      });
    }
  };

  const handleDeleteAward = (award) => {
    setDeleteConfirm({ message: 'Delete this award?', onConfirm: () => { deleteAward.mutate({ studentId: selectedStudentId, awardId: award.id }, { onSuccess: () => toast.success('Award deleted'), onError: (err) => toast.error(err.response?.data?.detail || 'Failed to delete award') }); setDeleteConfirm(null); } });
  };

  const handleOpenActivityModal = (activity = null) => {
    if (activity) {
      setEditingActivity(activity);
      setActivityForm({ name: activity.name || '', activity_type: activity.activity_type || '', description: activity.description || '', role: activity.role || '', start_date: activity.start_date || '', end_date: activity.end_date || '', achievement: activity.achievement || '' });
    } else {
      setEditingActivity(null);
      setActivityForm({ name: '', activity_type: '', description: '', role: '', start_date: '', end_date: '', achievement: '' });
    }
    setActivityModalOpen(true);
  };

  const handleSaveActivity = () => {
    const payload = Object.fromEntries(Object.entries(activityForm).filter(([, v]) => v !== '' && v !== undefined));
    if (editingActivity) {
      updateActivity.mutate({ studentId: selectedStudentId, activityId: editingActivity.id, data: payload }, {
        onSuccess: () => { setActivityModalOpen(false); toast.success('Activity updated'); },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to update activity'),
      });
    } else {
      createActivity.mutate({ studentId: selectedStudentId, data: payload }, {
        onSuccess: () => { setActivityModalOpen(false); toast.success('Activity added'); },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to add activity'),
      });
    }
  };

  const handleDeleteActivity = (activity) => {
    setDeleteConfirm({ message: 'Delete this activity?', onConfirm: () => { deleteActivity.mutate({ studentId: selectedStudentId, activityId: activity.id }, { onSuccess: () => toast.success('Activity deleted'), onError: (err) => toast.error(err.response?.data?.detail || 'Failed to delete activity') }); setDeleteConfirm(null); } });
  };

  const handleOpenMeetingModal = (meeting = null) => {
    if (meeting) {
      setEditingMeeting(meeting);
      setMeetingForm({ meeting_date: meeting.date || '', meeting_type: meeting.type || '', agenda: meeting.agenda || '', discussion_notes: meeting.notes || '', remarks: meeting.remarks || '', follow_up_required: meeting.follow_up_required || false, parent_attended: meeting.parent_attended !== false, next_meeting_date: meeting.next_meeting_date || '', status: meeting.status || '' });
    } else {
      setEditingMeeting(null);
      setMeetingForm({ meeting_date: '', meeting_type: '', agenda: '', discussion_notes: '', remarks: '', follow_up_required: false, parent_attended: true, next_meeting_date: '' });
    }
    setMeetingModalOpen(true);
  };

  const handleSaveMeeting = () => {
    const payload = Object.fromEntries(Object.entries(meetingForm).filter(([, v]) => v !== '' && v !== undefined && v !== null));
    if (editingMeeting) {
      updateParentMeeting.mutate({ studentId: selectedStudentId, meetingId: editingMeeting.id, data: payload }, {
        onSuccess: () => { setMeetingModalOpen(false); toast.success('Meeting updated'); },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to update meeting'),
      });
    } else {
      createParentMeeting.mutate({ studentId: selectedStudentId, data: payload }, {
        onSuccess: () => { setMeetingModalOpen(false); toast.success('Meeting added'); },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to add meeting'),
      });
    }
  };

  const handleDeleteMeeting = (meeting) => {
    setDeleteConfirm({ message: 'Delete this meeting?', onConfirm: () => { deleteParentMeeting.mutate({ studentId: selectedStudentId, meetingId: meeting.id }, { onSuccess: () => toast.success('Meeting deleted'), onError: (err) => toast.error(err.response?.data?.detail || 'Failed to delete meeting') }); setDeleteConfirm(null); } });
  };

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
    const payload = Object.fromEntries(Object.entries(disciplinaryForm).filter(([, v]) => v !== '' && v !== undefined && v !== null));
    if (editingDisciplinary) {
      updateDisciplinary.mutate({ studentId: selectedStudentId, recordId: editingDisciplinary.id, data: payload }, {
        onSuccess: () => { setDisciplinaryModalOpen(false); toast.success('Record updated'); },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to update record'),
      });
    } else {
      createDisciplinary.mutate({ studentId: selectedStudentId, data: payload }, {
        onSuccess: () => { setDisciplinaryModalOpen(false); toast.success('Record added'); },
        onError: (err) => toast.error(err.response?.data?.detail || 'Failed to add record'),
      });
    }
  };

  const handleDeleteDisciplinary = (record) => {
    setDeleteConfirm({ message: 'Delete this disciplinary record?', onConfirm: () => { deleteDisciplinary.mutate({ studentId: selectedStudentId, recordId: record.id }, { onSuccess: () => toast.success('Record deleted'), onError: (err) => toast.error(err.response?.data?.detail || 'Failed to delete record') }); setDeleteConfirm(null); } });
  };

  const handlePrint = () => setShowPrintModal(true);

  const handleExportPdf = () => setShowPrintModal(true);

  const executePrint = () => {
    const s = studentDetail;
    const raw2 = raw || {};
    const school = schoolProfile || {};
    const w = window.open('', '_blank');
    const css = `body{font-family:-apple-system,sans-serif;padding:40px;max-width:800px;margin:0 auto;color:#1e293b;font-size:13px} .header{text-align:center;border-bottom:2px solid #1e293b;padding-bottom:16px;margin-bottom:24px} .header h1{margin:0;font-size:20px;text-transform:uppercase;letter-spacing:1px} .header p{margin:3px 0;font-size:11px;color:#64748b} .doc-title{text-align:center;margin:12px 0 0;padding-top:10px;border-top:1px solid #e2e8f0;font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px} .section{margin-bottom:20px} .section h3{font-size:13px;font-weight:bold;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;text-transform:uppercase;letter-spacing:0.5px;color:#334155} .grid{display:grid;grid-template-columns:1fr 1fr;gap:6px 24px} .field{display:flex;gap:8px;padding:4px 0} .field .label{font-size:11px;color:#64748b;min-width:120px} .field .value{font-size:12px;font-weight:500} table{width:100%;border-collapse:collapse;margin-top:8px;font-size:11px} th,td{padding:6px 10px;border:1px solid #e2e8f0;text-align:left} th{background:#f8fafc;font-weight:600;font-size:10px;text-transform:uppercase} @media print{body{padding:20px}}`;
    
    let html = `<html><head><title>${s.name} - Student Profile</title><style>${css}</style></head><body>`;
    html += `<div class="header"><h1>${school.name || 'School'}</h1>${school.affiliation ? `<p>${school.affiliation}</p>` : ''}${school.address ? `<p>${school.address}</p>` : ''}<p>${[school.phone, school.email].filter(Boolean).join(' • ')}</p><div class="doc-title">Student Profile</div></div>`;

    if (printSections.academic) {
      html += `<div class="section"><h3>Academic Information</h3><div class="grid">`;
      html += `<div class="field"><span class="label">Name</span><span class="value">${s.name || ''}</span></div>`;
      html += `<div class="field"><span class="label">Admission No</span><span class="value">${s.admissionNo || raw2.admission_number || ''}</span></div>`;
      html += `<div class="field"><span class="label">Roll No</span><span class="value">${s.rollNumber || raw2.roll_number || ''}</span></div>`;
      html += `<div class="field"><span class="label">Class</span><span class="value">${raw2.class_name || ''} - ${raw2.section || ''}</span></div>`;
      html += `<div class="field"><span class="label">Status</span><span class="value">${raw2.status || 'Active'}</span></div>`;
      html += `</div></div>`;
    }
    if (printSections.personal) {
      html += `<div class="section"><h3>Personal Information</h3><div class="grid">`;
      html += `<div class="field"><span class="label">Phone</span><span class="value">${s.phone || raw2.phone || ''}</span></div>`;
      html += `<div class="field"><span class="label">Email</span><span class="value">${s.email || raw2.email || ''}</span></div>`;
      html += `<div class="field"><span class="label">Date of Birth</span><span class="value">${s.personal?.dob || raw2.date_of_birth || ''}</span></div>`;
      html += `<div class="field"><span class="label">Gender</span><span class="value">${raw2.gender || ''}</span></div>`;
      html += `<div class="field"><span class="label">Address</span><span class="value">${s.personal?.address || raw2.address || ''}</span></div>`;
      html += `</div></div>`;
    }
    if (printSections.parent) {
      html += `<div class="section"><h3>Parent/Guardian Information</h3><div class="grid">`;
      html += `<div class="field"><span class="label">Parent Name</span><span class="value">${s.parent?.name || raw2.parent_name || ''}</span></div>`;
      html += `<div class="field"><span class="label">Phone</span><span class="value">${s.parent?.phone || raw2.parent_phone || ''}</span></div>`;
      html += `<div class="field"><span class="label">Email</span><span class="value">${s.parent?.email || raw2.parent_email || ''}</span></div>`;
      html += `</div></div>`;
    }
    if (printSections.examinations && s.exams?.length) {
      html += `<div class="section"><h3>Examination Results</h3><table><tr><th>Exam</th><th>Subject</th><th>Marks</th><th>Grade</th></tr>`;
      s.exams.forEach(e => { (e.results || e.subjects || []).forEach(sub => { html += `<tr><td>${e.exam_name || e.name || ''}</td><td>${sub.subject_name || sub.subject || ''}</td><td>${sub.marks_obtained ?? sub.marks ?? ''}/${sub.total_marks || sub.max_marks || ''}</td><td>${sub.grade || ''}</td></tr>`; }); });
      html += `</table></div>`;
    }
    if (printSections.awards && s.awards?.length) {
      html += `<div class="section"><h3>Awards & Achievements</h3><table><tr><th>Title</th><th>Category</th><th>Date</th></tr>`;
      s.awards.forEach(a => { html += `<tr><td>${a.title || ''}</td><td>${a.category || ''}</td><td>${a.date || a.award_date || ''}</td></tr>`; });
      html += `</table></div>`;
    }
    if (printSections.activities && s.activities?.length) {
      html += `<div class="section"><h3>Activities</h3><table><tr><th>Name</th><th>Type</th><th>Date</th></tr>`;
      s.activities.forEach(a => { html += `<tr><td>${a.name || a.activity_name || ''}</td><td>${a.type || a.activity_type || ''}</td><td>${a.date || ''}</td></tr>`; });
      html += `</table></div>`;
    }
    if (printSections.disciplinary && s.disciplinaryRecords?.length) {
      html += `<div class="section"><h3>Disciplinary Records</h3><table><tr><th>Date</th><th>Category</th><th>Severity</th><th>Description</th></tr>`;
      s.disciplinaryRecords.forEach(d => { html += `<tr><td>${d.incident_date || ''}</td><td>${d.category || ''}</td><td>${d.severity || ''}</td><td>${d.description || ''}</td></tr>`; });
      html += `</table></div>`;
    }
    if (printSections.meetings && s.parentMeetings?.length) {
      html += `<div class="section"><h3>Parent Meetings</h3><table><tr><th>Date</th><th>Type</th><th>Summary</th></tr>`;
      s.parentMeetings.forEach(m => { html += `<tr><td>${m.meeting_date || ''}</td><td>${m.meeting_type || ''}</td><td>${m.summary || ''}</td></tr>`; });
      html += `</table></div>`;
    }

    html += `<div style="margin-top:40px;border-top:1px solid #e2e8f0;padding-top:12px;display:flex;justify-content:space-between;font-size:10px;color:#94a3b8"><span>Generated on ${new Date().toLocaleDateString('en-IN')}</span><span>${school.name || ''}</span></div>`;
    html += `</body></html>`;
    w.document.write(html);
    w.document.close();
    w.print();
    setShowPrintModal(false);
  };

  const handleEdit = () => {
    setEditForm({ full_name: raw.full_name || '', email: raw.email || '', phone: raw.phone || '', class_name: raw.class_name || '', section: raw.section || '', gender: raw.gender || '', date_of_birth: raw.date_of_birth || '', address: raw.address || '', blood_group: raw.medical?.blood_group || '', religion: raw.medical?.religion || '', medical_conditions: raw.medical?.conditions || '' });
    setEditOpen(true);
  };

  const handleEditSection = (section) => {
    const formData = {
      academic: { full_name: raw.full_name || '', email: raw.email || '', phone: raw.phone || '', class_name: raw.class_name || '', section: raw.section || '' },
      personal: { date_of_birth: raw.date_of_birth || '', admission_date: raw.admission_date || '', address: raw.address || '' },
      parent: { parents: (raw.parents && raw.parents.length ? raw.parents.map(p => ({ name: p.name || '', relationship: p.relationship || '', phone: p.phone || '', email: p.email || '' })) : [{ name: raw.parent?.name || '', relationship: raw.parent?.relationship || 'Father', phone: raw.parent?.phone || '', email: raw.parent?.email || '' }]) },
      medical: { blood_group: raw.medical?.blood_group || '', gender: raw.gender || '', religion: raw.medical?.religion || '', medical_conditions: raw.medical?.conditions || '' },
    };
    setEditForm(formData[section] || {});
    setEditingSection(section);
  };

  const handleSaveSection = () => {
    let payload;
    if (Array.isArray(editForm.parents)) {
      const parents = editForm.parents
        .filter(p => (p.name || '').trim())
        .map(p => ({ name: p.name.trim(), relationship: p.relationship || 'Parent/Guardian', phone: p.phone || null, email: p.email || null }));
      if (parents.length === 0) { toast.error('At least one parent/guardian is required'); return; }
      const rels = parents.map(p => (p.relationship || '').toLowerCase());
      if (new Set(rels).size !== rels.length) { toast.error('Each parent/guardian must have a unique relationship'); return; }
      payload = { parents };
    } else {
      const allowedFields = ['full_name', 'email', 'phone', 'date_of_birth', 'admission_date', 'gender', 'student_type', 'blood_group', 'religion', 'medical_conditions', 'address', 'address_line2', 'city', 'state', 'pincode', 'status', 'class_name', 'section', 'parent_name', 'parent_phone', 'parent_email', 'parent_relationship'];
      payload = Object.fromEntries(
        Object.entries(editForm).filter(([k, v]) => v !== undefined && v !== '' && allowedFields.includes(k))
      );
    }
    updateStudent.mutate({ id: selectedStudentId, data: payload }, {
      onSuccess: () => { setEditingSection(null); toast.success('Updated successfully'); },
      onError: (err) => { toast.error(err.response?.data?.detail || err.response?.data?.error || 'Update failed'); },
    });
  };

  const handleFieldChange = (key, value) => setEditForm(prev => ({ ...prev, [key]: value }));

  const handleSelectStudent = (id) => {
    setSelectedStudentId(id);
    navigate(`/admin/students/${id}`, { replace: true });
  };

  return (
    <>
      <StudentDetailView
        student={studentDetail}
        examResults={examData}
        meetings={meetings}
        activities={activitiesObj}
        feeHistory={feeHistoryObj}
        disciplinaryRecords={disciplinaryData?.records || []}
        students={students}
        selectedStudentId={selectedStudentId}
        onSelectStudent={handleSelectStudent}
        classFilter={classFilter}
        setClassFilter={setClassFilter}
        classOptions={classOptions}
        searchName={searchName}
        setSearchName={setSearchName}
        onEdit={handleEdit}
        onResetPassword={() => setResetPwOpen(true)}
        onPrint={handlePrint}
        onExportPdf={handleExportPdf}
        breadcrumbItems={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Students', href: '/admin/students' }, { label: 'Student Details' }]}
        editingSection={editingSection}
        editForm={editForm}
        onEditSection={handleEditSection}
        onSaveSection={handleSaveSection}
        onCancelEdit={() => setEditingSection(null)}
        onFieldChange={handleFieldChange}
        isSaving={updateStudent.isPending}
        onAwardAdd={() => handleOpenAwardModal()}
        onAwardEdit={(award) => handleOpenAwardModal(award)}
        onAwardDelete={handleDeleteAward}
        onActivityAdd={() => handleOpenActivityModal()}
        onActivityEdit={(activity) => handleOpenActivityModal(activity)}
        onActivityDelete={handleDeleteActivity}
        onMeetingAdd={() => handleOpenMeetingModal()}
        onMeetingEdit={(meeting) => handleOpenMeetingModal(meeting)}
        onMeetingDelete={handleDeleteMeeting}
        onDisciplinaryAdd={() => handleOpenDisciplinaryModal()}
        onDisciplinaryEdit={(record) => handleOpenDisciplinaryModal(record)}
        onDisciplinaryDelete={handleDeleteDisciplinary}
      >
        {/* Edit Student Modal */}
        <Modal open={editOpen} onClose={() => setEditOpen(false)} title="Edit Student Details" size="lg">
          <EditStudentForm form={editForm} setForm={setEditForm} studentId={selectedStudentId} onClose={() => setEditOpen(false)} />
        </Modal>

        <ResetPasswordModal
          open={resetPwOpen}
          onClose={() => setResetPwOpen(false)}
          userName={studentData?.full_name || ''}
          loading={resetPwLoading}
          onSubmit={(pw) => {
            setResetPwLoading(true);
            api.post(`/admin/students/${selectedStudentId}/reset-password`, { password: pw })
              .then(() => { setResetPwOpen(false); setResetPwLoading(false); toast.success('Password reset successfully'); })
              .catch(err => { setResetPwLoading(false); toast.error(err.response?.data?.detail || 'Failed to reset password'); });
          }}
        />

        {/* Awards CRUD Modal */}
        <Modal open={awardModalOpen} onClose={() => setAwardModalOpen(false)} title={editingAward ? 'Edit Award' : 'Add Award'} size="md">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2"><label className="text-xs text-slate-600">Title *</label><input value={awardForm.title} onChange={e => setAwardForm({...awardForm, title: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            <div><label className="text-xs text-slate-600">Category</label><SearchableSelect value={awardForm.category} onChange={v => setAwardForm({...awardForm, category: v})} options={[{value:'',label:'Select'},{value:'Academic',label:'Academic'},{value:'Sports',label:'Sports'},{value:'Arts',label:'Arts'},{value:'Cultural',label:'Cultural'},{value:'Other',label:'Other'}]} placeholder="Select..." /></div>
            <div><label className="text-xs text-slate-600">Level</label><SearchableSelect value={awardForm.level} onChange={v => setAwardForm({...awardForm, level: v})} options={[{value:'',label:'Select'},{value:'School',label:'School'},{value:'District',label:'District'},{value:'State',label:'State'},{value:'National',label:'National'},{value:'International',label:'International'}]} placeholder="Select..." /></div>
            <div><DateInput label="Date" value={awardForm.awarded_date} onChange={v => setAwardForm({...awardForm, awarded_date: v})} /></div>
            <div><label className="text-xs text-slate-600">Awarded By</label><input value={awardForm.awarded_by} onChange={e => setAwardForm({...awardForm, awarded_by: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            <div className="col-span-2"><label className="text-xs text-slate-600">Description</label><textarea value={awardForm.description} onChange={e => setAwardForm({...awardForm, description: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="ghost" onClick={() => setAwardModalOpen(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleSaveAward} disabled={!awardForm.title || createAward.isPending || updateAward.isPending}>{(createAward.isPending || updateAward.isPending) ? 'Saving...' : editingAward ? 'Update' : 'Add Award'}</Button>
          </div>
        </Modal>

        {/* Activities CRUD Modal */}
        <Modal open={activityModalOpen} onClose={() => setActivityModalOpen(false)} title={editingActivity ? 'Edit Activity' : 'Add Activity'} size="md">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2"><label className="text-xs text-slate-600">Name *</label><input value={activityForm.name} onChange={e => setActivityForm({...activityForm, name: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            <div><label className="text-xs text-slate-600">Activity Type *</label><SearchableSelect value={activityForm.activity_type} onChange={v => setActivityForm({...activityForm, activity_type: v})} options={[{value:'',label:'Select'},{value:'Sports',label:'Sports'},{value:'Arts',label:'Arts'},{value:'Music',label:'Music'},{value:'Dance',label:'Dance'},{value:'Debate',label:'Debate'},{value:'Coding',label:'Coding'},{value:'Volunteering',label:'Volunteering'},{value:'Other',label:'Other'}]} placeholder="Select..." /></div>
            <div><label className="text-xs text-slate-600">Role</label><input value={activityForm.role} onChange={e => setActivityForm({...activityForm, role: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            <div><DateInput label="Start Date" value={activityForm.start_date} onChange={v => setActivityForm({...activityForm, start_date: v})} /></div>
            <div><DateInput label="End Date" value={activityForm.end_date} onChange={v => setActivityForm({...activityForm, end_date: v})} /></div>
            <div className="col-span-2"><label className="text-xs text-slate-600">Description</label><textarea value={activityForm.description} onChange={e => setActivityForm({...activityForm, description: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            <div className="col-span-2"><label className="text-xs text-slate-600">Achievement</label><input value={activityForm.achievement} onChange={e => setActivityForm({...activityForm, achievement: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="ghost" onClick={() => setActivityModalOpen(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleSaveActivity} disabled={!activityForm.name || !activityForm.activity_type || createActivity.isPending || updateActivity.isPending}>{(createActivity.isPending || updateActivity.isPending) ? 'Saving...' : editingActivity ? 'Update' : 'Add Activity'}</Button>
          </div>
        </Modal>

        {/* Parent Meeting CRUD Modal */}
        <Modal open={meetingModalOpen} onClose={() => setMeetingModalOpen(false)} title={editingMeeting ? 'Edit Meeting' : 'Add Meeting'} size="md">
          <div className="grid grid-cols-2 gap-3">
            <div><DateInput label="Meeting Date *" value={meetingForm.meeting_date} onChange={v => setMeetingForm({...meetingForm, meeting_date: v})} /></div>
            <div><label className="text-xs text-slate-600">Meeting Type</label><SearchableSelect value={meetingForm.meeting_type} onChange={v => setMeetingForm({...meetingForm, meeting_type: v})} options={[{value:'',label:'Select'},{value:'Regular',label:'Regular'},{value:'Behavioral',label:'Behavioral'},{value:'Academic',label:'Academic'},{value:'Emergency',label:'Emergency'},{value:'Other',label:'Other'}]} placeholder="Select..." /></div>
            <div className="col-span-2"><label className="text-xs text-slate-600">Agenda</label><textarea value={meetingForm.agenda} onChange={e => setMeetingForm({...meetingForm, agenda: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            <div className="col-span-2"><label className="text-xs text-slate-600">Discussion Notes</label><textarea value={meetingForm.discussion_notes} onChange={e => setMeetingForm({...meetingForm, discussion_notes: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            <div className="col-span-2"><label className="text-xs text-slate-600">Remarks</label><input value={meetingForm.remarks} onChange={e => setMeetingForm({...meetingForm, remarks: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            <div className="flex items-center gap-2"><input type="checkbox" checked={meetingForm.follow_up_required} onChange={e => setMeetingForm({...meetingForm, follow_up_required: e.target.checked})} className="rounded border-slate-300" /><label className="text-xs text-slate-600">Follow-up Required</label></div>
            <div className="flex items-center gap-2">
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" checked={meetingForm.parent_attended} onChange={e => setMeetingForm({...meetingForm, parent_attended: e.target.checked})} className="sr-only peer" />
                <div className="w-9 h-5 bg-slate-200 peer-focus:ring-2 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-500"></div>
              </label>
              <label className="text-xs text-slate-600">{meetingForm.parent_attended ? 'Parent Attended' : 'Parent Not Attended'}</label>
            </div>
            <div><DateInput label="Next Meeting Date" value={meetingForm.next_meeting_date} onChange={v => setMeetingForm({...meetingForm, next_meeting_date: v})} /></div>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="ghost" onClick={() => setMeetingModalOpen(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleSaveMeeting} disabled={!meetingForm.meeting_date || createParentMeeting.isPending || updateParentMeeting.isPending}>{(createParentMeeting.isPending || updateParentMeeting.isPending) ? 'Saving...' : editingMeeting ? 'Update' : 'Add Meeting'}</Button>
          </div>
        </Modal>

        {/* Disciplinary Record CRUD Modal */}
        <Modal open={disciplinaryModalOpen} onClose={() => setDisciplinaryModalOpen(false)} title={editingDisciplinary ? 'Edit Disciplinary Record' : 'Add Disciplinary Record'} size="md">
          <div className="grid grid-cols-2 gap-3">
            <div><DateInput label="Incident Date *" value={disciplinaryForm.incident_date} onChange={v => setDisciplinaryForm({...disciplinaryForm, incident_date: v})} /></div>
            <div><label className="text-xs text-slate-600">Category *</label><SearchableSelect value={disciplinaryForm.category} onChange={v => setDisciplinaryForm({...disciplinaryForm, category: v})} options={[{value:'',label:'Select'},{value:'Behavioral',label:'Behavioral'},{value:'Academic',label:'Academic'},{value:'Attendance',label:'Attendance'},{value:'Bullying',label:'Bullying'},{value:'Other',label:'Other'}]} placeholder="Select..." /></div>
            <div><label className="text-xs text-slate-600">Severity *</label><SearchableSelect value={disciplinaryForm.severity} onChange={v => setDisciplinaryForm({...disciplinaryForm, severity: v})} options={[{value:'',label:'Select'},{value:'Low',label:'Low'},{value:'Medium',label:'Medium'},{value:'High',label:'High'}]} placeholder="Select..." /></div>
            <div><label className="text-xs text-slate-600">Status</label><SearchableSelect value={disciplinaryForm.status} onChange={v => setDisciplinaryForm({...disciplinaryForm, status: v})} options={[{value:'Open',label:'Open'},{value:'Resolved',label:'Resolved'},{value:'Closed',label:'Closed'}]} placeholder="Select..." /></div>
            <div className="col-span-2"><label className="text-xs text-slate-600">Description *</label><textarea value={disciplinaryForm.description} onChange={e => setDisciplinaryForm({...disciplinaryForm, description: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            <div className="col-span-2"><label className="text-xs text-slate-600">Action Taken</label><textarea value={disciplinaryForm.action_taken} onChange={e => setDisciplinaryForm({...disciplinaryForm, action_taken: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            <div className="flex items-center gap-2"><input type="checkbox" checked={disciplinaryForm.parent_notified} onChange={e => setDisciplinaryForm({...disciplinaryForm, parent_notified: e.target.checked})} className="rounded border-slate-300" /><label className="text-xs text-slate-600">Parent Notified</label></div>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="ghost" onClick={() => setDisciplinaryModalOpen(false)}>Cancel</Button>
            <Button variant="primary" onClick={handleSaveDisciplinary} disabled={!disciplinaryForm.incident_date || !disciplinaryForm.category || !disciplinaryForm.severity || !disciplinaryForm.description || createDisciplinary.isPending || updateDisciplinary.isPending}>{(createDisciplinary.isPending || updateDisciplinary.isPending) ? 'Saving...' : editingDisciplinary ? 'Update' : 'Add Record'}</Button>
          </div>
        </Modal>
      </StudentDetailView>
      {selectedStudentId && <AttendanceCalendarSection studentId={selectedStudentId} />}

      {/* Delete Confirmation */}
      <ConfirmDialog open={!!deleteConfirm} onClose={() => setDeleteConfirm(null)} onConfirm={() => deleteConfirm?.onConfirm()} title="Confirm Delete" message={deleteConfirm?.message || 'Are you sure?'} confirmText="Delete" />

      {/* Print Profile Modal */}
      <Modal open={showPrintModal} onClose={() => setShowPrintModal(false)} title="Print Student Profile" size="sm">
        <div className="space-y-4">
          <p className="text-sm text-slate-600">Select sections to include in the printed profile:</p>
          <div className="space-y-2">
            {[
              { key: 'academic', label: 'Academic Information' },
              { key: 'personal', label: 'Personal Information' },
              { key: 'parent', label: 'Parent/Guardian Information' },
              { key: 'examinations', label: 'Examination Results' },
              { key: 'awards', label: 'Awards & Achievements' },
              { key: 'activities', label: 'Activities' },
              { key: 'disciplinary', label: 'Disciplinary Records' },
              { key: 'meetings', label: 'Parent Meetings' },
              { key: 'attendance', label: 'Attendance Summary' },
            ].map(s => (
              <label key={s.key} className="flex items-center gap-2 text-sm cursor-pointer hover:bg-slate-50 px-2 py-1.5 rounded-lg">
                <input type="checkbox" checked={printSections[s.key]} onChange={e => setPrintSections(prev => ({ ...prev, [s.key]: e.target.checked }))} className="rounded border-slate-300" />
                <span className="text-slate-700">{s.label}</span>
              </label>
            ))}
          </div>
          <div className="flex justify-between items-center pt-3 border-t border-slate-100">
            <button onClick={() => setPrintSections(Object.fromEntries(Object.keys(printSections).map(k => [k, true])))} className="text-xs text-primary-600 hover:underline">Select All</button>
            <div className="flex gap-2">
              <Button variant="ghost" onClick={() => setShowPrintModal(false)}>Cancel</Button>
              <Button variant="primary" onClick={executePrint}>Print / Export PDF</Button>
            </div>
          </div>
        </div>
      </Modal>
    </>
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
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      <button onClick={() => setExpanded(!expanded)} className="w-full flex items-center justify-between px-5 py-4 hover:bg-slate-50 transition-colors">
        <div className="flex items-center gap-2">
          <span className="text-base font-semibold text-slate-800">Attendance Overview</span>
          <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium">{MONTHS[+month - 1]} {year}</span>
        </div>
        <svg className={`w-5 h-5 text-slate-400 transition-transform ${expanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
      </button>

      {expanded && (
        <div className="px-5 pb-5 border-t border-slate-100">
          {/* Filters */}
          <div className="flex gap-3 py-4">
            <div className="w-40"><SearchableSelect value={month} onChange={setMonth} options={monthOptions} placeholder="Month" /></div>
            <div className="w-28"><SearchableSelect value={year} onChange={setYear} options={yearOptions} placeholder="Year" /></div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Calendar Grid */}
            <div className="lg:col-span-2">
              <div className="border border-slate-200 rounded-lg overflow-hidden">
                {/* Day headers */}
                <div className="grid grid-cols-7 bg-slate-50 border-b border-slate-200">
                  {['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map(d => (
                    <div key={d} className="text-center text-[11px] font-semibold text-slate-500 uppercase tracking-wide py-2">{d}</div>
                  ))}
                </div>
                {/* Day cells */}
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

              {/* Legend */}
              <div className="flex flex-wrap gap-4 mt-3 text-xs text-slate-600">
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-green-50 border border-green-200"></span>Present</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-red-50 border border-red-200"></span>Absent</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-slate-100 border border-slate-300"></span>Holiday</span>
                <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-sm bg-slate-50 border border-slate-200"></span>Weekend</span>
              </div>
            </div>

            {/* Stats + Pie */}
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

function EditStudentForm({ form, setForm, studentId, onClose }) {
  const updateStudent = useUpdateStudent();
  const handleSave = () => {
    const payload = Object.fromEntries(Object.entries(form).filter(([, v]) => v !== '' && v !== undefined));
    updateStudent.mutate({ id: studentId, data: payload }, { onSuccess: onClose });
  };
  const inp = "w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400";
  return (
    <div>
      <div className="grid grid-cols-2 gap-3">
        <div><label className="text-xs text-slate-600">Full Name</label><input value={form.full_name || ''} onChange={e => setForm({...form, full_name: e.target.value})} className={inp} /></div>
        <div><label className="text-xs text-slate-600">Email</label><input value={form.email || ''} onChange={e => setForm({...form, email: e.target.value})} className={inp} /></div>
        <div><label className="text-xs text-slate-600">Phone</label><input value={(form.phone || '').replace(/^\+91[-\s]?/, '')} onChange={e => setForm({...form, phone: e.target.value.replace(/^\+91[-\s]?/, '')})} maxLength={10} placeholder="9876543210" className={inp} /></div>
        <div><label className="text-xs text-slate-600">Gender</label><SearchableSelect value={form.gender || ''} onChange={(val) => setForm({...form, gender: val})} options={[{ value: '', label: 'Select' }, { value: 'Male', label: 'Male' }, { value: 'Female', label: 'Female' }, { value: 'Other', label: 'Other' }]} placeholder="Select Gender..." /></div>
        <div><DateInput label="Date of Birth" value={form.date_of_birth} onChange={v => setForm({...form, date_of_birth: v})} /></div>
        <div><label className="text-xs text-slate-600">Class</label><input value={form.class_name || ''} onChange={e => setForm({...form, class_name: e.target.value})} className={inp} /></div>
        <div><label className="text-xs text-slate-600">Section</label><input value={form.section || ''} onChange={e => setForm({...form, section: e.target.value})} className={inp} /></div>
        <div className="col-span-2"><label className="text-xs text-slate-600">Address</label><input value={form.address || ''} onChange={e => setForm({...form, address: e.target.value})} className={inp} /></div>
        <div><label className="text-xs text-slate-600">Blood Group</label><SearchableSelect value={form.blood_group || ''} onChange={(val) => setForm({...form, blood_group: val})} options={[{ value: '', label: 'Select' }, { value: 'A+', label: 'A+' }, { value: 'A-', label: 'A-' }, { value: 'B+', label: 'B+' }, { value: 'B-', label: 'B-' }, { value: 'O+', label: 'O+' }, { value: 'O-', label: 'O-' }, { value: 'AB+', label: 'AB+' }, { value: 'AB-', label: 'AB-' }]} placeholder="Select..." /></div>
        <div><label className="text-xs text-slate-600">Religion</label><input value={form.religion || ''} onChange={e => setForm({...form, religion: e.target.value})} className={inp} /></div>
        <div className="col-span-2"><label className="text-xs text-slate-600">Medical Conditions</label><textarea value={form.medical_conditions || ''} onChange={e => setForm({...form, medical_conditions: e.target.value})} rows={2} placeholder="Any medical conditions, allergies, or special needs..." className={inp} /></div>
      </div>
      <div className="flex justify-end gap-2 mt-4">
        <Button variant="ghost" onClick={onClose}>Cancel</Button>
        <Button variant="primary" onClick={handleSave} disabled={updateStudent.isPending}>{updateStudent.isPending ? 'Saving...' : 'Save Changes'}</Button>
      </div>
    </div>
  );
}
