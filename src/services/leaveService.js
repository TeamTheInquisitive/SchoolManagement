import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';
import { queryKeys } from '../config/queryKeys';

const EP = ENDPOINTS.leaves;

export const useLeaves = (params = {}) =>
  useQuery({ queryKey: queryKeys.leaves.list(params), queryFn: () => api.get(EP.list, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useTeacherLeaves = (teacherId) =>
  useQuery({ queryKey: queryKeys.leaves.teacher(teacherId), queryFn: () => api.get(EP.teacher(teacherId)).then(r => r.data), enabled: !!teacherId });

export const useLeaveBalances = () =>
  useQuery({ queryKey: queryKeys.leaves.balances, queryFn: () => api.get(EP.balances).then(r => r.data) });

export const useLeavePolicy = () =>
  useQuery({ queryKey: queryKeys.leaves.policy, queryFn: () => api.get(EP.policy).then(r => r.data) });

export const useUpdateLeavePolicy = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.put(EP.policy, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.leaves.all });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.all });
      qc.invalidateQueries({ queryKey: queryKeys.staff.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.all });
    },
  });
};

export const useLeaveCalendar = (params = {}) =>
  useQuery({ queryKey: queryKeys.leaves.calendar(params), queryFn: () => api.get(EP.calendar, { params }).then(r => r.data) });

export const useApproveLeave = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.post(EP.approve(id), data).then(r => r.data),
    onMutate: async ({ id }) => {
      await qc.cancelQueries({ queryKey: queryKeys.leaves.all });
      const queries = qc.getQueriesData({ queryKey: queryKeys.leaves.all });
      queries.forEach(([key, data]) => {
        if (data?.results) {
          qc.setQueryData(key, {
            ...data,
            results: data.results.map(l => l.id === id ? { ...l, status: 'Approved' } : l),
            overall_summary: data.overall_summary ? { ...data.overall_summary, pending: (data.overall_summary.pending || 1) - 1, approved: (data.overall_summary.approved || 0) + 1 } : data.overall_summary,
          });
        }
      });
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: queryKeys.leaves.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.leaveOverview });
    },
  });
};

export const useRejectLeave = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.post(EP.reject(id), data).then(r => r.data),
    onMutate: async ({ id }) => {
      await qc.cancelQueries({ queryKey: queryKeys.leaves.all });
      const queries = qc.getQueriesData({ queryKey: queryKeys.leaves.all });
      queries.forEach(([key, data]) => {
        if (data?.results) {
          qc.setQueryData(key, {
            ...data,
            results: data.results.map(l => l.id === id ? { ...l, status: 'Rejected' } : l),
            overall_summary: data.overall_summary ? { ...data.overall_summary, pending: (data.overall_summary.pending || 1) - 1, rejected: (data.overall_summary.rejected || 0) + 1 } : data.overall_summary,
          });
        }
      });
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: queryKeys.leaves.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.leaveOverview });
    },
  });
};

export const useAllocateLeaves = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.allocate, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.leaves.all });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.all });
      qc.invalidateQueries({ queryKey: queryKeys.staff.all });
    },
  });
};
