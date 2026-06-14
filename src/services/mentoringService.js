import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';

const EP = ENDPOINTS.mentoring;

export const useMentorList = () =>
  useQuery({ queryKey: ['mentoring', 'list'], queryFn: () => api.get(EP.list).then(r => r.data) });

export const useMentorStudentsByTeacher = (staffId) =>
  useQuery({
    queryKey: ['mentoring', 'teacher-students', staffId],
    queryFn: () => api.get(EP.teacherStudents(staffId)).then(r => r.data),
    enabled: !!staffId,
  });

export const useMentorTeachers = () =>
  useQuery({ queryKey: ['mentoring', 'teachers'], queryFn: () => api.get(EP.teachers).then(r => r.data) });

export const useMentorStudents = (classSectionId) =>
  useQuery({
    queryKey: ['mentoring', 'students', classSectionId],
    queryFn: () => api.get(EP.students, { params: { class_section_id: classSectionId } }).then(r => r.data),
    enabled: !!classSectionId,
  });

export const useAssignMentor = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.assign, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['mentoring'] }),
  });
};

export const useRemoveMentor = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.remove(id)).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['mentoring'] }),
  });
};

export const useShuffleAssign = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post(EP.shuffleAssign).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['mentoring'] }),
  });
};
