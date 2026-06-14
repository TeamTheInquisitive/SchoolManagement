import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';
import { ENDPOINTS } from '../config/api';

const EP = ENDPOINTS.notifications;

export const useNotifications = (params = {}) =>
  useQuery({ queryKey: ['notifications', params], queryFn: () => api.get(EP.list, { params }).then(r => r.data), placeholderData: (prev) => prev });

export const useNotification = (id) =>
  useQuery({ queryKey: ['notifications', id], queryFn: () => api.get(EP.detail(id)).then(r => r.data), enabled: !!id });

export const useCreateNotification = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => api.post(EP.list, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  });
};

export const useCustomTemplates = () =>
  useQuery({ queryKey: ['notifications', 'templates'], queryFn: () => api.get(EP.templates).then(r => r.data) });

export const useUpdateCustomTemplates = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (templates) => api.put(EP.templates, { templates }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications', 'templates'] }),
  });
};
