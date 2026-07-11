import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';
import { queryKeys } from '../config/queryKeys';

const EP = ENDPOINTS.payroll;

export const usePayroll = (params = {}) =>
  useQuery({ queryKey: queryKeys.payroll.list(params), queryFn: () => api.get(EP.list, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useSalaryStructure = (employeeId) =>
  useQuery({ queryKey: queryKeys.payroll.salaryStructure(employeeId), queryFn: () => api.get(EP.salaryStructure(employeeId)).then(r => r.data), enabled: !!employeeId });

export const useSalaryRevisions = (staffId) =>
  useQuery({ queryKey: queryKeys.payroll.salaryRevisions(staffId), queryFn: () => api.get(EP.salaryRevisions(staffId)).then(r => r.data), enabled: !!staffId });

export const useGeneratePayroll = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.generate, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.payroll.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.all });
    },
  });
};

export const useUpdatePayslip = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.update(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.payroll.all }),
  });
};

export const useRecordPayment = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.post(EP.pay(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.payroll.all }),
  });
};

export const useMarkAllPaid = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.markAllPaid, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.payroll.all }),
  });
};

export const usePayrollAdvances = () =>
  useQuery({ queryKey: queryKeys.payroll.advances, queryFn: () => api.get(EP.advances).then(r => r.data) });

export const useApproveAdvance = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.post(EP.approveAdvance(id)).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.payroll.all }),
  });
};

export const useRunPayroll = useGeneratePayroll;
export const useSalaryAdvances = usePayrollAdvances;
export const useApproveSalaryAdvance = useApproveAdvance;

export const useRejectSalaryAdvance = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.post(`${ENDPOINTS.payroll.advances}${id}/reject/`).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.payroll.all }),
  });
};

export const useUndoAllPaid = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.undoAllPaid, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.payroll.all }),
  });
};

export const useDeletePayroll = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.deletePayroll, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.payroll.all }),
  });
};
