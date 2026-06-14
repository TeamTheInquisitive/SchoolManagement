import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';

const EP = ENDPOINTS.settings;

export const useSchoolProfile = () =>
  useQuery({ queryKey: ['settings', 'school'], queryFn: () => api.get(EP.school).then(r => r.data) });

export const useAcademicYear = () =>
  useQuery({ queryKey: ['settings', 'academic-year'], queryFn: () => api.get(EP.academicYear).then(r => r.data) });

export const useAcademicYears = () =>
  useQuery({ queryKey: ['settings', 'academic-years'], queryFn: () => api.get(EP.academicYears).then(r => r.data) });

export const useCreateAcademicYear = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.academicYears, data).then(r => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['settings', 'academic-year'] }); qc.invalidateQueries({ queryKey: ['settings', 'academic-years'] }); },
  });
};

export const useUpdateAcademicYearById = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) => api.put(EP.academicYearDetail(id), data).then(r => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['settings', 'academic-year'] }); qc.invalidateQueries({ queryKey: ['settings', 'academic-years'] }); },
  });
};

export const useDeleteAcademicYear = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.academicYearDetail(id)).then(r => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['settings', 'academic-year'] }); qc.invalidateQueries({ queryKey: ['settings', 'academic-years'] }); },
  });
};

export const useSetCurrentAcademicYear = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.post(EP.academicYearSetCurrent(id)).then(r => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['settings', 'academic-year'] }); qc.invalidateQueries({ queryKey: ['settings', 'academic-years'] }); },
  });
};

export const useClassSections = () =>
  useQuery({ queryKey: ['settings', 'class-sections'], queryFn: () => api.get(EP.classSections).then(r => r.data) });

export const useSubjects = () =>
  useQuery({ queryKey: ['settings', 'subjects'], queryFn: () => api.get(EP.subjects).then(r => r.data) });

export const useUpdateSchoolProfile = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.put(EP.school, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'school'] }),
  });
};

export const useUpdateAcademicYear = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.put(EP.academicYear, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'academic-year'] }),
  });
};

export const useCreateClasses = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (classes) => api.post(EP.createClasses, { classes }).then(r => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['settings', 'class-sections'] }); qc.invalidateQueries({ queryKey: ['class-sections-lookup'] }); },
  });
};

export const useCreateSections = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.createSections, data).then(r => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['settings', 'class-sections'] }); qc.invalidateQueries({ queryKey: ['class-sections-lookup'] }); },
  });
};

export const useDeleteClass = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.deleteClass(id)).then(r => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['settings', 'class-sections'] }); qc.invalidateQueries({ queryKey: ['class-sections-lookup'] }); },
  });
};

export const useDeleteClassSection = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.deleteClassSection(id)).then(r => r.data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['settings', 'class-sections'] }); qc.invalidateQueries({ queryKey: ['class-sections-lookup'] }); },
  });
};

export const useCreateSubjects = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (subjects) => api.post(EP.createSubjects, { subjects }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'subjects'] }),
  });
};

export const useUpdateSubject = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) => api.put(EP.subjectDetail(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'subjects'] }),
  });
};

export const useDeleteSubject = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.subjectDetail(id)).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['settings', 'subjects'] });
      qc.invalidateQueries({ queryKey: ['settings', 'class-subjects'] });
    },
  });
};

export const useClassSubjects = () =>
  useQuery({ queryKey: ['settings', 'class-subjects'], queryFn: () => api.get(EP.classSubjects).then(r => r.data) });

export const useUpdateClassSubjects = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ classId, subject_ids }) => api.put(EP.updateClassSubjects(classId), { subject_ids }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'class-subjects'] }),
  });
};

export const useFeeStructures = () =>
  useQuery({ queryKey: ['settings', 'fee-structures'], queryFn: () => api.get(EP.feeStructures).then(r => r.data) });

export const useCreateFeeStructure = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.feeStructures, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'fee-structures'] }),
  });
};

export const useUpdateFeeStructure = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...data }) => api.put(EP.feeStructureDetail(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'fee-structures'] }),
  });
};

export const useDeleteFeeStructure = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.feeStructureDetail(id)).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'fee-structures'] }),
  });
};

export const useUploadLogo = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file) => {
      const formData = new FormData();
      formData.append('file', file);
      return api.post(EP.uploadLogo, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }).then(r => r.data);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'school'] }),
  });
};

export const useIdGenerationConfig = () =>
  useQuery({ queryKey: ['settings', 'id-generation'], queryFn: () => api.get(EP.idGeneration).then(r => r.data) });

export const useUpdateIdGenerationConfig = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.put(EP.idGeneration, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'id-generation'] }),
  });
};

export const fetchNextId = (type) => api.get(EP.nextId(type)).then(r => r.data);

export const useHolidays = () =>
  useQuery({ queryKey: ['settings', 'holidays'], queryFn: () => api.get(EP.holidays).then(r => r.data) });

export const useUpdateHolidays = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.put(EP.holidays, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'holidays'] }),
  });
};

export const useAttendanceConfig = () =>
  useQuery({ queryKey: ['settings', 'attendance-config'], queryFn: () => api.get(EP.attendanceConfig).then(r => r.data) });

export const useUpdateAttendanceConfig = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.put(EP.attendanceConfig, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings', 'attendance-config'] }),
  });
};

export const useClassSectionAssignments = () =>
  useQuery({ queryKey: ['settings', 'class-section-assignments'], queryFn: () => api.get(EP.classSectionAssignments).then(r => r.data) });

export const useUpdateClassSectionAssignment = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ classSectionId, data }) => api.put(EP.updateClassSectionAssignment(classSectionId), data).then(r => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['settings', 'class-section-assignments'] });
      qc.invalidateQueries({ queryKey: ['settings', 'class-subjects'] });
      qc.invalidateQueries({ queryKey: ['teachers'] });
      qc.invalidateQueries({ queryKey: ['teachers-list'] });
      qc.invalidateQueries({ queryKey: ['timetable'] });
    },
  });
};
