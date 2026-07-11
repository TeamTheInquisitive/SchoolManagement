import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTeacher, useTeacherAssignments, useUpdateTeacher, useCreateTeacherAward, useUpdateTeacherAward, useDeleteTeacherAward } from '../../services/teacherService';
import { Button, Modal, useRecentlyViewed, ResetPasswordModal, useToast, TeacherDetailView, PrintHeader, ConfirmDialog, DatePicker } from 'school-erp-ui-shared';
import api from '../../services/api';
import { useSchoolProfile } from '../../services/settingsService';

export default function TeacherDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: teacher, isLoading } = useTeacher(id);
  const { data: assignmentsData } = useTeacherAssignments(id);
  const updateTeacher = useUpdateTeacher();
  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [editingSection, setEditingSection] = useState(null);
  const [resetPwOpen, setResetPwOpen] = useState(false);
  const [resetPwLoading, setResetPwLoading] = useState(false);
  const { addItem } = useRecentlyViewed();
  const toast = useToast();
  const createAward = useCreateTeacherAward();
  const updateAward = useUpdateTeacherAward();
  const deleteAward = useDeleteTeacherAward();
  const [awardModalOpen, setAwardModalOpen] = useState(false);
  const [editingAward, setEditingAward] = useState(null);
  const [awardForm, setAwardForm] = useState({ title: '', category: '', description: '', awarded_date: '', awarded_by: '', level: '' });
  const [showPrintModal, setShowPrintModal] = useState(false);
  const [printSections, setPrintSections] = useState({ basic: true, personal: true, professional: true, salary: true, schedule: true, leaves: true, awards: true });
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const { data: schoolProfile } = useSchoolProfile();

  useEffect(() => {
    if (teacher && id) {
      addItem({ id, name: teacher.user?.full_name || teacher.full_name, type: 'teacher', path: '/admin/staff/' + id, subtitle: teacher.department });
    }
  }, [teacher, id]);

  const assignments = Array.isArray(assignmentsData?.assignments) ? assignmentsData.assignments : [];
  const teacherName = teacher?.user?.full_name || teacher?.full_name || '';
  const teacherEmail = teacher?.user?.email || teacher?.email || '';
  const teacherPhone = teacher?.user?.phone || teacher?.phone || '';

  const handlePrint = () => setShowPrintModal(true);
  const handleExportPdf = () => setShowPrintModal(true);

  const executePrint = () => {
    const t = teacher || {};
    const school = schoolProfile || {};
    const w = window.open('', '_blank');
    const css = `body{font-family:-apple-system,sans-serif;padding:40px;max-width:800px;margin:0 auto;color:#1e293b;font-size:13px} .header{text-align:center;border-bottom:2px solid #1e293b;padding-bottom:16px;margin-bottom:24px} .header h1{margin:0;font-size:20px;text-transform:uppercase;letter-spacing:1px} .header p{margin:3px 0;font-size:11px;color:#64748b} .doc-title{text-align:center;margin:12px 0 0;padding-top:10px;border-top:1px solid #e2e8f0;font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:1.5px} .section{margin-bottom:20px} .section h3{font-size:13px;font-weight:bold;border-bottom:1px solid #cbd5e1;padding-bottom:6px;margin:0 0 10px;text-transform:uppercase;letter-spacing:0.5px;color:#334155} .grid{display:grid;grid-template-columns:1fr 1fr;gap:6px 24px} .field{display:flex;gap:8px;padding:4px 0} .field .label{font-size:11px;color:#64748b;min-width:140px} .field .value{font-size:12px;font-weight:500} table{width:100%;border-collapse:collapse;margin-top:8px;font-size:11px} th,td{padding:6px 10px;border:1px solid #e2e8f0;text-align:left} th{background:#f8fafc;font-weight:600;font-size:10px;text-transform:uppercase} @media print{body{padding:20px}}`;
    let html = `<html><head><title>${teacherName} - Profile</title><style>${css}</style></head><body>`;
    html += `<div class="header"><h1>${school.name || 'School'}</h1>${school.affiliation ? `<p>${school.affiliation}</p>` : ''}${school.address ? `<p>${school.address}</p>` : ''}<p>${[school.phone, school.email].filter(Boolean).join(' • ')}</p><div class="doc-title">Staff Profile</div></div>`;
    if (printSections.basic) {
      html += `<div class="section"><h3>Basic Information</h3><div class="grid"><div class="field"><span class="label">Name</span><span class="value">${teacherName}</span></div><div class="field"><span class="label">Employee ID</span><span class="value">${t.employee_id || ''}</span></div><div class="field"><span class="label">Email</span><span class="value">${teacherEmail}</span></div><div class="field"><span class="label">Phone</span><span class="value">${teacherPhone}</span></div><div class="field"><span class="label">Department</span><span class="value">${t.department || ''}</span></div><div class="field"><span class="label">Designation</span><span class="value">${t.designation || ''}</span></div><div class="field"><span class="label">Subject</span><span class="value">${t.primary_subject || ''}</span></div><div class="field"><span class="label">Status</span><span class="value">${t.status || 'Active'}</span></div></div></div>`;
    }
    if (printSections.personal) {
      html += `<div class="section"><h3>Personal Details</h3><div class="grid"><div class="field"><span class="label">Date of Birth</span><span class="value">${t.date_of_birth || ''}</span></div><div class="field"><span class="label">Gender</span><span class="value">${t.gender || ''}</span></div><div class="field"><span class="label">Blood Group</span><span class="value">${t.blood_group || ''}</span></div><div class="field"><span class="label">Address</span><span class="value">${t.address || ''}</span></div><div class="field"><span class="label">Emergency Contact</span><span class="value">${t.emergency_contact_name || ''} - ${t.emergency_contact_phone || ''}</span></div></div></div>`;
    }
    if (printSections.professional) {
      html += `<div class="section"><h3>Professional Details</h3><div class="grid"><div class="field"><span class="label">Qualification</span><span class="value">${t.qualification || ''}</span></div><div class="field"><span class="label">Experience</span><span class="value">${t.experience_years ? t.experience_years + ' years' : ''}</span></div><div class="field"><span class="label">Join Date</span><span class="value">${t.join_date || ''}</span></div><div class="field"><span class="label">Specialization</span><span class="value">${t.specialization || ''}</span></div></div></div>`;
    }
    if (printSections.salary) {
      html += `<div class="section"><h3>Salary & Bank Details</h3><div class="grid"><div class="field"><span class="label">Basic Salary</span><span class="value">₹${Number(t.basic_salary || 0).toLocaleString()}</span></div><div class="field"><span class="label">HRA</span><span class="value">₹${Number(t.hra || 0).toLocaleString()}</span></div><div class="field"><span class="label">DA</span><span class="value">₹${Number(t.da || 0).toLocaleString()}</span></div><div class="field"><span class="label">Transport</span><span class="value">₹${Number(t.transport_allowance || t.ta || 0).toLocaleString()}</span></div><div class="field"><span class="label">Bank Name</span><span class="value">${t.bank_name || ''}</span></div><div class="field"><span class="label">Account No</span><span class="value">${t.bank_account || ''}</span></div></div></div>`;
    }
    if (printSections.schedule && assignments.length) {
      html += `<div class="section"><h3>Teaching Schedule</h3><table><tr><th>Class</th><th>Section</th><th>Subject</th><th>Role</th></tr>`;
      assignments.forEach(a => { html += `<tr><td>${a.class_name || ''}</td><td>${a.section_name || ''}</td><td>${a.subject_name || ''}</td><td>${a.is_class_teacher ? 'Class Teacher' : 'Subject Teacher'}</td></tr>`; });
      html += `</table></div>`;
    }
    if (printSections.leaves && t.leave_balances?.length) {
      html += `<div class="section"><h3>Leave Summary</h3><table><tr><th>Leave Type</th><th>Allocated</th><th>Used</th><th>Remaining</th></tr>`;
      t.leave_balances.forEach(l => { html += `<tr><td>${l.leave_type || l.type || ''}</td><td>${l.total_allocated || l.allocated || 0}</td><td>${l.used || 0}</td><td>${l.remaining || 0}</td></tr>`; });
      html += `</table></div>`;
    }
    if (printSections.awards && t.awards?.length) {
      html += `<div class="section"><h3>Awards & Achievements</h3><table><tr><th>Title</th><th>Category</th><th>Date</th></tr>`;
      t.awards.forEach(a => { html += `<tr><td>${a.title || ''}</td><td>${a.category || ''}</td><td>${a.awarded_date || ''}</td></tr>`; });
      html += `</table></div>`;
    }
    html += `<div style="margin-top:40px;border-top:1px solid #e2e8f0;padding-top:12px;display:flex;justify-content:space-between;font-size:10px;color:#94a3b8"><span>Generated on ${new Date().toLocaleDateString('en-IN')}</span><span>${school.name || ''}</span></div></body></html>`;
    w.document.write(html);
    w.document.close();
    w.focus();
    setTimeout(() => w.print(), 300);
    setShowPrintModal(false);
  };

  const handleEdit = () => {
    navigate(`/admin/staff?edit=${id}`);
  };

  const handleEditSection = (section) => {
    const formData = {
      personal: { full_name: teacherName, email: teacherEmail, phone: teacherPhone, gender: teacher?.gender || '', joining_date: teacher?.joining_date || '', address: [teacher?.address_line1, teacher?.city, teacher?.state, teacher?.pincode].filter(Boolean).join(', ') || '' },
      professional: { qualification: teacher?.qualification || '', primary_subject: teacher?.primary_subject || '', max_workload_hours: teacher?.max_workload_hours || '', department: teacher?.department || '', designation: teacher?.designation || '', employment_type: teacher?.employment_type || '' },
    };
    setEditForm(formData[section] || {});
    setEditingSection(section);
  };

  const handleSaveSection = () => {
    const payload = Object.fromEntries(Object.entries(editForm).filter(([, v]) => v !== '' && v !== undefined));
    updateTeacher.mutate({ id, data: payload }, {
      onSuccess: () => { setEditingSection(null); toast.success('Updated successfully'); },
      onError: (err) => { toast.error(err.response?.data?.detail || 'Update failed'); },
    });
  };

  const handleFieldChange = (key, value) => setEditForm(prev => ({ ...prev, [key]: value }));

  const handleAwardAdd = () => { setEditingAward(null); setAwardForm({ title: '', category: '', description: '', awarded_date: '', awarded_by: '', level: '' }); setAwardModalOpen(true); };
  const handleAwardEdit = (award) => { setEditingAward(award); setAwardForm({ title: award.title || '', category: award.category || '', description: award.description || '', awarded_date: award.awarded_date || '', awarded_by: award.awarded_by || '', level: award.level || '' }); setAwardModalOpen(true); };
  const handleAwardDelete = (award) => { setDeleteConfirm({ message: 'Delete this award?', onConfirm: () => { deleteAward.mutate({ id, awardId: award.id }, { onSuccess: () => toast.success('Award deleted'), onError: (e) => toast.error(e.response?.data?.detail || 'Failed') }); setDeleteConfirm(null); } }); };
  const handleAwardSave = () => {
    const payload = Object.fromEntries(Object.entries(awardForm).filter(([, v]) => v !== ''));
    if (editingAward) {
      updateAward.mutate({ id, awardId: editingAward.id, data: payload }, { onSuccess: () => { setAwardModalOpen(false); toast.success('Award updated'); }, onError: (e) => toast.error(e.response?.data?.detail || 'Failed') });
    } else {
      createAward.mutate({ id, data: payload }, { onSuccess: () => { setAwardModalOpen(false); toast.success('Award added'); }, onError: (e) => toast.error(e.response?.data?.detail || 'Failed') });
    }
  };

  return (
    <TeacherDetailView
      teacher={teacher}
      assignments={assignments}
      isLoading={isLoading}
      onEdit={handleEdit}
      onResetPassword={() => setResetPwOpen(true)}
      onPrint={handlePrint}
      onExportPdf={handleExportPdf}
      onBack={() => navigate('/admin/staff')}
      breadcrumbItems={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Staff', href: '/admin/staff' }, { label: 'Profile' }]}
      editingSection={editingSection}
      editForm={editForm}
      onEditSection={handleEditSection}
      onSaveSection={handleSaveSection}
      onCancelEdit={() => setEditingSection(null)}
      onFieldChange={handleFieldChange}
      isSaving={updateTeacher.isPending}
      onAwardAdd={handleAwardAdd}
      onAwardEdit={handleAwardEdit}
      onAwardDelete={handleAwardDelete}
    >
      <Modal open={awardModalOpen} onClose={() => setAwardModalOpen(false)} title={editingAward ? 'Edit Award' : 'Add Award'} size="md">
        <div className="grid grid-cols-2 gap-3">
          <div><label className="text-xs text-slate-600">Title *</label><input value={awardForm.title} onChange={e => setAwardForm({...awardForm, title: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
          <div><label className="text-xs text-slate-600">Category</label><input value={awardForm.category} onChange={e => setAwardForm({...awardForm, category: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
          <div><label className="text-xs text-slate-600">Awarded By</label><input value={awardForm.awarded_by} onChange={e => setAwardForm({...awardForm, awarded_by: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
          <div><label className="text-xs text-slate-600">Level</label><input value={awardForm.level} onChange={e => setAwardForm({...awardForm, level: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
          <div><label className="text-xs text-slate-600">Date</label><DatePicker value={awardForm.awarded_date} onChange={(v) => setAwardForm({...awardForm, awarded_date: v})} /></div>
          <div className="col-span-2"><label className="text-xs text-slate-600">Description</label><textarea value={awardForm.description} onChange={e => setAwardForm({...awardForm, description: e.target.value})} rows={2} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm" /></div>
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <Button variant="ghost" onClick={() => setAwardModalOpen(false)}>Cancel</Button>
          <Button variant="primary" disabled={!awardForm.title || createAward.isPending || updateAward.isPending} onClick={handleAwardSave}>{(createAward.isPending || updateAward.isPending) ? 'Saving...' : 'Save'}</Button>
        </div>
      </Modal>
      <Modal open={editOpen} onClose={() => setEditOpen(false)} title="Edit Teacher Profile" size="lg">
        <div className="grid grid-cols-2 gap-3">
          <div><label className="text-xs text-slate-600">Full Name</label><input value={editForm.full_name || ''} onChange={e => setEditForm({...editForm, full_name: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <div><label className="text-xs text-slate-600">Email</label><input value={editForm.email || ''} onChange={e => setEditForm({...editForm, email: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <div><label className="text-xs text-slate-600">Phone</label><input value={(editForm.phone || '').replace(/^\+91[-\s]?/, '')} onChange={e => setEditForm({...editForm, phone: e.target.value.replace(/^\+91[-\s]?/, '')})} maxLength={10} placeholder="9876543210" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <div><label className="text-xs text-slate-600">Primary Subject</label><input value={editForm.primary_subject || ''} onChange={e => setEditForm({...editForm, primary_subject: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <div><label className="text-xs text-slate-600">Qualification</label><input value={editForm.qualification || ''} onChange={e => setEditForm({...editForm, qualification: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <div><label className="text-xs text-slate-600">Max Workload (hrs/week)</label><input type="number" value={editForm.max_workload_hours || ''} onChange={e => setEditForm({...editForm, max_workload_hours: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <div><label className="text-xs text-slate-600">Department</label><input value={editForm.department || ''} onChange={e => setEditForm({...editForm, department: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <div><label className="text-xs text-slate-600">Designation</label><input value={editForm.designation || ''} onChange={e => setEditForm({...editForm, designation: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <div><label className="text-xs text-slate-600">Gender</label><select value={editForm.gender || ''} onChange={e => setEditForm({...editForm, gender: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400"><option value="">Select</option><option value="Male">Male</option><option value="Female">Female</option><option value="Other">Other</option></select></div>
          <div><label className="text-xs text-slate-600">Employment Type</label><select value={editForm.employment_type || ''} onChange={e => setEditForm({...editForm, employment_type: e.target.value})} className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400"><option value="">Select</option><option value="Full-time">Full-time</option><option value="Part-time">Part-time</option><option value="Contract">Contract</option></select></div>
          <div><label className="text-xs text-slate-600">Joining Date</label><DatePicker value={editForm.joining_date || ''} onChange={(v) => setEditForm({...editForm, joining_date: v})} /></div>
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <Button variant="ghost" onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button variant="primary" disabled={updateTeacher.isPending} onClick={() => { const payload = Object.fromEntries(Object.entries(editForm).filter(([,v]) => v !== '')); updateTeacher.mutate({ id, data: payload }, { onSuccess: () => setEditOpen(false) }); }}>{updateTeacher.isPending ? 'Saving...' : 'Save Changes'}</Button>
        </div>
      </Modal>

      <ResetPasswordModal
        open={resetPwOpen}
        onClose={() => setResetPwOpen(false)}
        userName={teacherName}
        loading={resetPwLoading}
        onSubmit={(pw) => {
          setResetPwLoading(true);
          api.post(`/admin/teachers/${id}/reset-password`, { password: pw })
            .then(() => { setResetPwOpen(false); setResetPwLoading(false); toast.success('Password reset successfully'); })
            .catch(err => { setResetPwLoading(false); toast.error(err.response?.data?.detail || 'Failed to reset password'); });
        }}
      />

      <ConfirmDialog open={!!deleteConfirm} onClose={() => setDeleteConfirm(null)} onConfirm={() => deleteConfirm?.onConfirm()} title="Confirm Delete" message={deleteConfirm?.message || 'Are you sure?'} confirmText="Delete" />

      {/* Print Profile Modal */}
      <Modal open={showPrintModal} onClose={() => setShowPrintModal(false)} title="Print Staff Profile" size="sm">
        <div className="space-y-4">
          <p className="text-sm text-slate-600">Select sections to include:</p>
          <div className="space-y-2">
            {[
              { key: 'basic', label: 'Basic Information' },
              { key: 'personal', label: 'Personal Details' },
              { key: 'professional', label: 'Professional Details' },
              { key: 'salary', label: 'Salary & Bank Details' },
              { key: 'schedule', label: 'Teaching Schedule' },
              { key: 'leaves', label: 'Leave Summary' },
              { key: 'awards', label: 'Awards & Achievements' },
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
    </TeacherDetailView>
  );
}
