import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';
import { queryKeys } from '../config/queryKeys';

const EP = ENDPOINTS.students;

export const useStudents = (params = {}) =>
  useQuery({ queryKey: queryKeys.students.list(params), queryFn: () => api.get(EP.list, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useStudent = (id) =>
  useQuery({ queryKey: queryKeys.students.detail(id), queryFn: () => api.get(EP.detail(id)).then(r => r.data), enabled: !!id });

export const useStudentExamResults = (id) =>
  useQuery({ queryKey: queryKeys.students.examResults(id), queryFn: () => api.get(EP.examResults(id)).then(r => r.data), enabled: !!id });

export const useStudentFeeHistory = (id) =>
  useQuery({ queryKey: queryKeys.students.feeHistory(id), queryFn: () => api.get(EP.feeHistory(id)).then(r => r.data), enabled: !!id });

export const useStudentAttendance = (id) =>
  useQuery({ queryKey: queryKeys.students.attendance(id), queryFn: () => api.get(EP.attendance(id)).then(r => r.data), enabled: !!id });

export const useStudentActivities = (id) =>
  useQuery({ queryKey: queryKeys.students.activities(id), queryFn: () => api.get(EP.activities(id)).then(r => r.data), enabled: !!id });

export const useStudentDisciplinary = (id) =>
  useQuery({ queryKey: queryKeys.students.disciplinary(id), queryFn: () => api.get(EP.disciplinary(id)).then(r => r.data), enabled: !!id });

export const useStudentParentMeetings = (id) =>
  useQuery({ queryKey: queryKeys.students.parentMeetings(id), queryFn: () => api.get(EP.parentMeetings(id)).then(r => r.data), enabled: !!id });

export const useCreateStudent = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.list, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.students.all });
      qc.invalidateQueries({ queryKey: queryKeys.fees.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.all });
    },
  });
};

export const useUpdateStudent = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.detail(id), data).then(r => r.data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: queryKeys.students.all });
      qc.invalidateQueries({ queryKey: queryKeys.fees.student(id) });
    },
  });
};

export const useDeleteStudent = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.detail(id)).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.students.all });
      qc.invalidateQueries({ queryKey: queryKeys.fees.all });
      qc.invalidateQueries({ queryKey: queryKeys.dashboard.all });
      qc.invalidateQueries({ queryKey: queryKeys.transport.all });
    },
  });
};

export const useStudentDisciplinaryRecords = useStudentDisciplinary;

export const useResetStudentPassword = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, password }) => api.post(EP.resetPassword(id), { password }).then(r => r.data),
  });
};

export const useCreateAward = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, data }) => api.post(EP.awards(studentId), data).then(r => r.data),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.activities(studentId) }),
  });
};

export const useUpdateAward = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, awardId, data }) => api.put(EP.awardDetail(studentId, awardId), data).then(r => r.data),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.activities(studentId) }),
  });
};

export const useDeleteAward = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, awardId }) => api.delete(EP.awardDetail(studentId, awardId)),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.activities(studentId) }),
  });
};

export const useCreateActivity = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, data }) => api.post(EP.activities(studentId), data).then(r => r.data),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.activities(studentId) }),
  });
};

export const useCreateParentMeeting = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, data }) => api.post(EP.parentMeetings(studentId), data).then(r => r.data),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.parentMeetings(studentId) }),
  });
};

export const useUpdateParentMeeting = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, meetingId, data }) => api.put(EP.parentMeetingDetail(studentId, meetingId), data).then(r => r.data),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.parentMeetings(studentId) }),
  });
};

export const useDeleteParentMeeting = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, meetingId }) => api.delete(EP.parentMeetingDetail(studentId, meetingId)),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.parentMeetings(studentId) }),
  });
};

export const useUpdateActivity = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, activityId, data }) => api.put(EP.activityDetail(studentId, activityId), data).then(r => r.data),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.activities(studentId) }),
  });
};

export const useDeleteActivity = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, activityId }) => api.delete(EP.activityDetail(studentId, activityId)),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.activities(studentId) }),
  });
};

export const useCreateDisciplinaryRecord = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, data }) => api.post(EP.disciplinary(studentId), data).then(r => r.data),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.disciplinary(studentId) }),
  });
};

export const useUpdateDisciplinaryRecord = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, recordId, data }) => api.put(EP.disciplinaryDetail(studentId, recordId), data).then(r => r.data),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.disciplinary(studentId) }),
  });
};

export const useDeleteDisciplinaryRecord = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, recordId }) => api.delete(EP.disciplinaryDetail(studentId, recordId)),
    onSuccess: (_, { studentId }) => qc.invalidateQueries({ queryKey: queryKeys.students.disciplinary(studentId) }),
  });
};
