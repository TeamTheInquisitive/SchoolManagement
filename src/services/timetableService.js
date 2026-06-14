import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';
import { queryKeys } from '../config/queryKeys';

const EP = ENDPOINTS.timetable;

export const useClassSections = () =>
  useQuery({ queryKey: queryKeys.settings.classSections, queryFn: () => api.get(ENDPOINTS.settings.classSections).then(r => r.data) });

export const usePeriods = () =>
  useQuery({ queryKey: queryKeys.timetable.periods, queryFn: () => api.get(EP.periods).then(r => r.data) });

export const useTimetable = (params = {}) =>
  useQuery({
    queryKey: queryKeys.timetable.grid(params),
    queryFn: () => api.get(EP.list, { params }).then(r => r.data),
    enabled: !!params.class_section_id,
  });

export const useCreateSlot = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.slot, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.timetable.all }),
  });
};

export const useUpdateSlot = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.slotDetail(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.timetable.all }),
  });
};

export const useDeleteSlot = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.slotDetail(id)).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.timetable.all }),
  });
};

export const useSubjects = () =>
  useQuery({ queryKey: queryKeys.settings.subjects, queryFn: () => api.get(ENDPOINTS.settings.subjects).then(r => r.data) });

export const useAssignSlot = useCreateSlot;
export const useTeachers = () =>
  useQuery({ queryKey: queryKeys.teachers.lookup, queryFn: () => api.get(ENDPOINTS.teachers.list).then(r => r.data) });

export const useTeacherAvailability = (periodConfigId, day) =>
  useQuery({
    queryKey: queryKeys.timetable.teacherAvailability(periodConfigId, day),
    queryFn: () => api.get(`${EP.list}/teacher-availability`, { params: { period_config_id: periodConfigId, day } }).then(r => r.data),
    enabled: !!periodConfigId && !!day,
  });

export const useCreatePeriod = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.periods, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.timetable.periods });
      qc.invalidateQueries({ queryKey: queryKeys.timetable.all });
    },
  });
};

export const useUpdatePeriod = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(`${EP.periods}/${id}`, data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.timetable.periods });
      qc.invalidateQueries({ queryKey: queryKeys.timetable.all });
    },
  });
};

export const useDeletePeriod = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(`${EP.periods}/${id}`).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.timetable.periods });
      qc.invalidateQueries({ queryKey: queryKeys.timetable.all });
    },
  });
};

export const useSlotTypes = () =>
  useQuery({
    queryKey: queryKeys.timetable.slotTypes,
    queryFn: () => api.get(ENDPOINTS.settings.enums('slot_types')).then(r => r.data),
  });

export const useUpdateSlotTypes = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (values) => api.put(ENDPOINTS.settings.enums('slot_types'), { values }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.timetable.slotTypes }),
  });
};
