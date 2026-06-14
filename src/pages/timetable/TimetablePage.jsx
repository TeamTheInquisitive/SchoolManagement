import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Settings, Plus, Pencil, Trash2, Clock, EyeOff, X, Download, Layers } from 'lucide-react';
import { usePeriods, useTimetable, useAssignSlot, useDeleteSlot, useSubjects, useTeachers, useTeacherAvailability, useCreatePeriod, useUpdatePeriod, useDeletePeriod, useSlotTypes } from '../../services/timetableService';
import { useClassSectionFilter } from '../../hooks/useClassSectionFilter';
import { useClassSubjects, useClassSectionAssignments } from '../../services/settingsService';
import { Button, Modal, ConfirmDialog, SearchableSelect, Checkbox, FilterBar, TimeInput, useToast, generatePdf, Breadcrumb, TimetableGrid } from 'school-erp-ui-shared';

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

export default function TimetablePage() {
  const toast = useToast();
  const navigate = useNavigate();
  const { className: urlClass, sectionName: urlSection } = useParams();
  const { selectedClass: classFilter, selectedSection: sectionFilter, setSelectedClass: setClassFilter, setSelectedSection: setSectionFilter, classOptions, sectionOptions, classes: allClasses } = useClassSectionFilter();
  const [showPeriodConfig, setShowPeriodConfig] = useState(false);
  const [showSubjectPool, setShowSubjectPool] = useState(false);
  const [slotDialog, setSlotDialog] = useState(null);
  const [periodDialog, setPeriodDialog] = useState(false);
  const [editPeriodData, setEditPeriodData] = useState(null);
  const [deleteSlotData, setDeleteSlotData] = useState(null);
  const [tileView, setTileView] = useState(!urlClass && !classFilter);

  useEffect(() => {
    if (urlClass && urlSection) {
      setClassFilter(urlClass);
      setSectionFilter(urlSection);
      setTileView(false);
    } else {
      setClassFilter('');
      setSectionFilter('');
      setTileView(true);
    }
  }, [urlClass, urlSection]);

  const classSections = allClasses.flatMap(cls => cls.sections.map(sec => ({ id: sec.id, class_name: cls.name, section: sec.section_name })));
  const { data: periodsData } = usePeriods();
  const { data: subjectsData } = useSubjects();
  const { data: teachersData } = useTeachers();
  const { data: classSubjectsData } = useClassSubjects();
  const { data: sectionAssignmentsData } = useClassSectionAssignments();

  const selectedCS = classSections.find(cs => cs.class_name === classFilter && cs.section === sectionFilter);
  const { data: timetableData, isLoading } = useTimetable({ class_section_id: selectedCS?.id });

  const allPeriods = periodsData?.periods || periodsData?.results || (Array.isArray(periodsData) ? periodsData : []);
  const breaks = periodsData?.breaks || [];
  const periods = [...allPeriods, ...breaks].sort((a, b) => (a.start_time || '').localeCompare(b.start_time || ''));
  const teachingPeriods = periods.filter(p => !p.is_break);

  const slots = timetableData?.timetable || {};
  const subjects = Array.isArray(subjectsData?.results) ? subjectsData.results : Array.isArray(subjectsData) ? subjectsData : [];
  const teachers = Array.isArray(teachersData?.results) ? teachersData.results : Array.isArray(teachersData) ? teachersData : [];

  const classSubjectsList = classSubjectsData?.classes || [];
  const selectedClassObj = allClasses.find(c => c.name === classFilter);
  const classSubjectsForSelected = classSubjectsList.find(c => c.id === selectedClassObj?.id);
  const classFilteredSubjects = classSubjectsForSelected?.subjects?.length > 0
    ? subjects.filter(s => classSubjectsForSelected.subjects.some(cs => cs.id === s.id))
    : subjects;

  const assignSlot = useAssignSlot();
  const deleteSlot = useDeleteSlot();
  const createPeriod = useCreatePeriod();
  const updatePeriod = useUpdatePeriod();
  const deletePeriod = useDeletePeriod();

  const formatTime = (t) => {
    if (!t) return '';
    const [h, m] = t.split(':');
    const hr = parseInt(h);
    return `${hr > 12 ? hr - 12 : hr}:${m} ${hr >= 12 ? 'PM' : 'AM'}`;
  };

  // Get slot from grid data (API returns { Monday: [{...}, null, ...], Tuesday: [...] })
  const getSlot = (periodIndex, day) => {
    const daySlots = slots[day];
    if (!daySlots) return null;
    return daySlots[periodIndex] || null;
  };

  const openClassTimetable = (cls, sec) => {
    navigate(`/admin/timetable/${cls}/${sec}`);
  };

  if (tileView && !classFilter) {
    return (
      <div>
        <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Timetable' }]} />
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Timetable</h1>
            <p className="text-sm text-slate-500 mt-1">Select a class to view or edit its timetable</p>
          </div>
          <Button variant="secondary" size="sm" icon={Settings} onClick={() => { setTileView(false); setShowPeriodConfig(true); }}>Configure Periods</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {allClasses.flatMap((cls) =>
            cls.sections.map((sec) => (
              <TimetableTile key={sec.id} classId={sec.id} className={cls.name} sectionName={sec.section_name} onClick={() => openClassTimetable(cls.name, sec.section_name)} />
            ))
          )}
        </div>
      </div>
    );
  }

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Timetable', href: '/admin/timetable', onClick: (e) => { e.preventDefault(); setClassFilter(''); setSectionFilter(''); setTileView(true); navigate('/admin/timetable'); } }, ...(classFilter ? [{ label: `Class ${classFilter}${sectionFilter ? ` - ${sectionFilter}` : ''}` }] : [])]} />
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Timetable Builder</h1>
          <p className="text-sm text-slate-500 mt-1">Create and manage class schedules</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" icon={Layers} onClick={() => setShowSubjectPool(!showSubjectPool)}>
            {showSubjectPool ? 'Hide Subject Pool' : 'Show Subject Pool'}
          </Button>
          <Button variant="secondary" size="sm" icon={showPeriodConfig ? EyeOff : Settings} onClick={() => setShowPeriodConfig(!showPeriodConfig)}>
            {showPeriodConfig ? 'Hide Period Settings' : 'Configure Periods'}
          </Button>
        </div>
      </div>

      {/* Filters */}
      <FilterBar>
        <FilterBar.Item>
          <SearchableSelect value={classFilter} onChange={(v) => { setClassFilter(v); setTileView(false); if (v && sectionFilter) navigate(`/admin/timetable/${v}/${sectionFilter}`, { replace: true }); }} options={classOptions} placeholder="Class" />
        </FilterBar.Item>
        <FilterBar.Item>
          <SearchableSelect value={sectionFilter} onChange={(v) => { setSectionFilter(v); setTileView(false); if (classFilter && v) navigate(`/admin/timetable/${classFilter}/${v}`, { replace: true }); }} options={sectionOptions} placeholder="Section" />
        </FilterBar.Item>
      </FilterBar>

      {/* Period Configuration Panel */}
      {showPeriodConfig && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 mb-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-slate-600" />
              <h3 className="text-base font-semibold text-slate-800">Period Configuration</h3>
              <span className="text-xs text-slate-400 ml-2">Periods are shared across all classes and sections</span>
            </div>
            <Button variant="primary" size="sm" icon={Plus} onClick={() => setPeriodDialog(true)}>Add Period</Button>
          </div>
          <div className="space-y-0">
            {periods.map((p, i) => (
              <div key={p.id} className={`flex justify-between items-center py-3 transition-colors duration-150 hover:bg-slate-50 rounded-lg px-2 -mx-2 ${i < periods.length - 1 ? 'border-b border-slate-100' : ''}`}>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-semibold text-slate-800 min-w-[80px]">{p.name || `Period ${i + 1}`}</span>
                  <span className="text-sm text-slate-700">{formatTime(p.start_time)} - {formatTime(p.end_time)}</span>
                  <span className="text-xs text-slate-400">({p.duration_minutes || '--'} mins)</span>
                  {p.is_break && <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded">Break</span>}
                </div>
                <div className="flex gap-1">
                  <button className="p-1.5 hover:bg-slate-100 rounded" onClick={() => setEditPeriodData(p)}><Pencil className="w-4 h-4 text-slate-400" /></button>
                  <button className="p-1.5 hover:bg-red-50 rounded" onClick={() => deletePeriod.mutate(p.id)}><Trash2 className="w-4 h-4 text-red-500" /></button>
                </div>
              </div>
            ))}
            {periods.length === 0 && <div className="text-center py-8 text-slate-400">No periods configured yet. Add periods to build the timetable.</div>}
          </div>
        </div>
      )}

      {/* Subject Pool Panel */}
      {showSubjectPool && (
        <div className="bg-white border border-slate-200 rounded-xl p-4 mb-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <h3 className="text-sm font-semibold text-slate-900 mb-3">Subject Pool — Drag to assign</h3>
          <div className="flex flex-wrap gap-2">
            {subjects.map(s => (
              <div
                key={s.id}
                draggable
                onDragStart={(e) => e.dataTransfer.setData('application/json', JSON.stringify({ subject_id: s.id, subject_name: s.name }))}
                className="px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg text-sm font-medium text-blue-700 cursor-grab active:cursor-grabbing hover:bg-blue-100 transition-colors"
              >
                {s.name}
              </div>
            ))}
            {subjects.length === 0 && <p className="text-sm text-slate-400">No subjects available. Add subjects in the Subjects module first.</p>}
          </div>
        </div>
      )}

      {/* Timetable Grid */}
      {!classFilter || !sectionFilter ? (
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-slate-400">Select a class and section to view the timetable</div>
      ) : isLoading ? (
        <div className="flex items-center justify-center py-12"><div className="animate-pulse text-slate-400">Loading timetable...</div></div>
      ) : (
        <TimetableGrid
          periods={periods}
          timetable={slots}
          editable
          onSlotClick={(periodIndex, day, slot) => {
            const period = teachingPeriods[periodIndex];
            setSlotDialog({ periodId: period?.id, day, existing: slot, classSectionId: selectedCS?.id });
          }}
          onSlotDelete={(periodIndex, day, slot) => {
            const period = teachingPeriods[periodIndex];
            setDeleteSlotData({ slotId: slot.id, subject: slot.subject, day, period: period?.name || `Period ${periodIndex + 1}` });
          }}
          onEmptyClick={(periodIndex, day) => {
            const period = teachingPeriods[periodIndex];
            setSlotDialog({ periodId: period?.id, day, classSectionId: selectedCS?.id });
          }}
          onDrop={(periodIndex, day, data) => {
            const period = teachingPeriods[periodIndex];
            setSlotDialog({ periodId: period?.id, day, classSectionId: selectedCS?.id, prefillSubject: data.subject_id });
          }}
        />
      )}

      {/* Timetable Stats */}
      {classFilter && sectionFilter && teachingPeriods.length > 0 && !isLoading && (() => {
        const totalSlots = DAYS.length * teachingPeriods.length;
        const filledSlots = DAYS.reduce((count, day) => count + (slots[day] || []).filter(Boolean).length, 0);
        const fillPct = totalSlots > 0 ? Math.round((filledSlots / totalSlots) * 100) : 0;

        // Subject distribution
        const subjectCounts = {};
        const teacherCounts = {};
        const emptyByDay = {};
        const consecutiveWarnings = [];

        DAYS.forEach(day => {
          const daySlots = slots[day] || [];
          let emptyCount = 0;
          let prevSubject = null;
          let consecutiveCount = 1;

          teachingPeriods.forEach((_, idx) => {
            const slot = daySlots[idx];
            if (slot) {
              subjectCounts[slot.subject] = (subjectCounts[slot.subject] || 0) + 1;
              if (slot.teacher_name) teacherCounts[slot.teacher_name] = (teacherCounts[slot.teacher_name] || 0) + 1;
              if (slot.subject === prevSubject) {
                consecutiveCount++;
                if (consecutiveCount >= 2) {
                  const existing = consecutiveWarnings.find(w => w.day === day && w.subject === slot.subject);
                  if (!existing) consecutiveWarnings.push({ day, subject: slot.subject, count: consecutiveCount });
                  else existing.count = consecutiveCount;
                }
              } else {
                consecutiveCount = 1;
              }
              prevSubject = slot.subject;
            } else {
              emptyCount++;
              prevSubject = null;
              consecutiveCount = 1;
            }
          });
          if (emptyCount > 0) emptyByDay[day] = emptyCount;
        });

        const sortedSubjects = Object.entries(subjectCounts).sort((a, b) => b[1] - a[1]);
        const sortedTeachers = Object.entries(teacherCounts).sort((a, b) => b[1] - a[1]);
        const mostFrequent = sortedSubjects[0];

        // Current time indicator
        const now = new Date();
        const currentTimeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
        const todayName = now.toLocaleDateString('en-US', { weekday: 'long' });
        const currentPeriodIdx = teachingPeriods.findIndex(p => p.start_time <= currentTimeStr && p.end_time > currentTimeStr);

        return (
          <div className="mt-4 space-y-3">
            {/* Completion bar */}
            <div className="bg-white border border-slate-200 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-800">Timetable Completion</span>
                <span className="text-sm font-bold text-primary-600">{filledSlots}/{totalSlots} slots ({fillPct}%)</span>
              </div>
              <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden">
                <div className={`h-full rounded-full transition-all duration-700 ${fillPct === 100 ? 'bg-emerald-500' : fillPct >= 75 ? 'bg-primary-500' : fillPct >= 50 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${fillPct}%` }} />
              </div>
              {currentPeriodIdx >= 0 && DAYS.includes(todayName) && (
                <p className="text-xs text-red-500 mt-2 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                  Now: {teachingPeriods[currentPeriodIdx]?.name || `Period ${currentPeriodIdx + 1}`} ({todayName})
                </p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {/* Subject Distribution */}
              <div className="bg-white border border-slate-200 rounded-xl p-4">
                <p className="text-xs font-semibold text-slate-600 mb-2">Subject Distribution</p>
                {sortedSubjects.length > 0 ? (
                  <div className="space-y-1.5">
                    {sortedSubjects.map(([subj, count]) => (
                      <div key={subj} className="flex items-center gap-2">
                        <span className="text-xs text-slate-700 w-24 truncate">{subj}</span>
                        <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-primary-400 rounded-full" style={{ width: `${(count / (mostFrequent?.[1] || 1)) * 100}%` }} />
                        </div>
                        <span className="text-xs font-semibold text-slate-600 w-8 text-right">{count}</span>
                      </div>
                    ))}
                  </div>
                ) : <p className="text-xs text-slate-400">No slots assigned yet</p>}
              </div>

              {/* Teacher Load */}
              <div className="bg-white border border-slate-200 rounded-xl p-4">
                <p className="text-xs font-semibold text-slate-600 mb-2">Teacher Load (this section)</p>
                {sortedTeachers.length > 0 ? (
                  <div className="space-y-1.5">
                    {sortedTeachers.map(([name, count]) => (
                      <div key={name} className="flex items-center gap-2">
                        <span className="text-xs text-slate-700 w-24 truncate">{name}</span>
                        <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-indigo-400 rounded-full" style={{ width: `${(count / (sortedTeachers[0]?.[1] || 1)) * 100}%` }} />
                        </div>
                        <span className="text-xs font-semibold text-slate-600 w-8 text-right">{count}</span>
                      </div>
                    ))}
                  </div>
                ) : <p className="text-xs text-slate-400">No teachers assigned yet</p>}
              </div>
            </div>

            {/* Warnings & Info */}
            <div className="flex flex-wrap gap-3">
              {/* Empty slots by day */}
              {Object.keys(emptyByDay).length > 0 && (
                <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
                  <span className="text-xs text-amber-700">Empty slots:</span>
                  {Object.entries(emptyByDay).map(([day, count]) => (
                    <span key={day} className="text-[10px] font-medium bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded">{day.slice(0, 3)}: {count}</span>
                  ))}
                </div>
              )}

              {/* Consecutive same subject warnings */}
              {consecutiveWarnings.length > 0 && (
                <div className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  <span className="text-xs text-red-700">⚠ Consecutive:</span>
                  {consecutiveWarnings.map((w, i) => (
                    <span key={i} className="text-[10px] font-medium bg-red-100 text-red-800 px-1.5 py-0.5 rounded">{w.subject} × {w.count} on {w.day.slice(0, 3)}</span>
                  ))}
                </div>
              )}

              {/* Most frequent */}
              {mostFrequent && (
                <div className="flex items-center gap-1.5 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
                  <span className="text-xs text-blue-700">Most periods: <strong>{mostFrequent[0]}</strong> ({mostFrequent[1]})</span>
                </div>
              )}
            </div>
          </div>
        );
      })()}

      {/* Download PDF */}
      {classFilter && sectionFilter && teachingPeriods.length > 0 && (
        <div className="flex justify-end mt-4">
          <Button variant="primary" size="lg" icon={Download} onClick={() => { const headers = ['Period', 'Time', ...DAYS]; const rows = teachingPeriods.map((p, idx) => { const row = [p.name || `Period ${idx + 1}`, `${p.start_time} - ${p.end_time}`]; DAYS.forEach(day => { const slot = getSlot(idx, day); row.push(slot ? `${slot.subject || ''} (${slot.teacher_name || ''})` : ''); }); return row; }); generatePdf({ title: `Timetable - Class ${classFilter}-${sectionFilter}`, subtitle: `Generated from School ERP`, headers, rows, filename: `timetable-${classFilter}-${sectionFilter}`, orientation: 'landscape' }); toast.success('Timetable PDF downloaded'); }}>Download PDF</Button>
        </div>
      )}

      {/* Slot Assignment Modal */}
      {slotDialog && (
        <SlotFormDialog
          open={!!slotDialog}
          onClose={() => setSlotDialog(null)}
          slot={slotDialog}
          subjects={classFilteredSubjects}
          teachers={teachers}
          classSection={`Class ${classFilter}-${sectionFilter}`}
          periods={teachingPeriods}
          sectionAssignments={sectionAssignmentsData}
          onSave={(data) => {
            assignSlot.mutate({ ...data, class_section_id: slotDialog.classSectionId }, {
              onSuccess: () => toast.success('Slot assigned successfully'),
              onError: (err) => toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to assign slot'),
            });
            setSlotDialog(null);
          }}
        />
      )}

      {/* Add Period Modal */}
      <PeriodFormDialog
        open={periodDialog}
        onClose={() => setPeriodDialog(false)}
        onCreate={createPeriod}
        existingPeriods={periods}
      />

      {/* Edit Period Modal */}
      {editPeriodData && (
        <EditPeriodDialog
          open={!!editPeriodData}
          onClose={() => setEditPeriodData(null)}
          period={editPeriodData}
          onUpdate={updatePeriod}
          existingPeriods={periods}
        />
      )}

      {/* Delete Slot Confirmation */}
      <ConfirmDialog
        open={!!deleteSlotData}
        onClose={() => setDeleteSlotData(null)}
        onConfirm={() => {
          if (deleteSlotData?.slotId) {
            deleteSlot.mutate(deleteSlotData.slotId);
          }
          setDeleteSlotData(null);
        }}
        loading={deleteSlot.isPending}
        title="Remove Timetable Slot"
        message={deleteSlotData ? `Are you sure you want to remove "${deleteSlotData.subject}" from ${deleteSlotData.day} (${deleteSlotData.period})? This action cannot be undone.` : ''}
        confirmText="Remove"
      />
    </div>
  );
}

function SlotFormDialog({ open, onClose, slot, subjects, teachers, classSection, periods, onSave, sectionAssignments }) {
  const [slotType, setSlotType] = useState(slot.existing?.slot_type || 'Subject');
  const [customLabel, setCustomLabel] = useState(slot.existing?.slot_type === 'Other' ? '' : '');
  const [subject, setSubject] = useState(slot.existing?.subject_id || slot.existing?.subject || slot.prefillSubject || '');
  const [teacher, setTeacher] = useState(slot.existing?.teacher_id || '');

  // Auto-select teacher from section assignments when subject changes
  const getAssignedTeacher = (subjectId) => {
    if (!sectionAssignments?.classes || !slot.classSectionId) return null;
    for (const cls of sectionAssignments.classes) {
      for (const sec of cls.sections) {
        if (sec.id === slot.classSectionId) {
          const match = (sec.subject_teachers || []).find(st => st.subject_id === subjectId);
          return match?.staff_id || null;
        }
      }
    }
    return null;
  };
  const period = periods.find(p => p.id === slot.periodId);

  const { data: slotTypesData } = useSlotTypes();
  const { data: availabilityData } = useTeacherAvailability(slot.periodId, slot.day);
  const busyTeachers = availabilityData?.busy_teachers || {};

  const slotTypeOptions = (slotTypesData?.values || []).map(v => ({ value: v.value || v.code || v, label: v.label || v.value || v }));
  const defaultSlotTypes = [
    { value: 'Subject', label: 'Subject' },
    { value: 'Sports', label: 'Sports' },
    { value: 'Special Class', label: 'Special Class' },
    { value: 'Library', label: 'Library' },
    { value: 'Other', label: 'Other' },
  ];
  const typeOptions = slotTypeOptions.length > 0 ? slotTypeOptions : defaultSlotTypes;

  const isSubjectType = slotType === 'Subject';

  const matchedSubject = subjects.find(s => s.id === subject || s.name === subject);
  const subjectValue = matchedSubject?.id || subject;
  const selectedSubjectName = matchedSubject?.name || '';

  const teachingStaff = teachers.filter(t => t.department === 'Teaching' && t.status === 'Active');

  const subjectMatchedTeachers = (isSubjectType && selectedSubjectName)
    ? teachingStaff.filter(t => {
        const teacherSubjects = (t.subjects || []).map(s => s.toLowerCase().trim());
        const primary = (t.primary_subject || '').toLowerCase().trim();
        const subName = selectedSubjectName.toLowerCase().trim();
        return primary === subName || teacherSubjects.includes(subName);
      })
    : [];

  const teacherPool = isSubjectType && subjectMatchedTeachers.length > 0 ? subjectMatchedTeachers : teachingStaff;

  const teacherOptions = teacherPool.map(t => {
    const id = t.id;
    const name = t.user?.full_name || t.full_name;
    const subj = t.primary_subject || t.subject || '';
    const busy = isSubjectType ? busyTeachers[id] : null;
    return {
      value: id,
      label: `${name}${subj ? ` – ${subj}` : ''}`,
      disabled: !!busy,
      busyInfo: busy,
      name,
    };
  });

  const sortedTeacherOptions = [...teacherOptions].sort((a, b) => {
    if (a.disabled && !b.disabled) return 1;
    if (!a.disabled && b.disabled) return -1;
    return 0;
  });

  const isOtherType = slotType === 'Other';
  const canSave = isSubjectType ? (!!subjectValue && !!teacher) : isOtherType ? (!!customLabel.trim() && !!teacher) : !!teacher;

  return (
    <Modal open={open} onClose={onClose} title={slot.existing ? 'Edit Timetable Slot' : 'Add Timetable Slot'} size="lg">
      {/* Slot Info Header */}
      <div className="bg-gradient-to-r from-primary-50 to-indigo-50 rounded-xl p-4 mb-5 border border-primary-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-white border border-primary-200 flex items-center justify-center">
            <Clock size={18} className="text-primary-600" />
          </div>
          <div>
            <p className="text-sm font-bold text-slate-900">{slot.day} • {period?.name || 'Period'}</p>
            <p className="text-xs text-slate-500">{period ? `${period.start_time} – ${period.end_time}` : ''} • {classSection}</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium text-slate-700 mb-1.5 block">Slot Type *</label>
          <div className="flex flex-wrap gap-2">
            {typeOptions.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => { setSlotType(opt.value); if (opt.value !== 'Subject') { setSubject(''); } if (opt.value !== 'Other') { setCustomLabel(''); } setTeacher(''); }}
                className={`px-3.5 py-2 text-sm rounded-lg border transition-all duration-150 ${slotType === opt.value ? 'bg-primary-500 text-white border-primary-500 font-semibold shadow-sm' : 'bg-white text-slate-700 border-slate-200 hover:border-primary-300 hover:bg-primary-50'}`}
              >
                {opt.label}
              </button>
            ))}
          </div>
          {slotType === 'Other' && (
            <div className="mt-2">
              <input
                value={customLabel}
                onChange={e => setCustomLabel(e.target.value)}
                placeholder="Enter activity name (e.g. Yoga, Assembly, Career Counselling)"
                className="w-full border border-slate-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-150 hover:border-slate-400"
              />
            </div>
          )}
        </div>

        {isSubjectType && (
          <div>
            <label className="text-sm font-medium text-slate-700 mb-1.5 block">Subject *</label>
            <SearchableSelect
              value={subjectValue}
              onChange={(val) => { setSubject(val); const assigned = getAssignedTeacher(val); setTeacher(assigned || ''); }}
              options={subjects.map(s => ({ value: s.id, label: s.name + (s.code ? ` (${s.code})` : '') }))}
              placeholder="Search and select subject..."
              renderOption={(opt) => (
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-md bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center flex-shrink-0">
                    <span className="text-[10px] font-bold text-primary-600">{(opt.label || '').slice(0, 2).toUpperCase()}</span>
                  </div>
                  <span>{opt.label}</span>
                </div>
              )}
            />
          </div>
        )}

        <div>
          <label className="text-sm font-medium text-slate-700 mb-1.5 block">Teacher/Instructor *</label>
          <SearchableSelect
            value={teacher}
            onChange={(val) => { const opt = sortedTeacherOptions.find(o => o.value === val); if (opt && !opt.disabled) setTeacher(val); }}
            options={sortedTeacherOptions}
            placeholder={isSubjectType ? 'Search and select teacher...' : 'Select instructor (no conflict check)...'}
            renderOption={(opt) => {
              const busy = opt.busyInfo;
              return (
                <div className={`flex items-center gap-2 w-full ${busy ? 'opacity-50' : ''}`}>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${busy ? 'bg-slate-300' : 'bg-gradient-to-br from-indigo-500 to-indigo-700'}`}>
                    <span className={`text-[9px] font-bold ${busy ? 'text-slate-500' : 'text-white'}`}>{(opt.name || opt.label || '').slice(0, 1).toUpperCase()}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className={busy ? 'text-slate-400 line-through' : ''}>{opt.label}</span>
                    {busy && (
                      <p className="text-[10px] text-red-500 mt-0.5">Busy — {busy.subject} in Class {busy.class}</p>
                    )}
                  </div>
                </div>
              );
            }}
          />
          {!isSubjectType && <p className="text-[11px] text-slate-400 mt-1">No conflict checking for non-subject slots — all teachers shown</p>}
          {isSubjectType && teacher && subjectValue && (() => {
            const assignedId = getAssignedTeacher(subjectValue);
            if (assignedId && teacher !== assignedId) {
              const assignedName = teachingStaff.find(t => t.id === assignedId)?.user?.full_name || teachingStaff.find(t => t.id === assignedId)?.full_name || 'another teacher';
              return <p className="text-[11px] text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-2.5 py-1.5 mt-2 flex items-center gap-1.5">⚠️ <span><strong>{assignedName}</strong> is the assigned teacher for this subject in this section. You're selecting a different teacher.</span></p>;
            }
            return null;
          })()}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-slate-100">
        <Button variant="ghost" onClick={onClose}>Cancel</Button>
        <Button disabled={!canSave} onClick={() => onSave({ period_config_id: slot.periodId, day: slot.day, subject_id: isSubjectType ? subjectValue : undefined, teacher_id: teacher, slot_type: isOtherType ? customLabel.trim() : slotType })}>
          {slot.existing ? 'Update Slot' : 'Add Slot'}
        </Button>
      </div>
    </Modal>
  );
}

function PeriodFormDialog({ open, onClose, onCreate, existingPeriods }) {
  const [name, setName] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [isBreak, setIsBreak] = useState(false);
  const [error, setError] = useState('');

  const checkOverlap = (start, end) => {
    if (!start || !end) return '';
    if (end <= start) return 'End time must be after start time';
    const overlap = existingPeriods.find(p => p.start_time < end && p.end_time > start);
    if (overlap) return `Overlaps with "${overlap.name || 'Period'}" (${overlap.start_time} - ${overlap.end_time})`;
    return '';
  };

  const handleStartChange = (val) => {
    setStartTime(val);
    setError(checkOverlap(val, endTime));
  };

  const handleEndChange = (val) => {
    setEndTime(val);
    setError(checkOverlap(startTime, val));
  };

  const handleSubmit = () => {
    const overlapError = checkOverlap(startTime, endTime);
    if (overlapError) { setError(overlapError); return; }
    const periodName = isBreak ? (name || 'Break') : (name ? `Period ${name}` : `Period ${existingPeriods.filter(p => !p.is_break).length + 1}`);
    onCreate.mutate({ name: periodName, start_time: startTime, end_time: endTime, is_break: isBreak }, {
      onSuccess: () => { onClose(); setName(''); setStartTime(''); setEndTime(''); setIsBreak(false); setError(''); },
      onError: (err) => { setError(err?.response?.data?.detail || 'Failed to add period'); },
    });
  };

  const handleClose = () => { onClose(); setName(''); setStartTime(''); setEndTime(''); setIsBreak(false); setError(''); };

  return (
    <Modal open={open} onClose={handleClose} title="Add New Period">
      <div className="p-4 space-y-4">
        <div>
          <label className="text-xs text-slate-600 font-medium">Period Number *</label>
          <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. 1, 2, 3" className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm mt-1" />
        </div>
        <div>
          <TimeInput label="Start Time *" value={startTime} onChange={handleStartChange} />
        </div>
        <div>
          <TimeInput label="End Time *" value={endTime} onChange={handleEndChange} />
        </div>
        <Checkbox checked={isBreak} onChange={e => setIsBreak(e.target.checked)} label="This is a break period" />
        {error && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>}
      </div>
      <div className="flex justify-end gap-2 px-4 pb-4">
        <Button variant="ghost" onClick={handleClose}>Cancel</Button>
        <Button variant="primary" disabled={!startTime || !endTime || !!error || onCreate.isPending} onClick={handleSubmit}>
          {onCreate.isPending ? 'Adding...' : 'Add Period'}
        </Button>
      </div>
    </Modal>
  );
}

function EditPeriodDialog({ open, onClose, period, onUpdate, existingPeriods }) {
  const [name, setName] = useState(period.name || '');
  const [startTime, setStartTime] = useState(period.start_time || '');
  const [endTime, setEndTime] = useState(period.end_time || '');
  const [isBreak, setIsBreak] = useState(period.is_break || false);
  const [error, setError] = useState('');

  const checkOverlap = (start, end) => {
    if (!start || !end) return '';
    if (end <= start) return 'End time must be after start time';
    const overlap = existingPeriods.find(p => p.id !== period.id && p.start_time < end && p.end_time > start);
    if (overlap) return `Overlaps with "${overlap.name || 'Period'}" (${overlap.start_time} - ${overlap.end_time})`;
    return '';
  };

  const handleSubmit = () => {
    const overlapError = checkOverlap(startTime, endTime);
    if (overlapError) { setError(overlapError); return; }
    onUpdate.mutate({ id: period.id, data: { name, start_time: startTime, end_time: endTime, is_break: isBreak } }, {
      onSuccess: () => onClose(),
      onError: (err) => setError(err?.response?.data?.detail || 'Failed to update period'),
    });
  };

  return (
    <Modal open={open} onClose={onClose} title="Edit Period">
      <div className="p-4 space-y-4">
        <div>
          <label className="text-xs text-slate-600 font-medium">Period Name *</label>
          <input value={name} onChange={e => setName(e.target.value)} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm mt-1" />
        </div>
        <div>
          <TimeInput label="Start Time *" value={startTime} onChange={(val) => { setStartTime(val); setError(checkOverlap(val, endTime)); }} />
        </div>
        <div>
          <TimeInput label="End Time *" value={endTime} onChange={(val) => { setEndTime(val); setError(checkOverlap(startTime, val)); }} />
        </div>
        <Checkbox checked={isBreak} onChange={e => setIsBreak(e.target.checked)} label="This is a break period" />
        {error && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>}
      </div>
      <div className="flex justify-end gap-2 px-4 pb-4">
        <Button variant="ghost" onClick={onClose}>Cancel</Button>
        <Button variant="primary" disabled={!name || !startTime || !endTime || !!error || onUpdate.isPending} onClick={handleSubmit}>
          {onUpdate.isPending ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>
    </Modal>
  );
}

function TimetableTile({ classId, className, sectionName, onClick }) {
  const { data } = useTimetable({ class_section_id: classId });
  const { data: periodsData } = usePeriods();

  const slots = data?.timetable || {};
  const allPeriods = periodsData?.periods || periodsData?.results || (Array.isArray(periodsData) ? periodsData : []);
  const breaks = periodsData?.breaks || [];
  const periods = [...allPeriods, ...breaks].sort((a, b) => (a.start_time || '').localeCompare(b.start_time || ''));
  const teachingPeriods = periods.filter(p => !p.is_break);
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const daysFull = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  const filledSlots = daysFull.reduce((count, day) => count + (slots[day] || []).filter(Boolean).length, 0);
  const totalSlots = daysFull.length * teachingPeriods.length;
  const fillPct = totalSlots > 0 ? Math.round((filledSlots / totalSlots) * 100) : 0;

  return (
    <button onClick={onClick} className="group relative bg-white border border-slate-200 rounded-2xl overflow-hidden hover:shadow-lg hover:border-primary-300 transition-all duration-200 hover:-translate-y-0.5 active:scale-[0.99] text-left w-full">
      {/* Hover overlay */}
      <div className="absolute inset-0 z-10 flex items-center justify-center bg-gradient-to-br from-primary-600/90 to-indigo-700/90 opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-2xl backdrop-blur-[1px]">
        <div className="text-center">
          <p className="text-4xl font-black text-white tracking-tight">{className}-{sectionName}</p>
          <p className="text-sm text-white/70 font-medium mt-1">{fillPct}% scheduled</p>
          <p className="text-xs text-white/50 mt-2">Click to manage →</p>
        </div>
      </div>

      <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-slate-50 to-white border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center shadow-sm">
            <span className="text-sm font-black text-white">{className}</span>
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">Class {className} - {sectionName}</h3>
            <p className="text-[10px] text-slate-400">{filledSlots}/{totalSlots} slots filled • {fillPct}% complete</p>
          </div>
        </div>
        <svg className="w-4 h-4 text-slate-400 group-hover:text-primary-500 group-hover:translate-x-0.5 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
      </div>

      <div className="p-3 overflow-hidden">
        <div className="overflow-hidden rounded-lg border border-slate-100">
          <table className="w-full text-[9px] border-collapse">
            <thead>
              <tr className="bg-slate-50">
                <th className="px-1.5 py-1.5 text-slate-400 font-semibold border-r border-slate-100 w-10 text-left">Day</th>
                {teachingPeriods.slice(0, 7).map((p, i) => (
                  <th key={i} className="px-1 py-1.5 text-slate-400 font-semibold border-r border-slate-100 last:border-r-0">P{i + 1}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {days.map((day, di) => (
                <tr key={day} className="border-t border-slate-100">
                  <td className="px-1.5 py-1 text-slate-600 font-bold border-r border-slate-100 bg-slate-50/50">{day}</td>
                  {teachingPeriods.slice(0, 7).map((_, pi) => {
                    const slot = (slots[daysFull[di]] || [])[pi];
                    const hasSlot = !!slot;
                    return (
                      <td key={pi} className="px-0.5 py-1 border-r border-slate-50 last:border-r-0 text-center">
                        {hasSlot ? (
                          <span className="inline-block w-full px-0.5 py-0.5 rounded bg-primary-50 text-primary-700 font-semibold truncate leading-tight">
                            {slot.subject || slot.subject_name || ''}
                          </span>
                        ) : (
                          <span className="inline-block w-full px-0.5 py-0.5 text-slate-200">·</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </button>
  );
}
