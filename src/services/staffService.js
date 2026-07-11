import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';
import { queryKeys } from '../config/queryKeys';

const EP = ENDPOINTS.staff;

export const useStaff = (params = {}) =>
  useQuery({ queryKey: queryKeys.staff.list(params), queryFn: () => api.get(EP.list, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useCreateStaff = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.list, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.staff.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.all });
    },
  });
};

export const useUpdateStaff = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.detail(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.staff.all }),
  });
};

export const useDeleteStaff = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.detail(id)).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.staff.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.all });
      qc.invalidateQueries({ queryKey: queryKeys.payroll.all });
    },
  });
};
