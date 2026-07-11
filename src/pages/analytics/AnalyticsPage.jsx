import { Users, GraduationCap, DollarSign, TrendingUp, TrendingDown, BookOpen, BarChart2, PieChart as PieIcon, ArrowUpRight, ArrowDownRight, Minus, Bus } from 'lucide-react';
import {
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, Legend, Area, AreaChart,
  RadialBarChart, RadialBar, LineChart, Line, ScatterChart, Scatter, ZAxis,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from 'recharts';
import {
  useDashboardStats,
  useAnalyticsAttendanceByClass,
  useAnalyticsFeeTrend,
  useAnalyticsExamPerformance,
  useAnalyticsTeacherWorkload,
  useAnalyticsEnrollmentTrend,
  useAnalyticsFeeDefaulters,
  useAnalyticsAttendanceComparison,
  useAnalyticsStudentTypeRatio,
  useAnalyticsSubjectPerformance,
  useAnalyticsClassToppers,
  useAnalyticsCorrelation,
  useAnalyticsRevenueTarget,
  useAnalyticsTeacherLeavePatterns,
  useAnalyticsTransportUtilization,
  useAnalyticsConcessionSummary,
  useAnalyticsGrowthRate,
  useAnalyticsFeeCollectionRate,
} from '../../services/dashboardService';
import { SkeletonDashboard, Breadcrumb, ErrorBoundary } from 'school-erp-ui-shared';

const COLORS = ['#3b82f6', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#ef4444', '#84cc16'];
const CHART_TOOLTIP = { contentStyle: { borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 20px -4px rgba(0,0,0,0.1)', fontSize: '12px' } };

function ChartCard({ title, subtitle, children, className = '' }) {
  return (
    <div className={`bg-white border border-slate-200 rounded-xl p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300 ${className}`}>
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
        {subtitle && <p className="text-[11px] text-slate-400 mt-0.5">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}

function EmptyChart({ message = 'No data available' }) {
  return (
    <div className="h-[220px] flex flex-col items-center justify-center text-slate-300">
      <BarChart2 size={32} className="mb-2" />
      <p className="text-sm text-slate-400">{message}</p>
    </div>
  );
}

function ChangeIndicator({ value }) {
  if (!value || value === 0) return <span className="flex items-center gap-0.5 text-[10px] text-slate-400"><Minus size={10} />No change</span>;
  const isPositive = value > 0;
  return (
    <span className={`flex items-center gap-0.5 text-[10px] font-medium ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
      {isPositive ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />}
      {Math.abs(value).toFixed(1)}%
    </span>
  );
}

export default function AnalyticsPage() {
  const { data: stats, isLoading } = useDashboardStats();
  const { data: attendanceByClass } = useAnalyticsAttendanceByClass();
  const { data: feeTrend } = useAnalyticsFeeTrend();
  const { data: examPerformance } = useAnalyticsExamPerformance();
  const { data: teacherWorkload } = useAnalyticsTeacherWorkload();
  const { data: enrollmentTrend } = useAnalyticsEnrollmentTrend();
  const { data: feeDefaulters } = useAnalyticsFeeDefaulters();
  const { data: attendanceComparison } = useAnalyticsAttendanceComparison();
  const { data: studentTypeRatio } = useAnalyticsStudentTypeRatio();
  const { data: subjectPerformance } = useAnalyticsSubjectPerformance();
  const { data: classToppers } = useAnalyticsClassToppers();
  const { data: correlationData } = useAnalyticsCorrelation();
  const { data: revenueTarget } = useAnalyticsRevenueTarget();
  const { data: teacherLeavePatterns } = useAnalyticsTeacherLeavePatterns();
  const { data: transportUtilization } = useAnalyticsTransportUtilization();
  const { data: concessionSummary } = useAnalyticsConcessionSummary();
  const { data: growthRate } = useAnalyticsGrowthRate();
  const { data: feeCollectionRate } = useAnalyticsFeeCollectionRate();

  if (isLoading) return <SkeletonDashboard />;

  const attendanceClassData = attendanceByClass?.data || [];
  const feeTrendData = feeTrend?.data || [];
  const examData = examPerformance?.data || [];
  const workloadData = teacherWorkload?.data || [];
  const enrollmentData = enrollmentTrend?.data || [];
  const defaultersData = feeDefaulters?.data || [];
  const comparisonData = attendanceComparison?.data || [];
  const studentType = studentTypeRatio || { dayscholar: 0, hostler: 0, total: 0 };
  const subjectData = subjectPerformance?.data || [];
  const toppersData = classToppers?.data || [];
  const scatterData = correlationData?.data || [];
  const revenueData = revenueTarget?.data || [];
  const leavePatternData = teacherLeavePatterns?.data || [];
  const transportData = transportUtilization?.data || [];
  const concessionData = concessionSummary?.data || [];
  const growthData = growthRate?.data || [];
  const feeRateData = feeCollectionRate?.data || [];

  const studentTypePieData = [
    { name: 'Dayscholar', value: studentType.dayscholar || 0, color: '#3b82f6' },
    { name: 'Hostler', value: studentType.hostler || 0, color: '#f59e0b' },
  ].filter(d => d.value > 0);

  const avgAttendance = attendanceClassData.length > 0 ? Math.round(attendanceClassData.reduce((s, d) => s + (d.attendance_pct || 0), 0) / attendanceClassData.length) : null;
  const avgExamScore = examData.length > 0 ? Math.round(examData.reduce((s, d) => s + (d.avg_percentage || 0), 0) / examData.length) : null;
  const totalCollected = feeTrendData.reduce((s, d) => s + (d.collected || 0), 0);
  const avgWorkload = workloadData.length > 0 ? Math.round(workloadData.reduce((s, d) => s + (d.utilization_pct || 0), 0) / workloadData.length) : null;

  const summaryKpis = [
    { label: 'Avg Attendance', value: avgAttendance != null ? `${avgAttendance}%` : '—', icon: TrendingUp, color: 'text-sky-600', bg: 'from-sky-50 to-sky-100' },
    { label: 'Avg Exam Score', value: avgExamScore != null ? `${avgExamScore}%` : '—', icon: BookOpen, color: 'text-emerald-600', bg: 'from-emerald-50 to-emerald-100' },
    { label: 'Fee Collected', value: totalCollected > 0 ? `₹${(totalCollected / 1000).toFixed(0)}K` : '—', icon: DollarSign, color: 'text-purple-600', bg: 'from-purple-50 to-purple-100' },
    { label: 'Staff Utilization', value: avgWorkload != null ? `${avgWorkload}%` : '—', icon: GraduationCap, color: 'text-amber-600', bg: 'from-amber-50 to-amber-100' },
    { label: 'Total Students', value: stats?.total_students ?? '—', icon: Users, color: 'text-blue-600', bg: 'from-blue-50 to-blue-100' },
  ];

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Analytics' }]} />
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Analytics</h1>
          <p className="text-sm text-slate-500 mt-0.5">Deep insights into your institution's performance</p>
        </div>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        {summaryKpis.map(k => (
          <div key={k.label} className="bg-white border border-slate-200 rounded-xl p-4 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg cursor-default group">
            <div className="flex items-center gap-2 mb-2">
              <div className={`bg-gradient-to-br ${k.bg} p-2 rounded-lg transition-transform duration-200 group-hover:scale-110`}>
                <k.icon size={16} className={k.color} />
              </div>
            </div>
            <p className="text-xl font-bold text-slate-900">{k.value}</p>
            <p className="text-[11px] text-slate-500 font-medium mt-0.5">{k.label}</p>
          </div>
        ))}
      </div>

      {/* Row 1: Attendance by Class + Gender Ratio */}
      <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-4">
        <ChartCard title="Attendance by Class" subtitle="Average attendance percentage per class" className="md:col-span-8">
          {attendanceClassData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={attendanceClassData} barCategoryGap="25%">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="class_name" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `Class ${v}`} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} unit="%" />
                <Tooltip {...CHART_TOOLTIP} formatter={(v) => `${v}%`} />
                <Bar dataKey="attendance_pct" name="Attendance" radius={[6, 6, 0, 0]} maxBarSize={40}>
                  {attendanceClassData.map((entry, i) => (
                    <Cell key={i} fill={entry.attendance_pct >= 90 ? '#10b981' : entry.attendance_pct >= 75 ? '#f59e0b' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyChart message="No attendance data yet" />}
        </ChartCard>

        <ChartCard title="Dayscholar / Hostler" subtitle={`Total: ${studentType.total} students`} className="md:col-span-4">
          {studentTypePieData.length > 0 ? (
            <div>
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={studentTypePieData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} dataKey="value" paddingAngle={3}>
                    {studentTypePieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                  </Pie>
                  <Tooltip {...CHART_TOOLTIP} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 mt-2">
                {studentTypePieData.map(d => (
                  <div key={d.name} className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                    <span className="text-xs text-slate-600">{d.name}: <span className="font-semibold">{d.value}</span></span>
                  </div>
                ))}
              </div>
            </div>
          ) : <EmptyChart message="No student data" />}
        </ChartCard>
      </div>
      </ErrorBoundary>

      {/* Row 2: Fee Collection Trend + Exam Performance */}
      <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <ChartCard title="Fee Collection Trend" subtitle="Monthly collection over last 6 months">
          {feeTrendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={feeTrendData}>
                <defs>
                  <linearGradient id="feeGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} tickFormatter={v => `₹${(v/1000).toFixed(0)}K`} />
                <Tooltip {...CHART_TOOLTIP} formatter={(v) => `₹${Number(v).toLocaleString()}`} />
                <Area type="monotone" dataKey="collected" stroke="#8b5cf6" strokeWidth={2.5} fill="url(#feeGradient)" name="Collected" dot={{ r: 3, fill: '#8b5cf6' }} />
                <Area type="monotone" dataKey="pending" stroke="#f59e0b" strokeWidth={1.5} fill="none" strokeDasharray="4 4" name="Pending" dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          ) : <EmptyChart message="No fee collection data" />}
        </ChartCard>

        <ChartCard title="Exam Performance by Class" subtitle="Average score percentage across all exams">
          {examData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={examData} barCategoryGap="20%">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="class_name" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `Class ${v}`} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} unit="%" />
                <Tooltip {...CHART_TOOLTIP} formatter={(v, name) => [`${v}%`, name]} />
                <Bar dataKey="avg_percentage" name="Avg Score" radius={[6, 6, 0, 0]} maxBarSize={36} fill="#10b981" />
                <Bar dataKey="pass_rate" name="Pass Rate" radius={[6, 6, 0, 0]} maxBarSize={36} fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyChart message="No exam data yet" />}
        </ChartCard>
      </div>
      </ErrorBoundary>

      {/* Row 3: Attendance Comparison + Teacher Workload */}
      <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <ChartCard title="Attendance: This Month vs Last Month" subtitle="Class-wise comparison showing improvement or decline">
          {comparisonData.length > 0 ? (
            <div>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={comparisonData} barGap={2} barCategoryGap="25%">
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="class_name" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `Class ${v}`} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} unit="%" />
                  <Tooltip {...CHART_TOOLTIP} formatter={(v) => `${v}%`} />
                  <Bar dataKey="last_month" name="Last Month" fill="#cbd5e1" radius={[4, 4, 0, 0]} maxBarSize={24} />
                  <Bar dataKey="this_month" name="This Month" fill="#3b82f6" radius={[4, 4, 0, 0]} maxBarSize={24} />
                  <Legend verticalAlign="top" height={30} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
                </BarChart>
              </ResponsiveContainer>
              <div className="grid grid-cols-3 md:grid-cols-5 gap-2 mt-3 pt-3 border-t border-slate-100">
                {comparisonData.slice(0, 5).map(d => (
                  <div key={d.class_name} className="text-center">
                    <p className="text-[10px] text-slate-400">Class {d.class_name}</p>
                    <ChangeIndicator value={d.change} />
                  </div>
                ))}
              </div>
            </div>
          ) : <EmptyChart message="Insufficient data for comparison" />}
        </ChartCard>

        <ChartCard title="Teacher Workload Distribution" subtitle="Period utilization across staff">
          {workloadData.length > 0 ? (
            <div className="space-y-2.5 max-h-[260px] overflow-y-auto pr-1">
              {workloadData.map((t, i) => {
                const pct = t.utilization_pct || 0;
                const barColor = pct > 90 ? 'bg-red-500' : pct > 70 ? 'bg-amber-500' : 'bg-emerald-500';
                return (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-24 truncate">
                      <p className="text-xs font-medium text-slate-700 truncate">{t.name}</p>
                    </div>
                    <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all duration-500 ${barColor}`} style={{ width: `${Math.min(pct, 100)}%` }} />
                    </div>
                    <span className="text-[10px] text-slate-500 w-16 text-right">{t.assigned_periods}/{t.max_periods} <span className="text-slate-400">({pct}%)</span></span>
                  </div>
                );
              })}
            </div>
          ) : <EmptyChart message="No workload data" />}
        </ChartCard>
      </div>
      </ErrorBoundary>

      {/* Row 4: Fee Defaulters + Fee Collection Rate */}
      <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <ChartCard title="Fee Defaulters by Class" subtitle="Students with overdue fee payments">
          {defaultersData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={defaultersData} barCategoryGap="25%">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="class_name" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `Class ${v}`} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <Tooltip {...CHART_TOOLTIP} formatter={(v, name) => [name === 'Defaulter %' ? `${v}%` : v, name]} />
                <Bar dataKey="defaulter_count" name="Defaulters" fill="#ef4444" radius={[6, 6, 0, 0]} maxBarSize={32} />
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyChart message="No fee defaulter data" />}
        </ChartCard>

        <ChartCard title="Fee Collection Rate" subtitle="% of expected fees collected each month">
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={feeRateData}>
              <defs>
                <linearGradient id="feeRateGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} unit="%" />
              <Tooltip {...CHART_TOOLTIP} formatter={(v) => `${v}%`} />
              <Area type="monotone" dataKey="rate" stroke="#10b981" fill="url(#feeRateGrad)" strokeWidth={2.5} dot={{ r: 3, fill: '#10b981' }} name="Collection Rate" />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      </ErrorBoundary>

      {/* Row 5: Class Toppers */}
      <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 mb-4">
        <ChartCard title="Class Toppers" subtitle="Highest scoring students per class (latest exam)" className="md:col-span-5">
          <div className="space-y-2 max-h-[240px] overflow-y-auto pr-1">
            {toppersData.map((t, i) => (
              <div key={i} className="flex items-center gap-3 p-2.5 rounded-xl border border-slate-100 hover:bg-slate-50 transition-colors">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">#{i + 1}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800 truncate">{t.name}</p>
                  <p className="text-[10px] text-slate-400">Class {t.class_name} • {t.exam}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-emerald-600">{t.percentage}%</p>
                  <p className="text-[10px] text-slate-400">{t.marks}/{t.total}</p>
                </div>
              </div>
            ))}
          </div>
        </ChartCard>

        <ChartCard title="Student Strength Growth" subtitle="Percentage change year-over-year" className="md:col-span-7">
          <div className="flex gap-6">
            <div className="flex-1">
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={enrollmentData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="academic_year" tick={{ fontSize: 9, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                  <Tooltip {...CHART_TOOLTIP} />
                  <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2.5} dot={{ r: 5, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff' }} name="Students" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="w-28 flex flex-col justify-center gap-2">
              {growthData.map((g, i) => (
                <div key={i} className="text-center">
                  <p className="text-[10px] text-slate-400">{g.year}</p>
                  <p className={`text-xs font-bold ${g.growth_pct >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>{g.growth_pct > 0 ? '+' : ''}{g.growth_pct}%</p>
                </div>
              ))}
            </div>
          </div>
        </ChartCard>
      </div>
      </ErrorBoundary>

      {/* Row 6: Revenue Overview */}
      <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <ChartCard title="Fee Revenue vs Target" subtitle="Monthly revenue vs expected collection">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={revenueData} barGap={2} barCategoryGap="20%">
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} tickFormatter={v => `₹${(v/1000)}K`} />
              <Tooltip {...CHART_TOOLTIP} formatter={(v) => `₹${Number(v).toLocaleString()}`} />
              <Bar dataKey="target" name="Target" fill="#e2e8f0" radius={[4, 4, 0, 0]} maxBarSize={28} />
              <Bar dataKey="collected" name="Collected" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={28} />
              <Legend verticalAlign="top" height={30} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Subject-wise Performance" subtitle="Average scores across all classes by subject">
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={subjectData}>
              <PolarGrid stroke="#e2e8f0" />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: '#64748b' }} />
              <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 9, fill: '#94a3b8' }} />
              <Tooltip {...CHART_TOOLTIP} formatter={(v) => `${v}%`} />
              <Radar name="Avg Score" dataKey="avg_score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} strokeWidth={2} />
              <Radar name="Pass Rate" dataKey="pass_rate" stroke="#10b981" fill="#10b981" fillOpacity={0.1} strokeWidth={2} />
              <Legend verticalAlign="bottom" height={30} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
            </RadarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      </ErrorBoundary>

      {/* Row 7: Teacher Absence */}
      <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <ChartCard title="Teacher Leave Patterns" subtitle="Monthly leave days taken by department">
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={leavePatternData}>
              <defs>
                <linearGradient id="teachingGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="nonTeachingGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip {...CHART_TOOLTIP} />
              <Area type="monotone" dataKey="teaching" stroke="#3b82f6" fill="url(#teachingGrad)" strokeWidth={2} name="Teaching" />
              <Area type="monotone" dataKey="non_teaching" stroke="#f59e0b" fill="url(#nonTeachingGrad)" strokeWidth={2} name="Non-Teaching" />
              <Legend verticalAlign="top" height={30} iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Attendance vs Academic Performance" subtitle="Correlation between attendance % and exam scores">
          <ResponsiveContainer width="100%" height={220}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="attendance" name="Attendance" unit="%" tick={{ fontSize: 10, fill: '#64748b' }} domain={[50, 100]} />
              <YAxis dataKey="marks" name="Marks" unit="%" tick={{ fontSize: 10, fill: '#94a3b8' }} domain={[30, 100]} />
              <ZAxis range={[40, 40]} />
              <Tooltip {...CHART_TOOLTIP} formatter={(v, name) => [`${v}%`, name]} cursor={{ strokeDasharray: '3 3' }} />
              <Scatter name="Students" data={scatterData} fill="#8b5cf6" fillOpacity={0.6} />
            </ScatterChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      </ErrorBoundary>

      {/* Row 8: Concession Impact */}
      <ErrorBoundary>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <ChartCard title="Fee Concession Impact" subtitle="Concession distribution and amount by category">
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={concessionData} cx="50%" cy="50%" innerRadius={45} outerRadius={80} dataKey="amount" paddingAngle={3} label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`} labelLine={false}>
                {concessionData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip {...CHART_TOOLTIP} formatter={(v) => `₹${Number(v).toLocaleString()}`} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Transport Utilization" subtitle="Vehicle capacity usage across routes">
          <div className="space-y-3 max-h-[220px] overflow-y-auto pr-1">
            {transportData.map((r, i) => {
              const pct = r.capacity > 0 ? Math.round((r.occupied / r.capacity) * 100) : 0;
              const barColor = pct > 90 ? 'bg-red-500' : pct > 70 ? 'bg-amber-500' : 'bg-emerald-500';
              return (
                <div key={i} className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center flex-shrink-0">
                    <Bus size={14} className="text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-xs font-medium text-slate-700 truncate">{r.route}</p>
                      <span className="text-[10px] text-slate-500">{r.occupied}/{r.capacity} seats</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${barColor} transition-all duration-500`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                  <span className={`text-xs font-bold ${pct > 90 ? 'text-red-600' : pct > 70 ? 'text-amber-600' : 'text-emerald-600'}`}>{pct}%</span>
                </div>
              );
            })}
          </div>
        </ChartCard>
      </div>
      </ErrorBoundary>

    </div>
  );
}

