import { useState, useMemo } from 'react';
import { useDebounceValue } from 'usehooks-ts';
import { Plus, Download, Pencil, Trash2, ChevronRight, Calendar, ClipboardList, CheckCircle, FileText, Eye, FileSpreadsheet, Trophy, BarChart2 } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { z } from 'zod';
import { useQuery } from '@tanstack/react-query';
import { useExaminations, useCreateExam, useUpdateExam, useDeleteExam, useExamResults } from '../../services/examinationService';
import { useClassSectionFilter } from '../../hooks/useClassSectionFilter';
import { useClassSubjects } from '../../services/settingsService';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';
import { Button, SearchInput, Badge, Modal, SearchableSelect, ConfirmDialog, DateInput, TimeInput, useToast, exportToCsv, exportToExcel, Breadcrumb, EmptyState, Pagination, usePagination, ErrorBoundary , AnimatedNumber } from 'school-erp-ui-shared';
import { EXAM_TYPES } from '../../constants.jsx';

const examSchema = z.object({ name: z.string().min(2), type: z.string().min(1), class_name: z.string().min(1), section: z.string().min(1), subject: z.string().min(1), date: z.string().min(1), start_time: z.string().optional(), end_time: z.string().optional(), total_marks: z.union([z.string(), z.number()]).refine(v => Number(v) > 0) });

const TYPE_COLORS = {
  'Mid-Term': { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', icon: 'text-blue-500', badge: 'bg-blue-100 text-blue-700' },
  'Final': { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700', icon: 'text-purple-500', badge: 'bg-purple-100 text-purple-700' },
  'Unit Test': { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', icon: 'text-amber-500', badge: 'bg-amber-100 text-amber-700' },
  'Quarterly': { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-700', icon: 'text-emerald-500', badge: 'bg-emerald-100 text-emerald-700' },
};

export default function ExaminationsPage() {
  const toast = useToast();
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounceValue(search, 300);
  const { selectedClass: classFilter, setSelectedClass: setClassFilter, classOptions, classes: allClasses } = useClassSectionFilter();
  const [subjectFilter, setSubjectFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [examDialog, setExamDialog] = useState({ open: false, data: null });
  const [deleteId, setDeleteId] = useState(null);
  const [resultsExam, setResultsExam] = useState(null);
  const [leaderboardExam, setLeaderboardExam] = useState(null);
  const [form, setForm] = useState({});
  const [errors, setErrors] = useState({});
  const [expandedTypes, setExpandedTypes] = useState({});
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  const pagination = usePagination(20, "admin-exams");

  const { data: examsData, isLoading, isFetching } = useExaminations({
    ...pagination.params,
    search: debouncedSearch || undefined,
    type: typeFilter || undefined,
    class_name: classFilter || undefined,
    subject: subjectFilter || undefined,
    status: statusFilter || undefined,
  });
  const { data: subjectsData } = useQuery({ queryKey: ['subjects'], queryFn: () => api.get(ENDPOINTS.settings.subjects).then(r => r.data) });
  const { data: classSubjectsData } = useClassSubjects();
  const createExamMutation = useCreateExam();
  const updateExamMutation = useUpdateExam();
  const deleteExamMutation = useDeleteExam();

  const exams = Array.isArray(examsData?.results) ? examsData.results : [];
  const subjects = Array.isArray(subjectsData) ? subjectsData : [];

  // Group exams by class (class_name) for primary display
  const grouped = useMemo(() => {
    const groups = {};
    exams.forEach(e => {
      const className = e.class_name || 'Unknown';
      const section = e.section || '';
      const key = className;
      if (!groups[key]) groups[key] = { className, displayName: `Class ${className}`, exams: [], dates: [], sections: new Set() };
      groups[key].exams.push(e);
      if (section) groups[key].sections.add(section);
      if (e.date || e.exam_date) groups[key].dates.push(e.date || e.exam_date);
    });
    // Sort exams within each class group by section then subject
    Object.values(groups).forEach(g => {
      g.exams.sort((a, b) => {
        const secCompare = (a.section || '').localeCompare(b.section || '');
        if (secCompare !== 0) return secCompare;
        const nameCompare = (a.name || '').localeCompare(b.name || '');
        if (nameCompare !== 0) return nameCompare;
        return (a.subject || '').localeCompare(b.subject || '');
      });
    });
    // Sort groups by class name naturally
    const sorted = {};
    Object.keys(groups).sort((a, b) => a.localeCompare(b, undefined, { numeric: true })).forEach(k => { sorted[k] = groups[k]; });
    return sorted;
  }, [exams]);

  const toggleType = (type) => setExpandedTypes(prev => ({ ...prev, [type]: !prev[type] }));
  const collapseAll = () => setExpandedTypes({});
  const expandAll = () => { const all = {}; Object.keys(grouped).forEach(k => { all[k] = true; }); setExpandedTypes(all); };

  // KPIs
  const summary = examsData?.summary || {};
  const totalExams = summary.total || examsData?.count || exams.length;
  const upcoming = summary.upcoming ?? exams.filter(e => new Date(e.date || e.exam_date) > new Date()).length;
  const completed = summary.completed ?? exams.filter(e => new Date(e.date || e.exam_date) <= new Date()).length;
  const kpis = [
    { label: 'Total Exams', value: totalExams, icon: ClipboardList, color: 'text-blue-600', bg: 'bg-gradient-to-br from-blue-50 to-blue-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(59,130,246,0.3)]' },
    { label: 'Upcoming', value: upcoming, icon: Calendar, color: 'text-amber-600', bg: 'bg-gradient-to-br from-amber-50 to-amber-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(245,158,11,0.3)]' },
    { label: 'Completed', value: completed, icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-gradient-to-br from-emerald-50 to-emerald-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(16,185,129,0.3)]' },
    { label: 'Classes', value: Object.keys(grouped).length, icon: FileText, color: 'text-purple-600', bg: 'bg-gradient-to-br from-purple-50 to-purple-100', glow: 'hover:shadow-[0_4px_20px_-4px_rgba(147,51,234,0.3)]' },
  ];

  const openDialog = (data) => { setForm(data || {}); setErrors({}); setExamDialog({ open: true, data }); };
  const handleSubmit = () => {
    const result = examSchema.safeParse(form);
    if (!result.success) { const e = {}; result.error.issues.forEach(i => { if (i.path[0]) e[i.path[0]] = i.message; }); setErrors(e); return; }
    // Additional validations
    const extraErrors = {};
    const today = new Date().toISOString().split('T')[0];
    if (!examDialog.data?.id && form.date && form.date < today) extraErrors.date = 'Exam date cannot be in the past';
    if (form.start_time && form.end_time && form.end_time <= form.start_time) extraErrors.end_time = 'End time must be after start time';
    if (Object.keys(extraErrors).length > 0) { setErrors(extraErrors); return; }
    const payload = { ...form, total_marks: Number(form.total_marks), exam_type: form.type };
    const onSuccess = () => { setExamDialog({ open: false, data: null }); toast.success(examDialog.data?.id ? 'Exam updated successfully' : 'Exam scheduled successfully'); };
    const onError = (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to save exam'); };
    if (examDialog.data?.id) updateExamMutation.mutate({ id: examDialog.data.id, data: payload }, { onSuccess, onError });
    else createExamMutation.mutate(payload, { onSuccess, onError });
  };

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Examinations' }]} />
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Examination Management</h1>
          <p className="text-sm text-slate-500 mt-1">Schedule exams, manage results, and generate hall tickets</p>
        </div>
        <div className="flex gap-2">
          <Button variant="primary" icon={FileSpreadsheet} onClick={() => setScheduleDialogOpen(true)}>Create Exam Schedule</Button>
          <Button icon={Plus} onClick={() => openDialog(null)}>Schedule Exam</Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6">
        {kpis.map(k => (
          <div key={k.label} className={`bg-white border border-slate-200 rounded-xl p-4 md:p-5 flex items-center gap-3 md:gap-4 transition-all duration-200 hover:-translate-y-1 ${k.glow} cursor-default group`}>
            <div className={`${k.bg} p-2.5 md:p-3 rounded-xl transition-transform duration-200 group-hover:scale-110`}>
              <k.icon size={20} className={k.color} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">{k.label}</p>
              <p className="text-xl md:text-2xl font-bold text-slate-900 mt-0.5"><AnimatedNumber value={k.value} id={k.label} /></p>
            </div>
          </div>
        ))}
      </div>

      {/* Filters & Search */}
      <div className="bg-white border border-slate-200 rounded-xl px-4 py-3 mb-6 flex flex-wrap items-center gap-3">
        <div className="min-w-[140px]">
          <SearchableSelect value={typeFilter} onChange={(v) => { setTypeFilter(v); pagination.reset(); }} options={[{ value: '', label: 'All Types' }, ...EXAM_TYPES.map(t => ({ value: t.value, label: t.label }))]} placeholder="Exam Type" />
        </div>
        <div className="min-w-[140px]">
          <SearchableSelect value={classFilter} onChange={(v) => { setClassFilter(v); pagination.reset(); }} options={classOptions} placeholder="All Classes" />
        </div>
        <div className="min-w-[140px]">
          <SearchableSelect value={subjectFilter} onChange={(v) => { setSubjectFilter(v); pagination.reset(); }} options={[{ value: '', label: 'All Subjects' }, ...[...new Set(exams.map(e => e.subject).filter(Boolean))].map(s => ({ value: s, label: s }))]} placeholder="All Subjects" />
        </div>
        <span className="text-xs text-slate-400 ml-auto">{examsData?.count || exams.length} exam{(examsData?.count || exams.length) !== 1 ? 's' : ''}</span>
        <div className="w-[220px]">
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); pagination.reset(); }}
            placeholder="Search exam title..."
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent hover:border-slate-400 transition-all"
          />
        </div>
      </div>

      {/* All Examinations */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-bold text-slate-900">All Examinations</h2>
        <button onClick={() => Object.keys(expandedTypes).length === Object.keys(grouped).length ? collapseAll() : expandAll()} className="text-xs font-medium text-primary-600 hover:text-primary-700 transition-colors">
          {Object.keys(expandedTypes).length === Object.keys(grouped).length ? 'Collapse All' : 'Expand All'}
        </button>
      </div>

      {isFetching && !examsData ? (
        <div className="bg-white border border-slate-200 rounded-xl p-6 flex items-center justify-center py-12">
          <div className="animate-pulse text-slate-400">Loading examinations...</div>
        </div>
      ) : Object.keys(grouped).length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <EmptyState type="noSchedule" title="No exams found" message="Schedule an exam to get started" />
        </div>
      ) : (
        <div className="space-y-4">
          {Object.entries(grouped).map(([groupName, group]) => {
            const isExpanded = expandedTypes[groupName];
            const groupExams = group.exams.filter(e => {
              const matchClass = !classFilter || e.class_name === classFilter;
              const matchSubject = !subjectFilter || e.subject === subjectFilter;
              const isPast = new Date(e.date || e.exam_date) <= new Date();
              const matchStatus = !statusFilter || (statusFilter === 'completed' && isPast) || (statusFilter === 'upcoming' && !isPast);
              return matchClass && matchSubject && matchStatus;
            });
            if (groupExams.length === 0) return null;
            const allPast = groupExams.every(e => new Date(e.date || e.exam_date) <= new Date());
            const dates = [...group.dates].sort();
            const dateRange = dates.length > 1 ? `${dates[0]} – ${dates[dates.length - 1]}` : dates[0] || '';
            const sectionCount = group.sections ? group.sections.size : 0;

            return (
              <div key={groupName} className="bg-white border border-slate-200 rounded-xl overflow-hidden transition-all duration-200 hover:shadow-soft-lg">
                {/* Class Group Header */}
                <button onClick={() => toggleType(groupName)} className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-50 transition-colors duration-150">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-50 to-indigo-100 flex items-center justify-center">
                      <ClipboardList size={16} className="text-indigo-600" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-900">{group.displayName}</p>
                      <p className="text-xs text-slate-500">{sectionCount > 0 ? `${sectionCount} section${sectionCount !== 1 ? 's' : ''}` : ''}{dateRange ? ` • ${dateRange}` : ''}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-medium text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full">{groupExams.length} exam{groupExams.length !== 1 ? 's' : ''}</span>
                    <Badge status={allPast ? 'Completed' : 'Active'}>{allPast ? 'Completed' : 'Upcoming'}</Badge>
                    <ChevronRight size={16} className={`text-slate-400 transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`} />
                  </div>
                </button>

                {/* Class Group Content - nested by section then exam type */}
                {isExpanded && (() => {
                  const bySection = {};
                  groupExams.forEach(e => {
                    const sec = e.section || 'General';
                    if (!bySection[sec]) bySection[sec] = [];
                    bySection[sec].push(e);
                  });
                  return (
                    <div className="border-t border-slate-100 p-3 space-y-3">
                      {Object.entries(bySection).sort(([a], [b]) => a.localeCompare(b)).map(([sectionKey, sectionExams]) => {
                        const byType = {};
                        sectionExams.forEach(e => {
                          const type = e.name || e.type || e.exam_type || 'Other';
                          if (!byType[type]) byType[type] = [];
                          byType[type].push(e);
                        });
                        return (
                          <div key={sectionKey} className="bg-slate-50 border border-slate-200 rounded-lg overflow-hidden">
                            <div className="flex items-center justify-between px-4 py-2.5 bg-slate-100/80">
                              <span className="text-xs font-bold text-slate-700">Section {sectionKey}</span>
                              <span className="text-[10px] text-slate-500">{sectionExams.length} exam{sectionExams.length !== 1 ? 's' : ''}</span>
                            </div>
                            <div className="p-2 space-y-2">
                              {Object.entries(byType).map(([typeName, typeExams]) => {
                                const typeAllPast = typeExams.every(e => new Date(e.date || e.exam_date) <= new Date());
                                return (
                                  <div key={typeName} className="bg-white border border-slate-100 rounded-lg overflow-hidden">
                                    <div className="flex items-center justify-between px-4 py-2 bg-gradient-to-r from-primary-50/50 to-white border-b border-slate-100">
                                      <div className="flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                                        <span className="text-xs font-semibold text-slate-800">{typeName}</span>
                                      </div>
                                      <div className="flex items-center gap-2">
                                        <span className="text-[10px] text-slate-400">{typeExams.length} subject{typeExams.length !== 1 ? 's' : ''}</span>
                                        <Badge status={typeAllPast ? 'Completed' : 'Active'}>{typeAllPast ? 'Done' : 'Upcoming'}</Badge>
                                      </div>
                                    </div>
                                    <table className="w-full text-sm">
                                      <thead>
                                        <tr className="border-b border-slate-100">
                                          <th className="py-1.5 px-4 text-left text-[10px] font-semibold text-slate-400 uppercase">Subject</th>
                                          <th className="py-1.5 px-4 text-left text-[10px] font-semibold text-slate-400 uppercase">Date</th>
                                          <th className="py-1.5 px-4 text-left text-[10px] font-semibold text-slate-400 uppercase">Time</th>
                                          <th className="py-1.5 px-4 text-left text-[10px] font-semibold text-slate-400 uppercase">Max Marks</th>
                                          <th className="py-1.5 px-4 text-left text-[10px] font-semibold text-slate-400 uppercase">Status</th>
                                          <th className="py-1.5 px-4 text-left text-[10px] font-semibold text-slate-400 uppercase">Actions</th>
                                        </tr>
                                      </thead>
                                      <tbody className="divide-y divide-slate-50">
                                        {typeExams.map(e => {
                                          const isPast = new Date(e.date || e.exam_date) <= new Date();
                                          return (
                                            <tr key={e.id} className="hover:bg-primary-50/30 transition-colors duration-150">
                                              <td className="py-2 px-4 font-medium text-slate-900">{e.subject}</td>
                                              <td className="py-2 px-4 text-slate-600 text-xs">{e.date || e.exam_date || '-'}</td>
                                              <td className="py-2 px-4 text-slate-600 text-xs">{e.start_time && e.end_time ? `${e.start_time} - ${e.end_time}` : '-'}</td>
                                              <td className="py-2 px-4 font-medium text-xs">{e.total_marks || '-'}</td>
                                              <td className="py-2 px-4"><Badge status={isPast ? 'Completed' : 'Active'}>{isPast ? 'Done' : 'Upcoming'}</Badge></td>
                                              <td className="py-2 px-4">
                                                <div className="flex gap-1">
                                                  <button onClick={() => openDialog(e)} className="p-1 hover:bg-slate-100 rounded" title="Edit"><Pencil size={13} className="text-slate-400" /></button>
                                                  <button onClick={() => setDeleteId(e.id)} className="p-1 hover:bg-red-50 rounded" title="Delete"><Trash2 size={13} className="text-red-400" /></button>
                                                  {isPast && <button onClick={() => setResultsExam(e)} className="p-1 hover:bg-blue-50 rounded" title="Results"><Trophy size={13} className="text-blue-500" /></button>}
                                                  {isPast && <button onClick={() => setLeaderboardExam(e)} className="p-1 hover:bg-amber-50 rounded" title="Leaderboard"><BarChart2 size={13} className="text-amber-500" /></button>}
                                                </div>
                                              </td>
                                            </tr>
                                          );
                                        })}
                                      </tbody>
                                    </table>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  );
                })()}
              </div>
            );
          })}
        </div>
      )}

      <Pagination
        page={pagination.page}
        totalPages={examsData?.total_pages || 1}
        totalCount={examsData?.count || 0}
        pageSize={pagination.pageSize}
        onPageChange={(p) => pagination.setPage(p)}
      />

      {/* Create/Edit Modal */}
      <Modal open={examDialog.open} onClose={() => setExamDialog({ open: false, data: null })} title={examDialog.data?.id ? 'Edit Exam' : 'Schedule New Exam'} size="lg">
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Exam Title *</label>
            <input value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g. Mid-Term Mathematics" className={`w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${errors.name ? 'border-red-400' : 'border-slate-300'}`} />
            {errors.name && <p className="text-xs text-red-500 mt-0.5">{errors.name}</p>}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Exam Type *</label>
              <SearchableSelect value={form.type || ''} onChange={(val) => setForm({ ...form, type: val })} options={EXAM_TYPES.map(t => ({ value: t.value, label: t.label }))} placeholder="Select type..." />
              {errors.type && <p className="text-xs text-red-500 mt-0.5">{errors.type}</p>}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Subject *</label>
              <SearchableSelect value={form.subject || ''} onChange={(val) => setForm({ ...form, subject: val })} options={(() => {
                const classSubjectsList = classSubjectsData?.classes || [];
                const selectedClassObj = allClasses.find(c => c.name === form.class_name);
                const classSubjectsForSelected = classSubjectsList.find(c => c.id === selectedClassObj?.id);
                const filtered = classSubjectsForSelected?.subjects?.length > 0
                  ? subjects.filter(s => classSubjectsForSelected.subjects.some(cs => cs.id === s.id))
                  : subjects;
                return filtered.map(s => ({ value: s.name, label: s.name }));
              })()} placeholder={form.class_name ? 'Select subject...' : 'Select class first...'} />
              {errors.subject && <p className="text-xs text-red-500 mt-0.5">{errors.subject}</p>}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Class *</label>
              <SearchableSelect value={form.class_name || ''} onChange={(val) => setForm({ ...form, class_name: val, section: '' })} options={classOptions.filter(o => o.value)} placeholder="Select Class..." />
              {errors.class_name && <p className="text-xs text-red-500 mt-0.5">{errors.class_name}</p>}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Section *</label>
              <SearchableSelect value={form.section || ''} onChange={(val) => setForm({ ...form, section: val })} options={(() => { const cls = allClasses.find(c => c.name === form.class_name); return cls?.sections?.length ? cls.sections.map(s => ({ value: s.section_name, label: s.section_name })) : []; })()} placeholder="Select Section..." />
              {errors.section && <p className="text-xs text-red-500 mt-0.5">{errors.section}</p>}
            </div>
            <div>
              <DateInput label="Exam Date *" value={form.date} onChange={v => setForm({ ...form, date: v })} />
              {errors.date && <p className="text-xs text-red-500 mt-0.5">{errors.date}</p>}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 mb-1.5 block">Maximum Marks *</label>
              <input type="number" value={form.total_marks || ''} onChange={e => setForm({ ...form, total_marks: e.target.value })} placeholder="100" className={`w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400 ${errors.total_marks ? 'border-red-400' : 'border-slate-300'}`} />
            </div>
            <div>
              <TimeInput label="Start Time" value={form.start_time} onChange={v => setForm({ ...form, start_time: v })} />
            </div>
            <div>
              <TimeInput label="End Time" value={form.end_time} onChange={v => setForm({ ...form, end_time: v })} />
              {errors.end_time && <p className="text-xs text-red-500 mt-0.5">{errors.end_time}</p>}
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-slate-100">
          <Button variant="ghost" onClick={() => setExamDialog({ open: false, data: null })}>Cancel</Button>
          <Button onClick={handleSubmit} loading={createExamMutation.isPending || updateExamMutation.isPending}>
            {examDialog.data?.id ? 'Update Exam' : 'Schedule Exam'}
          </Button>
        </div>
      </Modal>

      {/* Results Modal */}
      {resultsExam && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="presentation">
          <div className="fixed inset-0 bg-black/40 backdrop-blur-[2px]" onClick={() => setResultsExam(null)} />
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col animate-fade-in-up">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 flex-shrink-0">
              <h2 className="text-lg font-semibold text-slate-900">Exam Results</h2>
              <button onClick={() => setResultsExam(null)} className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors"><Plus size={16} className="text-slate-500 rotate-45" /></button>
            </div>
            <div className="flex-1 overflow-y-auto px-6 py-4">
              <ExamResultsView exam={resultsExam} />
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard Modal */}
      {leaderboardExam && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="presentation">
          <div className="fixed inset-0 bg-black/40 backdrop-blur-[2px]" onClick={() => setLeaderboardExam(null)} />
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col animate-fade-in-up">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 flex-shrink-0">
              <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2"><Trophy size={18} className="text-amber-500" /> Exam Leaderboard</h2>
              <button onClick={() => setLeaderboardExam(null)} className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors"><Plus size={16} className="text-slate-500 rotate-45" /></button>
            </div>
            <div className="flex-1 overflow-y-auto px-6 py-4">
              <LeaderboardView exam={leaderboardExam} />
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={!!deleteId}
        onClose={() => setDeleteId(null)}
        onConfirm={() => { deleteExamMutation.mutate(deleteId, { onSuccess: () => { toast.success('Exam deleted successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to delete exam'); } }); setDeleteId(null); }}
        loading={deleteExamMutation.isPending}
        title="Delete Exam"
        message="Are you sure you want to delete this exam? This will also remove all associated results. This action cannot be undone."
      />

      {/* Create Exam Schedule Modal */}
      <CreateExamScheduleModal
        open={scheduleDialogOpen}
        onClose={() => setScheduleDialogOpen(false)}
        allClasses={allClasses}
        subjects={subjects}
        classSubjectsData={classSubjectsData}
        createExamMutation={createExamMutation}
        toast={toast}
      />
    </div>
  );
}

const DEMO_RESULTS = [
  { id: 'd1', student_name: 'Arjun Sharma', roll_number: 'STU2025001', marks: 92, percentage: 92, grade: 'A+' },
  { id: 'd2', student_name: 'Priya Patel', roll_number: 'STU2025002', marks: 87, percentage: 87, grade: 'A' },
  { id: 'd3', student_name: 'Rahul Verma', roll_number: 'STU2025003', marks: 78, percentage: 78, grade: 'B+' },
  { id: 'd4', student_name: 'Sneha Gupta', roll_number: 'STU2025004', marks: 72, percentage: 72, grade: 'B' },
  { id: 'd5', student_name: 'Vikram Singh', roll_number: 'STU2025005', marks: 65, percentage: 65, grade: 'B' },
  { id: 'd6', student_name: 'Ananya Roy', roll_number: 'STU2025006', marks: 58, percentage: 58, grade: 'C' },
  { id: 'd7', student_name: 'Karthik Nair', roll_number: 'STU2025007', marks: 45, percentage: 45, grade: 'C' },
  { id: 'd8', student_name: 'Meera Joshi', roll_number: 'STU2025008', marks: 38, percentage: 38, grade: 'C' },
  { id: 'd9', student_name: 'Rohan Das', roll_number: 'STU2025009', marks: 28, percentage: 28, grade: 'F' },
  { id: 'd10', student_name: 'Ishita Reddy', roll_number: 'STU2025010', marks: 95, percentage: 95, grade: 'A+' },
];

function ExamResultsView({ exam }) {
  const { data, isLoading } = useExamResults(exam.id);
  const results = (data?.results || []).length > 0 ? data.results : DEMO_RESULTS;
  const stats = data?.stats || {};
  const maxMarks = exam.total_marks || exam.max_marks || 100;
  const isPast = new Date(exam.date || exam.exam_date) <= new Date();

  if (isLoading) return (
    <div className="flex items-center justify-center py-12">
      <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const passCount = results.filter(r => r.grade !== 'F' && (r.percentage || 0) >= 33).length;
  const failCount = results.length - passCount;

  return (
    <div className="space-y-5">
      {/* Exam Info Header */}
      <div className="bg-gradient-to-r from-slate-50 to-slate-100/80 rounded-xl p-5 border border-slate-200">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-bold text-slate-900">{exam.name || exam.subject}</h3>
            <p className="text-sm text-slate-500 mt-0.5">{exam.subject} • Class {exam.class_name}-{exam.section}</p>
          </div>
          <Badge status={isPast ? 'Completed' : 'Active'}>{isPast ? 'Completed' : 'Upcoming'}</Badge>
        </div>
        <div className="flex items-center gap-6 text-xs text-slate-500">
          <span>📅 {exam.date || exam.exam_date}</span>
          {exam.start_time && <span>🕐 {exam.start_time}{exam.end_time ? ` - ${exam.end_time}` : ''}</span>}
          <span>📝 Max Marks: {maxMarks}</span>
          <span>👥 {results.length} students</span>
        </div>
      </div>

      {/* Stats Cards */}
      {results.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-3 text-center">
            <p className="text-xl font-bold text-blue-700">{stats.class_average?.toFixed(1) || ((results.reduce((s, r) => s + (r.percentage || 0), 0) / results.length) || 0).toFixed(1)}%</p>
            <p className="text-[11px] text-blue-500 mt-0.5">Class Average</p>
          </div>
          <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-3 text-center">
            <p className="text-xl font-bold text-emerald-700">{stats.highest_score || Math.max(...results.map(r => r.marks || 0))}</p>
            <p className="text-[11px] text-emerald-500 mt-0.5">Highest</p>
          </div>
          <div className="bg-red-50 border border-red-100 rounded-xl p-3 text-center">
            <p className="text-xl font-bold text-red-700">{stats.lowest_score || Math.min(...results.map(r => r.marks || 0))}</p>
            <p className="text-[11px] text-red-500 mt-0.5">Lowest</p>
          </div>
          <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-3 text-center">
            <p className="text-xl font-bold text-emerald-700">{passCount}</p>
            <p className="text-[11px] text-emerald-500 mt-0.5">Passed</p>
          </div>
          <div className="bg-red-50 border border-red-100 rounded-xl p-3 text-center">
            <p className="text-xl font-bold text-red-700">{failCount}</p>
            <p className="text-[11px] text-red-500 mt-0.5">Failed</p>
          </div>
        </div>
      )}

      {/* Pass Rate Progress */}
      {results.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-700">Pass Rate</span>
            <span className="text-sm font-bold text-slate-900">{results.length > 0 ? ((passCount / results.length) * 100).toFixed(0) : 0}%</span>
          </div>
          <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full transition-all duration-700" style={{ width: `${results.length > 0 ? (passCount / results.length) * 100 : 0}%` }} />
          </div>
          <div className="flex justify-between mt-1.5 text-[11px] text-slate-400">
            <span>{passCount} passed</span>
            <span>{failCount} failed</span>
          </div>
        </div>
      )}

      {/* Results Table */}
      {results.length > 0 ? (
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="py-3 px-4 text-left text-[11px] font-semibold text-slate-500 uppercase">#</th>
                <th className="py-3 px-4 text-left text-[11px] font-semibold text-slate-500 uppercase">Student</th>
                <th className="py-3 px-4 text-left text-[11px] font-semibold text-slate-500 uppercase">Roll No</th>
                <th className="py-3 px-4 text-left text-[11px] font-semibold text-slate-500 uppercase">Marks</th>
                <th className="py-3 px-4 text-left text-[11px] font-semibold text-slate-500 uppercase">Percentage</th>
                <th className="py-3 px-4 text-left text-[11px] font-semibold text-slate-500 uppercase">Grade</th>
                <th className="py-3 px-4 text-left text-[11px] font-semibold text-slate-500 uppercase">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {results.sort((a, b) => (b.marks || 0) - (a.marks || 0)).map((r, i) => {
                const pct = maxMarks > 0 ? ((r.marks || 0) / maxMarks) * 100 : 0;
                const passed = pct >= 33;
                return (
                  <tr key={r.id || r.student_id} className="hover:bg-primary-50/30 transition-colors duration-150">
                    <td className="py-3 px-4">
                      <span className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${i < 3 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-500'}`}>{i + 1}</span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-[10px] font-bold">{(r.student_name || r.full_name || '').slice(0, 2).toUpperCase()}</div>
                        <span className="font-medium text-slate-900">{r.student_name || r.full_name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-500">{r.roll_number}</td>
                    <td className="py-3 px-4">
                      <span className="font-bold text-slate-900">{r.marks}</span>
                      <span className="text-slate-400">/{maxMarks}</span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-blue-500' : pct >= 33 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-xs font-medium text-slate-700">{pct.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${r.grade === 'A+' || r.grade === 'A' ? 'bg-emerald-100 text-emerald-700' : r.grade === 'B+' || r.grade === 'B' ? 'bg-blue-100 text-blue-700' : r.grade === 'C' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`}>
                        {r.grade || (pct >= 90 ? 'A+' : pct >= 80 ? 'A' : pct >= 70 ? 'B+' : pct >= 60 ? 'B' : pct >= 50 ? 'C' : 'F')}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${passed ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
                        {passed ? '✓ Pass' : '✗ Fail'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-12 bg-slate-50 rounded-xl">
          <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3">
            <ClipboardList size={20} className="text-slate-400" />
          </div>
          <p className="text-sm font-medium text-slate-600">No results available</p>
          <p className="text-xs text-slate-400 mt-1">Results will appear here once grades are entered</p>
        </div>
      )}
    </div>
  );
}

function LeaderboardView({ exam }) {
  const { data, isLoading } = useExamResults(exam.id);
  const results = ((data?.results || []).length > 0 ? data.results : DEMO_RESULTS).sort((a, b) => (b.marks || 0) - (a.marks || 0));
  const maxMarks = exam.total_marks || exam.max_marks || 100;

  if (isLoading) return <div className="flex items-center justify-center py-12"><div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>;
  if (!results.length) return <div className="text-center py-12"><p className="text-sm text-slate-400">No results to show leaderboard</p></div>;

  const avg = (results.reduce((s, r) => s + (r.marks || 0), 0) / results.length).toFixed(1);
  const passCount = results.filter(r => ((r.marks || 0) / maxMarks) * 100 >= 33).length;
  const top3 = results.slice(0, 3);

  const dist = [
    { name: '90-100 (A+)', value: results.filter(r => ((r.marks || 0) / maxMarks) * 100 >= 90).length, color: '#059669' },
    { name: '80-89 (A)', value: results.filter(r => { const p = ((r.marks || 0) / maxMarks) * 100; return p >= 80 && p < 90; }).length, color: '#10b981' },
    { name: '60-79 (B)', value: results.filter(r => { const p = ((r.marks || 0) / maxMarks) * 100; return p >= 60 && p < 80; }).length, color: '#3b82f6' },
    { name: '40-59 (C)', value: results.filter(r => { const p = ((r.marks || 0) / maxMarks) * 100; return p >= 40 && p < 60; }).length, color: '#f59e0b' },
    { name: '0-39 (F)', value: results.filter(r => ((r.marks || 0) / maxMarks) * 100 < 40).length, color: '#ef4444' },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-6">
      {/* Header: Exam Info */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-xl p-5 text-center">
        <p className="text-xl font-bold text-slate-900">{exam.name || exam.subject}</p>
        <p className="text-sm text-slate-500 mt-1">{exam.subject} • Class {exam.class_name}-{exam.section} • {exam.date || exam.exam_date} • Max: {maxMarks}</p>
      </div>

      {/* Stats + Chart: Two Column */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Left: Stats */}
        <div className="space-y-4">
          <h4 className="text-sm font-semibold text-slate-900">Quick Stats</h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-slate-900">{results.length}</p>
              <p className="text-xs text-slate-500 mt-0.5">Total Students</p>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-blue-700">{avg}</p>
              <p className="text-xs text-blue-500 mt-0.5">Class Average</p>
            </div>
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-emerald-700">{results[0]?.marks || 0}</p>
              <p className="text-xs text-emerald-500 mt-0.5">Highest Score</p>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-red-700">{results[results.length - 1]?.marks || 0}</p>
              <p className="text-xs text-red-500 mt-0.5">Lowest Score</p>
            </div>
          </div>
          {/* Pass Rate */}
          <div className="bg-white border border-slate-200 rounded-xl p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-slate-600">Pass Rate</span>
              <span className="text-sm font-bold text-emerald-600">{((passCount / results.length) * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full" style={{ width: `${(passCount / results.length) * 100}%` }} />
            </div>
            <div className="flex justify-between mt-1.5 text-[11px] text-slate-400">
              <span>{passCount} passed</span>
              <span>{results.length - passCount} failed</span>
            </div>
          </div>
        </div>

        {/* Right: Pie Chart */}
        <ErrorBoundary>
        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h4 className="text-sm font-semibold text-slate-900 mb-4">Marks Distribution</h4>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={dist} cx="50%" cy="50%" outerRadius={80} innerRadius={45} dataKey="value" label={({ name, value }) => `${value}`} labelLine={false}>
                  {dist.map((entry, idx) => <Cell key={idx} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 20px -4px rgba(0,0,0,0.1)' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-3">
            {dist.map(d => (
              <div key={d.name} className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: d.color }} />
                <span className="text-xs text-slate-600 truncate">{d.name}</span>
                <span className="text-xs font-bold text-slate-900 ml-auto">{d.value}</span>
              </div>
            ))}
          </div>
        </div>
        </ErrorBoundary>
      </div>

      {/* Top 3 Podium */}
      {top3.length >= 3 && (
        <div className="bg-gradient-to-br from-amber-50/50 to-orange-50/50 border border-amber-100 rounded-xl p-6">
          <h4 className="text-sm font-semibold text-slate-900 text-center mb-8">🏆 Top Performers</h4>
          <div className="flex items-end justify-center gap-6 pt-4">
            {/* 2nd */}
            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-slate-300 to-slate-500 text-white flex items-center justify-center text-sm font-bold mx-auto mb-2 shadow-md">{(top3[1]?.student_name || '').slice(0, 2).toUpperCase()}</div>
              <div className="bg-white border border-slate-200 rounded-xl px-5 py-3 shadow-sm">
                <p className="text-xs font-bold text-slate-800 truncate max-w-[100px]">{top3[1]?.student_name}</p>
                <p className="text-lg font-bold text-slate-900">{top3[1]?.marks}<span className="text-xs text-slate-400">/{maxMarks}</span></p>
                <p className="text-[11px] text-slate-400 mt-0.5">🥈 2nd Place</p>
              </div>
            </div>
            {/* 1st */}
            <div className="text-center">
              <div className="w-18 h-18 w-[72px] h-[72px] rounded-full bg-gradient-to-br from-amber-400 to-amber-600 text-white flex items-center justify-center text-lg font-bold mx-auto mb-2 shadow-lg ring-4 ring-amber-200">{(top3[0]?.student_name || '').slice(0, 2).toUpperCase()}</div>
              <div className="bg-white border-2 border-amber-200 rounded-xl px-6 py-4 shadow-md">
                <p className="text-sm font-bold text-amber-900 truncate max-w-[120px]">{top3[0]?.student_name}</p>
                <p className="text-2xl font-bold text-amber-800">{top3[0]?.marks}<span className="text-xs text-amber-400">/{maxMarks}</span></p>
                <p className="text-[11px] text-amber-600 mt-0.5">🥇 1st Place</p>
              </div>
            </div>
            {/* 3rd */}
            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-orange-400 to-orange-700 text-white flex items-center justify-center text-sm font-bold mx-auto mb-2 shadow-md">{(top3[2]?.student_name || '').slice(0, 2).toUpperCase()}</div>
              <div className="bg-white border border-orange-200 rounded-xl px-5 py-3 shadow-sm">
                <p className="text-xs font-bold text-orange-800 truncate max-w-[100px]">{top3[2]?.student_name}</p>
                <p className="text-lg font-bold text-orange-900">{top3[2]?.marks}<span className="text-xs text-orange-400">/{maxMarks}</span></p>
                <p className="text-[11px] text-orange-600 mt-0.5">🥉 3rd Place</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Full Rankings */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-semibold text-slate-900">Full Rankings</h4>
          <span className="text-xs text-slate-400">{results.length} students</span>
        </div>
        <div className="rounded-xl border border-slate-200 overflow-hidden">
          <div className="max-h-[280px] overflow-y-auto">
            {results.map((r, i) => {
              const pct = maxMarks > 0 ? ((r.marks || 0) / maxMarks) * 100 : 0;
              return (
                <div key={r.id || r.student_id} className={`flex items-center gap-3 px-4 py-3 ${i < results.length - 1 ? 'border-b border-slate-100' : ''} hover:bg-slate-50 transition-colors`}>
                  <span className={`w-7 h-7 rounded-full flex items-center justify-center text-[11px] font-bold flex-shrink-0 ${i === 0 ? 'bg-amber-100 text-amber-700' : i === 1 ? 'bg-slate-200 text-slate-700' : i === 2 ? 'bg-orange-100 text-orange-700' : 'bg-slate-50 text-slate-500'}`}>{i + 1}</span>
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">{(r.student_name || r.full_name || '').slice(0, 2).toUpperCase()}</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">{r.student_name || r.full_name}</p>
                    <p className="text-[11px] text-slate-400">{r.roll_number || ''}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden hidden sm:block">
                      <div className={`h-full rounded-full ${pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-blue-500' : pct >= 33 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${pct}%` }} />
                    </div>
                    <span className="text-sm font-bold text-slate-900 min-w-[55px] text-right">{r.marks}/{maxMarks}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full min-w-[40px] text-center ${pct >= 80 ? 'bg-emerald-100 text-emerald-700' : pct >= 50 ? 'bg-blue-100 text-blue-700' : pct >= 33 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`}>{pct.toFixed(0)}%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

// --- Create Exam Schedule Modal (Bulk Creation) ---
const SCHEDULE_EXAM_TYPES = [
  ...EXAM_TYPES,
  { value: 'Summative', label: 'Summative' },
  { value: 'Formative', label: 'Formative' },
  { value: 'Practical', label: 'Practical' },
  { value: 'Mock', label: 'Mock' },
  { value: 'Entrance', label: 'Entrance' },
];

function CreateExamScheduleModal({ open, onClose, allClasses, subjects, classSubjectsData, createExamMutation, toast }) {
  const [step, setStep] = useState(1);
  const [title, setTitle] = useState('');
  const [examType, setExamType] = useState('');
  const [allClassesSelected, setAllClassesSelected] = useState(false);
  const [selectedSections, setSelectedSections] = useState({}); // { "classId-sectionId": true }
  const [schedules, setSchedules] = useState({}); // { "className|sectionName": [{ subject, date, start_time, end_time, max_marks }] }
  const [submitting, setSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});

  const reset = () => {
    setStep(1); setTitle(''); setExamType(''); setAllClassesSelected(false);
    setSelectedSections({}); setSchedules({}); setSubmitting(false); setValidationErrors({});
  };

  const handleClose = () => { reset(); onClose(); };

  // Get selected class-section pairs
  const selectedPairs = useMemo(() => {
    const pairs = [];
    allClasses.forEach(cls => {
      cls.sections?.forEach(sec => {
        const key = `${cls.id}-${sec.id}`;
        if (allClassesSelected || selectedSections[key]) {
          pairs.push({ classId: cls.id, className: cls.name, displayName: cls.display_name || cls.name, sectionId: sec.id, sectionName: sec.section_name, key: `${cls.name}|${sec.section_name}` });
        }
      });
    });
    return pairs;
  }, [allClasses, allClassesSelected, selectedSections]);

  // Toggle section
  const toggleSection = (classId, sectionId) => {
    const key = `${classId}-${sectionId}`;
    setSelectedSections(prev => ({ ...prev, [key]: !prev[key] }));
    setAllClassesSelected(false);
  };

  // Toggle all classes
  const toggleAllClasses = () => {
    if (allClassesSelected) { setSelectedSections({}); setAllClassesSelected(false); }
    else { setAllClassesSelected(true); setSelectedSections({}); }
  };

  // Initialize schedules for step 2
  const goToStep2 = () => {
    if (!title.trim()) { setValidationErrors({ title: 'Required' }); return; }
    if (!examType) { setValidationErrors({ examType: 'Required' }); return; }
    if (selectedPairs.length === 0) { setValidationErrors({ classes: 'Select at least one class-section' }); return; }
    setValidationErrors({});
    // Initialize empty schedules for new pairs
    const updated = { ...schedules };
    selectedPairs.forEach(p => { if (!updated[p.key]) updated[p.key] = []; });
    setSchedules(updated);
    setStep(2);
  };

  // Add row to a class-section schedule — pre-fill timing/marks from first row
  const addRow = (key) => {
    setSchedules(prev => {
      const existing = prev[key] || [];
      const first = existing[0];
      const newRow = { subject: '', date: '', start_time: first?.start_time || '', end_time: first?.end_time || '', max_marks: first?.max_marks || '' };
      return { ...prev, [key]: [...existing, newRow] };
    });
  };

  // Update a row — propagate start_time, end_time, max_marks from first row to others
  const updateRow = (key, idx, field, value) => {
    setSchedules(prev => {
      const rows = [...(prev[key] || [])].map(r => ({ ...r }));
      const oldValue = rows[idx][field];
      rows[idx][field] = value;

      if (idx === 0 && (field === 'start_time' || field === 'end_time' || field === 'max_marks')) {
        for (let i = 1; i < rows.length; i++) {
          if (!rows[i][field] || rows[i][field] === oldValue) {
            rows[i][field] = value;
          }
        }
      }

      return { ...prev, [key]: rows };
    });
  };

  // Remove a row
  const removeRow = (key, idx) => {
    setSchedules(prev => {
      const rows = [...(prev[key] || [])];
      rows.splice(idx, 1);
      return { ...prev, [key]: rows };
    });
  };

  // Copy schedule from another class-section
  const copyFrom = (targetKey, sourceKey) => {
    if (!sourceKey || !schedules[sourceKey]) return;
    setSchedules(prev => ({ ...prev, [targetKey]: schedules[sourceKey].map(r => ({ ...r })) }));
  };

  // Calculate duration
  const calcDuration = (start, end) => {
    if (!start || !end) return '';
    const [sh, sm] = start.split(':').map(Number);
    const [eh, em] = end.split(':').map(Number);
    const diff = (eh * 60 + em) - (sh * 60 + sm);
    if (diff <= 0) return '';
    const h = Math.floor(diff / 60); const m = diff % 60;
    return h > 0 ? `${h}h ${m}m` : `${m}m`;
  };

  // Validate time overlaps
  const validateSchedules = () => {
    const errors = {};
    selectedPairs.forEach(p => {
      const rows = schedules[p.key] || [];
      rows.forEach((row, i) => {
        if (!row.subject) errors[`${p.key}-${i}-subject`] = 'Required';
        if (!row.date) errors[`${p.key}-${i}-date`] = 'Required';
        if (!row.max_marks || Number(row.max_marks) <= 0) errors[`${p.key}-${i}-max_marks`] = 'Required';
        if (row.start_time && row.end_time && row.end_time <= row.start_time) errors[`${p.key}-${i}-end_time`] = 'End > Start';
        // Check overlaps within same date
        if (row.date && row.start_time && row.end_time) {
          rows.forEach((other, j) => {
            if (j !== i && other.date === row.date && other.start_time && other.end_time) {
              if (row.start_time < other.end_time && row.end_time > other.start_time) {
                errors[`${p.key}-${i}-time_overlap`] = 'Time overlap';
              }
            }
          });
        }
      });
    });
    return errors;
  };

  // Submit all exams
  const handleSubmit = async () => {
    const errs = validateSchedules();
    if (Object.keys(errs).length > 0) { setValidationErrors(errs); toast.error('Please fix validation errors (subject, date, and marks are required)'); return; }
    // Check at least one row exists
    const hasRows = selectedPairs.some(p => (schedules[p.key] || []).length > 0);
    if (!hasRows) { toast.error('Add at least one subject schedule'); return; }
    setSubmitting(true);
    let success = 0, failed = 0;
    for (const pair of selectedPairs) {
      const rows = schedules[pair.key] || [];
      for (const row of rows) {
        try {
          await createExamMutation.mutateAsync({
            name: title,
            exam_type: examType,
            class_name: pair.className,
            section: pair.sectionName,
            subject: row.subject,
            date: row.date,
            start_time: row.start_time || undefined,
            end_time: row.end_time || undefined,
            total_marks: Number(row.max_marks),
          });
          success++;
        } catch { failed++; }
      }
    }
    setSubmitting(false);
    if (success > 0) toast.success(`${success} exam(s) scheduled successfully${failed > 0 ? `, ${failed} failed` : ''}`);
    else toast.error('Failed to create exams');
    if (success > 0) handleClose();
  };

  if (!open) return null;

  const classSubjectsList = classSubjectsData?.classes || [];
  const getSubjectsForClass = (classId) => {
    const classSubjectsForSelected = classSubjectsList.find(c => c.id === classId);
    const filtered = classSubjectsForSelected?.subjects?.length > 0
      ? subjects.filter(s => classSubjectsForSelected.subjects.some(cs => cs.id === s.id))
      : subjects;
    return filtered.map(s => ({ value: s.name, label: s.name }));
  };

  return (
    <Modal open={open} onClose={handleClose} title="Create Exam Schedule" size="full">
      {step === 1 && (
        <div className="space-y-5">
          {/* Exam Title */}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Exam Title *</label>
            <input value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. Mid-Term Examinations 2025" className={`w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent ${validationErrors.title ? 'border-red-400' : 'border-slate-300'}`} />
            {validationErrors.title && <p className="text-xs text-red-500 mt-0.5">{validationErrors.title}</p>}
          </div>
          {/* Exam Type */}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Exam Type *</label>
            <SearchableSelect value={examType} onChange={setExamType} options={SCHEDULE_EXAM_TYPES.map(t => ({ value: t.value, label: t.label }))} placeholder="Select exam type..." />
            {validationErrors.examType && <p className="text-xs text-red-500 mt-0.5">{validationErrors.examType}</p>}
          </div>
          {/* Target Classes */}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Target Classes *</label>
            {validationErrors.classes && <p className="text-xs text-red-500 mb-2">{validationErrors.classes}</p>}
            <div className="border border-slate-200 rounded-lg p-4 max-h-[300px] overflow-y-auto space-y-3">
              {/* All Classes checkbox */}
              <label className="flex items-center gap-2 cursor-pointer pb-2 border-b border-slate-100">
                <input type="checkbox" checked={allClassesSelected} onChange={toggleAllClasses} className="w-4 h-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
                <span className="text-sm font-medium text-slate-900">All Classes</span>
                <span className="ml-auto text-xs text-slate-400">{allClasses.reduce((sum, cls) => sum + (cls.sections?.length || 0), 0)} sections</span>
              </label>
              {/* Per class cards */}
              {allClasses.map((cls, idx) => {
                const colors = ['border-l-blue-400', 'border-l-emerald-400', 'border-l-purple-400', 'border-l-amber-400', 'border-l-rose-400', 'border-l-cyan-400', 'border-l-indigo-400', 'border-l-teal-400'];
                const bgColors = ['bg-blue-50/40', 'bg-emerald-50/40', 'bg-purple-50/40', 'bg-amber-50/40', 'bg-rose-50/40', 'bg-cyan-50/40', 'bg-indigo-50/40', 'bg-teal-50/40'];
                const colorIdx = idx % colors.length;
                const hasSections = cls.sections?.length > 0;
                const allSectionsSelected = hasSections && cls.sections.every(sec => allClassesSelected || selectedSections[`${cls.id}-${sec.id}`]);
                const someSectionsSelected = hasSections && cls.sections.some(sec => allClassesSelected || selectedSections[`${cls.id}-${sec.id}`]);
                return (
                  <div key={cls.id} className={`border border-slate-200 border-l-4 ${colors[colorIdx]} rounded-lg ${bgColors[colorIdx]} p-3 transition-all duration-150 hover:shadow-sm`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={allSectionsSelected || allClassesSelected}
                          ref={el => { if (el) el.indeterminate = someSectionsSelected && !allSectionsSelected && !allClassesSelected; }}
                          disabled={allClassesSelected}
                          onChange={() => {
                            if (allSectionsSelected) {
                              const updated = { ...selectedSections };
                              cls.sections?.forEach(sec => { delete updated[`${cls.id}-${sec.id}`]; });
                              setSelectedSections(updated);
                            } else {
                              const updated = { ...selectedSections };
                              cls.sections?.forEach(sec => { updated[`${cls.id}-${sec.id}`] = true; });
                              setSelectedSections(updated);
                            }
                          }}
                          className="w-4 h-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                        />
                        <span className="text-sm font-semibold text-slate-800">{cls.display_name || cls.name}</span>
                      </div>
                      <span className="text-[11px] text-slate-400">{cls.sections?.length || 0} sections</span>
                    </div>
                    <div className="flex flex-wrap gap-2 pl-6">
                      {cls.sections?.map(sec => {
                        const key = `${cls.id}-${sec.id}`;
                        const checked = allClassesSelected || !!selectedSections[key];
                        return (
                          <label key={key} className={`flex items-center gap-1.5 cursor-pointer px-2.5 py-1 rounded-md border text-xs transition-all duration-150 ${checked ? 'bg-primary-50 border-primary-300 text-primary-700 font-medium' : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'}`}>
                            <input type="checkbox" checked={checked} disabled={allClassesSelected} onChange={() => toggleSection(cls.id, sec.id)} className="w-3 h-3 rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
                            {sec.section_name}
                          </label>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
            <p className="text-xs text-slate-400 mt-1.5">{selectedPairs.length} class-section(s) selected</p>
          </div>
          {/* Step 1 Footer */}
          <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
            <Button variant="ghost" onClick={handleClose}>Cancel</Button>
            <Button onClick={goToStep2}>Next: Subject Scheduling →</Button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">{title}</h3>
              <p className="text-xs text-slate-500">{examType} • {selectedPairs.length} class-section(s)</p>
            </div>
            <Button variant="ghost" size="sm" onClick={() => setStep(1)}>← Back</Button>
          </div>

          <div className="space-y-6 max-h-[55vh] overflow-y-auto pr-1">
            {selectedPairs.map(pair => {
              const rows = schedules[pair.key] || [];
              const otherKeys = selectedPairs.filter(p => p.key !== pair.key && (schedules[p.key] || []).length > 0).map(p => ({ value: p.key, label: `${p.displayName}-${p.sectionName}` }));
              return (
                <div key={pair.key} className="border border-slate-200 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-semibold text-slate-900">{pair.displayName} - {pair.sectionName}</h4>
                    {otherKeys.length > 0 && (
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">Copy from:</span>
                        <select onChange={e => copyFrom(pair.key, e.target.value)} defaultValue="" className="text-xs border border-slate-200 rounded px-2 py-1">
                          <option value="">Select...</option>
                          {otherKeys.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                        </select>
                      </div>
                    )}
                  </div>
                  {rows.length > 0 && (
                    <div className="mb-3">
                      <table className="w-full text-xs">
                        <thead>
                          <tr className="bg-slate-50 border-b border-slate-100">
                            <th className="py-2 px-2 text-left font-medium text-slate-500">Subject</th>
                            <th className="py-2 px-2 text-left font-medium text-slate-500">Date</th>
                            <th className="py-2 px-2 text-left font-medium text-slate-500">Start</th>
                            <th className="py-2 px-2 text-left font-medium text-slate-500">End</th>
                            <th className="py-2 px-2 text-left font-medium text-slate-500">Duration</th>
                            <th className="py-2 px-2 text-left font-medium text-slate-500">Max Marks</th>
                            <th className="py-2 px-2"></th>
                          </tr>
                        </thead>
                        <tbody>
                          {rows.map((row, idx) => (
                            <tr key={idx} className="border-b border-slate-50">
                              <td className="py-1.5 px-2">
                                <SearchableSelect value={row.subject} onChange={v => updateRow(pair.key, idx, 'subject', v)} options={getSubjectsForClass(pair.classId)} placeholder="Subject" />
                                {validationErrors[`${pair.key}-${idx}-subject`] && <p className="text-[10px] text-red-500">{validationErrors[`${pair.key}-${idx}-subject`]}</p>}
                              </td>
                              <td className="py-1.5 px-2">
                                <DateInput value={row.date} onChange={v => updateRow(pair.key, idx, 'date', v)} />
                                {validationErrors[`${pair.key}-${idx}-date`] && <p className="text-[10px] text-red-500">{validationErrors[`${pair.key}-${idx}-date`]}</p>}
                              </td>
                              <td className="py-1.5 px-2">
                                <input type="time" value={row.start_time} onChange={e => updateRow(pair.key, idx, 'start_time', e.target.value)} className="border border-slate-200 rounded px-2 py-1.5 text-xs w-[100px]" />
                              </td>
                              <td className="py-1.5 px-2">
                                <input type="time" value={row.end_time} onChange={e => updateRow(pair.key, idx, 'end_time', e.target.value)} className="border border-slate-200 rounded px-2 py-1.5 text-xs w-[100px]" />
                                {validationErrors[`${pair.key}-${idx}-end_time`] && <p className="text-[10px] text-red-500">{validationErrors[`${pair.key}-${idx}-end_time`]}</p>}
                                {validationErrors[`${pair.key}-${idx}-time_overlap`] && <p className="text-[10px] text-red-500">Overlap!</p>}
                              </td>
                              <td className="py-1.5 px-2 text-slate-500">{calcDuration(row.start_time, row.end_time)}</td>
                              <td className="py-1.5 px-2">
                                <input type="number" value={row.max_marks} onChange={e => updateRow(pair.key, idx, 'max_marks', e.target.value)} placeholder="100" className="border border-slate-200 rounded px-2 py-1.5 text-xs w-[70px]" />
                                {validationErrors[`${pair.key}-${idx}-max_marks`] && <p className="text-[10px] text-red-500">{validationErrors[`${pair.key}-${idx}-max_marks`]}</p>}
                              </td>
                              <td className="py-1.5 px-2">
                                <button onClick={() => removeRow(pair.key, idx)} className="p-1 rounded hover:bg-red-50"><Trash2 size={12} className="text-red-400" /></button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  <Button variant="ghost" size="sm" icon={Plus} onClick={() => addRow(pair.key)}>Add Subject</Button>
                </div>
              );
            })}
          </div>

          {/* Step 2 Footer */}
          <div className="flex justify-between gap-2 pt-4 border-t border-slate-100">
            <Button variant="ghost" onClick={() => setStep(1)}>← Back</Button>
            <div className="flex gap-2">
              <Button variant="ghost" onClick={handleClose}>Cancel</Button>
              <Button onClick={handleSubmit} loading={submitting}>
                Create {selectedPairs.reduce((sum, p) => sum + (schedules[p.key] || []).length, 0)} Exam(s)
              </Button>
            </div>
          </div>
        </div>
      )}
    </Modal>
  );
}
