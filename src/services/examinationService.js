import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';
import { queryKeys } from '../config/queryKeys';

const EP = ENDPOINTS.examinations;

export const useExams = (params = {}) =>
  useQuery({ queryKey: queryKeys.examinations.list(params), queryFn: () => api.get(EP.list, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useExam = (id) =>
  useQuery({ queryKey: queryKeys.examinations.detail(id), queryFn: () => api.get(EP.detail(id)).then(r => r.data), enabled: !!id });

export const useExamResults = (examId) =>
  useQuery({ queryKey: queryKeys.examinations.results(examId), queryFn: () => api.get(EP.results(examId)).then(r => r.data), enabled: !!examId });

export const useGradeSystem = () =>
  useQuery({ queryKey: queryKeys.examinations.gradeSystem, queryFn: () => api.get(EP.gradeSystem).then(r => r.data) });

export const useUpdateGradeSystem = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.put(EP.gradeSystem, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.examinations.gradeSystem }),
  });
};

export const useCreateExam = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.list, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.examinations.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.all });
    },
  });
};

export const useUpdateExam = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.detail(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.examinations.all }),
  });
};

export const useDeleteExam = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.detail(id)).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.examinations.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.all });
    },
  });
};

export const usePublishExam = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.post(EP.publish(id)).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.examinations.all });
      qc.invalidateQueries({ queryKey: queryKeys.students.all });
    },
  });
};

export const useReportCard = (studentId) =>
  useQuery({ queryKey: queryKeys.examinations.reportCard(studentId), queryFn: () => api.get(EP.reportCard(studentId)).then(r => r.data), enabled: !!studentId });

export const useExaminations = useExams;
