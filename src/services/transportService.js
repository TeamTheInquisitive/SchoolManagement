import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';
import { queryKeys } from '../config/queryKeys';

const EP = ENDPOINTS.transport;

export const useTransportStats = () =>
  useQuery({ queryKey: queryKeys.transport.stats, queryFn: () => api.get(EP.stats).then(r => r.data) });

export const useVehicles = (params = {}) =>
  useQuery({ queryKey: queryKeys.transport.vehicles(params), queryFn: () => api.get(EP.vehicles, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useCreateVehicle = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.vehicles, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useUpdateVehicle = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.vehicleDetail(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useDeleteVehicle = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.vehicleDetail(id)).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useDrivers = (params = {}) =>
  useQuery({ queryKey: queryKeys.transport.drivers(params), queryFn: () => api.get(EP.drivers, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useCreateDriver = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.drivers, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useHelpers = (params = {}) =>
  useQuery({ queryKey: queryKeys.transport.helpers(params), queryFn: () => api.get(EP.helpers, { params }).then(r => r.data) });

export const useCreateHelper = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.helpers, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useRoutes = (params = {}) =>
  useQuery({ queryKey: queryKeys.transport.routes(params), queryFn: () => api.get(EP.routes, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useCreateRoute = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.routes, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useRouteAssignments = (params = {}) =>
  useQuery({ queryKey: queryKeys.transport.assignments(params), queryFn: () => api.get(EP.assignments, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useCreateAssignment = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.assignments, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useDeleteAssignment = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.assignmentDetail(id)).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useUpdateDriver = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.driverDetail(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useDeleteDriver = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.driverDetail(id)).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useUpdateHelper = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.helperDetail(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useDeleteHelper = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.helperDetail(id)).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useUpdateRoute = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.routeDetail(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useDeleteRoute = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => api.delete(EP.routeDetail(id)).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useUpdateAssignment = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => api.put(EP.assignmentDetail(id), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useRouteStudents = (routeId) =>
  useQuery({ queryKey: queryKeys.transport.routeStudents(routeId), queryFn: () => api.get(EP.routeStudents(routeId)).then(r => r.data), enabled: !!routeId });

export const useAssignRouteStudents = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ routeId, data }) => api.post(EP.routeStudents(routeId), data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

export const useRemoveRouteStudent = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ routeId, studentId }) => api.delete(EP.removeRouteStudent(routeId, studentId)).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.transport.all }),
  });
};

