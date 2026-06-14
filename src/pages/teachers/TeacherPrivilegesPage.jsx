import { useState } from 'react';
import { Plus, Pencil, Trash2, Users, CheckCircle, GraduationCap, BookOpen } from 'lucide-react';
import { useTeachers, useAssignClass, useUpdateTeacher, useRemoveClassAssignment } from '../../services/teacherService';
import { Button, Modal, Badge } from 'school-erp-ui-shared';

const PRIVILEGE_CATEGORIES = [
  { key: 'attendance', label: 'Attendance', permissions: ['view', 'mark', 'edit'] },
  { key: 'assignments', label: 'Assignments', permissions: ['view', 'create', 'edit', 'delete', 'grade'] },
  { key: 'grades', label: 'Grades', permissions: ['view', 'add', 'edit'] },
  { key: 'examinations', label: 'Exams', permissions: ['view', 'create', 'edit'] },
];

export default function TeacherPrivilegesPage() {
  const [assignDialog, setAssignDialog] = useState({ open: false, teacher: null });
  const [privDialog, setPrivDialog] = useState({ open: false, teacher: null, assignment: null });
  const [assignForm, setAssignForm] = useState({ class_name: '', section: '', subject: '', is_class_teacher: false });
  const [privileges, setPrivileges] = useState({});

  const { data: teachersData } = useTeachers();
  const assignClass = useAssignClass();
  const updateTeacher = useUpdateTeacher();
  const removeAssignment = useRemoveClassAssignment();

  const teachers = (teachersData?.results || teachersData) ?? [];

  const handleAssignClass = () => {
    assignClass.mutate({ id: assignDialog.teacher.id, data: assignForm }, {
      onSuccess: () => { setAssignDialog({ open: false, teacher: null }); setAssignForm({ class_name: '', section: '', subject: '', is_class_teacher: false }); },
    });
  };

  const handleSavePrivileges = () => {
    updateTeacher.mutate({ id: privDialog.teacher.id, data: { privileges, assignmentId: privDialog.assignment.id } }, {
      onSuccess: () => setPrivDialog({ open: false, teacher: null, assignment: null }),
    });
  };

  const handleRemoveAssignment = (teacherId, assignmentId) => { removeAssignment.mutate({ teacherId, assignmentId }); };

  const getPrivilegeProgress = (assignment, category) => {
    const privs = assignment.privileges?.[category.key] || [];
    return `${privs.length}/${category.permissions.length}`;
  };

  const totalTeachers = teachers.length;
  const assignedTeachers = teachers.filter(t => t.class_assignments?.length > 0).length;
  const classTeachers = teachers.filter(t => t.class_assignments?.some(a => a.is_class_teacher)).length;
  const totalAssignments = teachers.reduce((sum, t) => sum + (t.class_assignments?.length || 0), 0);

  const kpis = [
    { label: 'Total Teachers', value: totalTeachers, icon: Users, color: 'text-blue-600', bg: 'bg-gradient-to-br from-blue-50 to-blue-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(59,130,246,0.3)]' },
    { label: 'Assigned Teachers', value: assignedTeachers, icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-gradient-to-br from-emerald-50 to-emerald-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(16,185,129,0.3)]' },
    { label: 'Class Teachers', value: classTeachers, icon: GraduationCap, color: 'text-purple-600', bg: 'bg-gradient-to-br from-purple-50 to-purple-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(147,51,234,0.3)]' },
    { label: 'Total Assignments', value: totalAssignments, icon: BookOpen, color: 'text-orange-600', bg: 'bg-gradient-to-br from-orange-50 to-orange-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(249,115,22,0.3)]' },
  ];

  return (
    <div>
      <div className="mb-4"><h1 className="text-2xl md:text-3xl font-bold text-slate-900">Teacher Privileges & Class Assignments</h1><p className="text-sm text-slate-500 mt-1">Manage teacher access rights and class assignments</p></div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
        {kpis.map(k => (
          <div key={k.label} className={`bg-white border border-slate-200 rounded-xl p-4 md:p-5 flex items-center justify-between transition-all duration-200 hover:-translate-y-1 ${k.glow} cursor-default group`}>
            <div><p className="text-xs text-slate-500 font-medium">{k.label}</p><p className="text-xl md:text-2xl font-bold text-slate-900 mt-0.5">{k.value}</p></div>
            <div className={`${k.bg} p-2.5 md:p-3 rounded-xl transition-transform duration-200 group-hover:scale-110`}><k.icon className={`w-5 h-5 ${k.color}`} /></div>
          </div>
        ))}
      </div>

      <div className="flex flex-col gap-4">
        {teachers.map(teacher => (
          <div key={teacher.id} className="bg-white border border-slate-200 rounded-xl overflow-visible transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
            <div className="flex justify-between items-start p-4 pb-3">
              <div className="flex gap-3">
                <div className="w-[52px] h-[52px] rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-sm font-bold shadow-sm">{teacher.user?.full_name?.split(' ').map(n => n[0]).join('').slice(0, 3)}</div>
                <div>
                  <p className="text-base font-semibold text-slate-800">{teacher.user?.full_name}</p>
                  <p className="text-xs text-slate-500">{teacher.subject} • {teacher.employee_id}</p>
                  <p className="text-xs text-slate-400">{teacher.user?.email}</p>
                </div>
              </div>
              <Button variant="primary" size="sm" icon={Plus} onClick={() => setAssignDialog({ open: true, teacher })}>Assign Class</Button>
            </div>

            {teacher.class_assignments?.length > 0 && (
              <div className="px-4 pb-4">
                <p className="text-xs font-semibold text-slate-600 mb-2">Assigned Classes:</p>
                <div className="flex flex-col gap-2">
                  {teacher.class_assignments?.map(assignment => (
                    <div key={assignment.id} className="bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 rounded-xl p-3 transition-all duration-200 hover:shadow-sm">
                      <div className="flex justify-between items-center mb-2">
                        <div className="flex gap-2 items-center">
                          <span className="text-xs font-semibold text-slate-800 bg-white border border-slate-200 rounded-md px-2 py-0.5">Class {assignment.class_name}-{assignment.section}</span>
                          <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600">{assignment.subject}</span>
                          {assignment.is_class_teacher && <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-green-100 text-green-600">Class Teacher</span>}
                        </div>
                        <div className="flex items-center gap-1">
                          <button className="text-xs text-slate-500 hover:text-slate-700 flex items-center gap-1 transition-all duration-150 active:scale-[0.97]" onClick={() => { setPrivDialog({ open: true, teacher, assignment }); setPrivileges(assignment.privileges || {}); }}><Pencil className="w-3 h-3" /> Edit Privileges</button>
                          <button className="p-1.5 hover:bg-red-50 rounded-lg transition-all duration-150 active:scale-[0.97]" onClick={() => handleRemoveAssignment(teacher.id, assignment.id)}><Trash2 className="w-4 h-4 text-red-500" /></button>
                        </div>
                      </div>
                      <div className="grid grid-cols-4 gap-3">
                        {PRIVILEGE_CATEGORIES.map(cat => {
                          const pct = (assignment.privileges?.[cat.key]?.length || 0) / cat.permissions.length * 100;
                          return (
                            <div key={cat.key}>
                              <p className="text-[10px] text-slate-500 mb-1">{cat.label}: {getPrivilegeProgress(assignment, cat)}</p>
                              <div className="w-full h-1.5 bg-slate-200 rounded-full"><div className="h-full bg-green-500 rounded-full transition-all duration-300" style={{ width: `${pct}%` }} /></div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Assign Class Modal */}
      <Modal open={assignDialog.open} onClose={() => setAssignDialog({ open: false, teacher: null })} title={`Assign Class to ${assignDialog.teacher?.user?.full_name}`}>
        <div className="flex flex-col gap-3 p-4">
          <div><label className="text-xs text-slate-600">Class</label><input value={assignForm.class_name} onChange={e => setAssignForm({ ...assignForm, class_name: e.target.value })} placeholder="e.g., 10" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <div><label className="text-xs text-slate-600">Section</label><input value={assignForm.section} onChange={e => setAssignForm({ ...assignForm, section: e.target.value })} placeholder="e.g., A" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <div><label className="text-xs text-slate-600">Subject</label><input value={assignForm.subject} onChange={e => setAssignForm({ ...assignForm, subject: e.target.value })} placeholder="e.g., Mathematics" className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400" /></div>
          <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={assignForm.is_class_teacher} onChange={e => setAssignForm({ ...assignForm, is_class_teacher: e.target.checked })} className="rounded" /> Assign as Class Teacher (Full privileges)</label>
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 text-xs text-blue-700">Note: Subject teachers get standard privileges with limited administrative access.</div>
        </div>
        <div className="flex justify-end gap-2 px-4 pb-4">
          <Button variant="ghost" onClick={() => setAssignDialog({ open: false, teacher: null })}>Cancel</Button>
          <Button variant="primary" onClick={handleAssignClass}>Assign Class</Button>
        </div>
      </Modal>

      {/* Edit Privileges Modal */}
      <Modal open={privDialog.open} onClose={() => setPrivDialog({ open: false, teacher: null, assignment: null })} title={`Edit Privileges - Class ${privDialog.assignment?.class_name}-${privDialog.assignment?.section}`} size="lg">
        <div className="p-4 space-y-4">
          {PRIVILEGE_CATEGORIES.map(cat => (
            <div key={cat.key}>
              <p className="text-sm font-semibold text-slate-800 mb-2">{cat.label}</p>
              <div className="flex gap-4 flex-wrap">
                {cat.permissions.map(perm => (
                  <label key={perm} className="flex items-center gap-2 text-sm">
                    <input type="checkbox" checked={privileges[cat.key]?.includes(perm) || false} onChange={e => {
                      const current = privileges[cat.key] || [];
                      setPrivileges({ ...privileges, [cat.key]: e.target.checked ? [...current, perm] : current.filter(p => p !== perm) });
                    }} className="rounded" />
                    {perm}
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="flex justify-end gap-2 px-4 pb-4">
          <Button variant="ghost" onClick={() => setPrivDialog({ open: false, teacher: null, assignment: null })}>Cancel</Button>
          <Button variant="primary" onClick={handleSavePrivileges}>Save Privileges</Button>
        </div>
      </Modal>
    </div>
  );
}
