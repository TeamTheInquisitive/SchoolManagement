import { useQuery } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';

const EP = ENDPOINTS.dashboard;

export const useDashboardStats = () =>
  useQuery({ queryKey: ['dashboard', 'stats'], queryFn: () => api.get(EP.stats).then(r => r.data) });

export const useAttendanceTrends = () =>
  useQuery({ queryKey: ['dashboard', 'attendance-trends'], queryFn: () => api.get(EP.attendanceTrends).then(r => r.data) });

export const useFeeCollectionStatus = () =>
  useQuery({ queryKey: ['dashboard', 'fee-collection'], queryFn: () => api.get(EP.feeCollection).then(r => r.data) });

export const useStudentDistribution = () =>
  useQuery({ queryKey: ['dashboard', 'student-distribution'], queryFn: () => api.get(EP.studentDistribution).then(r => r.data) });

export const useRecentActivities = () =>
  useQuery({ queryKey: ['dashboard', 'recent-activities'], queryFn: () => api.get(EP.recentActivities).then(r => r.data) });

export const useLeaveOverview = () =>
  useQuery({ queryKey: ['dashboard', 'leave-overview'], queryFn: () => api.get(EP.leaveOverview).then(r => r.data) });

export const useLowAttendance = () =>
  useQuery({ queryKey: ['dashboard', 'low-attendance'], queryFn: () => api.get(EP.lowAttendance).then(r => r.data) });

export const useBirthdays = () =>
  useQuery({ queryKey: ['dashboard', 'birthdays'], queryFn: () => api.get('/admin/dashboard/birthdays').then(r => r.data).catch(() => ({ today: [], upcoming: [] })) });

export const useAnalyticsAttendanceByClass = () =>
  useQuery({ queryKey: ['analytics', 'attendance-by-class'], queryFn: () => api.get(EP.analyticsAttendanceByClass).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsFeeTrend = () =>
  useQuery({ queryKey: ['analytics', 'fee-trend'], queryFn: () => api.get(EP.analyticsFeeTrend).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsExamPerformance = () =>
  useQuery({ queryKey: ['analytics', 'exam-performance'], queryFn: () => api.get(EP.analyticsExamPerformance).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsTeacherWorkload = () =>
  useQuery({ queryKey: ['analytics', 'teacher-workload'], queryFn: () => api.get(EP.analyticsTeacherWorkload).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsEnrollmentTrend = () =>
  useQuery({ queryKey: ['analytics', 'enrollment-trend'], queryFn: () => api.get(EP.analyticsEnrollmentTrend).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsFeeDefaulters = () =>
  useQuery({ queryKey: ['analytics', 'fee-defaulters'], queryFn: () => api.get(EP.analyticsFeeDefaulters).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsAttendanceComparison = () =>
  useQuery({ queryKey: ['analytics', 'attendance-comparison'], queryFn: () => api.get(EP.analyticsAttendanceComparison).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsStudentTypeRatio = () =>
  useQuery({ queryKey: ['analytics', 'student-type-ratio'], queryFn: () => api.get(EP.analyticsStudentTypeRatio).then(r => r.data).catch(() => ({ dayscholar: 0, hostler: 0, total: 0 })) });

export const useAnalyticsSubjectPerformance = () =>
  useQuery({ queryKey: ['analytics', 'subject-performance'], queryFn: () => api.get(EP.analyticsSubjectPerformance).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsClassToppers = () =>
  useQuery({ queryKey: ['analytics', 'class-toppers'], queryFn: () => api.get(EP.analyticsClassToppers).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsCorrelation = () =>
  useQuery({ queryKey: ['analytics', 'correlation'], queryFn: () => api.get(EP.analyticsCorrelation).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsRevenueTarget = () =>
  useQuery({ queryKey: ['analytics', 'revenue-target'], queryFn: () => api.get(EP.analyticsRevenueTarget).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsTeacherLeavePatterns = () =>
  useQuery({ queryKey: ['analytics', 'teacher-leave-patterns'], queryFn: () => api.get(EP.analyticsTeacherLeavePatterns).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsTransportUtilization = () =>
  useQuery({ queryKey: ['analytics', 'transport-utilization'], queryFn: () => api.get(EP.analyticsTransportUtilization).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsConcessionSummary = () =>
  useQuery({ queryKey: ['analytics', 'concession-summary'], queryFn: () => api.get(EP.analyticsConcessionSummary).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsGrowthRate = () =>
  useQuery({ queryKey: ['analytics', 'growth-rate'], queryFn: () => api.get(EP.analyticsGrowthRate).then(r => r.data).catch(() => ({ data: [] })) });

export const useAnalyticsFeeCollectionRate = () =>
  useQuery({ queryKey: ['analytics', 'fee-collection-rate'], queryFn: () => api.get(EP.analyticsFeeCollectionRate).then(r => r.data).catch(() => ({ data: [] })) });
