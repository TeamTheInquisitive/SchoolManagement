import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';
import { queryKeys } from '../config/queryKeys';

const EP = ENDPOINTS.fees;

export const useFees = (params = {}) =>
  useQuery({ queryKey: queryKeys.fees.list(params), queryFn: () => api.get(EP.list, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useFee = (id) =>
  useQuery({ queryKey: queryKeys.fees.detail(id), queryFn: () => api.get(EP.detail(id)).then(r => r.data), enabled: !!id });

export const useStudentFees = (studentId) =>
  useQuery({ queryKey: queryKeys.fees.student(studentId), queryFn: () => api.get(EP.student(studentId)).then(r => r.data), enabled: !!studentId });

export const useStudentReceipt = (studentId) =>
  useQuery({ queryKey: queryKeys.fees.studentReceipt(studentId), queryFn: () => api.get(EP.studentReceipt(studentId)).then(r => r.data), enabled: !!studentId });

export const useFeeStructures = () =>
  useQuery({ queryKey: queryKeys.fees.structures, queryFn: () => api.get(EP.structures).then(r => r.data) });

export const useRecordPayment = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.post(EP.recordPayment(id), data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.fees.all });
      qc.invalidateQueries({ queryKey: queryKeys.fees.studentFeeDetail });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.feeCollection });
    },
  });
};

export const useBulkRecordPayment = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, data }) => api.post(EP.bulkRecordPayment(studentId), data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.fees.all });
      qc.invalidateQueries({ queryKey: queryKeys.fees.studentFeeDetail });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.feeCollection });
    },
  });
};

export const useSendReminder = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.reminders, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.fees.all }),
  });
};

export const useCreateFeeStructure = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.structures, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.fees.all });
      qc.invalidateQueries({ queryKey: queryKeys.settings.feeStructures });
    },
  });
};

export const useCreateFeeRecord = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.list, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.fees.all });
      qc.invalidateQueries({ queryKey: queryKeys.fees.studentFeeDetail });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.feeCollection });
    },
  });
};

export const useUpdateFeeRecord = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.detail(id), data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.fees.all });
      qc.invalidateQueries({ queryKey: queryKeys.fees.studentFeeDetail });
    },
  });
};

export const useDeleteFeeRecord = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.detail(id)).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.fees.all });
      qc.invalidateQueries({ queryKey: queryKeys.fees.studentFeeDetail });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.feeCollection });
    },
  });
};

export const useGenerateDue = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.generateDue, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.fees.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.feeCollection });
    },
  });
};

export const useBulkApplyLateFees = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(`${EP.list}bulk-apply-late-fees/`, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.fees.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.feeCollection });
    },
  });
};

export const exportFeeCsv = () =>
  api.get(EP.export, { responseType: 'blob' }).then(r => r.data);
