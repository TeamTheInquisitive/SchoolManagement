import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserCheck, Trash2, ChevronDown, ChevronRight, Users, Shuffle, BarChart2, User, Eye } from 'lucide-react';
import { Button, Badge, Modal, SearchableSelect, Skeleton, useToast, Breadcrumb, Checkbox, SearchInput, ConfirmDialog } from 'school-erp-ui-shared';
import { useMentorList, useMentorStudentsByTeacher, useMentorTeachers, useMentorStudents, useAssignMentor, useRemoveMentor, useShuffleAssign } from '../../services/mentoringService';
import { useClassSections } from '../../services/settingsService';

export default function MentoringPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const [showAssign, setShowAssign] = useState(false);
  const [preSelectedTeacher, setPreSelectedTeacher] = useState('');
  const [expanded, setExpanded] = useState({});
  const [teacherSearch, setTeacherSearch] = useState('');
  const [showShuffle, setShowShuffle] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const { data: mentorData, isLoading } = useMentorList();
  const removeMutation = useRemoveMentor();
  const shuffleMutation = useShuffleAssign();

  const allMentors = mentorData?.mentors || [];
  const mentors = allMentors.filter(m => !teacherSearch || m.staff_name.toLowerCase().includes(teacherSearch.toLowerCase()));

  const totalMentees = mentorData?.total_mentees || allMentors.reduce((s, m) => s + (m.mentee_count || 0), 0);
  const avgPerMentor = allMentors.length > 0 ? Math.round(totalMentees / allMentors.length) : 0;
  const totalEnrolled = mentorData?.total_enrolled || 0;
  const unassignedCount = Math.max(0, totalEnrolled - totalMentees);

  const toggleExpand = (staffId) => setExpanded(prev => ({ ...prev, [staffId]: !prev[staffId] }));

  const confirmRemove = (id, studentName) => {
    setDeleteConfirm({ id, studentName });
  };

  const executeRemove = () => {
    if (!deleteConfirm) return;
    removeMutation.mutate(deleteConfirm.id, {
      onSuccess: () => { toast.success('Student removed from mentor'); setDeleteConfirm(null); },
      onError: (err) => { toast.error(err.response?.data?.detail || 'Failed to remove'); setDeleteConfirm(null); },
    });
  };

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Mentoring' }]} />
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Mentoring</h1>
          <p className="text-sm text-slate-500 mt-1">Manage teacher-student mentor assignments</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" icon={Shuffle} onClick={() => setShowShuffle(true)} disabled={shuffleMutation.isPending}>{shuffleMutation.isPending ? 'Shuffling...' : 'Shuffle & Auto Assign'}</Button>
          <Button variant="primary" icon={UserCheck} onClick={() => { setPreSelectedTeacher(''); setShowAssign(true); }}>Assign Students</Button>
        </div>
      </div>

      {/* Summary Stats */}
      {!isLoading && allMentors.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-50 to-indigo-100 flex items-center justify-center">
              <Users size={18} className="text-indigo-600" />
            </div>
            <div>
              <p className="text-xl font-bold text-slate-900">{allMentors.length}</p>
              <p className="text-[11px] text-slate-500">Total Mentors</p>
            </div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-50 to-emerald-100 flex items-center justify-center">
              <UserCheck size={18} className="text-emerald-600" />
            </div>
            <div>
              <p className="text-xl font-bold text-slate-900">{totalMentees}</p>
              <p className="text-[11px] text-slate-500">Total Mentees</p>
            </div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-50 to-amber-100 flex items-center justify-center">
              <BarChart2 size={18} className="text-amber-600" />
            </div>
            <div>
              <p className="text-xl font-bold text-slate-900">{avgPerMentor}</p>
              <p className="text-[11px] text-slate-500">Avg per Mentor</p>
            </div>
          </div>
          <div className={`bg-white border rounded-xl p-4 flex items-center gap-3 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm ${unassignedCount > 0 ? 'border-red-200' : 'border-slate-200'}`}>
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${unassignedCount > 0 ? 'bg-gradient-to-br from-red-50 to-red-100' : 'bg-gradient-to-br from-emerald-50 to-emerald-100'}`}>
              <User size={18} className={unassignedCount > 0 ? 'text-red-600' : 'text-emerald-600'} />
            </div>
            <div>
              <p className={`text-xl font-bold ${unassignedCount > 0 ? 'text-red-600' : 'text-emerald-600'}`}>{unassignedCount}</p>
              <p className="text-[11px] text-slate-500">Unassigned</p>
            </div>
          </div>
        </div>
      )}

      {!isLoading && mentors.length > 0 && (
        <div className="mb-4">
          <SearchInput value={teacherSearch} onChange={setTeacherSearch} placeholder="Search teacher by name..." />
        </div>
      )}

      {isLoading ? (
        <div className="space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-20 rounded-xl" />)}</div>
      ) : mentors.length === 0 && !teacherSearch ? (
        <div className="text-center py-12 text-slate-500">
          <Users className="w-12 h-12 mx-auto mb-3 text-slate-300" />
          <p className="text-sm font-medium">No mentor assignments yet</p>
          <p className="text-xs text-slate-400 mt-1">Click "Assign Students" or "Shuffle & Auto Assign" to get started.</p>
        </div>
      ) : mentors.length === 0 && teacherSearch ? (
        <div className="text-center py-8 text-slate-400 text-sm">No teachers matching "{teacherSearch}"</div>
      ) : (
        <div className="space-y-3">
          {mentors.map(m => {
            const loadPct = avgPerMentor > 0 ? Math.round(((m.mentee_count || 0) / avgPerMentor) * 100) : 0;
            const loadColor = loadPct > 130 ? 'text-red-600' : loadPct > 100 ? 'text-amber-600' : 'text-emerald-600';
            const loadBarColor = loadPct > 130 ? 'bg-red-500' : loadPct > 100 ? 'bg-amber-500' : 'bg-emerald-500';
            return (
              <div key={m.staff_id} className="bg-white border border-slate-200 rounded-xl overflow-hidden transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
                <div className="flex items-center justify-between p-4 cursor-pointer" onClick={() => toggleExpand(m.staff_id)}>
                  <div className="flex items-center gap-3">
                    <div className="w-11 h-11 rounded-full bg-gradient-to-br from-primary-500 to-indigo-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                      {(m.staff_name || '').slice(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-semibold text-slate-900">{m.staff_name}</p>
                      <p className="text-xs text-slate-500">{m.designation || m.department || 'Teacher'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    {/* Load indicator */}
                    <div className="hidden md:flex items-center gap-2 w-32">
                      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${loadBarColor} transition-all duration-500`} style={{ width: `${Math.min(loadPct, 150)}%` }} />
                      </div>
                      <span className={`text-[10px] font-semibold ${loadColor}`}>{m.mentee_count || 0}</span>
                    </div>
                    <Badge variant="info">{m.mentee_count} mentee{m.mentee_count !== 1 ? 's' : ''}</Badge>
                    <button onClick={(e) => { e.stopPropagation(); setPreSelectedTeacher(m.staff_id); setShowAssign(true); }} className="flex items-center gap-1 px-2.5 py-1.5 text-[11px] font-medium text-primary-600 hover:bg-primary-50 rounded-lg transition-colors">
                      <UserCheck size={12} /> Add
                    </button>
                    {expanded[m.staff_id] ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                  </div>
                </div>
                {expanded[m.staff_id] && (
                  <MentorStudentsList staffId={m.staff_id} onRemove={confirmRemove} navigate={navigate} />
                )}
              </div>
            );
          })}
        </div>
      )}

      {showAssign && <AssignModal onClose={() => { setShowAssign(false); setPreSelectedTeacher(''); }} defaultTeacherId={preSelectedTeacher} />}

      {/* Shuffle Confirmation Modal */}
      <Modal open={showShuffle} onClose={() => setShowShuffle(false)} title="Shuffle & Auto Assign" size="sm" persistent={false}>
        <div className="space-y-4">
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
            <p className="text-sm font-medium text-amber-800">This will replace all existing assignments</p>
            <p className="text-xs text-amber-700 mt-1">All current mentor-student mappings will be removed and redistributed evenly.</p>
          </div>
          <ul className="text-xs text-slate-500 space-y-1 list-disc list-inside">
            <li>Remove all current mentor assignments</li>
            <li>Randomly shuffle all active students</li>
            <li>Distribute evenly across active teachers</li>
          </ul>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" onClick={() => setShowShuffle(false)}>Cancel</Button>
            <Button variant="primary" icon={Shuffle} onClick={() => { shuffleMutation.mutate(undefined, { onSuccess: (d) => { toast.success(d.message); setShowShuffle(false); }, onError: (e) => toast.error(e.response?.data?.detail || 'Failed') }); }} disabled={shuffleMutation.isPending}>{shuffleMutation.isPending ? 'Shuffling...' : 'Confirm & Shuffle'}</Button>
          </div>
        </div>
      </Modal>

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        onConfirm={executeRemove}
        loading={removeMutation.isPending}
        title="Remove Mentee"
        message={deleteConfirm ? `Are you sure you want to remove "${deleteConfirm.studentName}" from their mentor? This can be re-assigned later.` : ''}
        confirmText="Remove"
      />
    </div>
  );
}

function MentorStudentsList({ staffId, onRemove, navigate }) {
  const { data, isLoading } = useMentorStudentsByTeacher(staffId);
  const students = data?.students || [];

  if (isLoading) return <div className="px-4 pb-4"><Skeleton className="h-16 rounded-lg" /></div>;
  if (students.length === 0) return <div className="px-4 pb-4 text-sm text-slate-400 ml-14">No students assigned yet</div>;

  return (
    <div className="border-t border-slate-100 bg-slate-50/50 px-4 py-3">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 ml-14">
        {students.map(s => (
          <div key={s.id} className="flex items-center justify-between p-2.5 bg-white rounded-lg border border-slate-100 group hover:border-slate-200 transition-colors">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                {(s.student_name || '').slice(0, 2).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium text-slate-800 truncate">{s.student_name}</p>
                <p className="text-[10px] text-slate-400">{s.class_section}{s.assigned_date ? ` • Since ${s.assigned_date}` : ''}</p>
              </div>
            </div>
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button onClick={() => navigate(`/admin/students/${s.student_id || s.id}`)} className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors" title="View student">
                <Eye size={13} className="text-slate-400" />
              </button>
              <button onClick={() => onRemove(s.id, s.student_name)} className="p-1.5 hover:bg-red-50 rounded-lg transition-colors" title="Remove from mentor">
                <Trash2 size={13} className="text-red-400" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AssignModal({ onClose, defaultTeacherId = '' }) {
  const toast = useToast();
  const [teacherId, setTeacherId] = useState(defaultTeacherId);
  const [classSectionId, setClassSectionId] = useState('');
  const [selectedStudents, setSelectedStudents] = useState([]);

  const { data: teachersData } = useMentorTeachers();
  const { data: classSectionsData } = useClassSections();
  const { data: studentsData, isLoading: studentsLoading } = useMentorStudents(classSectionId);
  const assignMutation = useAssignMentor();

  const teachers = (teachersData?.teachers || []).map(t => ({ value: t.id, label: t.name }));
  const classSections = (classSectionsData?.classes || []).flatMap(cls =>
    cls.sections.map(sec => ({ value: sec.id, label: `Class ${cls.name} - ${sec.section_name}` }))
  );
  const students = studentsData?.students || [];

  const toggleStudent = (id) => {
    setSelectedStudents(prev => prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]);
  };

  const selectAll = () => setSelectedStudents(students.map(s => s.id));
  const deselectAll = () => setSelectedStudents([]);

  const handleSubmit = () => {
    if (!teacherId || selectedStudents.length === 0) {
      toast.error('Select a teacher and at least one student');
      return;
    }
    assignMutation.mutate({ staff_id: teacherId, student_ids: selectedStudents }, {
      onSuccess: (data) => { toast.success(`${data.assigned} student(s) assigned`); onClose(); },
      onError: (err) => toast.error(err.response?.data?.detail || 'Failed to assign'),
    });
  };

  return (
    <Modal open onClose={onClose} title="Assign Students to Mentor" size="lg">
      <div className="space-y-4">
        <SearchableSelect
          label="Teacher *"
          options={teachers}
          value={teacherId}
          onChange={setTeacherId}
          placeholder="Select a teacher..."
        />
        <SearchableSelect
          label="Class & Section"
          options={classSections}
          value={classSectionId}
          onChange={(v) => { setClassSectionId(v); setSelectedStudents([]); }}
          placeholder="Filter by class-section..."
        />
        {classSectionId && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-slate-700">
                Students {selectedStudents.length > 0 && <span className="text-xs text-primary-600 ml-1">({selectedStudents.length} selected)</span>}
              </label>
              {students.length > 0 && (
                <div className="flex gap-2">
                  <button onClick={selectAll} className="text-[11px] text-primary-600 hover:text-primary-700 font-medium">Select All</button>
                  {selectedStudents.length > 0 && <button onClick={deselectAll} className="text-[11px] text-slate-500 hover:text-slate-700 font-medium">Clear</button>}
                </div>
              )}
            </div>
            {studentsLoading ? (
              <Skeleton className="h-32 rounded-lg" />
            ) : students.length === 0 ? (
              <div className="text-center py-6 border border-dashed border-slate-200 rounded-lg">
                <p className="text-sm text-slate-400">No unassigned students in this class-section</p>
              </div>
            ) : (
              <div className="max-h-60 overflow-y-auto border border-slate-200 rounded-lg divide-y divide-slate-100">
                {students.map(s => (
                  <label key={s.id} className="flex items-center gap-3 px-3 py-2.5 hover:bg-primary-50/40 cursor-pointer transition-colors">
                    <input
                      type="checkbox"
                      checked={selectedStudents.includes(s.id)}
                      onChange={() => toggleStudent(s.id)}
                      className="rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                    />
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 text-white flex items-center justify-center text-[9px] font-bold flex-shrink-0">
                      {(s.name || '').slice(0, 2).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-800">{s.name}</p>
                      <p className="text-[10px] text-slate-400">{s.class_section}</p>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>
        )}
        <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button variant="primary" onClick={handleSubmit} disabled={assignMutation.isPending || !teacherId || selectedStudents.length === 0}>
            {assignMutation.isPending ? 'Assigning...' : `Assign ${selectedStudents.length || ''} Student${selectedStudents.length !== 1 ? 's' : ''}`}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
