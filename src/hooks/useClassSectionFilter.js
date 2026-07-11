import { useClassSectionFilter as useSharedClassSectionFilter } from 'school-erp-ui-shared';
import api from '../services/api';
import { ENDPOINTS } from '../config/api';

export function useClassSectionFilter(options) {
  return useSharedClassSectionFilter(
    () => api.get(ENDPOINTS.settings.classSections).then(r => r.data),
    options
  );
}
