import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, Skeleton, useToast, Breadcrumb, DatePicker, SearchableSelect, AttendanceMarkingView, exportStyledMultiSheetExcel } from 'school-erp-ui-shared';
import { CheckCircle2, Clock, CalendarDays, Search, Users, ArrowLeft, BookOpen, User, Download } from 'lucide-react';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';
import { useClassSections, useAcademicYear, useAttendanceConfig, useHolidays, useSchoolProfile } from '../../services/settingsService';
import { getSchoolInfo } from '../../utils/getSchoolInfo';

export default function AttendancePage() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const { data: schoolProfile } = useSchoolProfile();
  const [selectedSection, setSelectedSection] = useState(null);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const today = new Date().toISOString().split('T')[0];
  const [date, setDate] = useState(today);
  const [cardSearch, setCardSearch] = useState('');
  const [downloading, setDownloading] = useState(false);
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');

  const { data: classSectionsData, isLoading: classesLoading } = useClassSections();
  const { data: academicYear } = useAcademicYear();
  const { data: attendanceConfig } = useAttendanceConfig();
  const { data: holidaysData } = useHolidays();

  const attendanceMode = 'daily'; // Force daily mode (subject-wise coming soon)
  const isSubjectWise = false;

  const holidays = holidaysData?.holidays || holidaysData?.results || (Array.isArray(holidaysData) ? holidaysData : []);
  const workingDays = attendanceConfig?.working_days || ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
  const isNonWorkingDay = (() => {
    const d = new Date(date + 'T00:00:00');
    const dayName = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][d.getDay()];
    return !workingDays.includes(dayName);
  })();
  const matchedHoliday = holidays.find(h => h.date === date);
  const isHolidayOrWeekend = isNonWorkingDay || !!matchedHoliday;

  const classes = classSectionsData?.classes || [];
  const allSections = classes.flatMap(cls =>
    cls.sections.map(sec => ({ id: sec.id, label: `${cls.name} - ${sec.section_name}`, className: cls.name, sectionName: sec.section_name }))
  );

  const handleDownloadReport = async (sectionFilter = null) => {
    setDownloading(true);
    try {
      const sectionsToDownload = sectionFilter ? allSections.filter(s => s.id === sectionFilter) : allSections;
      const sheets = [];
      for (const sec of sectionsToDownload) {
        const res = await api.get(ENDPOINTS.attendance.get, { params: { class_section_id: sec.id, date } });
        const records = res.data?.records || [];
        if (records.length === 0) continue;
        const headers = ['Roll Number', 'Student Name', 'Status'];
        const rows = records.map(r => [r.roll_number || '', r.full_name || '', r.status || 'Not Marked']);
        const present = records.filter(r => r.status === 'Present').length;
        const absent = records.filter(r => r.status === 'Absent').length;
        const late = records.filter(r => r.status === 'Late').length;
        rows.push([]);
        rows.push(['Summary', '', '']);
        rows.push(['Present', present, '']);
        rows.push(['Absent', absent, '']);
        rows.push(['Late', late, '']);
        rows.push(['Total', records.length, '']);
        sheets.push({ name: sec.label.slice(0, 31), headers, rows });
      }
      if (sheets.length === 0) { toast.info('No attendance data found for this date'); setDownloading(false); return; }
      const filename = `Attendance_Report_${date}${sectionFilter ? `_${sectionsToDownload[0]?.label}` : '_All_Classes'}`;
      await exportStyledMultiSheetExcel({ filename, schoolInfo: getSchoolInfo(schoolProfile), reportTitle: `Attendance Report - ${date}`, sheets });
      toast.success(`Report downloaded with ${sheets.length} sheet(s)`);
    } catch (err) {
      toast.error('Failed to generate report');
    }
    setDownloading(false);
  };

  // Fetch attendance data - in subject-wise mode, pass subject_id and period
  const { data: attendanceData, isLoading, refetch } = useQuery({
    queryKey: ['admin-attendance', selectedSection?.id, date, selectedSubject?.subject_id, selectedSubject?.period_number],
    queryFn: () => {
      const params = { class_section_id: selectedSection.id, date };
      if (isSubjectWise && selectedSubject) {
        params.subject_id = selectedSubject.subject_id;
        params.period = selectedSubject.period_number;
      }
      return api.get(ENDPOINTS.attendance.get, { params }).then(r => r.data);
    },
    enabled: isSubjectWise
      ? !!selectedSection?.id && !!date && !!selectedSubject
      : !!selectedSection?.id && !!date,
  });

  const studentList = attendanceData?.records || [];
  const isSubmitted = attendanceData?.is_submitted || false;

  const submitMutation = useMutation({
    mutationFn: (payload) => api.post(ENDPOINTS.attendance.submit, payload).then(r => r.data),
    onSuccess: () => {
      toast.success('Attendance submitted successfully');
      refetch();
      queryClient.invalidateQueries({ queryKey: ['students'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['attendance-overview'] });
      queryClient.invalidateQueries({ queryKey: ['class-subjects-status'] });
      queryClient.invalidateQueries({ queryKey: ['admin-attendance'] });
    },
    onError: (err) => {
      const d = err.response?.data;
      const msg = typeof d?.detail === 'string' ? d.detail : Array.isArray(d?.detail) ? d.detail.map(e => e.msg).join(', ') : d?.error || 'Failed to submit';
      toast.error(msg);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload) => api.put(ENDPOINTS.attendance.update, payload).then(r => r.data),
    onSuccess: () => {
      toast.success('Attendance updated successfully');
      refetch();
      queryClient.invalidateQueries({ queryKey: ['students'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['attendance-overview'] });
      queryClient.invalidateQueries({ queryKey: ['class-subjects-status'] });
      queryClient.invalidateQueries({ queryKey: ['admin-attendance'] });
    },
    onError: (err) => toast.error(err.response?.data?.detail || err.response?.data?.error || 'Failed to update'),
  });

  const handleSubmit = (records) => {
    if (!academicYear?.current) { toast.error('Academic year not configured. Please set up academic year in Settings.'); return; }
    if (!selectedSection) { toast.error('Please select a class and section'); return; }
    if (!records.length) { toast.error('No students to mark attendance for'); return; }

    const payload = {
      class_id: selectedSection.id,
      date,
      academic_year: academicYear.current,
      records,
    };

    if (isSubjectWise && selectedSubject) {
      payload.subject_id = selectedSubject.subject_id;
      payload.period_number = selectedSubject.period_number;
    }

    if (isSubmitted) {
      const updatePayload = {
        class_id: selectedSection.id,
        date,
        records,
      };
      if (isSubjectWise && selectedSubject) {
        updatePayload.subject_id = selectedSubject.subject_id;
        updatePayload.period_number = selectedSubject.period_number;
      }
      updateMutation.mutate(updatePayload);
    } else {
      submitMutation.mutate(payload);
    }
  };

  const openSection = (section) => {
    setSelectedSection(section);
    setSelectedSubject(null);
  };

  const openSubject = (subject) => {
    setSelectedSubject(subject);
  };

  const goBack = () => {
    if (isSubjectWise && selectedSubject) {
      setSelectedSubject(null);
    } else {
      setSelectedSection(null);
      setSelectedSubject(null);
    }
  };

  const goBackToClasses = () => {
    setSelectedSection(null);
    setSelectedSubject(null);
  };

  // Compute holiday warning string
  const holidayWarning = isHolidayOrWeekend
    ? (matchedHoliday ? `Holiday: ${matchedHoliday.name || matchedHoliday.title || 'School Holiday'}` : (() => {
        const d = new Date(date + 'T00:00:00');
        const dayName = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][d.getDay()];
        return `${dayName} is not a working day`;
      })())
    : null;

  // Header extra for subject-wise mode (teacher info)
  const headerExtra = isSubjectWise && selectedSubject?.teacher_name ? (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 rounded-lg border border-slate-200 w-fit">
      <User size={14} className="text-slate-500" />
      <span className="text-sm text-slate-600">{selectedSubject.teacher_name}</span>
    </div>
  ) : null;

  // Subject-wise mode: show subject grid for selected class
  if (isSubjectWise && selectedSection && !selectedSubject) {
    return (
      <SubjectGridView
        section={selectedSection}
        date={date}
        setDate={(d) => { setDate(d); }}
        onSelectSubject={openSubject}
        onBack={goBackToClasses}
      />
    );
  }

  // Attendance marking view (both daily and subject-wise after subject selection)
  if (selectedSection && (!isSubjectWise || selectedSubject)) {
    return (
      <div className="space-y-6">
        <Breadcrumb items={[
          { label: 'Dashboard', href: '/admin/dashboard' },
          { label: 'Attendance', href: '#', onClick: goBackToClasses },
          ...(isSubjectWise ? [{ label: selectedSection.label, href: '#', onClick: goBack }] : []),
          { label: isSubjectWise ? selectedSubject.subject_name : selectedSection.label },
        ]} />
        <div className="flex items-center gap-4 mb-6">
          <button onClick={goBack} className="p-2 hover:bg-slate-100 rounded-lg transition-colors"><ArrowLeft size={20} className="text-slate-600" /></button>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              {isSubjectWise ? `${selectedSubject.subject_name}` : `Class ${selectedSection.label}`}
            </h1>
            <p className="text-sm text-slate-500">
              {isSubjectWise
                ? `${selectedSection.label} | ${selectedSubject.period_name} (${selectedSubject.period_start || ''} - ${selectedSubject.period_end || ''})`
                : `Mark attendance for ${date}`
              }
            </p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <div className="relative">
              <CalendarDays className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <DatePicker value={date} onChange={(v) => { setDate(v); }} max={today} />
            </div>
            <Button variant="secondary" size="sm" icon={Download} onClick={() => handleDownloadReport(selectedSection.id)} loading={downloading}>Report</Button>
          </div>
        </div>

        <AttendanceMarkingView
          studentList={studentList}
          isSubmitted={isSubmitted}
          isLoading={isLoading}
          onSubmit={handleSubmit}
          isSubmitting={submitMutation.isPending || updateMutation.isPending}
          date={date}
          onDateChange={null}
          showDateNav={false}
          showHistory={false}
          showDownloadReport={false}
          className={isSubjectWise ? selectedSubject.subject_name : selectedSection.label}
          headerExtra={headerExtra}
          showKeyboardHints={true}
          holidayWarning={holidayWarning}
        />
      </div>
    );
  }

  // Home view: class-section grid (same for both modes)
  return (
    <div className="space-y-6">
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Attendance' }]} />
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Attendance</h1>
          <p className="text-sm text-slate-500 mt-1">
            {isSubjectWise
              ? 'Mark and manage subject-wise student attendance by class'
              : 'Mark and manage student attendance by class'
            }
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isSubjectWise && (
            <span className="px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold border border-indigo-200">Subject-wise Mode</span>
          )}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input type="text" value={cardSearch} onChange={(e) => setCardSearch(e.target.value)} placeholder="Search class or section..." className="pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm w-52 focus:outline-none focus:ring-2 focus:ring-primary-500" />
          </div>
          <div className="relative">
            <CalendarDays className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <DatePicker value={date} onChange={(v) => setDate(v)} max={today} />
          </div>
          <Button variant="secondary" size="sm" icon={Download} onClick={() => handleDownloadReport()} loading={downloading}>Download Report</Button>
        </div>
      </div>

      {!classesLoading && allSections.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center"><Users size={18} className="text-blue-600" /></div>
            <div><p className="text-xs text-slate-500">Total Sections</p><p className="text-xl font-bold text-slate-900">{allSections.length}</p></div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-50 to-emerald-100 flex items-center justify-center"><CheckCircle2 size={18} className="text-emerald-600" /></div>
            <div><p className="text-xs text-slate-500">Classes</p><p className="text-xl font-bold text-slate-900">{classes.length}</p></div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center"><CalendarDays size={18} className="text-primary-600" /></div>
            <div><p className="text-xs text-slate-500">Date</p><p className="text-lg font-bold text-slate-900">{new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</p></div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-50 to-amber-100 flex items-center justify-center"><Clock size={18} className="text-amber-600" /></div>
            <div><p className="text-xs text-slate-500">Academic Year</p><p className="text-lg font-bold text-slate-900">{academicYear?.current || '—'}</p></div>
          </div>
        </div>
      )}

      {/* Date Range Filter for Report Download */}
      <div className="flex items-center gap-2 flex-wrap bg-white border border-slate-200 rounded-xl px-4 py-3">
        <span className="text-sm font-medium text-slate-600">Report Date Range:</span>
        <label className="text-sm text-gray-600">From</label>
        <input type="date" className="border border-slate-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" value={fromDate} onChange={e => setFromDate(e.target.value)} />
        <label className="text-sm text-gray-600">To</label>
        <input type="date" className="border border-slate-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" value={toDate} onChange={e => setToDate(e.target.value)} />
        {(fromDate || toDate) && <button onClick={() => { setFromDate(''); setToDate(''); }} className="text-xs text-red-500 hover:text-red-700 ml-2">Clear</button>}
      </div>

      {classesLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => <Skeleton key={i} className="h-44 rounded-xl" />)}
        </div>
      )}

      {!classesLoading && classes.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          <p>No classes configured. Set up classes in Settings first.</p>
        </div>
      )}

      {!classesLoading && classes.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {allSections.filter(s => !cardSearch || s.label.toLowerCase().includes(cardSearch.toLowerCase()) || s.className.toLowerCase().includes(cardSearch.toLowerCase()) || s.sectionName.toLowerCase().includes(cardSearch.toLowerCase())).map((section) => (
            <ClassSectionCard key={section.id} section={section} date={date} onTakeAttendance={() => openSection(section)} />
          ))}
        </div>
      )}
    </div>
  );
}

// ===== Subject Grid View (shown when mode is subject_wise and a class is selected) =====

function SubjectGridView({ section, date, setDate, onSelectSubject, onBack }) {
  const today = new Date().toISOString().split('T')[0];
  const { data: subjectsData, isLoading } = useQuery({
    queryKey: ['class-subjects-status', section.id, date],
    queryFn: () => api.get(ENDPOINTS.attendance.classSubjectsStatus, {
      params: { class_section_id: section.id, date }
    }).then(r => r.data),
    staleTime: 15000,
  });

  const subjects = subjectsData?.subjects || [];
  const summary = subjectsData?.summary || {};
  const dayOfWeek = subjectsData?.day_of_week || '';

  return (
    <div className="space-y-6">
      <Breadcrumb items={[
        { label: 'Dashboard', href: '/admin/dashboard' },
        { label: 'Attendance', href: '#', onClick: onBack },
        { label: section.label },
      ]} />

      <div className="flex items-center gap-4 mb-6">
        <button onClick={onBack} className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
          <ArrowLeft size={20} className="text-slate-600" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Class {section.label}</h1>
          <p className="text-sm text-slate-500">
            Subject-wise attendance for {dayOfWeek}, {new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
          </p>
        </div>
        <div className="ml-auto">
          <div className="relative">
            <CalendarDays className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <DatePicker value={date} onChange={(v) => setDate(v)} max={today} />
          </div>
        </div>
      </div>

      {/* Summary cards */}
      {!isLoading && subjects.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-50 to-indigo-100 flex items-center justify-center">
              <BookOpen size={18} className="text-indigo-600" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Total Subjects</p>
              <p className="text-xl font-bold text-slate-900">{summary.total_subjects || 0}</p>
            </div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-50 to-emerald-100 flex items-center justify-center">
              <CheckCircle2 size={18} className="text-emerald-600" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Marked</p>
              <p className="text-xl font-bold text-slate-900">{summary.subjects_marked || 0}</p>
            </div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-50 to-amber-100 flex items-center justify-center">
              <Clock size={18} className="text-amber-600" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Pending</p>
              <p className="text-xl font-bold text-slate-900">{summary.subjects_pending || 0}</p>
            </div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center">
              <Users size={18} className="text-green-600" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Total Present</p>
              <p className="text-xl font-bold text-slate-900">{summary.total_present || 0}</p>
            </div>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => <Skeleton key={i} className="h-40 rounded-xl" />)}
        </div>
      )}

      {!isLoading && subjects.length === 0 && (
        <div className="text-center py-12">
          <BookOpen size={48} className="mx-auto text-slate-300 mb-4" />
          <p className="text-slate-500">No subjects scheduled for {dayOfWeek}.</p>
          <p className="text-sm text-slate-400 mt-1">Please check the timetable configuration for this class.</p>
        </div>
      )}

      {!isLoading && subjects.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {subjects.map((subject) => (
            <SubjectCard key={`${subject.subject_id}-${subject.period_number}`} subject={subject} onClick={() => onSelectSubject(subject)} />
          ))}
        </div>
      )}
    </div>
  );
}

// ===== Subject Card (within subject grid) =====

function SubjectCard({ subject, onClick }) {
  const totalStudents = subject.total_present + subject.total_absent + subject.total_late;

  return (
    <div
      className="group bg-white border border-slate-200 rounded-xl overflow-hidden hover:shadow-soft-lg hover:border-slate-300 transition-all duration-200 cursor-pointer"
      onClick={onClick}
    >
      <div className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-50 to-indigo-100 flex items-center justify-center border border-indigo-200">
              <BookOpen size={18} className="text-indigo-600" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 group-hover:text-primary-700 transition-colors">
                {subject.subject_name}
              </h3>
              <p className="text-xs text-slate-400">{subject.period_name}</p>
            </div>
          </div>
          {subject.is_submitted ? (
            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">Marked</span>
          ) : (
            <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-600 text-[10px] font-semibold border border-amber-200">Pending</span>
          )}
        </div>

        {/* Time and teacher info */}
        <div className="space-y-2 mb-3">
          {(subject.period_start || subject.period_end) && (
            <div className="flex items-center gap-2">
              <Clock size={12} className="text-slate-400" />
              <span className="text-xs text-slate-500">{subject.period_start} - {subject.period_end}</span>
            </div>
          )}
          {subject.teacher_name && (
            <div className="flex items-center gap-2">
              <User size={12} className="text-slate-400" />
              <span className="text-xs text-slate-500">{subject.teacher_name}</span>
            </div>
          )}
        </div>

        {/* Attendance counts if marked */}
        {subject.is_submitted && totalStudents > 0 && (
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-emerald-50 rounded-lg px-2 py-1.5 text-center border border-emerald-100">
              <p className="text-sm font-bold text-emerald-700">{subject.total_present}</p>
              <p className="text-[9px] font-medium text-emerald-600 uppercase">Present</p>
            </div>
            <div className="bg-red-50 rounded-lg px-2 py-1.5 text-center border border-red-100">
              <p className="text-sm font-bold text-red-600">{subject.total_absent}</p>
              <p className="text-[9px] font-medium text-red-500 uppercase">Absent</p>
            </div>
            <div className="bg-amber-50 rounded-lg px-2 py-1.5 text-center border border-amber-100">
              <p className="text-sm font-bold text-amber-600">{subject.total_late}</p>
              <p className="text-[9px] font-medium text-amber-500 uppercase">Late</p>
            </div>
          </div>
        )}

        {!subject.is_submitted && (
          <div className="flex items-center gap-2 py-2">
            <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center">
              <CalendarDays size={12} className="text-slate-400" />
            </div>
            <p className="text-xs text-slate-500">Attendance not marked yet</p>
          </div>
        )}
      </div>

      <div className="bg-slate-50/80 border-t border-slate-100 px-5 py-2.5 flex items-center justify-between">
        <span className="text-[10px] text-slate-400 font-medium">
          {subject.is_submitted ? 'Click to view or edit' : 'Click to mark attendance'}
        </span>
        <svg className="w-4 h-4 text-slate-400 group-hover:text-primary-500 group-hover:translate-x-0.5 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  );
}

// ===== ClassSection Card (existing, unchanged) =====

function ClassSectionCard({ section, date, onTakeAttendance }) {
  const { data, isLoading } = useQuery({
    queryKey: ['attendance-overview', section.id, date],
    queryFn: () => api.get(ENDPOINTS.attendance.get, { params: { class_section_id: section.id, date } }).then(r => r.data).catch(() => null),
    staleTime: 30000,
  });

  const students = data?.records || [];
  const total = students.length;
  const isSubmitted = data?.is_submitted || false;
  const present = students.filter(s => s.status === 'Present').length;
  const absent = students.filter(s => s.status === 'Absent').length;
  const late = students.filter(s => s.status === 'Late').length;
  const attendancePct = total > 0 && isSubmitted ? Math.round(((present + late) / total) * 100) : null;

  return (
    <div className="group bg-white border border-slate-200 rounded-xl overflow-hidden hover:shadow-soft-lg hover:border-slate-300 transition-all duration-200 cursor-pointer" onClick={onTakeAttendance}>
      <div className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center border border-primary-200">
              <Users size={18} className="text-primary-600" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 group-hover:text-primary-700 transition-colors">{section.label}</h3>
              <p className="text-xs text-slate-400">{total} students</p>
            </div>
          </div>
          {isSubmitted ? (
            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200">Submitted</span>
          ) : total > 0 ? (
            <span className="px-2 py-0.5 rounded-full bg-amber-50 text-amber-600 text-[10px] font-semibold border border-amber-200">Pending</span>
          ) : null}
        </div>

        {isLoading ? (
          <Skeleton className="h-12 rounded-lg" />
        ) : total === 0 ? (
          <p className="text-xs text-slate-400 py-2">No students enrolled</p>
        ) : isSubmitted ? (
          <>
            <div className="grid grid-cols-3 gap-2 mb-3">
              <div className="bg-emerald-50 rounded-lg px-2.5 py-2 text-center border border-emerald-100">
                <p className="text-lg font-bold text-emerald-700">{present}</p>
                <p className="text-[9px] font-medium text-emerald-600 uppercase">Present</p>
              </div>
              <div className="bg-red-50 rounded-lg px-2.5 py-2 text-center border border-red-100">
                <p className="text-lg font-bold text-red-600">{absent}</p>
                <p className="text-[9px] font-medium text-red-500 uppercase">Absent</p>
              </div>
              <div className="bg-amber-50 rounded-lg px-2.5 py-2 text-center border border-amber-100">
                <p className="text-lg font-bold text-amber-600">{late}</p>
                <p className="text-[9px] font-medium text-amber-500 uppercase">Late</p>
              </div>
            </div>
            {attendancePct !== null && (
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-medium text-slate-500">Today's Attendance</span>
                  <span className={`text-sm font-bold ${attendancePct >= 75 ? 'text-emerald-600' : attendancePct >= 50 ? 'text-amber-600' : 'text-red-600'}`}>{attendancePct}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className={`h-full rounded-full transition-all duration-500 ${attendancePct >= 75 ? 'bg-emerald-500' : attendancePct >= 50 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${attendancePct}%` }} />
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex items-center gap-2 py-3">
            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center">
              <CalendarDays size={14} className="text-slate-400" />
            </div>
            <p className="text-xs text-slate-500">Attendance not marked for today</p>
          </div>
        )}
      </div>

      <div className="bg-slate-50/80 border-t border-slate-100 px-5 py-3 flex items-center justify-between">
        <span className="text-[10px] text-slate-400 font-medium">{isSubmitted ? 'Click to view or edit' : 'Click to take attendance'}</span>
        <svg className="w-4 h-4 text-slate-400 group-hover:text-primary-500 group-hover:translate-x-0.5 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
      </div>
    </div>
  );
}
