import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';
import { queryKeys } from '../config/queryKeys';

const EP = ENDPOINTS.teachers;

export const useTeachers = (params = {}) =>
  useQuery({ queryKey: queryKeys.teachers.list(params), queryFn: () => api.get(EP.list, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useTeacher = (id) =>
  useQuery({ queryKey: queryKeys.teachers.detail(id), queryFn: () => api.get(EP.detail(id)).then(r => r.data), enabled: !!id });

export const useTeacherAssignments = (id) =>
  useQuery({ queryKey: queryKeys.teachers.assignments(id), queryFn: () => api.get(EP.assignments(id)).then(r => r.data), enabled: !!id });

export const useTeacherHistory = (id) =>
  useQuery({ queryKey: queryKeys.teachers.history(id), queryFn: () => api.get(EP.history(id)).then(r => r.data), enabled: !!id });

export const useTeachersByClass = (params = {}) =>
  useQuery({ queryKey: queryKeys.teachers.byClass(params), queryFn: () => api.get(EP.byClass, { params }).then(r => r.data), enabled: !!params.class_name });

export const useCreateTeacher = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.list, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.teachers.all });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.lookup });
      qc.invalidateQueries({ queryKey: queryKeys.staff.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.all });
    },
  });
};

export const useUpdateTeacher = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.detail(id), data).then(r => r.data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.teachers.all });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.lookup });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.detail(id) });
    },
  });
};

export const useDeleteTeacher = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.detail(id)).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.teachers.all });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.lookup });
      qc.invalidateQueries({ queryKey: queryKeys.staff.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.all });
      qc.invalidateQueries({ queryKey: queryKeys.timetable.all });
    },
  });
};

export const useAssignClass = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.post(EP.assignClass(id), data).then(r => r.data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.teachers.all });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.assignments(id) });
      qc.invalidateQueries({ queryKey: queryKeys.timetable.all });
    },
  });
};

export const useBulkAssign = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.post(EP.bulkAssign(id), data).then(r => r.data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.teachers.all });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.assignments(id) });
      qc.invalidateQueries({ queryKey: queryKeys.timetable.all });
    },
  });
};

export const useRemoveClassAssignment = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ teacherId, assignmentId }) => api.delete(EP.removeAssignment(teacherId, assignmentId)).then(r => r.data),
    onSuccess: (_, { teacherId }) => {
      qc.invalidateQueries({ queryKey: queryKeys.teachers.all });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.assignments(teacherId) });
      qc.invalidateQueries({ queryKey: queryKeys.timetable.all });
    },
  });
};

export const useResetTeacherPassword = () => {
  return useMutation({
    mutationFn: ({ id, password }) => api.post(EP.resetPassword(id), { password }).then(r => r.data),
  });
};

export const useTeacherAwards = (id) =>
  useQuery({ queryKey: queryKeys.teachers.awards(id), queryFn: () => api.get(EP.awards(id)).then(r => r.data), enabled: !!id });

export const useCreateTeacherAward = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.post(EP.awards(id), data).then(r => r.data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.teachers.detail(id) });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.awards(id) });
    },
  });
};

export const useUpdateTeacherAward = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, awardId, data }) => api.put(EP.awardDetail(id, awardId), data).then(r => r.data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.teachers.detail(id) });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.awards(id) });
    },
  });
};

export const useDeleteTeacherAward = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, awardId }) => api.delete(EP.awardDetail(id, awardId)),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.teachers.detail(id) });
      qc.invalidateQueries({ queryKey: queryKeys.teachers.awards(id) });
    },
  });
};
